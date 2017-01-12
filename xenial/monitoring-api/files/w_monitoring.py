
# !/usr/bin/env python3
# Copyright (C) 2016  Qrama
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
import logging
import json
import yaml
import requests

from elasticsearch import Elasticsearch #pylint: disable = e0401

from flask import  abort
from api import w_errors as errors, w_juju as juju #pylint: disable = e0401

def check_authentication(api_key):
    with open('{}/api-key'.format(juju.get_api_dir()), 'r') as key:
        apikey = key.readlines()[0]
    if api_key != apikey:
        abort(errors.unauthorized())

# def connect_to_es_webserver(es_ip):
#     conf = config()
#     username = conf['username']
#     passphrase = conf['pass']
#     elasticsearch = Elasticsearch(
#         [es_ip],
#         http_auth=(username, passphrase),
#         port=80,
#         )
    # return elasticsearch

def update_ip_list(file_path, data):
    charm_name = data['service-name']
    controller = charm_name.split('-')[0]
    model = charm_name.split('-')[1]
    es_ip = str(data['charm-ip'])
    es_data = {controller:{model: es_ip}}
    with open(file_path, 'a') as yaml_file:
        yaml.dump(es_data, yaml_file, default_flow_style=False)

def connect_to_elasticsearch(es_ip):
    elasticsearch = Elasticsearch(
        [es_ip],
        port=9200,
        )
    return elasticsearch

def receive_ip_address(controller, model): #pylint: disable = W0613
    file_path = '{}/elastic_ip.yaml'.format(get_monitor_dir())
    with open(file_path) as data:
        es_data = yaml.load(data)
        es_ip = es_data[controller][model]
    return es_ip

def get_machines_by_application(controller, model, application, api_key):
    url = 'http://127.0.0.1:5000/tengu/controllers/{}/models/{}/applications/{}'.format(
        controller, model, application
        )
    res = requests.get(url, headers={'api-key': api_key})
    logging.debug(res)
    result = {}
    jsonres = json.loads(res.text)
    for unit in jsonres['message']['units']:
        result[unit['name']] = unit['machine']
    return result

def get_monitor_dir():
    file_path = '{}/monitoring'.format(juju.get_api_dir())
    return file_path
