import falcon

import UserManager
import ServerInfo as serverInfo
from db import DatabaseManager

import UserDocumentResource as userDoc
import NoEndpointResource as noDoc

from RateLimiter import RateLimiter

# api = falcon.API(middleware=[RateLimiter(limit=2)])
api = falcon.API()

database_manager = DatabaseManager.DatabaseManager()
database = database_manager.get_db()
user_manager = UserManager.UserManager(database)

api.add_route('/', serverInfo.ServerInfoHTML())
api.add_route('/server-info', serverInfo.ServerInfo())

api.add_route('/{endpoint_type}/{table}/docs/delete', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/{endpoint_type}/{table}/docs/delete/{doc_id}', userDoc.UserDocumentResource(database, user_manager))

api.add_route('/{endpoint_type}/{table}/docs', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/{endpoint_type}/{table}/docs/{doc_id}', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/{endpoint_type}/{table}/docs/count', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/{endpoint_type}/{table}/docs/delete_all', userDoc.UserDocumentResource(database, user_manager))

api.add_route('/{endpoint_type}/{table}/{catch}', noDoc.NoEndpointResource())
api.add_route('/{endpoint_type}/{table}', noDoc.NoEndpointResource())
api.add_route('/{endpoint_type}', noDoc.NoEndpointResource())
api.add_route('/', noDoc.NoEndpointResource())
