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
from api import w_errors as errors, w_juju as juju, w_monitoring as monitoring #pylint: disable = e0401
from sojobo_api import create_response #pylint: disable = e0401


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
        monitoring.check_authentication(data['api_key'])
        file_path = '{}/elastic_ip.yaml'.format(monitoring.get_monitor_dir())
        monitoring.update_ip_list(file_path, data)
        code, response = 200, 'succesfully connected to SOJOBO-api'
    except KeyError:
        code, response = errors.invalid_data()
    return create_response(code, {'message': response})

@MONITOR.route('/<controller>/<model>', methods=['GET'])
def get_model_monitor(controller, model):
    try:
        juju.authenticate(request.args['api_key'], request.authorization, controller, model)
        es_ip = monitoring.receive_ip_address(controller, model)
        elasticsearch = monitoring.connect_to_elasticsearch(es_ip)
        result = elasticsearch.search(index='metricbeat-*', body={"query": {"match_all": {}}})
        code, response = 200, result
    except KeyError:
        code, response = errors.invalid_data()
    return create_response(code, {'message': response})

@MONITOR.route('/<controller>/<model>/application/<application>', methods=['GET'])
def get_application_monitor(controller, model, application):
    try:
        juju.authenticate(request.args['api_key'], request.authorization, controller, model)
        es_ip = monitoring.receive_ip_address(controller, model)
        elasticsearch = monitoring.connect_to_elasticsearch(es_ip)
        machines = monitoring.get_machines_by_application(controller, model, application, request.args['api_key'])
        match = ''
        for machine in machines.items():
            match += '{"match":{"beats.name" : {}}},\n'.format(machine) #pylint: disable = W1303
        match = match[:-2]
        result = elasticsearch.search(
            index='metricbeat-*',
            body={"query": match}
            )
        code, response = 200, result
    except KeyError:
        code, response = errors.invalid_data()
    return create_response(code, response)
