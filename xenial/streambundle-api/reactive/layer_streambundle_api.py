#!/usr/bin/python3
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
# pylint: disable=c0111,c0103,c0301,e0401,c0411
import os
import shutil
import subprocess
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import status_set, open_port, unit_private_ip
from charmhelpers.core.host import service_restart
from charms.reactive import when, when_not, set_state

API_DIR = '/opt/streambundle_api'
HOST = unit_private_ip()

@when_not('api.installed')
def install_layer_streambundle_api():
    if not os.path.isdir(API_DIR):
        os.mkdir(API_DIR)
    mergecopytree('files/api', API_DIR)
    for pkg in ['Jinja2', 'Flask', 'pyyaml', 'click', 'pygments', 'requests', 'pymongo']:
        subprocess.check_call(['pip3', 'install', pkg])
    set_state('api.installed')
    status_set('blocked', 'Waiting for a relation with Specific Database')


@when('api.configured', 'nginx.passenger.available')
@when_not('api.ready')
def configure_webapp():
    context = {'hostname': HOST, 'rootdir': API_DIR, 'port': 80}
    render('http.conf', '/etc/nginx/sites-enabled/streambundle.conf', context)
    open_port(80)
    service_restart('nginx')
    set_state('api.ready')
    status_set('active', 'API running and available')


@when('api.installed', 'db.available')
@when_not('api.configured')
def connect_db(db):
    database = db.db_data()['db']
    uri = db.db_data()['uri']
    render('settings.py', '{}/settings.py'.format(API_DIR), {
        'MONGO_URI': uri,
        'MONGO_DB': database})
    set_state('api.configured')


@when('bundleapi.available', 'api.ready')
def configure_http(bundleapi):
    bundleapi.configure(80)


def mergecopytree(src, dst, symlinks=False, ignore=None):
    """"Recursive copy src to dst, mergecopy directory if dst exists.
    OVERWRITES EXISTING FILES!!"""
    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        if symlinks and os.path.islink(src_item):
            if os.path.lexists(dst_item):
                os.remove(dst_item)
            os.symlink(os.readlink(src_item), dst_item)
        elif os.path.isdir(src_item):
            mergecopytree(src_item, dst_item, symlinks, ignore)
        else:
            shutil.copy2(src_item, dst_item)
