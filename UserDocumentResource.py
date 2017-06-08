import falcon
import json

from db_client import *


class UserDocumentResource:

    def on_get(self, req, resp, table=None, doc_id=None):
        # Return note for particular ID
        if doc_id:
            result = {'note': r.db(PROJECT_DB).table(table). get(doc_id).run(db_connection)}
        else:
            note_cursor = r.db(PROJECT_DB).table(table).run(db_connection)
            result = {'notes': [i for i in note_cursor]}
        resp.body = json.dumps(result)

    def on_post(self, req, resp, table=None):
        # If table does not exist, create it
        db_setup(table)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            result = json.loads(raw_json)
            sid = r.db(PROJECT_DB).table(table).insert(result).run(
                db_connection)
            resp.body = '{"message": "Successfully inserted.", "id": '+sid['generated_keys'][0]+'}'
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400 ,'Invalid JSON','Could not decode the request body. The ''JSON was incorrect.')


