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
from charms.reactive import when
from charms.reactive import when_any
from charms.reactive import when_not
from charms.reactive import set_state
from charms.reactive import remove_state
import charms.apt

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import service_restart

from elasticbeats import render_without_context
from elasticbeats import enable_beat_on_boot
from elasticbeats import push_beat_index


@when_not('apt.installed.metricbeat')
def metricbeat():
    status_set('maintenance', 'Installing Metricbeat.')
    charms.apt.queue_install(['metricbeat'])
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
