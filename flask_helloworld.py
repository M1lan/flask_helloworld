#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2016-02-22 milan.santosi@gmail.com>

import os
import hmac
import hashlib
import subprocess

from flask import Flask, jsonify, request

SECRET = os.environ['SECRET']
app = Flask(__name__)


class InvalidAPIUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidAPIUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/<something>')
def handle_invalid_routes(something):
    raise InvalidAPIUsage('Undefined route ' + something, status_code=404)


@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/version')
def version():
    cmd = ['git', 'rev-parse', 'HEAD']
    p = subprocess.Popen(cmd,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    out, err = p.communicate()
    return out


# c.f. https://pypi.python.org/pypi/pywebhooks
def verify_hmac_hash(incoming_json, secret_key, incoming_signature):
    signature = hmac.new(secret_key,
                         str(incoming_json),
                         digestmod=hashlib.sha1).hexdigest()
    try:
        return hmac.compare_digest(bytes(signature), bytes(incoming_signature))
    except Exception as e:
        raise InvalidAPIUsage('ERROR:' + str(e), status_code=400)


# c.f. https://developer.github.com/webhooks/securing/
@app.route("/self-deploy/{}".format(SECRET), methods=['POST'])
def self_deploy():
    signature = request.headers['X-Hub-Signature']
    payload = request.get_json()

    if verify_hmac_hash(payload, SECRET, signature):
        try:
            output = subprocess.check_output(['git', 'pull', '--ff-only',
                                              'origin', 'master'], )
            print output
        except subprocess.CalledProcessError as err:
            return err.output
    return jsonify(dict(ok=True))


if __name__ == "__main__":
    app.run(debug=True)
