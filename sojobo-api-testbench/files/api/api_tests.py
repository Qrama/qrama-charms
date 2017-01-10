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
# pylint: disable=c0111,c0301,c0325, r0903,w0406,c0103
import os
from subprocess import check_output
from flask import Blueprint, Response

from api import w_errors as errors, w_juju as juju
from sojobo_api import create_response


TESTS = Blueprint('tests', __name__)


def get():
    return TESTS


def list_tests():
    t_list = []
    for f_path in os.listdir('{}/tests'.format(juju.get_api_dir())):
        if 'test_' in f_path and '.pyc' not in f_path:
            t_list.append(f_path.split('.')[0])
    return t_list


@TESTS.route('/', methods=['GET'])
def get_tests():
    return create_response(200, list_tests())


@TESTS.route('/', methods=['POST'])
def start_tests():
    return Response(check_output('python3', '{}/sojobo_api_testbench.py'.format(juju.get_api_dir()), '-v'))


@TESTS.route('/<test>', methods=['PUT'])
def start_test(test):
    try:
        if test in list_tests():
            return Response(check_output('python3', '{}/tests/{}.py'.format(juju.get_api_dir(), test), '-v'))
        else:
            return create_response(errors.does_not_exist('test'))
    except KeyError:
        return create_response(errors.invalid_data())


@TESTS.route('/log', methods=['GET'])
def get_log():
    def return_log():
        with open('/home/ubuntu/flask-sojobo-api.log') as f:
            for line in f.readlines():
                if '\" 2' in line:
                    color = 'green'
                elif '\" 3' in line:
                    color = 'yellow'
                elif '\" 4' in line:
                    color = 'orange'
                elif '\" 5' in line:
                    color = 'red'
                else:
                    color = 'black'
                yield '<span style="color: {}">{}</span><br>'.format(color, line)
    return Response(return_log(), mimetype='text/html')


@TESTS.route('/results', methods=['GET'])
def get_results():
    def return_results():
        with open('/home/ubuntu/test-results.log') as f:
            for line in f.readlines():
                yield '{}<br>'.format(line)
    return Response(return_results(), mimetype='text/html')
