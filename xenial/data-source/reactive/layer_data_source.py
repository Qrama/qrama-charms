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
import os
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from charmhelpers.core.templating import render
from charms.reactive import when, when_not, set_state, hookenv
from charmhelpers.core.hookenv import status_set, service_name, log, unit_private_ip, config

SCRIPT_DIR = '/opt/script'

@when_not('layer-data-source.installed')
def install_layer_data_source():
    sp.check_call(['pip3', 'install', 'feedparser', 'stomp.py'])
    if not os.path.exists(SCRIPT_DIR):
        os.makedirs(SCRIPT_DIR)
    set_state('layer-data-source.installed')
    status_set('blocked', 'waiting for relation with ActiveMQ Topic')


@when_not('layer-data-source.script.deployed')
@when('topic.available', 'layer-data-source.installed')
def deploy_script(topic):
    data = topic.connection()
    context = {'host': data['host'], 'port': 61613, 'topic': data['name']}
    render('feed.py', '{}/topic_producer.py'.format(SCRIPT_DIR), context)
    sp.Popen(['python3', '{}/topic_producer.py'.format(SCRIPT_DIR)])
    status_set('active', 'RSS feed is sending data to ActiveMQ Topic')
    set_state('layer-data-source.script.deployed')
