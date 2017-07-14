import json
import falcon
from datetime import *
from bson import ObjectId

import config
from util.JSONEncoder import JSONEncoder
from AuthenticationManager import AuthenticationManager


class NoEndpointResource:

    def on_get(self, req, resp, endpoint_type=None, table=None, catch=None):
        resp.body = json.dumps({"status": "fail", "message": "Document not found"})
