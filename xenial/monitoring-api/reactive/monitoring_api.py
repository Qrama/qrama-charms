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
import os
import shutil

from charms.reactive import when, when_not, set_state, remove_state
from charmhelpers.core.hookenv import status_set, charm_dir, config
from charmhelpers.core.host import service_restart, chownr


@when('sojobo.available')
@when_not('sensuapi.available')
def waiting_for_api(sojobo):
    status_set('blocked', 'Waiting for relation with Sensu-Base')


@when('sojobo.available', 'sensuapi.available')
@when_not('monitoring-api.installed')
def install(sojobo, sensuapi):
    api_dir = list(sojobo.connection())[0]['api-dir']
    user = list(sojobo.connection())[0]['user']
    shutil.copyfile('{}/files/api_monitoring.py'.format(charm_dir()), '{}/api/api_monitoring.py'.format(api_dir))
    shutil.copyfile('{}/files/w_monitoring.py'.format(charm_dir()), '{}/api/w_monitoring.py'.format(api_dir))
    host = sensuapi.services()[0]['hosts'][0]
    with open('{}/settings.py'.format(api_dir), 'a') as settings_file:
        settings_file.write('\nSENSU_API = \'{}:{}\''.format(host['hostname'], host['port']))
        settings_file.write('\nSENSU_RABBITMQ = \"\"\"{}\"\"\"'.format(config()['rabbitmq']))
        settings_file.write('\nSENSU_SSL_KEY = \"\"\"{}\"\"\"'.format(config()['ssl_key']))
        settings_file.write('\nSENSU_SSL_CERT = \"\"\"{}\"\"\"'.format(config()['ssl_cert']))
        settings_file.write('\nSENSU_PASSWORD = \"\"\"{}\"\"\"'.format(config()['password']))
    chownr(api_dir, user, 'www-data', chowntopdir=True)
    service_restart('nginx')
    status_set('active', 'data copied')
    set_state('monitoring-api.installed')


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
