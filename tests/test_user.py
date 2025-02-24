import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base, engine, SessionLocal
from app.db import db_schema


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    yield db_session
    db_session.close()


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client
    Base.metadata.drop_all(bind=engine)


def test_user_register(client, db):
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/users/register", json=user_data)

    assert response.status_code == 200
    assert response.json() == {'id': 1, 'organization_id': None, 'username': 'testuser'}

    user = db.query(db_schema.User).filter(db_schema.User.username == "testuser").first()
    assert user is not None


# Test for user login
def test_user_login(client, db):

    user_data = {"username": "testuser", "password": "testpassword"}
    client.post("/users/register/", json=user_data)

    login_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/users/login/", json=login_data)

    assert response.status_code == 200
    assert "access_token" in response.json()

    assert response.json()["token_type"] == "bearer"


def test_user_login_wrong_password(client, db):
    user_data = {"username": "testuser", "password": "testpassword"}
    client.post("/users/register/", json=user_data)

    login_data = {"username": "testuser", "password": "wrongpassword"}
    response = client.post("/users/login/", json=login_data)

    assert response.status_code == 401
    assert response.json() == {'detail': 'Invalid credentials'}


def test_user_register_existing_username(client, db):
    user_data = {"username": "testuser", "password": "testpassword"}
    client.post("/users/register/", json=user_data)

    response = client.post("/users/register/", json=user_data)

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already exists"}
