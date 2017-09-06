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

from charms.reactive import when, when_not, set_state, hookenv
from charmhelpers.core.hookenv import status_set, service_name, log, unit_private_ip, config

TOPIC = ''
PORT = ''

@when_not('layer-kafka-topic.installed')
@when('kafka.ready')
def install_kafka_topic(kafka):
    TOPIC = service_name()
    log('Creating Kafka Topic {}'.format(TOPIC))
    zks = kafka.zookeepers()
    kafkas = kafka.kafkas()
    for unit in kafkas:
        if unit['host'] == unit_private_ip():
            PORT = unit['port']
    string_zks = ''
    for zk in zks:
        string_zks += '{}:{},'.format(zk['host'], zk['port'])
    string_zks = string_zks[:-1]
    conf = config()
    sp.check_call(['/usr/lib/kafka/bin/kafka-topics.sh', '--zookeeper', string_zks, '--create', '--topic',
                   TOPIC, '--partitions', str(conf['partitions']), '--replication-factor', str(conf['replication-factor'])])
    status_set('active', 'Topic {} is available.'.format(TOPIC))
    set_state('layer-kafka-topic.installed')

@when('topic.available', 'layer-kafka-topic.installed')
@when_not('layer-kafka-topic.exported')
def setup_topic(topic):
    topic.configure(TOPIC, PORT)
    set_state('layer-kafka-topic.exported')
