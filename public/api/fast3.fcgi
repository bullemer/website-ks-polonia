#!/usr/home/trusteei/virtualenvs/kspolonia/bin/python

import sys
from flup.server.fcgi import WSGIServer
from a2wsgi import ASGIMiddleware

# Absolute path to the backend directory on the Hetzner server
sys.path.append('/usr/home/trusteei/flaskprojects/kspolonia/backend')
from app import app as fastapi_app

# Convert ASGI (FastAPI) to WSGI
wsgi_app = ASGIMiddleware(fastapi_app)

class ScriptNameStripper(object):
  def __init__(self, app):
    self.app = app

  def __call__(self, environ, start_response):
    # Strip SCRIPT_NAME to ensure FastAPI routing works correctly when mounted under /api
    environ['SCRIPT_NAME'] = ''
    return self.app(environ, start_response)

wsgi_app = ScriptNameStripper(wsgi_app)

if __name__ == '__main__':
    WSGIServer(wsgi_app).run()
