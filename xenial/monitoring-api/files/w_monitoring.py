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
import os
import requests
from influxdb import InfluxDBClient
from sojobo_api import settings
from sojobo_api.api import w_juju as juju #pylint: disable = e0401


def influxdb_client():
    return InfluxDBClient(settings.INFLUXDB.split(':')[0], settings.INFLUXDB.split(':')[1],
                          settings.INFLUXDB_USER, settings.INFLUXDB_PASSWORD, settings.INFLUXDB_DB)


async def add_monitoring(token, con_con, mod_con, app):
    app_info = await juju.get_application_info(token, mod_con, app)
    charm, version = app_info['charm'].split(':')[1].rsplit('-', 1)
    serie = app_info['units'][0]['series']
    if not await check_monitoring(token, mod_con, app):
        await install_monitoring(token, con_con, mod_con, app, charm, serie)
    await juju.add_relation(token, mod_con, app, '{}-monitoring'.format(app))


async def remove_monitoring(token, con_con, mod_con, app):
    await juju.remove_app(token, mod_con, '{}-monitoring'.format(app))


async def install_monitoring(token, con_con, mod_con, app, charm, serie):
    with open(os.path.join(settings.SOJOBO_API_DIR, 'install_mapping.json'), 'r') as mapping:
        install_map = json.load(mapping)
    plugins = install_map['machine'][0]['install']#.extend(install_map[charm][0]['install'])
    scripts = install_map['machine'][0]['measurements']#.extend(install_map[charm][0]['measurements'])
    config = {'controller': con_con.c_name,
              'charm': charm,
              'plugins': ' '.join(plugins),
              'measurements': ' '.join(['{}|{}'.format(m['name'], m['script']) for m in scripts]),
              'rabbitmq': settings.SENSU_RABBITMQ,
              'ssl_key': settings.SENSU_SSL_KEY,
              'ssl_cert': settings.SENSU_SSL_CERT,
              'password': settings.SENSU_PASSWORD}
    await juju.deploy_app(token, mod_con, '{}/{}/sensu-client'.format(settings.LOCAL_CHARM_DIR, serie),
                          '{}-monitoring'.format(app), ser=serie, con=config, num_of_units=0)


async def check_monitoring(token, mod_con, app):
    res = await juju.get_application_info(token, mod_con, '{}-monitoring'.format(app))
    return bool(res)


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


def get_application(con, mod, app):
    measurements = [m['name'] for m in list(influxdb_client().query('show measurements').get_points())]
    results = {'application': app, 'units': {}}
    for m in measurements:
        query = 'select * from {} where \"controller\"=\'{}\' and \"model\"=\'{}\' and \"application\"=\'{}\' and time > now() - 1h group by \"unit\"'.format(m, con, mod, app)
        data = influxdb_client().query(query).items()
        for t in data:
            result = list(t[1])
            if result is not []:
                unit = t[0][1]['unit']
                if unit in results['units']:
                    results['units'][unit][m] = result
                else:
                    results['units'][unit] = {m: result}
    return results


def get_unit(con, mod, app, unit):
    measurements = [m['name'] for m in list(influxdb_client().query('show measurements').get_points())]
    results = {unit: {}}
    for m in measurements:
        query = 'select * from {} where \"controller\"=\'{}\' and \"model\"=\'{}\' and \"application\"=\'{}\' and \"unit\"=\'{}\' and time > now() - 1h'.format(m, con, mod, app, unit)
        result = list(influxdb_client().query(query).get_points())
        if result is not []:
            results[unit][m] = result
    return results


def check_sensu():
    try:
        res = requests.get('http://{}/info'.format(settings.SENSU_API))
        if res.status_code == 200:
            return {
                'Sensu-api': 'RUNNING',
                'Sensu-server': 'RUNNING' if res.json()['servers'] != [] else 'DOWN',
                'Sensu-Reddis-connection': 'RUNNING' if res.json()['redis']['connected'] else 'DOWN',
                'Sensu-RabbitMQ-connection': 'RUNNING' if res.json()['transport']['connected'] else 'DOWN'
            }
        else:
            return {
                'Sensu-api': 'ERROR',
                'Sensu-server': 'ERROR',
                'Sensu-Reddis-connection': 'ERROR',
                'Sensu-RabbitMQ-connection': 'ERROR'
            }
    except requests.exceptions.ConnectionError:
        return {
            'Sensu-api': 'DOWN',
            'Sensu-server': 'UNKNOWN',
            'Sensu-Reddis-connection': 'UNKNOWN',
            'Sensu-RabbitMQ-connection': 'UNKNOWN'
        }


def check_influxdb():
    try:
        temp = influxdb_client()
        return {'InfluxDB': 'RUNNING', 'Parser': check_parser(), 'RabbitMQ': check_rabbitmq(), 'Redis': check_redis()}
    except requests.exceptions.ConnectionError:
        return {'InfluxDB': 'DOWN', 'Parser': 'UNKNOWN', 'RabbitMQ': 'UNKNOWN', 'Redis': 'UNKNOWN'}


def check_parser():
    query = 'select * from heartbeat where \"name\"=\'sensu-influxdb-parser\' and time > now() - 10s'
    result = list(influxdb_client().query(query).get_points())
    if result == []:
        return 'ERROR'
    else:
        return result[-1]['status']


def check_rabbitmq():
    query = 'select * from heartbeat where \"name\"=\'rabbitmq-server\' and time > now() - 10s'
    result = list(influxdb_client().query(query).get_points())
    if result == []:
        return 'ERROR'
    else:
        return result[-1]['status']


def check_redis():
    query = 'select * from heartbeat where \"name\"=\'redis-server\' and time > now() - 10s'
    result = list(influxdb_client().query(query).get_points())
    if result == []:
        return 'ERROR'
    else:
        return result[-1]['status']
