import falcon
import json
import jwt

import RethinkDBDatabaseManager


class UserDocumentResource:

    def __init__(self):
        self.database_manager = RethinkDBDatabaseManager.RethinkDBDatabaseManager()

    def on_get(self, req, resp, table=None, doc_id=None):
        [status, jwt_result] = self.check_jwt(req.headers)
        if status is True:
            # Return note for particular ID
            if doc_id:
                resp.body = self.database_manager.get_one(table, doc_id)
            else:
                resp.body = self.database_manager.get_all(table)
        else:
            resp.body = jwt_result



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
            resp.body = '{"message": "Successfully inserted.", "id": "'+sid+'"}'
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400, 'Invalid JSON', 'Could not decode the request body. The ''JSON was incorrect.')

    def check_jwt(self, headers):
        if 'AUTHENTICATION' in headers:
            token = headers['AUTHENTICATION'].split("Bearer")[1].replace(" ", "")

            try:
                jwt_result = jwt.decode(token, 'secret', algorithm=['HS256'])
                res = json.loads('{"status": "OK"}')
                res['jwt'] = json.dumps(jwt_result)
                return [True, res]
            except jwt.InvalidTokenError:
                return [False, '{"status": "Fail", "message": "Invalid token"}']
        else:
            return [False, '{"status": "Fail", "message": "No authentication token supplied"}']
