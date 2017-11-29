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
import subprocess

from charms.reactive import when, when_not, set_state, remove_state
from charmhelpers.core.hookenv import status_set, config, service_name
from charmhelpers.core import unitdata
import xml.etree.ElementTree as ET

TOPIC = config()['topic']
unitd = unitdata.kv()

@when_not('activemq-topic.installed')
@when('messagebroker.available')
def install_activemq_topic(messagebroker):
    version = list(messagebroker.connection())[0]['version']
    port = list(messagebroker.connection())[0]['port']
    unitd.set('port', port)
    path = '/opt/apache-activemq/apache-activemq-{}/conf/activemq.xml'.format(version)
    subprocess.check_call(['/opt/apache-activemq/apache-activemq-{}/bin/activemq'.format(version), 'stop'])
    ET.register_namespace('','http://www.springframework.org/schema/beans')
    ET.register_namespace('','http://activemq.apache.org/schema/core')
    ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
    et = ET.parse(path)
    root_node = et.getroot()
    broker_node = validate_node(root_node)
    if not broker_node.findall('./{http://activemq.apache.org/schema/core}destinations'):
        dest_node = ET.SubElement(broker_node, 'destinations')
    else:
        dest_node = broker_node.findall('./{http://activemq.apache.org/schema/core}destinations')[0]
    new_topic = ET.SubElement(dest_node, TOPIC)
    new_topic.attrib['physicalName']= service_name()
    status_set('active', '{} {} is configured and available'.format(TOPIC, service_name()))
    et.write(path)
    subprocess.check_call(['/opt/apache-activemq/apache-activemq-{}/bin/activemq'.format(version), 'start'])
    set_state('activemq-topic.installed')

@when('activemq-topic.installed', 'activemqtopic.available')
def configure_topic(activemqtopic):
    port = unitd.get('port')
    activemqtopic.configure(TOPIC, service_name(), port)


@when('activemq-topic.installed', 'messagebroker.removed')
def remove_topic(messagebroker):
    version = list(messagebroker.connection())[0]['version']
    path = '/opt/apache-activemq/apache-activemq-{}/conf/activemq.xml'.format(version)
    subprocess.check_call(['/opt/apache-activemq/apache-activemq-{}/bin/activemq'.format(version), 'stop'])
    ET.register_namespace('','http://www.springframework.org/schema/beans')
    ET.register_namespace('','http://activemq.apache.org/schema/core')
    ET.register_namespace('xsi','http://www.w3.org/2001/XMLSchema-instance')
    et = ET.parse(path)
    root_node = et.getroot()
    broker_node = validate_node(root_node)
    dest_node = broker_node.findall('./{http://activemq.apache.org/schema/core}destinations')[0]
    for topic in dest_node.findall('*[@physicalName=\"{}\"]'.format(service_name())):
        dest_node.remove(topic)
    et.write(path)
    subprocess.check_call(['/opt/apache-activemq/apache-activemq-{}/bin/activemq'.format(version), 'start'])
    remove_state('activemq-topic.installed')



def validate_node(elem):
    return elem.findall('./{http://activemq.apache.org/schema/core}broker')[0]
