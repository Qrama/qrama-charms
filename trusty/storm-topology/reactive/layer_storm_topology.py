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

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set

@when_not('layer-storm-topology.installed')
def install_layer_storm_topology():
    status_set('active', 'Ready')
    set_state('layer-storm-topology.installed')

@when('layer-storm-topology.installed', 'db.availble')
@when_not('layer-storm-topology.dbconnected')
def connect_to_db(db):
    print(db.connection)
    set_state('layer-storm-topology.dbconnected')
