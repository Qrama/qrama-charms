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
import os
import requests
import shutil
from subprocess import check_call, check_output

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import config, status_set, open_port, unit_public_ip, charm_dir
from charmhelpers.core.host import service_restart
from charmhelpers.core.templating import render

from jujubigdata.utils import re_edit_in_place


@when('apt.installed.nginx-full', 'apt.installed.ufw', 'apt.installed.openssl', 'apt.installed.apache2-utils')
@when_not('proxy.installed')
def install():
    setup_firewall(['22', '80', '443', '9100'])
    setup_ssl(4096)
    setup_nginx()
    res = ping_sojobo()
    if res.status_code == 200:
        status_set('active', 'Sojobo-ping successfull and firewall configured')
        set_state('proxy.installed')
    else:
        status_set('blocked', 'Ping request failed, retrying')


@when('sojobo-monitoring-proxy.removed')
def disable():
    body = {
        'controller' : config()['controller'],
        'model': config()['model']
        }
    res = requests.delete(config()['monitoring-url'], json=body, headers={'api-key' : config()['monitoring-api-key']})
    while res.status_code != 200:
        status_set('blocked', 'Ping request failed, retrying')
        res = requests.delete(config()['monitoring-url'], json=body, headers={'api-key' : config()['monitoring-api-key']})
    check_output(['ufw', 'disable'], input='y\n', universal_newlines=True)


def setup_firewall(ports):
    re_edit_in_place('/etc/default/ufw', {r'IPV6=yes': 'IPV6=no'})
    for port in ports:
        check_call(['ufw', 'allow', port])
        open_port(int(port))
    check_output(['ufw', 'enable'], input='y\n', universal_newlines=True)


def setup_ssl(size):
    ssl_dir = os.path.join(os.sep, 'etc', 'nginx', 'ssl')
    if not os.path.isdir(ssl_dir):
        os.mkdir(ssl_dir)
    shutil.copyfile(os.path.join(charm_dir(), 'files', 'dhparam.pem'),
                    os.path.join(ssl_dir, 'dhparam.pem'))
    check_call(['openssl', 'req', '-x509', '-nodes', '-newkey',
                'rsa:{}'.format(size), '-batch',
                '-keyout', os.path.join(ssl_dir, 'selfsigned.key'),
                '-out', os.path.join(ssl_dir, 'selfsigned.crt')])


def setup_nginx():
    ht_dir = os.path.join(os.sep, 'etc', 'nginx', '.htpasswd')
    credentials = config()['credentials'].split(' ')
    if not os.path.exists(ht_dir):
        check_call(['htpasswd', '-c', '-b', ht_dir, credentials[0], credentials[1]])
    else:
        check_call(['htpasswd', '-b', ht_dir, credentials[0], credentials[1]])
    render(source='proxy.conf',
           target=os.path.join(os.sep, 'etc', 'nginx', 'sites-enabled', 'default'),
           context={'fqdn': unit_public_ip(), 'host': 'localhost', 'port': '9090'})
    service_restart('nginx')


def ping_sojobo():
    credentials = config()['credentials'].split(' ')
    body = {
        'url' : 'https://{}'.format(unit_public_ip()),
        'controller' : config()['controller'],
        'model' : config()['model'],
        'user': credentials[0],
        'password': credentials[1]
        }
    res = requests.put(config()['monitoring-url'],
                       json=body,
                       headers={'api-key' : config()['monitoring-api-key']})
    return res
