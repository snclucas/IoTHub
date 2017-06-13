import falcon
from falcon import testing
import pytest

from app import api


@pytest.fixture
def client():
    return testing.TestClient(api)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_list_images(client_in):
    doc = {
        'images': [
            {
                'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
            }
        ]
    }

    response = client_in.simulate_get('/test/docs')
    # result_doc = msgpack.unpackb(response.content, encoding='utf-8')
    print(response.content)
    result_doc = response.content

    assert result_doc == doc
    assert response.status == falcon.HTTP_OK
