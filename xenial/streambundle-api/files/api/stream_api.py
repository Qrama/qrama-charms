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
# pylint: disable=c0111,c0103,c0301,e0401,c0413
import json
import sys
sys.path.append('/opt/streambundle_api')
from streambundle_api import w_datastore as ds
from flask import Flask, Response

app = Flask(__name__)

@app.route("/")
def hello():
    data = {"Version": "0.1.0", "Name":"Streambundle-api"}
    return create_response(200, data)


@app.route("/users", methods=['GET'])
def get_all_users():
    res = ds.get_all_fridges()
    return create_response(200, res)


@app.route("/users/<user>", methods=['GET'])
def get_user(user):
    res = ds.get_user(user)
    return create_response(200, res)


@app.route("/tags", methods=['GET'])
def get_tags():
    res = ds.get_all_tags()
    return create_response(200, res)


@app.route("/tag/<tag>", methods=['GET'])
def get_tag(tag):
    res = ds.get_tag(tag)
    return create_response(200, res)


@app.route("/users/<user>/topics", methods=['GET'])
def get_user_topics(user):
    res = ds.get_user_topics(user)
    return create_response(200, res)


def create_response(stat, res):
    return_object = json.dumps(res)
    return Response(return_object,
                    status=stat,
                    mimetype='application/json')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
