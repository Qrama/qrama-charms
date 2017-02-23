#!/usr/bin/env python3

# pylint: disable=c0111,c0301
from importlib import import_module
import json
import logging
import os
from flask import Flask, redirect, request, Response, abort
from flask_pymongo import PyMongo
from functools import wraps
########################################################################################################################
# INIT FLASK
########################################################################################################################
APP = Flask(__name__)
APP.url_map.strict_slashes = False
APP.debug = True
APP.config.from_object('crm_backend.settings')
MONGO = PyMongo(APP)
########################################################################################################################
# SETUP LOGGING
########################################################################################################################
logging.basicConfig(filename='/home/ubuntu/flask-crm-backend.log', level=logging.DEBUG)
########################################################################################################################
# ROUTES
########################################################################################################################
@APP.after_request
def apply_caching(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Authorization,Content-Type,Location,id-token,api-key'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type,Location'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    response.headers['Accept'] = 'application/json'
    return response


@APP.route('/')
def index():
    return create_response(200, 'The service is running')


@APP.route('/favicon.ico')
def api_icon():
    return redirect("http://tengu.io/assets/icons/favicon.ico", code=302)
########################################################################################################################
# HELPERS
########################################################################################################################
def create_response(http_code, return_object, is_json=False):
    if not is_json:
        return_object = json.dumps(return_object)
    return Response(
        return_object,
        status=http_code,
        mimetype='application/json',
    )


def authenticate(func):
    @wraps(func)
    def function(*args, **kwargs):
        try:
            if request.headers['api-key'] != APP.config['API_KEY']:
                abort(403, 'You do not have permission to use the API')
            else:
                return func(*args, **kwargs)
        except KeyError:
            abort(400, 'The request does not have all the required data or the data is not in the right format.')
    return function
########################################################################################################################
# ERROR HANDLERS
########################################################################################################################
@APP.errorhandler(403)
def forbidden(error):
    return create_response(403, error.description)


@APP.errorhandler(400)
def invalid_data(error):
    return create_response(400, error.description)
########################################################################################################################
# API MODULES
########################################################################################################################
def get_apis():
    api_list = []
    for f_path in os.listdir('{}/api'.format(APP.config['API_DIR'])):
        if 'api_' in f_path and '.pyc' not in f_path:
            api_list.append(f_path.split('.')[0])
    return api_list


for api in get_apis():
    module = import_module('crm_backend.api.{}'.format(api))
    APP.register_blueprint(getattr(module, 'get')(), url_prefix='/{}'.format(api.split('_')[1]))
