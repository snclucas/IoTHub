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
        [status, jwt_result] = AuthenticationManager.verify_jwt(req.headers)
        if status is True:
            q_params = falcon.uri.parse_query_string(req.query_string, keep_blank_qs_values=False, parse_qs_csv=True)
            explode = False
            explode_on = ""
            if 'explode' in q_params:
                explode = True
                explode_on = q_params['explode']

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
                doc_save_result = []
                if len(parsed_json) > 1:
                    for i in range(len(parsed_json)):
                        sid = self.database_manager.save(parsed_json[i], table)
                        doc_save_result.append({"message": "Successfully inserted.", "id": sid, "doc": parsed_json[i]})
                else:
                    sid = self.database_manager.save(parsed_json, table)
                    doc_save_result.append({"message": "Successfully inserted.", "id": sid, "doc": parsed_json})

                resp.body = json.dumps({"saved_docs": doc_save_result})
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. The ''JSON was incorrect.')
        else:
            resp.body = jwt_result

    def on_delete(self, req, resp, table=None, doc_id=None):
        [status, jwt_result] = AuthenticationManager.verify_jwt(req.headers)
        if status is True:
            # Return note for particular ID
            if doc_id:
                resp.body = self.database_manager.delete_one(table, doc_id)
            else:
                resp.body = self.database_manager.delete_all(table)
        else:
            resp.body = jwt_result

    def on_put(self, req, resp, table=None, doc_id=None):
        [status, jwt_result] = AuthenticationManager.verify_jwt(req.headers)
        if status is True:
            # Return note for particular ID
            if doc_id:
                try:
                    raw_json = req.stream.read().decode('utf-8')
                    parsed_json = json.loads(raw_json)
                    resp.body = self.database_manager.update(table, doc_id, parsed_json)
                except ValueError:
                    raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. The ''JSON was incorrect.')
            else:
                resp.body = json.dumps({"Success": "Fail", "message": "No document found with supplied ID"})
        else:
            resp.body = jwt_result
