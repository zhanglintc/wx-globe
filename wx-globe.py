#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from flask import Flask
app = Flask(__name__)

host = '0.0.0.0'
port = '5657'
debug = 1

def run_tornado():
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port, address=host)
    IOLoop.instance().start()

def run_flask():
    app.run(host=host, port=port)

@app.route('/')
def index():
    return 'Hello World!'

if __name__ == '__main__':
    run_flask() if debug else run_tornado()
