import os
import random
from flask import Flask, current_app
import pytest
from app import create_app
from app.models import db
from app.config import TestConfig
from app.models import Bean, Roaster, User

ADMIN_USERNAME = "s_admin"
ADMIN_PASSWORD = "12345678"
TEST_DB = TestConfig.TEST_DB

@pytest.fixture(scope='session')
def app():
    app = create_app(config_obj=TestConfig)
    db_manager = app.db_manager

    with app.app_context():
        db.metadata.create_all(bind=db_manager.write_engine)

    yield app

    # Clean up
    with app.app_context():
        db.metadata.drop_all(bind=db_manager.write_engine)
        db.session.remove()
        db_manager.write_engine.dispose()
        if os.path.exists(TestConfig.TEST_DB):
            os.remove(TestConfig.TEST_DB)

@pytest.fixture(scope='session')
def client(app: Flask):
    with app.app_context():
        with app.test_client() as client:
            yield client

def register_user(client, app, username, password):
    response = client.post('/register', json={"username": username, "password": password})

    # If the user 's_admin' is created successfully, set the role to 'admin'
    with current_app.db_manager.get_write_session() as session:
        user = session.query(User).filter_by(username=ADMIN_USERNAME).first()
        user.role = "admin"
    return response

def login(client, username, password):
    return client.post('/login', json={"username": username, "password": password})

def get_admin_token(client, app):
    register_user(client, app, ADMIN_USERNAME, ADMIN_PASSWORD)
    response = login(client, ADMIN_USERNAME, ADMIN_PASSWORD)
    return response.get_json().get("access_token")

def get_regular_user_token(client, app):
    register_user(client, app, "simple_user", "12345678")
    response = login(client, "simple_user", "12345678")
    return response.get_json().get("access_token")

class AuthenticatedUser:
    def __init__(self, client, token):
        self.client = client
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }
    
    def get(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        merged_headers = {**headers, **self.headers}
        return self.client.get(path, headers=merged_headers, **kwargs)
    
    def post(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        merged_headers = {**headers, **self.headers}
        return self.client.post(path, headers=merged_headers, **kwargs)

    def patch(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        merged_headers = {**headers, **self.headers}
        return self.client.patch(path, headers=merged_headers, **kwargs)

    def delete(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        merged_headers = {**headers, **self.headers}
        return self.client.delete(path, headers=merged_headers, **kwargs)

    def put(self, path, **kwargs):
        headers = kwargs.pop("headers", {})
        merged_headers = {**headers, **self.headers}
        return self.client.put(path, headers=merged_headers, **kwargs)
    
@pytest.fixture(scope="session")
def auth_admin(client, app):
    return AuthenticatedUser(client=client, token=get_admin_token(client, app))

@pytest.fixture(scope="session")
def existing_roaster(app) -> dict:
    roaster = Roaster(
        name="Test Roaster",
        address=f"{random.randint(100, 999)} Existing Rd, Existing City, EC 67890",
        website=f"https://existingroaster{random.randint(100, 999)}.com"
    )
    with app.db_manager.get_write_session() as session:
        # Convert to dict before session closes to avoid DetachedInstanceError
        session.add(roaster)
        # Flush to get the 'id', 
        # Convert to dict before session closes to avoid DetachedInstanceError
        session.flush()
        roaster_dict = roaster.to_dict()
    return roaster_dict

@pytest.fixture(scope="session")
def existing_bean(app, existing_roaster) -> dict:
    bean = Bean(
        name="Test Bean",
        roast_level="Medium",
        origin="Colombia",
        price_per_100_grams=4.5,
        roaster_id=existing_roaster["id"]
    )
    with app.db_manager.get_write_session() as session:
        session.add(bean)
        # Flush to get the 'id', 
        # Convert to dict before session closes to avoid DetachedInstanceError
        session.flush()
        bean_dict = bean.to_dict()
    return bean_dict

def test_basic(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Welcome to the Home Brew Coffee Review API!'}

def test_register_and_login(client, app):
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    register_response = register_user(client, app, payload["username"], payload["password"])
    assert register_response.status_code == 201
    assert register_response.get_json() == {"message": f"User {ADMIN_USERNAME} was created successfully"}

    login_response = login(client, ADMIN_USERNAME, ADMIN_PASSWORD)

    # Check if login was successful
    assert login_response.status_code == 200
    assert 'Login successful' in login_response.get_json().values()
    assert 'access_token' in login_response.get_json().keys()

def test_login_wrong_password(client, app):
    payload = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    register_user(client, app, payload["username"], payload["password"])

    # Attempt to login with wrong password
    payload = {
        "username": ADMIN_USERNAME,
        "password": "123",
    }
    response = client.post('/login', json=payload)
    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid Credentials"}

def test_add_roaster(auth_admin):
    payload = {
        "name": "Test Roaster 2",
        "address": "Address of Test Roaster 2", 
        "website": "https://testroaster2.com"
    }

    response = auth_admin.post('/roasters', json=payload)
    assert response.status_code == 201
    assert response.get_json() == {"message": "New roaster Test Roaster 2 was created successfully"}

def test_add_bean(auth_admin, existing_roaster):
    payload = {
        "name": "Test Bean",
        "roast_level": "Medium",
        "origin": "Ethiopia",
        "price_per_100_grams": 12.99,
        "roaster_id": existing_roaster["id"]  # Use the existing roaster's ID
    }
    response = auth_admin.post('/beans', json=payload)
    assert response.status_code == 201
    assert response.get_json() == {"message": "New bean Test Bean was created successfully"}

def test_add_review(auth_admin, existing_bean):
    review_payload = {
        "content": "Great beans!",
        "rating": 4.5,
        "brew_method": "Cold Brew"
    }
    response = auth_admin.post(f'/beans/{existing_bean["id"]}/reviews', json=review_payload)
    assert response.status_code == 201
    assert response.get_json() == {"message": f"Review was added"}

    response = auth_admin.post(f'/beans/{existing_bean["id"]}/reviews', json=review_payload)
    assert response.status_code == 409
    assert response.get_json() == {"error": f"User already reviewed this bean"}

def test_get_reviews_for_existing_bean(auth_admin, existing_bean):
    response = auth_admin.get(f'beans/{existing_bean["id"]}/reviews')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert "reviews" in data
    assert isinstance(data["reviews"], list) and len(data["reviews"]) > 0

def test_get_reviews_for_nonexistent_bean(auth_admin):
    response = auth_admin.get(f'beans/123456789/reviews')
    assert response.status_code == 404