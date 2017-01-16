#!/usr/bin/env python3
# Copyright (C) 2016  Ghent University
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
# pylint: disable=c0111,c0103,c0301
import json
import socket
import subprocess as sp
import requests

from charms import apt #pylint: disable=E0611
from charms.reactive import (
    when,
    when_not,
    set_state,
)
from charmhelpers.core import templating, hookenv
from charmhelpers.core.hookenv import service_name
from charmhelpers.core.host import service_restart
from charmhelpers.contrib.python.packages import pip_install

from jujubigdata import utils

CHARMDIR = hookenv.charm_dir()

# @hook('config-changed')
# def config_changed():
#     configure_tengu_monitor()

@when('elasticsearch.base.available')
@when_not('tengu-monitor.installed')
def install_tengu_monitor():
    hookenv.log('Installing Webserver')
    apt.queue_install(['nginx', 'apache2-utils'])
    pip_install('ipgetter')
    hookenv.log('Sending IP request')
    conf = hookenv.config()
    sojobo = conf['sojobo-ip']
    api_key = conf['api-key']
    cont_type = conf['controller-type']
    if send_request(sojobo, api_key, cont_type) == 200:
        set_state('tengu-monitor.installed')
        hookenv.status_set('active', 'ready')
    else:
        hookenv.status_set('blocked', 'Unable to reach SOJOBO!')
    set_state('tengu-monitor.installed')

@when('tengu-monitor.installed')
@when_not('tengu-monitor.configured')
def configure_tengu_monitor():
    conf = hookenv.config()
    passphrase = conf['pass']
    username = conf['username']
    setpythonpath()
    sp.check_output(
        ['htpasswd', '-c', '/etc/nginx/.htpasswd', username],
        input='{}\n{}\n'.format(passphrase, passphrase), universal_newlines=True)
    render_config_template()
    service_restart('nginx')
    hookenv.status_set('active', 'ready')
    set_state('tengu-monitor.configured')

def render_config_template():
    conf = hookenv.config()
    port = conf['port']
    templating.render(
        source='nginx_conf',
        target='/etc/nginx/sites-available/default',
        context={
            'port': port
        }
    )

def setpythonpath():
    with utils.environment_edit_in_place('/etc/environment') as env:
        env['PYTHONPATH'] = CHARMDIR

def send_request(sojobo, api_key, controller_type):
    # send request to API and add sojobo-ip to FW rules
    if controller_type == 'MAAS':
        charm_ip = socket.gethostbyname(socket.gethostname())
    else:
        import ipgetter
        charm_ip = ipgetter.myip()
    add_sojobo_to_fw(sojobo)
    url = 'http://{}:5000/monitoring/ping'.format(sojobo)
    body = {
        'charm-ip' : charm_ip,
        'service-name' : service_name()
        }
    myheaders = {'Content-Type':'application/json', 'api_key' : api_key}
    res = requests.put(url, data=json.dumps(body), headers=myheaders)
    return res.status_code

def add_sojobo_to_fw(sojobo_ip):
    sp.check_call([
        'ufw', 'allow', 'proto', 'tcp', 'from', sojobo_ip,
        'to', 'any', 'port', '9200'])
