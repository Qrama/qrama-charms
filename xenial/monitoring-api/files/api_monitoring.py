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
import json
import requests
from flask import request, Blueprint
from sojobo_api import settings
from sojobo_api.api import w_errors as errors, w_monitoring as monitoring, w_juju as juju, w_mongo as mongo #pylint: disable = e0401
from sojobo_api.api.w_juju import check_input, get_api_key, create_response, execute_task, Model_Connection


MONITOR = Blueprint('monitoring', __name__)


def get():
    return MONITOR
#################
# Monitor route #
#################
@MONITOR.route('', methods=['GET'])
def status():
    res = {'Redis': 'Check not implemented',
           'RabbitMQ': 'Check not implemented',
           'Sensu-server': 'Check not implemented',
           'Sensu-API': 'Check not implemented',
           'Sensu-connection': {
               'Redis': 'Check not implemented',
               'RabbitMQ': 'Check not implemented'
           }
          }
    return create_response(200, res)


@MONITOR.route('', methods=['POST'])
def event_data():
    #monitoring.authenticate(request.authorization)
    monitoring.save_data(json.loads(request.data.decode('utf-8')))
    return create_response(200, 'OK')


# @MONITOR.route('/controllers', methods=['GET'])
# def get_controllers_monitor(controller):
#     req = requests.get('http://ip/users/{}'.format(request.authorization.username),
#                        auth=(request.authorization.username, request.authorization.password),
#                        headers={'api-key': get_api_key()})
#     if req.status_code == 200:
#         res = monitoring.get_controllers(req.json()['controllers'])
#         return create_response(200, res)
#     else:
#         return create_response(req.status_code, req.text)
#
#
@MONITOR.route('/controllers/<controller>', methods=['GET'])
def get_controller_monitor(controller):
    req = requests.get('https://collision-backend.tengu.io/users/{}'.format(request.path[1:].split('/', 1)[1]),
                       auth=(request.authorization.username, request.authorization.password),
                       headers={'api-key': get_api_key()})
    if req.status_code == 200:
        res = monitoring.get_models(check_input(controller), req.json())
        return create_response(200, res)
    else:
        return create_response(req.status_code, req.text)


@MONITOR.route('/controllers/<controller>/models/<model>', methods=['GET'])
def get_model_monitor(controller, model):
    req = requests.get('https://collision-backend.tengu.io/users/{}'.format(request.path[1:].split('/', 1)[1]),
                       auth=(request.authorization.username, request.authorization.password),
                       headers={'api-key': get_api_key()})
    if req.status_code == 200:
        res = monitoring.get_model(check_input(controller), check_input(model))
        return create_response(200, res)
    else:
        return create_response(req.status_code, req.text)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>', methods=['GET'])
def get_application_monitor(controller, model, application):
    token, con = execute_task(juju.authenticate, request.headers['api-key'], request.authorization,
                              juju.check_input(controller))
    if mongo.get_model_access(controller, model, request.authorization.username) is not None:
        code, response = 200, monitoring.get_application(controller, model, application)
    else:
        code, response = 200, {}
    execute_task(con.disconnect)
    return create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>', methods=['PUT'])
def add_monitoring_application(controller, model, application):
    try:
        token, con, mod = execute_task(juju.authenticate, request.headers['api-key'], request.authorization,
                                       juju.check_input(controller), juju.check_input(model))
        mod_access = mongo.get_model_access(controller, model, token.username)
        if mod_access == 'admin':
            app = juju.check_input(application)
            if execute_task(juju.app_exists, token, con, mod, app):
                execute_task(monitoring.add_monitoring, con, mod, app)
                code, response = 200, 'OK'
            else:
                code, response = errors.does_not_exist(app)
        else:
            code, response = errors.no_permission()
    except KeyError:
        code, response = errors.invalid_data()
    return create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>', methods=['DELETE'])
def remove_monitoring_application(controller, model, application):
    try:
        token, con, mod = execute_task(juju.authenticate, request.headers['api-key'], request.authorization,
                                       juju.check_input(controller), juju.check_input(model))
        mod_access = mongo.get_model_access(controller, model, token.username)
        if mod_access == 'admin':
            app = juju.check_input(application)
            if execute_task(juju.app_exists, token, con, mod, app):
                execute_task(monitoring.remove_monitoring, con, mod, app)
                code, response = 200, 'OK'
            else:
                code, response = errors.does_not_exist(app)
        else:
            code, response = errors.no_permission()
    except KeyError:
        code, response = errors.invalid_data()
    return create_response(code, response)


@MONITOR.route('/controllers/<controller>/models/<model>/applications/<application>/units/<unitnr>', methods=['GET'])
def get_unit_monitor(controller, model, application, unitnr):
    token, con = execute_task(juju.authenticate, request.headers['api-key'], request.authorization,
                              juju.check_input(controller))
    if mongo.get_model_access(controller, model, request.authorization.username) is not None:
        code, response = 200, monitoring.get_unit(controller, model, application, unitnr)
    else:
        code, response = 200, {}
    execute_task(con.disconnect)
    return create_response(code, response)
