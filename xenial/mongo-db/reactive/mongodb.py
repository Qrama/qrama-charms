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
import binascii
import os
import yaml
from charms import apt #pylint: disable=E0611
from charmhelpers.core.hookenv import status_set, log, config, open_port, unit_private_ip
from charmhelpers.core.templating import render
from charmhelpers.core.host import service_restart, service_start, service_stop
from charmhelpers.contrib.python.packages import pip_install
from charms.reactive import hook, when, when_not, set_state


CONF = '/etc/mongod.conf'
###############################################################################
# INSTALLATION AND UPGRADES
###############################################################################
@when_not('apt.installed.mongodb-org', 'mongodb.installed')
def install_apt():
    apt.queue_install(['mongodb-org'])


@when('apt.installed.mongodb-org')
@when_not('mongodb.installed')
def setup():
    log('Installing MongoDB')
    install()
    set_state('mongodb.installed')


@hook('upgrade-charm')
def upgrade_charm():
    log('Updating MongoDB')
    install()
    set_state('mongodb.installed')


@when('mongodb.installed', 'config.changed')
def configure():
    with open(CONF, 'r+') as conf:
        yconf = yaml.load(conf)
        yconf['security']['authorization'] = 'enabled'
        log_lvl = config()['log_lvl']
        if log_lvl > 5 or log_lvl < 0:
            log_lvl = 5
        for logtype in yconf['systemLog']['component'].keys():
            yconf['systemLog']['component'][logtype]['verbosity'] = log_lvl
        yconf['systemLog']['verbosity'] = log_lvl
        yconf['net']['port'] = config()['port']
        yconf['net']['bindIp'] = unit_private_ip()
        open_port(config()['port'])
    with open(CONF, 'w+') as conf:
        yaml.dump(yconf, conf, default_flow_style=False)
    restart()


def install():
    service_stop('mongod')
    for pkg in ['PyMongo']:
        pip_install(pkg)
    render('mongod.conf', CONF, {})
    service_start('mongod')
    from pymongo import MongoClient
    client = MongoClient('127.0.0.1:{}'.format(config()['port']))
    client.admin.add_user(config()['admin_usr'], config()['admin_pass'], roles=['root'])
    service_stop('mongod')


def restart():
    service_restart('mongod')
    status_set('active', 'MongoDB is running')


@when('mongodb.available')
def configure_db(mongodb):
    mongodb.configure(config()['admin_usr'], config()['admin_pass'], unit_private_ip(), config()['port'])
