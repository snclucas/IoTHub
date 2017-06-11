import falcon

import config
from db import DatabaseManager

import UserDocumentResource as userDoc

api = falcon.API()

config = config.read_config()
dbm = DatabaseManager.DatabaseManager(config)

api.add_route('/d/{table}/docs', userDoc.UserDocumentResource(dbm))
api.add_route('/d/{table}/docs/{doc_id}', userDoc.UserDocumentResource(dbm))
api.add_route('/d/{table}/docs/count', userDoc.UserDocumentResource(dbm))
api.add_route('/d/{table}/docs/delete_all', userDoc.UserDocumentResource(dbm))
