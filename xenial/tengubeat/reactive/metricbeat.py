#!/usr/bin/env python3
# Copyright (C) 2016  Ghent University
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
from charms.reactive import when, when_any, when_not, set_state, remove_state
from charms.templating.jinja2 import render
import charms.apt# pylint: disable=E
import requests

from charmhelpers.core.hookenv import config, status_set
from charmhelpers.core.host import service_restart
from charmhelpers.core.unitdata import kv

from elasticbeats import parse_protocols, enable_beat_on_boot, push_beat_index # pylint: disable=E0401

@when_not('apt.installed.metricbeat')
def metricbeat():
    status_set('maintenance', 'Installing Metricbeat.')
    charms.apt.queue_install(['metricbeat'])# pylint: disable=E
    set_state('metricbeat.installed')
    set_state('beat.render')

@when('beat.render')
@when_any('elasticsearch.available', 'logstash.available')
def render_metricbeat_template():
    render_without_context('metricbeat.yml', '/etc/metricbeat/metricbeat.yml')
    remove_state('beat.render')
    status_set('active', 'metricbeat ready.')
    service_restart('metricbeat')

@when('config.changed.install_sources')
@when('config.changed.install_keys')
def reinstall_metricbeat():
    remove_state('apt.installed.metricbeat')

@when('apt.installed.metricbeat')
@when_not('metricbeat.autostarted')
def enlist_metricbeat():
    enable_beat_on_boot('metricbeat')
    set_state('metricbeat.autostarted')

@when('apt.installed.metricbeat')
@when('elasticsearch.available')
@when_not('metricbeat.index.pushed')
def push_metricbeat_index(elasticsearch):
    hosts = elasticsearch.list_unit_data()
    for host in hosts:
        host_string = "{}:{}".format(host['host'], host['port'])
    push_beat_index(host_string, 'metricbeat')
    set_state('metricbeat.index.pushed')

def render_without_context(source, target):
    ''' Render beat template from global state context '''
    cache = kv()
    context = config()

    logstash_hosts = cache.get('beat.logstash')
    elasticsearch_hosts = cache.get('beat.elasticsearch')
    unitname = cache.get('principal_name')
    context['principal_unit'] = unitname
    context['application'] = unitname.split('/')[0]
    instance = get_instance_id(unitname)
    context['instance'] = instance
    if logstash_hosts:
        context.update({'logstash': logstash_hosts})
    if elasticsearch_hosts:
        context.update({'elasticsearch': elasticsearch_hosts})
    if 'protocols' in context.keys():
        context.update({'protocols': parse_protocols()})
    # Split the log paths
    if 'logpath' in context.keys() and not isinstance(context['logpath'], list):  # noqa
        context['logpath'] = context['logpath'].split(' ')
    render(source, target, context)


def get_instance_id(unitname):
    conf = config()
    url = 'http://{}:5000/tengu/controllers/{}/models/{}/applications/{}/units/{}'.format(conf['sojobo-ip'], conf['controller'], conf['model'], unitname.split('/')[0], unitname.split('/')[1])
    myheaders = {'api-key' : conf['api-key']}
    unit = requests.get(url, headers=myheaders, auth={conf['user'], conf['pass']})
    instance = unit['instance-id']
    return instance
