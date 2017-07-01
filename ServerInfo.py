import json


class ServerInfo:

    def on_get(self, req, resp):
        resp.body = json.dumps({'status': 'running'})
