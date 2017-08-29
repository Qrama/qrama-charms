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
# pylint: disable=c0111,c0103,c0301,c0412
import subprocess as sp
import tempfile
import requests
import json
import os

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, config, service_name

@when_not('layer-notebook.installed')
def install_layer_notebook():
    conf = config()
    if conf['notebook_location']:
        file = requests.post('http://127.0.0.1:9080/api/notebook', json={"name": service_name()})
        data = file.json()
        notebook_path = '/var/lib/zeppelin/notebook/{}/note.json'.format(data['body'])
        if os.path.exists(notebook_path):
            os.remove(notebook_path)
        d = {}
        json_data = json.dumps(d)
        tmp_dir = tempfile.mkdtemp()
        dest_file = '{}/note.json'.format(tmp_dir)
        sp.check_call(['wget', '-O', dest_file, conf['notebook_location']])
        with open(dest_file) as f:
            jdata = json.load(f)
            jdata['name'] = service_name()
            jdata['id'] = data['body']
            json_data = jdata
        with open(notebook_path, 'w+') as note:
            json.dump(json_data, note)
        sp.check_call(['sudo', 'service', 'zeppelin', 'restart'])
        status_set('active', 'Notebook {} succesfully deployed'.format(service_name()))
        set_state('layer-notebook.installed')
    else:
        status_set('blocked', 'Please provide a valid url to deploy job by changing job_location config')
#
# @when('zeppelin.notebook.accepted')
# def finish_install(notebook):

#
#
# @when('zeppelin.notebook.rejected')
# def report_rejected_notebook(zeppelin):
#     status_set('blocked', 'Zeppelin rejected our notebook')
