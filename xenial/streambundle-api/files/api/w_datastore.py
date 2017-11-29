#!/usr/bin/python3.6
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
# pylint: disable=c0111,c0103,c0301,e0401
from pymongo import MongoClient
from streambundle_api import settings

def connect_to_db():
    client = MongoClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB]
    return db

def get_all_users():
    db = connect_to_db()
    result = []
    collections = db.collection_names()
    for col in collections:
        if col.startswith('author'):
            result.append(col.split('_')[1])
    return result

def get_user(user):
    db = connect_to_db()
    return db['author_{}'.format(user)]

def get_all_tags():
    db = connect_to_db()
    result = []
    collections = db.collection_names()
    for col in collections:
        if col.startswith('tag'):
            result.append(col.split('_')[1])
    return result

def get_tag(tag):
    db = connect_to_db()
    return db['tag_{}'.format(tag)]

def get_user_topics(user):
    db = connect_to_db()
    usr = db[user]
    return usr['topics']
