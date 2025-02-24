import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base, engine, SessionLocal

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

def create_user(client, username):
    user_data = {"username": username, "password": "testpassword"}
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200

    login_data = {"username": username, "password": "testpassword"}
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 200

    return response.json().get("access_token")

def test_create_organization_valid_token(client, db):
    token = create_user(client, "org1user")

    create_data = {"name": "Test Organization 1"}
    response = client.post(
        "/organizations/create/",
        headers={"Authorization": f"Bearer {token}"},
        json=create_data
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Test Organization 1"
    assert "invite_code" in response.json()

# Test for user login
def test_join_valid_invite_code(client, db):
    token = create_user(client, "org2user")

    create_data = {"name": "Test Organization 2"}
    response = client.post(
        "/organizations/create/",
        headers={"Authorization": f"Bearer {token}"},
        json=create_data
    )

    assert response.status_code == 200
    response = client.post(
        "/organizations/join/",
        headers={"Authorization": f"Bearer {token}"},
        params={"invite_code": response.json()["invite_code"]}
    )
    assert response.status_code == 200
    assert response.json() == {'message': 'User org2user joined organization Test Organization 2'}
