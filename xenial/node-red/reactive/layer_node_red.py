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
# pylint: disable=c0111,c0301,c0325,c0103,r0913,r0902,e0401,C0302, R0914
import os
import shutil
import subprocess as sp
from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, open_port
from charmhelpers.core.host import service_start

@when('apt.installed.nodejs')
@when_not('layer-node-red.installed')
def install_layer_node_red():
    if not os.path.isdir('/root/.node-red'):
        os.mkdir('/root/.node-red')
    sp.check_call(['sudo', 'npm', 'install', '-g', '--unsafe-perm', 'node-red'])
    shutil.copyfile('files/nodered.service', '/etc/systemd/system/nodered.service')
    sp.check_call(['sudo', 'systemctl', 'daemon-reload'])
    service_start('nodered')
    open_port(1880)
    set_state('layer-node-red.installed')
    status_set('active', 'Node-RED installed and running!')

@when('http.available', 'layer-node-red.installed')
def configure_port(http):
    http.configure(1880)
