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
import subprocess
# Charm pip dependencies
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import status_set, log, config, open_port, close_port, unit_public_ip
from charmhelpers.core.host import service_restart, chownr, adduser
from charms.reactive import hook, when, when_not, set_state, remove_state


API_DIR = config()['api-dir']
USER = config()['user']
GROUP = config()['nginx-group']
HOST = config()['host'] if config()['host'] != '127.0.0.1' else unit_public_ip()
SETUP = config()['setup']
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


@when('tengu.configured', 'nginx.passenger.available')
@when_not('tengu.running')
def configure_webapp():
    if SETUP == 'https':
        close_port(80)
        close_port(443)
        render_httpsclient()
        open_port(443)
        open_port(80)
    elif SETUP == 'letsencrypt':
        close_port(80)
        close_port(443)
        render_httpsletsencrypt()
        open_port(80)
    else:
        close_port(80)
        close_port(443)
        render_http()
        open_port(80)
    restart_api()
    set_state('tengu.running')
    status_set('active', 'The Tengu-UI is running')


def install_tengu():
    mergecopytree('files/tengu_ui', API_DIR)
    try:
        os.mkdir('/home/{}'.format(USER))
        adduser(USER)
        chownr('/home/{}'.format(USER), USER, USER, chowntopdir=True)
        chownr(API_DIR, USER, GROUP, chowntopdir=True)
    except FileExistsError:
        pass


def render_httpsclient():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR, 'dhparam': config()['dhparam']}
    chownr(context['dhparam'], GROUP, 'root')
    if config()['fullchain'] == '' and config()['privatekey'] == '':
        chownr('/etc/letsencrypt/live/{}'.format(HOST), GROUP, 'root', chowntopdir=True)
        context['fullchain'] = '/etc/letsencrypt/live/{}/fullchain.pem'.format(HOST)
        context['privatekey'] = '/etc/letsencrypt/live/{}/privkey.pem'.format(HOST)
        render('https.conf', '/etc/nginx/sites-enabled/tengu.conf', context)
    elif config()['fullchain'] != '' and config()['privatekey'] != '':
        context['fullchain'] = config()['fullchain']
        context['privatekey'] = config()['privatekey']
        render('https.conf', '/etc/nginx/sites-enabled/tengu.conf', context)
    else:
        status_set('blocked', 'Invalid fullchain and privatekey config')


def render_httpsletsencrypt():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    if not os.path.isdir('{}/.well-known'.format(API_DIR)):
        os.mkdir('{}/.well-known'.format(API_DIR))
    chownr('{}/.well-known'.format(API_DIR), USER, GROUP, chowntopdir=True)
    render('letsencrypt.conf', '/etc/nginx/sites-enabled/tengu.conf', context)


def render_http():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    render('http.conf', '/etc/nginx/sites-enabled/tengu.conf', context)


def restart_api():
    service_restart('nginx')
    subprocess.check_call(['service', 'nginx', 'status'])


def dhparam(size):
    if not os.path.isdir('/etc/nginx/ssl'):
        os.mkdir('/etc/nginx/ssl')
    if not os.path.isdir('/etc/nginx/ssl/{}'.format(HOST)):
        os.mkdir('/etc/nginx/ssl/{}'.format(HOST))
    chownr('/etc/nginx/ssl/{}'.format(HOST), GROUP, 'root', chowntopdir=True)
    subprocess.check_call(['openssl', 'dhparam', '-out', '/etc/nignx/ssl/{}/dhparam.pem'.format(HOST), str(size)])
    return '/etc/nignx/ssl/{}/dhparam.pem'.format(HOST)


# Handeling changed configs
@when('tengu.configured', 'config.changed')
def feature_flags_changed():
    configure_webapp()
    restart_api()


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
            'bundles_url': config()['bundles_url'],
            'mappings_url': config()['mappings_url'],
            'api_key': data['api-key'],
            'init_cmd': ':signin'})
    set_state('tengu.configured')


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
