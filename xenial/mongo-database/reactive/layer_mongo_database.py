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
from charms.reactive import when, when_not, set_state, hook
from charmhelpers.core import unitdata
from charmhelpers.core.hookenv import status_set, service_name, log, unit_private_ip, config
from charmhelpers.contrib.python.packages import pip_install

unitd = unitdata.kv()

@when_not('layer-mongo-database.installed')
@when('mongodb.available')
def install_layer_mongo_database(mongodb):
    pip_install('pymongo')
    db_name = service_name()
    conf = config()
    import pymongo
    log('Creating database {}'.format(db_name))
    uri = mongodb.connection_string()
    conn = pymongo.MongoClient(uri)
    tengu_db = conn[db_name]
    tengu_db[conf['collection']]
    unitd.set('db_name', db_name)
    unitd.set('uri', uri)
    status_set('active', 'Database {} succesfully created'.format(db_name))
    set_state('layer-mongo-database.installed')

@when('layer-mongo-database.installed', 'db.available')
def export_db(db):
    conf = config()
    db.configure(unitd.get('uri'), unitd.get('db_name'), conf['collection'])
