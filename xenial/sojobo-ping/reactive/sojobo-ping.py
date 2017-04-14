# Copyright (C) 2017  Qrama
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
# pylint: disable=C0111, C0301
import requests
from subprocess import check_call, check_output

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import config, status_set, open_port, unit_private_ip, unit_public_ip

from jujubigdata.utils import re_edit_in_place


@when_not('ping.installed')
def install():
    re_edit_in_place('/etc/default/ufw', {r'IPV6=yes': 'IPV6=no'})
    for port in ['22', '80', '443', '9100']:
        check_call(['ufw', 'allow', port])
    open_port(9100)
    check_output(['ufw', 'enable'], input='y\n', universal_newlines=True)
    set_state('ping.installed')
    status_set('blocked', 'Waiting for proxy relation')


@when('ping.removed')
def disable():
    check_output(['ufw', 'disable'], input='y\n', universal_newlines=True)


@when('reverseproxy.available')
@when_not('ping.configured')
def proxy(reverseproxy):
    reverseproxy.configure(9090, 'localhost')
    credentials = config()['credentials'].split(' ')
    body = {
        'url' : 'https://{}'.format(config()['fqdn']),
        'controller' : config()['controller'],
        'model' : config()['model'],
        'user': credentials[0],
        'password': credentials[1]
        }
    res = requests.put(config()['monitoring-url'], json=body, headers={'api-key' : config()['monitoring-api-key']})
    if res.status_code == 200:
        status_set('active', 'Sojobo-ping successfull and firewall configured')
        set_state('ping.configured')
    else:
        status_set('blocked', 'Ping request failed, retrying')


@when('reverseproxy.removed')
def remove_proxy(reverseproxy):
    body = {
        'ip' : unit_private_ip() if config()['controller-type'] == 'MAAS' else unit_public_ip(),
        }
    res = requests.delete(config()['monitoring-url'], json=body, headers={'api-key' : config()['monitoring-api-key']})
    while res.status_code != 200:
        res = requests.delete(config()['monitoring-url'], json=body, headers={'api-key' : config()['monitoring-api-key']})
