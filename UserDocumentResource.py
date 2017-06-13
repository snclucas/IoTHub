import json
import falcon

from AuthenticationManager import AuthenticationManager


class UserDocumentResource:

    def __init__(self, database, user_manager):
        self.database = database
        self.user_manager = user_manager
        self.authentication_manager = AuthenticationManager(user_manager)

    def on_get(self, req, resp, table=None, doc_id=None):
        [status, jwt_result, username] = self.authentication_manager.verify_jwt(req.headers)
        print([status, jwt_result, username])
        if status is True:
            table = self.generate_table_name(table, username)
            print(table)
            if doc_id:
                resp.body = self.database.get_one_by_id(table, doc_id)
            else:
                resp.body = self.database.get_all(table)
        else:
            resp.body = jwt_result

    def on_post(self, req, resp, table=None):
        [status, jwt_result, username] = self.authentication_manager.verify_jwt(req.headers)
        if status is True:
            table = self.generate_table_name(table, username)
            q_params = falcon.uri.parse_query_string(req.query_string, keep_blank_qs_values=False, parse_qs_csv=True)
            explode = False
            explode_on = ""
            if 'explode' in q_params:
                explode = True
                explode_on = q_params['explode']

            # If table does not exist, create it
            self.database.add_table(table)
            try:
                raw_json = req.stream.read().decode('utf-8')
                parsed_json = json.loads(raw_json)
                doc_save_result = []
                if explode is True:
                    if explode_on in parsed_json:
                        parsed_json = parsed_json[explode_on]
                        if len(parsed_json) > 1:
                            doc_save_result = self.__save_documents__(table, parsed_json)
                        else:
                            doc_save_result = self.__save_documents__(table, [parsed_json])
                    else:
                        resp.body = json.dumps({"status": "fail", "message":
                                                "Could not find attribute '"+explode_on+"' to explode"})
                        return
                else:
                    sid = self.database.save(parsed_json, table)
                    doc_save_result.append({"status": "success", "message": "Successfully inserted.", "id": sid, "doc": parsed_json})

                resp.body = json.dumps({"saved_docs": doc_save_result})
            except ValueError:
                resp.body = json.dumps({"status": "fail", "message": "Bad JSON"})
                return
        else:
            resp.body = jwt_result

    def on_delete(self, req, resp, table=None, doc_id=None):
        [status, jwt_result, username] = self.authentication_manager.verify_jwt(req.headers)
        if status is True:
            table = self.generate_table_name(table, username)
            if doc_id:
                resp.body = self.database.delete_one(table, doc_id)
            else:
                resp.body = self.database.delete_all(table)
        else:
            resp.body = jwt_result

    def on_put(self, req, resp, table=None, doc_id=None):
        [status, jwt_result, username] = self.authentication_manager.verify_jwt(req.headers)
        if status is True:
            table = self.generate_table_name(table, username)
            # Return note for particular ID
            if doc_id:
                try:
                    raw_json = req.stream.read().decode('utf-8')
                    parsed_json = json.loads(raw_json)
                    resp.body = self.database.update(table, doc_id, parsed_json)
                except ValueError:
                    raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. '
                                                                            'The ''JSON was incorrect.')
            else:
                resp.body = json.dumps({"Success": "Fail", "message": "No document found with supplied ID"})
        else:
            resp.body = jwt_result

    def generate_table_name(self, table, username):
        if username != "":
            return table + "_" + username
        else:
            return table

    def __save_documents__(self, table, docs):
        doc_save_result = []
        for i in range(len(docs)):
            sid = self.database.save(docs[i], table)
            doc_save_result.append(
                {"message": "Successfully inserted.", "id": sid, "doc": docs[i]})
        return doc_save_result
