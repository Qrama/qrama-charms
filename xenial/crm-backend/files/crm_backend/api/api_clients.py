# pylint: disable=c0111,c0301
#!/usr/bin/env python3
from bson.json_util import dumps
from urllib.parse import unquote
from flask import request, Blueprint
from crm_backend.app import authenticate, APP, MONGO, invalid_data, create_response
from pymongo.errors import DuplicateKeyError


CLIENTS = Blueprint('clients', __name__)
CLIENT_FIELDS = ['_id', 'name', 'address', 'city', 'postal-code', 'country', 'contacts', 'vat', 'iban', 'logo', 'phone',
                 'email']


def parse_client(data):
    keys = list(data.keys())
    for key in keys:
        if key not in CLIENT_FIELDS:
            data.pop(key, None)
    return data


def get():
    with APP.app_context():
        MONGO.db.clients.create_index('name', unique=True)
    return CLIENTS


@CLIENTS.route('', methods=['GET'])
@authenticate
def get_clients():
    code, response = 200, dumps(MONGO.db.clients.find().sort('name', 1))
    response['id'] = response.pop('_id').str
    return create_response(code, response, True)


@CLIENTS.route('', methods=['POST'])
@authenticate
def add_client():
    try:
        code = 200
        result = MONGO.db.clients.insert_one(parse_client(request.json))
        response = dumps(MONGO.db.clients.find_one_or_404({'_id': result.inserted_id}))
        is_json = True
    except DuplicateKeyError:
        code, response, is_json = 409, 'Name already exists', False
    return create_response(code, response, is_json)


@CLIENTS.route('/<name>', methods=['GET'])
@authenticate
def get_client(name):
    code, response = 200, dumps(MONGO.db.clients.find_one_or_404({'name': unquote(name)}))
    return create_response(code, response, True)


@CLIENTS.route('/<name>', methods=['PUT'])
@authenticate
def update_client(name):
    try:
        MONGO.db.clients.update_one({'name': unquote(name)}, {'$set': parse_client(request.json)})
        code, response, is_json = 200, dumps(MONGO.db.clients.find_one_or_404({'name': unquote(name)})), True
    except DuplicateKeyError:
        code, response, is_json = 409, 'Name already exists', True
    return create_response(code, response, is_json)


@CLIENTS.route('/<name>', methods=['DELETE'])
@authenticate
def delete_client(name):
    MONGO.db.clients.delete_one({'name': unquote(name)})
    code, response = 200, dumps(MONGO.db.clients.find().sort('name', 1))
    return create_response(code, response, True)
