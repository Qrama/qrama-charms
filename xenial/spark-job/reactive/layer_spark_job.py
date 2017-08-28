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
import tempfile

from charms.reactive import when, when_not, set_state
from charmhelpers.core.hookenv import status_set, config, service_name


@when_not('spark-job.installed')
def deploy_job():
    conf = config()
    if conf['job_location']:
        tmp_dir = tempfile.mkdtemp()
        serv_name = service_name()
        sp.check_call(['hdfs', 'dfs', '-chmod', '777', '/user/root'])
        sp.check_call(['wget', '-O', '{}/{}.py'.format(tmp_dir, serv_name), conf['job_location']])
        sp.check_call(['/usr/lib/spark/bin/spark-submit', '{}/{}.py'.format(tmp_dir,serv_name), '--master', 'spark://127.0.0.1:7077'])
        status_set('active', 'Spark job {} is deployed and running on spark'.format(serv_name))
        set_state('spark-job.installed')
    else:
        status_set('blocked', 'Please provide a valid url to deploy job by changing job_location config')
