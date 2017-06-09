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
from base64 import b64encode
import os
import shutil

from charms.reactive import when, when_not, set_state, remove_state
from charmhelpers.core.hookenv import status_set, charm_dir, config
from charmhelpers.core.host import service_restart, chownr
from charmhelpers.contrib.python.packages import pip_install


@when('sojobo.available')
@when_not('influxdb.connected')
def waiting_for_api(sojobo):
    status_set('blocked', 'Waiting for relation with influxdb')


@when('sojobo.available', 'influxdb.available')
@when_not('monitoring-api.installed')
def install(sojobo, influxdb):
    for pkg in ['influxdb']:
        pip_install(pkg)
    api_dir = list(sojobo.connection())[0]['api-dir']
    user = list(sojobo.connection())[0]['user']
    dbname = 'tengu_monitoring'
    shutil.copyfile('{}/files/api_monitoring.py'.format(charm_dir()), '{}/api/api_monitoring.py'.format(api_dir))
    shutil.copyfile('{}/files/w_monitoring.py'.format(charm_dir()), '{}/api/w_monitoring.py'.format(api_dir))
    shutil.copyfile('{}/files/install_mapping.json'.format(charm_dir()), '{}/install_mapping.json'.format(api_dir))
    shutil.copyfile('{}/files/w_filters.py'.format(charm_dir()), '{}/api/w_filters.py'.format(api_dir))
    with open('{}/settings.py'.format(api_dir), 'a') as settings_file:
        settings_file.write('\nMONITOR_USER = \'sensu-base-monitor\'')
        settings_file.write('\nMONITOR_PASSWORD = \'{}\''.format(b64encode(os.urandom(16)).decode('utf-8')))
        settings_file.write('\nINFLUXDB = \'{}:{}\''.format(influxdb.hostname(), influxdb.port()))
        settings_file.write('\nINFLUXDB_USER = \'{}\''.format(influxdb.user()))
        settings_file.write('\nINFLUXDB_PASSWORD = \'{}\''.format(influxdb.password()))
        settings_file.write('\nINFLUXDB_DB = \'{}\''.format(dbname))
        settings_file.write('\nSENSU_RABBITMQ = \"\"\"{}\"\"\"'.format(config()['rabbitmq']))
        settings_file.write('\nSENSU_SSL_KEY = \"\"\"{}\"\"\"'.format(config()['ssl_key']))
        settings_file.write('\nSENSU_SSL_CERT = \"\"\"{}\"\"\"'.format(config()['ssl_cert']))
        settings_file.write('\nSENSU_PASSWORD = \"\"\"{}\"\"\"'.format(config()['password']))
    chownr(api_dir, user, 'www-data', chowntopdir=True)
    service_restart('nginx')
    from influxdb import InfluxDBClient
    client = InfluxDBClient(influxdb.hostname(), influxdb.port(), influxdb.user(), influxdb.password())
    client.create_database(dbname)
    status_set('active', 'data copied and database created')
    set_state('monitoring-api.installed')


@when('monitoring-api.installed', 'endpoint.available')
@when_not('endpoint.configured')
def setup_endpoint(endpoint):
    with open('/opt/sojobo_api/settings.py', 'r') as settings_file:
        for line in settings_file.readlines():
            if 'MONITOR_PASSWORD = ' in line:
                password = line.split('=', 1)[-1][2:1]
                break
    endpoint.configure('sensu-base-monitor', password)
    set_state('endpoint.configured')


@when('sojobo.removed', 'monitoring-api.installed')
def remove_controller(sojobo):
    try:
        api_dir = list(sojobo.connection())[0]['api-dir']
        os.remove('{}/api/api_monitoring.py'.format(api_dir))
        os.remove('{}/api/w_monitoring.py'.format(api_dir))
        service_restart('nginx')
    except FileNotFoundError:
        pass
    remove_state('monitoring-api.installed')
