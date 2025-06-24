import os
import pytest
from app import create_app, db, Config

TEST_DB = os.path.abspath('test_temp.db')

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DB}'
from app import create_app, db, Config

TEST_DB = os.path.abspath('test_temp.db')

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DB}'

@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
    yield app

    # Clean up
    with app.app_context():
        db.drop_all()
        db.session.remove()
        db.engine.dispose()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

@pytest.fixture(scope='function')
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client
@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
    yield app

    # Clean up
    with app.app_context():
        db.drop_all()
        db.session.remove()
        db.engine.dispose()
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

@pytest.fixture(scope='function')
def client(app):
    with app.app_context():
        with app.test_client() as client:
            yield client

def test_basic(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Welcome to the Home Brew Coffee Review API!'}

def test_register_and_login(client):
    payload = {
        "username": "s_admin",
        "password": "12345678"
    }
    response = client.post('/register', json=payload)
    assert response.status_code == 201
    assert response.get_json() == {"message": f"User s_admin was created successfully"}


def test_register_and_login(client):
    payload = {
        "username": "s_admin",
        "password": "12345678"
    }
    response = client.post('/register', json=payload)
    assert response.status_code == 201
    assert response.get_json() == {"message": f"User s_admin was created successfully"}


    payload = {
        "username": "s_admin",
        "password": "12345678"
    }
    response = client.post('/login', json=payload)
    set_cookie = response.headers.get('Set-Cookie')
    assert set_cookie is not None
    assert 'access_token=' in set_cookie
    assert response.get_json() == {'message': 'Login successful'}


def test_login_wrong_password(client):
    payload = {
        "username": "s_admin",
        "password": "1234567",
    }
    response = client.post('/login', json=payload)
    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid Credentials"}

def test_add_roaster(client):
    pass

def test_add_bean(client):
    pass

def test_add_review(client):
    pass

# def test_new_review_after_login(client):
    # payload = {
    #     "username": "s_admin",
    #     "password": "12345678"
    # }
    # response = client.post('/login', json=payload)
    # set_cookie = response.headers.get('Set-Cookie')
    # assert set_cookie is not None
    # assert 'access_token=' in set_cookie
    # assert response.get_json() == {'message': 'Login successful'}

    # print('Login successfull')
    # review_payload = {
    #     "content": "Very nice beans!",
    #     "rating": 4.6
    # }
    
    # response = client.post('/view_bean/1/add_review', json=review_payload)
    # assert response.status_code == 201
# 
# def test_login_wrong_creds(client):
#     payload = {
#         "username": "snir",
#         "password": "supersecret"
#     }
#     response = client.post('/login', json=payload)
#     print(response)
#     assert response.status_code == 401
#     assert response.get_json() == {"error": "Invalid Credentials"}

# def test_new_review_after_login(client):
    # payload = {
    #     "username": "s_admin",
    #     "password": "12345678"
    # }
    # response = client.post('/login', json=payload)
    # set_cookie = response.headers.get('Set-Cookie')
    # assert set_cookie is not None
    # assert 'access_token=' in set_cookie
    # assert response.get_json() == {'message': 'Login successful'}

    # print('Login successfull')
    # review_payload = {
    #     "content": "Very nice beans!",
    #     "rating": 4.6
    # }
    
    # response = client.post('/view_bean/1/add_review', json=review_payload)
    # assert response.status_code == 201
# 
# def test_login_wrong_creds(client):
#     payload = {
#         "username": "snir",
#         "password": "supersecret"
#     }
#     response = client.post('/login', json=payload)
#     print(response)
#     assert response.status_code == 401
#     assert response.get_json() == {'error': 'Invalid Credentials'}