# !/usr/bin/env python3
# Copyright (C) 2016  Qrama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# pylint: disable=c0111,c0301,c0325,w0406
from flask import request, Blueprint
from sojobo_api.api import w_errors as errors, w_juju as juju, w_monitoring as monitoring #pylint: disable = e0401

MONITOR = Blueprint('monitoring', __name__)

def get():
    return MONITOR

#################
# Monitor route #
#################

@MONITOR.route('/ping', methods=['PUT'])
def get_elasticsearch_ip():
    data = request.json
    try:
        monitoring.check_authentication(request.headers['api-key'])
        file_path = '{}/elastic_ip.yaml'.format(monitoring.get_monitor_dir())
        monitoring.update_ip_list(file_path, data)
        code, response = 200, 'succesfully connected to SOJOBO-api'
    except KeyError:
        code, response = errors.invalid_data()
    return juju.create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>', methods=['GET'])
def get_model_monitor(controller, model):
    try:
        juju.authenticate(request.headers['api-key'], request.authorization, controller, model)
        es_ip = monitoring.receive_ip_address(controller, model)
        elasticsearch = monitoring.connect_to_elasticsearch(es_ip)
        result = elasticsearch.search(index='metricbeat-*', body={"query": {"match_all": {}}})
        reformat_result = monitoring.reformat_json(result)
        code, response = 200, reformat_result
    except KeyError:
        code, response = errors.invalid_data()
    return juju.create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>', methods=['GET'])
def get_application_monitor(controller, model, application):
    try:
        juju.authenticate(request.headers['api-key'], request.authorization, controller, model)
        match = "fields.application: {}*".format(application)
        reformat_result = monitoring.reformat_json(monitoring.execute_specific_query(controller, model, match))
        code, response = 200, reformat_result
    except KeyError:
        code, response = errors.invalid_data()
    return juju.create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>', methods=['PUT'])
def add_monitoring_application(controller, model, application):
    try:
        token = juju.authenticate(request.headers['api-key'], request.authorization,
                                  juju.check_input(controller), juju.check_input(model))
        if token.m_access == 'admin':
            app = juju.check_input(application)
            if juju.app_exists(token, app):
                res = monitoring.add_application(token, app)
                if res == 'OK':
                    code, response = 200, juju.get_application_info(token, app)
                else:
                    code, response = errors.invalid_series()
            else:
                code, response = errors.does_not_exist('application')
        else:
            code, response = errors.no_permission()
    except KeyError:
        code, response = errors.invalid_data()
    return juju.create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>', methods=['DELETE'])
def remove_monitoring_application(controller, model, application):
    try:
        token = juju.authenticate(request.headers['api-key'], request.authorization,
                                  juju.check_input(controller), juju.check_input(model))
        if token.m_access == 'admin':
            app = juju.check_input(application)
            if juju.app_exists(token, app):
                monitoring.remove_application(token, app)
                code, response = 200, juju.get_application_info(token, app)
            else:
                code, response = errors.does_not_exist('application')
        else:
            code, response = errors.no_permission()
    except KeyError:
        code, response = errors.invalid_data()
    return juju.create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>/units/<unitnr>', methods=['GET'])
def get_unit_monitor(controller, model, application, unitnr):
    try:
        juju.authenticate(request.headers['api-key'], request.authorization, controller, model)
        machines = monitoring.get_machines_by_application(controller, model, application, request)
        unit = ''
        for machine in machines:
            if machine['name'] == "{}/{}".format(application, unitnr):
                unit = machine['instance-id']
        match = "fields.instance-id: {}*".format(unit)
        reformat_result = monitoring.reformat_json(monitoring.execute_specific_query(controller, model, match))
        code, response = 200, reformat_result
    except KeyError:
        code, response = errors.invalid_data()
    return juju.create_response(code, response)
