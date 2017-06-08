import falcon
import json
import jwt

import RethinkDBDatabaseManager


class UserDocumentResource:

    def __init__(self):
        self.database_manager = RethinkDBDatabaseManager.RethinkDBDatabaseManager()

    def on_get(self, req, resp, table=None, doc_id=None):
        # Return note for particular ID
        if doc_id:
            resp.body = self.database_manager.get_one(table, doc_id)
        else:
            resp.body = self.database_manager.get_all(table)

        print(req.headers)
        if 'AUTHENTICATION' in req.headers:
            print(jwt.decode(req.headers['AUTHENTICATION'], 'tree', algorithm=['HS256']))
        # jwt.decode(encoded, 'secret', algorithm=['HS256'])

    def on_post(self, req, resp, table=None):
        # If table does not exist, create it
        self.database_manager.add_table(table)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            result = json.loads(raw_json)
            sid = self.database_manager.save(result, table)
            resp.body = '{"message": "Successfully inserted.", "id": '+sid+'}'
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. The ''JSON was incorrect.')
