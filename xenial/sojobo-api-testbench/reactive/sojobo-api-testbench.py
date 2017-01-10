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
# pylint: disable=c0111,c0301,c0325, r0903,w0406
from os import remove
from shutil import copyfile, copytree, rmtree
import requests


from charms.reactive import when_not, hook, set_state
from charmhelpers.core.hookenv import status_set, charm_dir
from charmhelpers.core.host import service_restart


@when_not('sojobo-api-testbench.installed')
def install():
    api_dir = requests.get('http://localhost:5000').json()['message']['api_dir']
    copyfile('{}/files/sojobo_api_testbench.py'.format(charm_dir()), '{}/sojobo_api_testbench.py'.format(api_dir))
    copyfile('{}/files/menu.py'.format(charm_dir()), '{}/menu.py'.format(api_dir))
    copyfile('{}/files/api/api_tests.py'.format(charm_dir()), '{}/api/api_tests.py'.format(api_dir))
    copytree('{}/files/tests'.format(charm_dir()), '{}/tests'.format(api_dir))
    copyfile('{}/files/monitoring.py'.format(charm_dir()), '{}/tests/test_monitoring.py'.format(api_dir))
    service_restart('sojobo-api')
    status_set('active', 'data copied')
    set_state('sojobo-api-testbench.installed')


@hook('stop')
def remove_controller():
    api_dir = requests.get('http://localhost:5000').json()['message']['api_dir']
    remove('{}/sojobo_api_testbench.py'.format(api_dir))
    remove('{}/api/api_tests.py'.format(api_dir))
    rmtree('{}/tests'.format(api_dir))
    service_restart('sojobo-api')
