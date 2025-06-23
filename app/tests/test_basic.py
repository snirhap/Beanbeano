import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_basic(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Welcome to the Home Brew Coffee Review API!'}


def test_login(client):
    payload = {
        "username": "s_admin",
        "password": "12345678"
    }
    response = client.post('/login', json=payload)
    set_cookie = response.headers.get('Set-Cookie')
    assert set_cookie is not None
    assert 'access_token=' in set_cookie
    assert response.get_json() == {'message': 'Login successful'}

def test_login_wrong_creds(client):
    payload = {
        "username": "snir",
        "password": "supersecret"
    }
    response = client.post('/login', json=payload)
    print(response)
    assert response.status_code == 401
    assert response.get_json() == {'error': 'Invalid Credentials'}