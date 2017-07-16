import json


class NoEndpointResource:

    def on_get(self, req, resp, endpoint_type=None, table=None, catch=None):
        if endpoint_type is None:
            resp.body = json.dumps({"status": "fail", "message": "Missing endpoint type"})
        elif endpoint_type != 'd' and endpoint_type != 'p':
            resp.body = json.dumps({"status": "fail", "message": "Invalid endpoint type"})
        elif table is None:
            resp.body = json.dumps({"status": "fail", "message": "Endpoint not specified"})
        elif endpoint_type is None:
            resp.body = json.dumps({"status": "fail", "message": "Invalid endpoint type"})
        else:
            resp.body = json.dumps({"status": "fail", "message": "Document not found"})

    def on_post(self, req, resp, endpoint_type=None, table=None, catch=None):
        if endpoint_type is None:
            resp.body = json.dumps({"status": "fail", "message": "Missing endpoint type"})
        elif endpoint_type != 'd' and endpoint_type != 'p':
            resp.body = json.dumps({"status": "fail", "message": "Invalid endpoint type"})
        elif table is None:
            resp.body = json.dumps({"status": "fail", "message": "Endpoint not specified"})
        elif endpoint_type is None:
            resp.body = json.dumps({"status": "fail", "message": "Invalid endpoint type"})
        else:
            resp.body = json.dumps({"status": "fail", "message": "Document not found"})
