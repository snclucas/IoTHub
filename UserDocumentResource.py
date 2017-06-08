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

        if 'AUTHENTICATION' in req.headers:
            token = req.headers['AUTHENTICATION'].split("Bearer")[1].replace(" ", "")

            jwt_result = ""
            try:
                jwt_result = jwt.decode(token, 'tree', algorithm=['HS256'])
            except jwt.ExpiredSignatureError:
                resp.body = '{"Token expired"}'
            except jwt.InvalidTokenError:
                resp.body = '{"Invalid token"}'
            print(self.check_jwt(req.headers))
        else:
            resp.body = '{"No authentication token supplied"}'

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

    def check_jwt(self, headers):
        if 'AUTHENTICATION' in headers:
            token = headers['AUTHENTICATION'].split("Bearer")[1].replace(" ", "")

            try:
                jwt_result = jwt.decode(token, 'tree', algorithm=['HS256'])
                res = '{"status": "OK"}'
                res['jwt'] = json.dumps(jwt_result)
                return res
            except jwt.ExpiredSignatureError:
                return '{"status": "Fail", "message": "Token expired"}'
            except jwt.InvalidTokenError:
                return '{"status": "Fail", "message": "Invalid token"}'
        else:
            return '{"status": "Fail", "message": "No authentication token supplied"}'
