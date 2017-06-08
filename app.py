import falcon

import UserDocumentResource as udr

api = falcon.API()
api.add_route('/d/{table}/docs', udr.UserDocumentResource())
api.add_route('/d/{table}/docs/{doc_id}', udr.UserDocumentResource())
api.add_route('/d/{table}/docs/delete_all', udr.UserDocumentResource())
