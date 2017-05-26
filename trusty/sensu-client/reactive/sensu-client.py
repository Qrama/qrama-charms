#!/usr/bin/env python3
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
# pylint: disable=c0111,c0103,c0301
import os
import subprocess
from subprocess import call
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import status_set, config, open_port, application_version_set, unit_public_ip
from charmhelpers.core.host import service_restart
from charms.reactive import when, when_not, set_state, remove_state


CONFIG_DIR = '/etc/sensu/conf.d'
SSL_DIR = '/etc/sensu/ssl'


@when('apt.installed.sensu', 'info.available')
@when_not('sensu.monitoring')
def setup_sensu(info):
    if not os.path.isdir(SSL_DIR):
        os.mkdir(SSL_DIR)
    with open('{}/ssl_key.pem'.format(SSL_DIR), 'w+') as ssl_key:
        ssl_key.write(config()['ssl_key'])
    with open('{}/ssl_cert.pem'.format(SSL_DIR), 'w+') as ssl_cert:
        ssl_cert.write(config()['ssl_cert'])
    rabbitmq = {'host': config()['rabbitmq'].split(':')[0],
                'port': config()['rabbitmq'].split(':')[1],
                'password': config()['password'],
                'ssl_cert': '{}/ssl_cert.pem'.format(SSL_DIR),
                'ssl_key': '{}/ssl_key.pem'.format(SSL_DIR)}
    application = os.environ['JUJU_REMOTE_UNIT']
    render('rabbitmq.json', '{}/rabbitmq.json'.format(CONFIG_DIR), context=rabbitmq)
    client = {'name': '{}/{}'.format(config()['name'], application),
              'public_ip': unit_public_ip(), 'subscriptions': '[\"monitoring\"]'}
    render('client.json', '{}/client.json'.format(CONFIG_DIR), context=client)
    render('transport.json', '{}/transport.json'.format(CONFIG_DIR), context={})
    open_port(3030)
    application_version_set('0.29')
    service_restart('sensu-client')
    status_set('active', 'Sensu-client is active')
    set_state('sensu.installed')


@when('sensu.installed')
@when_not('sensu.monitoring')
def install_machine_monitoring():
    call(['/opt/sensu/embedded/bin/gem', 'install', 'sensu-plugin', '--version', '\'=1.2.0\''])
    call(['sensu-install', '-p', 'sensu-plugins-load-checks'])
    call(['sensu-install', '-p', 'sensu-plugins-memory-checks'])
    call(['sensu-install', '-p', 'sensu-plugins-disk-checks'])
    render('checks.json', '{}/checks.json'.format(CONFIG_DIR), context={})
    service_restart('sensu-client')
    status_set('active', 'Sensu-client is monitoring CPU, memory and disk ')
    set_state('sensu.monitoring')


@when('sensu.monitoring')
@when_not('info.available')
def uninstall():
    subprocess.call(['apt-get', 'remove', 'sensu', '--purge'])
    remove_state('sensu.monitoring')
