#!/usr/home/trusteei/virtualenvs/kspolonia/bin/python
import sys
import traceback

try:
    from flup.server.fcgi import WSGIServer
    from a2wsgi import ASGIMiddleware

    sys.path.append('/usr/home/trusteei/flaskprojects/kspolonia/backend')
    from app import app as fastapi_app

    wsgi_app = ASGIMiddleware(fastapi_app)

    class ScriptNameStripper(object):
      def __init__(self, app):
        self.app = app

      def __call__(self, environ, start_response):
        try:
            environ['SCRIPT_NAME'] = ''
            return self.app(environ, start_response)
        except Exception as e:
            with open("/usr/home/trusteei/fcgi_runtime_error.txt", "a") as f:
                f.write("Runtime exception:\n" + traceback.format_exc() + "\n")
            raise

    wrapper = ScriptNameStripper(wsgi_app)
    
    if __name__ == '__main__':
        WSGIServer(wrapper).run()

except Exception as e:
    with open("/usr/home/trusteei/fcgi_startup_error.txt", "w") as f:
        f.write("Startup exception:\n" + traceback.format_exc() + "\n")
