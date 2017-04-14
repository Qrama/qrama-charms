# !/usr/bin/env python3
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
# pylint: disable=c0111,c0301,c0325,w0406
from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, unit_private_ip, open_port, close_port


@when('apt.installed.prometheus-node-exporter')
@when_not('node-exporter.installed')
def install():
    status_set('blocked', 'Waiting for relation with Prometheus')
    set_state('node-exporter.installed')


@when('prometheus.available', 'node-exporter.installed')
def config(prometheus):
    open_port(9100)
    prometheus.configure(9100, unit_private_ip())
    status_set('active', 'Sending info to Prometheus')


@when('monitoring.removed', 'node-exporter.installed')
def remove_controller(monitoring):
    close_port(9100)
    status_set('blocked', 'Waiting for relation with Prometheus')
