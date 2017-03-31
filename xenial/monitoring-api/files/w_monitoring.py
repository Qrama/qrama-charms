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
import json
import yaml
import requests
from sojobo_api import settings

from elasticsearch import Elasticsearch #pylint: disable = e0401

from flask import  abort
from sojobo_api.api import w_errors as errors, w_juju as juju #pylint: disable = e0401


def monitor_names():
    return {'db': 'monitor-tengu', 'xenial': 'xenial-tengubeat', 'trusty': 'trusty-tengubeat'}


def get_series():
    return ['xenial', 'trusty']


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
    controller = data['controller']
    model = data['model']
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


def get_machines_by_application(controller, model, application, req):
    url = '{}/tengu/controllers/{}/models/{}/applications/{}'.format(
        settings.SOJOBO_IP, controller, model, application
        )
    res = requests.get(url, headers={'api-key': req.headers['api-key']}, auth=(req.authorization.username, req.authorization.password))
    result = []
    jsonres = json.loads(res.text)
    for unit in jsonres['units']:
        result.append({'name': unit['name'], 'instance-id':unit['instance-id']})
    return result


def get_monitor_dir():
    file_path = '{}/monitoring'.format(settings.SOJOBO_API_DIR)
    return file_path


def reformat_json(old_json):
    data = {}
    for hit in old_json['hits']['hits']:
        data[hit['_id']] = {
            'name' : hit['_source']['beat']['name'],
            'timestamp': hit['_source']['@timestamp'],
            'metrics': hit['_source']['system']
        }
    return data


def execute_specific_query(controller, model, match):
    es_ip = receive_ip_address(controller, model)
    elasticsearch = connect_to_elasticsearch(es_ip)
    result = elasticsearch.search(
        index='metricbeat-*',
        body={"query":{"query_string":{"query": match, "analyze_wildcard":True}}}
        )
    return result


def add_application(token, application):
    serie = juju.get_application_info(token, application)['series']
    names = monitor_names()
    if serie in get_series():
        if juju.app_exists(token, names['db']):
            juju.add_relation(token, application, monitor_names()[serie])
            result = 'OK'
        else:
            with open('{}/monitoring.yaml'.format(get_monitor_dir()), 'r') as ybundle:
                bundle = yaml.load(ybundle)
            data1 = {'api-key': juju.get_api_key(), 'sojobo-ip': settings.SOJOBO_IP, 'controller': token.c_name,
                     'model': token.m_name, 'user': settings.JUJU_ADMIN_USER, 'pass': settings.JUJU_ADMIN_PASSWORD}
            data2 = {'api-key': juju.get_api_key(), 'sojobo-ip': settings.SOJOBO_IP, 'controller': token.c_name,
                     'model': token.m_name, 'controller-type': token.c_token.type}
            relations = []
            for series in get_series():
                bundle['services'][names[series]]['charm'] = '{}/qrama-charms/{}/tengubeat'.format(settings.LOCAL_CHARM_DIR, series)
                bundle['services'][names[series]]['options'] = data1
                relations.append(['{}:client'.format(names['db']), '{}:elasticsearch'.format(names[series])])
            bundle['relations'] = relations
            bundle['services'][names['db']]['charm'] = '{}/qrama-charms/xenial/elasticsearch-tengu'.format(settings.LOCAL_CHARM_DIR)
            bundle['services'][names['db']]['options'] = data2
            juju.deploy_bundle(token, bundle)
            juju.add_relation(token, application, monitor_names()[serie])
            result = 'OK'
    else:
        result = 'Series not supported'
    return result


def remove_application(token, application):
    series = juju.get_application_info(token, application)['series']
    if series in get_series():
        juju.remove_relation(token, application, monitor_names()[series])
        result = 'OK'
    else:
        result = 'Series not supported'
    return result
