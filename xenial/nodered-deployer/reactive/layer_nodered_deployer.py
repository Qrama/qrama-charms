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
import subprocess as sp
import requests
import ast
import json
import time
from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import service_restart
from charmhelpers.core import unitdata

unitd = unitdata.kv()

@when_not('nodered-deployer.installed')
def install_layer_nodered_deployer():
    unitd.set('port', 1880)
    status_set('active', 'Node-RED-deployer installed and ready for deployment!')
    set_state('nodered-deployer.installed')

@when('nodered-deployer.installed', 'dataflow.available')
@when_not('dataflow.deployed')
def deploy_topology(dataflow):
    nodes = ast.literal_eval(dataflow.connection()['nodes'])
    for node in nodes:
        sp.check_call(['sudo', 'npm', 'install', '--prefix', '/root/.node-red',node])
    service_restart('nodered')
    time.sleep(100)
    flow = json.loads(dataflow.connection()['dataflow'])
    r= requests.post('http://localhost:1880/flows', json=flow)
    dataflow.deployed()
