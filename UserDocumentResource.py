import json
import falcon
from datetime import *

import config
from util.JSONEncoder import JSONEncoder
from AuthenticationManager import AuthenticationManager


class UserDocumentResource:

    def __init__(self, database, user_manager):
        self.database = database
        self.user_manager = user_manager
        self.authentication_manager = AuthenticationManager(user_manager)

    def validate_json_content(req, resp, resource, params):
        if req.content_type is None or req.content_type not in "application/json":
            msg = 'Body of request should be application/json'
            raise falcon.HTTPBadRequest('Bad request', msg)

    @falcon.before(validate_json_content)
    def on_get(self, req, resp, endpoint_type, table=None, doc_id=None):
        [valid_end_point, end_point_type] = self.__check_endpoint__(endpoint_type)

        if valid_end_point is False:
            raise falcon.HTTPBadRequest('Bad request', "404")

        [valid_token, token_result, user] = self.authentication_manager.verify_token(req.headers)

        if valid_token is False or user is None:
            resp.body = token_result
            return

        table = self.__generate_table_name__(table, user['local']['displayName'], end_point_type)
        if doc_id:
            resp.body = self.database.get_one_by_id(table, doc_id)
        else:
            [filter_by, sort_by] = self.__construct_filter_from_query_params__(req.query_string)
            resp.body = self.database.get_all(table, filter_by=filter_by, select_by=None, sort=sort_by)

    @falcon.before(validate_json_content)
    def on_post(self, req, resp, endpoint_type, table=None):
        [valid_end_point, end_point_type] = self.__check_endpoint__(endpoint_type)
        if valid_end_point is False:
            raise falcon.HTTPBadRequest('Bad request', "404")

        [valid_token, token_result, user] = self.authentication_manager.verify_token(req.headers)

        if user is None or valid_token is False:
            resp.body = token_result
            return

        if end_point_type == 'public':
            self.__check_user_can_post_to_endpoint(user, table)

        metadata = self.__construct_metadata_from_query_params__(req.query_string)

        if 'addDatestampToPosts' in user:
            add_datestamp = user['addDatestampToPosts']
        else:
            add_datestamp = False
        table = self.__generate_table_name__(table, user['local']['displayName'], end_point_type)

        # If table does not exist, create it
        self.database.add_table(table)
        try:

            raw_json = req.stream.read().decode('utf-8')
            print(raw_json)
            parsed_json = json.loads(raw_json)

            if 'explode' in metadata:
                if metadata['explode'] in parsed_json:
                    parsed_json = parsed_json[metadata['explode']]
                    doc_save_result = self.__save_documents__(table, parsed_json, add_datestamp)
                else:
                    resp.body = json.dumps({"status": "fail", "message":
                                            "Could not find attribute '"+metadata['explode']+"' to explode"})
                    return
            else:
                doc_save_result = self.__save_documents__(table, [parsed_json], add_datestamp)

            resp.body = json.dumps(doc_save_result, cls=JSONEncoder).replace('_id', 'id')
        except ValueError:
            resp.body = json.dumps({"status": "fail", "message": "Bad JSON"})
            return

    def on_delete(self, req, resp, endpoint_type, table=None, doc_id=None):
        [valid_end_point, end_point_type] = self.__check_endpoint__(endpoint_type)
        if valid_end_point is False:
            raise falcon.HTTPBadRequest('Bad request', "404")

        [status, jwt_result, username] = self.authentication_manager.verify_token(req.headers)
        if status is True:
            table = self.__generate_table_name__(table, username, end_point_type)
            if doc_id:
                resp.body = self.database.delete_one(table, doc_id)
            else:
                resp.body = self.database.delete_all(table)
        else:
            resp.body = jwt_result

    @falcon.before(validate_json_content)
    def on_put(self, req, resp, endpoint_type, table=None, doc_id=None):
        [valid_end_point, end_point_type] = self.__check_endpoint__(endpoint_type)
        if valid_end_point is False:
            raise falcon.HTTPBadRequest('Bad request', "404")

        [status, token_result, username] = self.authentication_manager.verify_token(req.headers)
        if status is True:
            table = self.__generate_table_name__(table, username, end_point_type)
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
                resp.body = json.dumps({"success": "fail", "message": "No document found with supplied ID"})
        else:
            resp.body = token_result

    def __generate_table_name__(self, table, username, end_point_type):
        """Append the name of the user to the table name."""
        # If private endpoint
        if end_point_type == 'private':
            if username != "":
                return table + "_" + username
            else:
                return table
        else:
            return table

    def __save_documents__(self, table, docs, add_datestamp):
        doc_save_result = []
        for i in range(len(docs)):
            if add_datestamp:
                docs[i]['created'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            self.database.save(docs[i], table)
            doc_save_result.append(docs[i])
        return doc_save_result

    def __construct_filter_from_query_params__(self, query_params):
        filter_val = {}
        sort_by = [('_id', 1)]
        q_params = falcon.uri.parse_query_string(query_params, keep_blank_qs_values=False, parse_qs_csv=True)
        sortby_val = '_id'
        order_val = 1
        sortby = False
        if 'sortby' in q_params:
            sortby = True
            sortby_val = q_params['sortby']
        if 'order' in q_params:
            order_val = q_params['order']
            if order_val.lower() == 'asc' or order_val == 1:
                order_val = 1
            elif order_val.lower() == 'desc' or order_val == -1:
                order_val = -1

        if sortby is True:
            sort_by = [(sortby_val, int(order_val))]

        # Get user supplied filters
        for key, value in q_params.items():
            if not self.__reserved__word__(key):
                filter_val[key] = value

        return [filter_val, sort_by]

    def __construct_metadata_from_query_params__(self, query_params):
        metadata = {}
        q_params = falcon.uri.parse_query_string(query_params, keep_blank_qs_values=False, parse_qs_csv=True)

        for key, value in q_params.items():
            if key[:len(config.metadata_key)] == config.metadata_key:
                metadata[key[len(config.metadata_key):]] = value

        return metadata

    def __reserved__word__(self, word):
        return word in config.reserved_words

    def __check_endpoint__(self, end_point):
        if end_point == 'd':
            return [True, 'private']
        elif end_point == 'p':
            return [True, 'public']
        else:
            return [False, '']

    def __check_user_can_post_to_endpoint(self, user, table):
        allowed_to_post_to_endpoint = False
        for public_endpoint in user['publicEndpoints']:
            if public_endpoint['endpoint'] == table:
                allowed_to_post_to_endpoint = True

        if allowed_to_post_to_endpoint is False:
            raise falcon.HTTPBadRequest('Bad request', "Cannot post to this endpoint")
