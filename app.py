import falcon

import config
import UserManager
from db import DatabaseManager

import UserDocumentResource as userDoc

api = falcon.API()

config = config.read_config()
database_manager = DatabaseManager.DatabaseManager(config)
database = database_manager.get_db()
user_manager = UserManager.UserManager(database)

api.add_route('/d/{table}/docs', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/d/{table}/docs/{doc_id}', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/d/{table}/docs/count', userDoc.UserDocumentResource(database, user_manager))
api.add_route('/d/{table}/docs/delete_all', userDoc.UserDocumentResource(database, user_manager))
