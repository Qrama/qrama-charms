# !/usr/bin/env python3
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
# pylint: disable=c0111,c0301,c0325,w0406
from os import mkdir, path
from subprocess import check_call
import tarfile
from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, unit_private_ip, open_port, close_port, charm_dir, resource_get
from charmhelpers.core.host import service_restart
from charmhelpers.core.templating import render


filesdir = '{}/files'.format(charm_dir())


@when_not('node-exporter.installed')
def install():
    if not path.isdir(filesdir):
        mkdir(filesdir)
    # tfile = tarfile.open(resource_get('node-exporter'), 'r')
    tarfiledir = '{}/node_exporter-0.14.0.linux-amd64.tar.gz'.format(filesdir)
    check_call(['wget',
                'https://github.com/prometheus/node_exporter/releases/download/v0.14.0/node_exporter-0.14.0.linux-amd64.tar.gz',
                '-O', tarfiledir])
    tfile = tarfile.open(tarfiledir)
    tfile.extractall(filesdir)
    if not path.islink('/usr/bin/node_exporter'):
        check_call(['ln', '-s', '{}/node_exporter-0.14.0.linux-amd64/node_exporter'.format(filesdir), '/usr/bin'])
    render('node_exporter.conf', '/etc/init/node_exporter.conf', context={})
    render('node_exporter.service', '/etc/systemd/system/node_exporter.service', context={})
    service_restart('node_exporter')
    status_set('blocked', 'Waiting for relation with Prometheus')
    set_state('node-exporter.installed')


@when('prometheus.available', 'node-exporter.installed')
def config(prometheus):
    open_port(9100)
    prometheus.configure(9100, unit_private_ip())
    status_set('active', 'Sending info to Prometheus')


@when('prometheus.removed', 'node-exporter.installed')
def remove_controller(prometheus):
    close_port(9100)
    status_set('blocked', 'Waiting for relation with Prometheus')
