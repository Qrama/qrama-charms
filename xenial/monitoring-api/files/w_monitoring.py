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
import requests
from sojobo_api import settings
from sojobo_api.api import w_errors as errors, w_juju as juju #pylint: disable = e0401


MON_APPS = {'trusty': 'monitoring-trusty', 'xenial': 'monitoring-xenial'}


async def add_monitoring(con_con, mod_con, app):
    if not await check_monitoring(mod_con):
        await init_monitoring(con_con, mod_con)
    units_info = await juju.get_units_info(mod_con, app)
    series = units_info[0]['series']
    await juju.add_relation(mod_con, app, MON_APPS[series])


async def remove_monitoring(con_con, mod_con, app):
    units_info = await juju.get_units_info(mod_con, app)
    series = units_info[0]['series']
    await juju.remove_relation(mod_con, app, MON_APPS[series])


async def init_monitoring(con_con, mod_con):
    config = {'name': '{}/{}'.format(con_con.c_name, mod_con.m_name),
              'rabbitmq': settings.SENSU_RABBITMQ,
              'ssl_key': settings.SENSU_SSL_KEY,
              'ssl_cert': settings.SENSU_SSL_CERT,
              'password': settings.SENSU_PASSWORD}
    for serie, name in MON_APPS.items():
        await juju.deploy_app(mod_con, '/home/ubuntu/qrama-charms/{}/sensu-client'.format(serie),
                              name, ser=serie, con=config, units=0)


async def check_monitoring(mod_mod):
    applications = await juju.get_applications_info(mod_mod)
    apps = [app['name'] for app in applications]
    return set(MON_APPS.values()) <= set(apps)


def get_metrics():
    res = requests.get('http://{}/results'.format(settings.SENSU_API))
    if res.status_code == 200:
        return res.json()
    else:
        return []


# def get_controllers(controllers):
#     # Waiting for rewrite for a fast implementation
#     # return {c: get_controller(token) for c in juju.get_controllers_info(token)}
#     return None
#
#
# def get_models(controller, controller_info):
#     return {'name': controller, 'metrics': [get_model(controller, model['name']) for model in controller_info['models']]}
#
#
# def get_model(controller, model):
#     result = {'name': model, 'metrics': {}}
#     try:
#         conn_data = get_prometheus(controller, model)
#         req = requests.get('{}/api/v1/query?query=%7Binstance%3D~".%2B"%7D'.format(conn_data['url']),
#                            auth=(conn_data['usr'], conn_data['pwd']), verify=False)
#         result['metrics'] = req.json()
#     except KeyError:
#         pass
#     except TypeError:
#         result['metrics'] = {"status":"success","data":{"resultType":"vector","result":[]}}
#     return result


async def get_application(con, mod, application):
    search = '{}/{}/{}'.format(con.c_name, mod.m_name, application)
    app = await juju.get_application_info(mod, application)
    units = app['units']
    result = {unit['name'].split('/')[-1]: [] for unit in units}
    for metric in get_metrics():
        if search in metric['client']:
            result[metric['client'].split('/')[-1]].append({'name': metric['client'],
                                                            'result': metric['check']['output'],
                                                            'type': metric['check']['name']})
    return result


def get_unit(controller, model, application, unit):
    unit = '{}/{}/{}/{}'.format(controller, model, application, unit)
    return [{'result': metric['output'], 'name': metric['client'],
             'type': metric['check']['name']} for metric in get_metrics() if unit == metric['client']]
