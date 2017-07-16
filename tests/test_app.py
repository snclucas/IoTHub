import json

from tests.stashy_test_case import StashyTestCase


class TestStashyAuthorization(StashyTestCase):
    def test_get_no_token(self):
        headers = {"Content-Type": "application/json"}
        result = self.simulate_request(method='GET', path='/d/test/docs', headers=headers, protocol='http')
        self.assertEqual(result.json, {'status': 'fail', 'message': 'No authentication token supplied'})

    def test_get_invalid_token(self):
        headers = {"Content-Type": "application/json", "Authorization": "Bearer 0d24a"}
        result = self.simulate_request(method='GET', path='/d/test/docs', headers=headers, protocol='http')
        self.assertEqual(result.json, {"status": "fail", "message": "No user with that token"})

    def test_get_valid_token_no_doc(self):
        result = self.get_document_with_good_header(doc_id="99")
        self.assertEqual(result.json, {'message': 'Document not found', 'status': 'Fail'})

    def test_post_get_delete_valid_token(self):
        newdoc_id = self.test_save_document()

        result = self.get_document_with_good_header(newdoc_id)

        json_data_get = result.json

        json_data_get.pop('id', None)
        self.assertEqual(self.ordered(json_data_get), self.ordered(self.test_doc))

        result = self.simulate_request(method='DELETE', path='/d/test/docs/' + newdoc_id,
                                       headers=self.header_with_user1_token, protocol='http')

        self.assertEqual(result.json, {'status': 'success', 'id': newdoc_id})

        result = self.get_document_with_good_header(newdoc_id)

        json_data_get = result.json
        self.assertEqual(json_data_get, {'message': 'Document not found', 'status': 'Fail'})

    def test_delete_not_valid_token(self):
        newdoc_id = self.test_save_document()

        result = self.get_document_with_good_header(newdoc_id)

        json_data_get = result.json

        json_data_get.pop('id', None)
        self.assertEqual(self.ordered(json_data_get), self.ordered(self.test_doc))

        result = self.simulate_request(method='DELETE', path='/d/test/docs/' + newdoc_id,
                                       headers=self.header_with_bad_token, protocol='http')

        self.assertEqual(result.json, {'message': 'No user with that token', 'status': 'fail'})

    def test_save_document(self):
        result = self.simulate_request(method='POST', path='/d/test/docs',
                                       headers=self.header_with_user1_token, protocol='http',
                                       body=json.dumps(self.test_doc))

        json_data = result.json

        self.assertIn('id', json_data)

        newdoc_id = json_data['id']

        json_data.pop('id', None)
        self.assertEqual(self.ordered(json_data), self.ordered(self.test_doc))

        return newdoc_id

    def test_save_document_with_explode(self):
        params = {"st::explode": "docs"}
        result = self.simulate_request(method='POST', path='/d/test/docs',
                                       headers=self.header_with_user1_token, protocol='http', params=params,
                                       body=json.dumps(self.test_doc_explode))

        if isinstance(result.json, list):
            json_data = result.json
        else:
            self.fail("Failed to save doc [" + json.dumps(result.json) + "]")

        for doc in json_data:
            self.assertIn('id', doc)

        self.assertEqual(len(json_data), 2)

    def test_delete_with_filter(self):
        self.test_save_document_with_explode()

        result_get = self.get_documents_with_good_header()
        # Should be 2 documents
        self.assertEqual(len(result_get.json), 2)

        filter_by = {"spam": "1"}
        result_post = self.simulate_request(method='DELETE', path='/d/test/docs',
                                            headers=self.header_with_user1_token, protocol='http', params=filter_by)

        self.assertEqual(result_post.json, {'status': 'success', 'deleted_count': 1})

        result_get = self.get_documents_with_good_header()
        # Now should be 1 document
        self.assertEqual(len(result_get.json), 1)

    def get_document_with_good_header(self, doc_id):
        return self.simulate_request(method='GET', path='/d/test/docs/' + doc_id,
                                     headers=self.header_with_user1_token, protocol='http')

    def get_documents_with_good_header(self):
        return self.simulate_request(method='GET', path='/d/test/docs',
                                     headers=self.header_with_user1_token, protocol='http')
