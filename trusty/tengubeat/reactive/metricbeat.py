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
import json
import subprocess
import yaml

from charms.reactive import when, when_any, when_not, set_state, remove_state
from charms.templating.jinja2 import render
import charms.apt# pylint: disable=E

from charmhelpers.core.hookenv import config, status_set, remote_unit
from charmhelpers.core.host import service_restart
from charmhelpers.core.unitdata import kv
from charmhelpers.contrib.python.packages import pip_install

from elasticbeats import parse_protocols, enable_beat_on_boot, push_beat_index, render_without_context # pylint: disable=E0401

@when_not('apt.installed.metricbeat')
def metricbeat():
    status_set('maintenance', 'Installing Metricbeat.')
    charms.apt.queue_install(['metricbeat'])# pylint: disable=E
    pip_install(['requests'])
    service_restart('metricbeat')
    set_state('metricbeat.installed')
    set_state('beat.render')

@when('beat.render')
@when_any('elasticsearch.available', 'logstash.available')
def render_metricbeat_template():
    target = '/etc/metricbeat/metricbeat.yml'
    render_without_context('metricbeat.yml', target)
    add_extra_context(target)
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
    service_restart('metricbeat')
    set_state('metricbeat.autostarted')


@when('apt.installed.metricbeat')
@when('elasticsearch.available')
@when_not('metricbeat.index.pushed')
def push_metricbeat_index(elasticsearch):
    hosts = elasticsearch.list_unit_data()
    for host in hosts:
        host_string = "{}:{}".format(host['host'], host['port'])
        push_beat_index(host_string, 'metricbeat')
        subprocess.check_call(['curl', '-XPUT', 'http://{}/metricbeat'.format(host_string)])
    set_state('metricbeat.index.pushed')
    service_restart('metricbeat')


def add_extra_context(target):
    with open(target, 'r') as metric:
        data = yaml.load(metric)
    unitname = data['shipper']['name']
    application = unitname.split('/')[0]
    instance = get_instance_id(unitname)
    with open(target, 'a') as metric:
        metric.write('fields: application: {}, instance-id: {}'.format(application, instance))


def get_instance_id(unitname):
    import requests
    conf = config()
    url = '{}/tengu/controllers/{}/models/{}/applications/{}/units/{}'.format(conf['sojobo-ip'], conf['controller'], conf['model'], unitname.split('/')[0], unitname.split('/')[1])
    myheaders = {'api-key' : conf['api-key']}
    unit = requests.get(url, headers=myheaders, auth=(conf['user'], conf['pass']))
    instance = json.loads(unit.text)['instance-id']
    return instance
