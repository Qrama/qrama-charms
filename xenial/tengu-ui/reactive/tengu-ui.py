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
import shutil
# Charm pip dependencies
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import status_set, log, config, open_port, unit_private_ip
from charmhelpers.core.host import service_restart, chownr, adduser
from charms.reactive import hook, when, when_not, set_state, remove_state


API_DIR = '/opt/tengu_ui'
USER = 'tengu'
GROUP = 'www-data'
HOST = unit_private_ip()
###############################################################################
# INSTALLATION AND UPGRADES
###############################################################################
@when_not('tengu.installed')
def install():
    log('Installing Tengu-UI')
    install_tengu()
    set_state('tengu.installed')


@hook('upgrade-charm')
def upgrade_charm():
    log('Updating Tengu-UI')
    shutil.rmtree(API_DIR)
    install_tengu()
    set_state('tengu.installed')


@when('sojobo.available')
@when_not('tengu.running')
def configure(sojobo):
    loc = '{}/scripts'.format(API_DIR)
    for i in os.listdir(loc):
        if os.path.isfile(os.path.join(loc, i)) and 'settings.js' in i:
            prefix = i.split('.')[0]
    data = list(sojobo.connection())[0]
    render('settings.js', '{}/scripts/{}.settings.js'.format(API_DIR, prefix),
           {'sojobo_url': data['url'],
            'mappings_url': config()['mappings_url'],
            'api_key': data['api-key'],
            'init_cmd': ':signin'})
    set_state('tengu.configured')


@when('tengu.installed', 'nginx.passenger.available', 'tengu.configured')
@when_not('tengu.running')
def render_http():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    render('http.conf', '/etc/nginx/sites-enabled/tengu_ui.conf', context)
    open_port(80)
    service_restart('nginx')
    set_state('tengu.running')
    status_set('active', 'active (ready)')


@when('tengu.running', 'proxy.available')
def configure_proxy(proxy):
    proxy.configure(80)
    set_state('tengu.proxy-configured')


@when('tengu.installed', 'nginx.passenger.available')
@when_not('sojobo.available')
def waiting_for_relation():
    remove_state('tengu.configured')
    remove_state('tengu.running')
    status_set('blocked', 'The Tengu-UI is installed. Waiting for relation with Sojobo-API!')
###############################################################################
# UTILS
###############################################################################
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


def install_tengu():
    if not os.path.isdir('/home/{}'.format(USER)):
        os.mkdir('/home/{}'.format(USER))
        adduser(USER)
        chownr('/home/{}'.format(USER), USER, USER, chowntopdir=True)
    if not os.path.isdir(API_DIR):
        os.mkdir(API_DIR)
    mergecopytree('files/tengu_ui', API_DIR)
    chownr(API_DIR, USER, GROUP, chowntopdir=True)
