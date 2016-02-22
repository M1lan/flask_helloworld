#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Time-stamp: <2016-02-22 milan.santosi@gmail.com>

import os
import subprocess

from flask import Flask, jsonify
from flask.ext.hookserver import Hooks


app = Flask(__name__)
app.config['GITHUB_WEBHOOKS_KEY'] = os.environ['SECRET']
hooks = Hooks(app, url='/self-deploy')


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


if __name__ == "__main__":
    app.run(host='0.0.0.0')
