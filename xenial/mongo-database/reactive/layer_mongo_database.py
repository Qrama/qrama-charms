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

from charms.reactive import when, when_not, set_state, hookenv, hook
from charmhelpers.core.hookenv import status_set, service_name, log, unit_private_ip
from charmhelpers.contrib.python.packages import pip_install

URI= ''
DB_NAME= ''

@when_not('layer-mongo-database.installed')
@when('mongodb.available')
def install_layer_mongo_database(mongodb):
    pip_install('pymongo')
    DB_NAME = service_name()
    import pymongo
    log('Creating database {}'.format(DB_NAME ))
    URI = mongodb.connection_string()
    conn = pymongo.MongoClient(URI)
    tengu_db = conn[DB_NAME ]
    status_set('active', 'Database {} succesfully created'.format(DB_NAME ))
    set_state('layer-mongo-database.installed')

@when('layer-mongo-database.installed', 'db.available')
@when_not('layer-mongo-database.configured')
def export_db(db):
    print(db)
    db.configure(URI, DB_NAME)
    set_state('layer-mongo-database.configured')
