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
# pylint: disable=c0111,c0103,c0301
from base64 import b64encode
from hashlib import sha256
import os
import shutil
import subprocess
from charmhelpers.core import unitdata
from charmhelpers.core.templating import render
from charmhelpers.core.hookenv import status_set, log, config, open_port, unit_private_ip, application_version_set, leader_get, leader_set
from charmhelpers.core.host import service_restart, chownr, adduser
from charmhelpers.contrib.python.packages import pip_install
from charms.reactive import hook, when, when_not, set_state, remove_state
import charms.leadership


API_DIR = '/opt/sojobo_api'
USER = 'sojobo'
GROUP = 'www-data'
HOST = config()['host'] if config()['host'] != '127.0.0.1' else unit_private_ip()
db = unitdata.kv()
###############################################################################
# INSTALLATION AND UPGRADES
###############################################################################
@when('juju.installed')
@when_not('api.installed')
def install():
    subprocess.call(['python3.6', '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'])
    log('Installing Sojobo API')
    if not os.path.isdir(API_DIR):
        os.mkdir(API_DIR)
    install_api()
    set_state('api.installed')


@hook('upgrade-charm')
def upgrade_charm():
    log('Updating Sojobo API')
    install_api()
    set_state('api.installed')


@when('api.installed', 'nginx.passenger.available')
@when_not('api.configured')
def configure_webapp():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    render('http.conf', '/etc/nginx/sites-enabled/sojobo.conf', context)
    open_port(80)
    service_restart('nginx')
    set_state('api.configured')
    status_set('blocked', 'Waiting for a connection with Redis')


@when('config.changed', 'api.running')
def config_changed():
    context = {'hostname': HOST, 'user': USER, 'rootdir': API_DIR}
    render('http.conf', '/etc/nginx/sites-enabled/sojobo.conf', context)
    service_restart('nginx')


@when('leadership.is_leader')
@when_not('secrets.configured')
def set_secrets():
    api_key = sha256(os.urandom(256)).hexdigest()
    password = b64encode(os.urandom(18)).decode('utf-8')
    leader_set({
        'api-key': api_key,
        'password': password
    })
    db.set('api-key', api_key)
    db.set('password', password)
    set_state('secrets.configured')


@when('api.configured')
@when_not('leadership.is_leader')
def set_secrets_local():
    db.set('api-key', leader_get()['api-key'])
    db.set('password', leader_get()['password'])


@when('api.configured', 'redis.available')
@when_not('api.running')
def connect_to_redis(redis):
    redis_db = redis.redis_data()
    api_key = db.get('api-key')
    password = db.get('password')
    render('settings.py', '{}/settings.py'.format(API_DIR), {
        'API_KEY': api_key,
        'JUJU_ADMIN_USER': 'admin',
        'JUJU_ADMIN_PASSWORD': password,
        'SOJOBO_API_DIR': API_DIR,
        'LOCAL_CHARM_DIR': config()['charm-dir'],
        'SOJOBO_IP': 'http://{}'.format(HOST),
        'SOJOBO_USER': USER,
        'REDIS_HOST': redis_db['host'],
        'REDIS_PORT': redis_db['port']
    })
    set_state('api.running')
    service_restart('nginx')
    status_set('active', 'admin-password: {} api-key: {}'.format(password, api_key))


@when_not('redis.available')
def redis_db_removed():
    remove_state('api.running')
    status_set('blocked', 'Waiting for a connection with redis')


@when('sojobo.available', 'api.running')
def configure(sojobo):
    api_key = db.get('api-key')
    sojobo.configure('https://{}'.format(HOST), API_DIR, api_key, USER)


@when('proxy.available', 'api.running')
def configure_proxy(proxy):
    proxy.configure(80)
    set_state('api.proxy-configured')
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


def install_api():
    for pkg in ['Jinja2', 'Flask', 'pyyaml', 'click', 'pygments', 'apscheduler',
                'gitpython', 'redis', 'asyncio_extras', 'requests']:
        subprocess.check_call(['pip3', 'install', pkg])
    subprocess.check_call(['pip3', 'install', 'juju==0.6.0'])
    mergecopytree('files/sojobo_api', API_DIR)
    if not os.path.isdir('{}/files'.format(API_DIR)):
        os.mkdir('{}/files'.format(API_DIR))
    if not os.path.isdir('{}/bundle'.format(API_DIR)):
        os.mkdir('{}/bundle'.format(API_DIR))
    if not os.path.isdir('{}/log'.format(API_DIR)):
        os.mkdir('{}/log'.format(API_DIR))
    if not os.path.isdir('{}/backup'.format(API_DIR)):
        os.mkdir('{}/backup'.format(API_DIR))
    adduser(USER)
    if not os.path.isdir('/home/{}'.format(USER)):
        os.mkdir('/home/{}'.format(USER))
    chownr('/home/{}'.format(USER), USER, USER, chowntopdir=True)
    chownr(API_DIR, USER, GROUP, chowntopdir=True)
    service_restart('nginx')
    status_set('active', 'The Sojobo-api is installed')
    application_version_set('1.0.0')