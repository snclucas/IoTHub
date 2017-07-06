import falcon
import json


class ServerInfo:

    def on_get(self, req, resp):
        resp.body = json.dumps({'status': 'running'})


class ServerInfoHTML:

   def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.content_type = 'text/html'
        with open('api.html', 'r') as f:
            resp.body = f.read()

