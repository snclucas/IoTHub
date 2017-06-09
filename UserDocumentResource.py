import falcon
import json
import pprint

from AuthenticationManager import AuthenticationManager

import RethinkDBDatabaseManager


class UserDocumentResource:

    def __init__(self):
        self.database_manager = RethinkDBDatabaseManager.RethinkDBDatabaseManager()

    def on_get(self, req, resp, table=None, doc_id=None):
        [status, jwt_result] = AuthenticationManager.verify_jwt(req.headers)
        if status is True:
            # Return note for particular ID
            if doc_id:
                resp.body = self.database_manager.get_one(table, doc_id)
            else:
                resp.body = self.database_manager.get_all(table)
        else:
            resp.body = jwt_result

    def on_post(self, req, resp, table=None):
        q_params = falcon.uri.parse_query_string(req.query_string, keep_blank_qs_values=False, parse_qs_csv=True)
        explode = False
        explode_on = ""
        if 'explode' in q_params:
            explode = True
            explode_on = q_params['explode']
            print(explode_on)
        print(q_params)

        # If table does not exist, create it
        self.database_manager.add_table(table)
        try:
            raw_json = req.stream.read().decode('utf-8')
            parsed_json = json.loads(raw_json)
            if explode is True:
                if explode_on in parsed_json:
                    parsed_json = parsed_json[explode_on]
                else:
                    print("Oops")
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)

        try:
            doc_save_result = {}
            doc_save_result2 = []
            for i in range(len(parsed_json)):
                sid = self.database_manager.save(parsed_json[i], table)
                doc_save_result[str(i)] = '{"message": "Successfully inserted.", "id": "'+sid+'"}'
                doc_save_result2.append({"message": "Successfully inserted.", "id": sid})
            pprint.pprint({"saved_docs": json.dumps(doc_save_result2)})
            resp.body = {"saved_docs": json.dumps(doc_save_result2)}
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. The ''JSON was incorrect.')
