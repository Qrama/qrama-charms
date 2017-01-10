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
import pwd
import grp
import os
import shutil
import requests

from charms.reactive import when_not, hook, set_state
from charmhelpers.core.hookenv import status_set, charm_dir
from charmhelpers.core.host import service_restart
from charmhelpers.contrib.python.packages import pip_install

@when_not('monitoring-api.installed')
def install():
    api_dir = requests.get('http://localhost:5000').json()['message']['api_dir']
    shutil.copyfile('{}/files/api_monitoring.py'.format(charm_dir()), '{}/api/api_monitoring.py'.format(api_dir))
    shutil.copyfile('{}/files/w_monitoring.py'.format(charm_dir()), '{}/api/w_monitoring.py'.format(api_dir))
    os.mkdir('{}/monitoring'.format(api_dir))
    ip_list_path = '{}/monitoring/elastic_ip.yaml'.format(api_dir)
    shutil.copyfile('{}/files/elastic_ip.yaml'.format(charm_dir()), ip_list_path)
    uid = pwd.getpwnam("ubuntu").pw_uid
    gid = grp.getgrnam("ubuntu").gr_gid
    os.chown(ip_list_path, uid, gid)
    pip_install('elasticsearch')
    service_restart('sojobo-api')
    status_set('active', 'data copied')
    set_state('monitoring-api.installed')


@hook('stop')
def remove_controller():
    api_dir = requests.get('http://localhost:5000').json()['message']['api_dir']
    os.remove('{}/api/api_monitoring.py'.format(api_dir))
    shutil.rmtree('{}/monitoring'.format(api_dir))
    service_restart('sojobo-api')
