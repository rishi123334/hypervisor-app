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


def test_create_cluster(client, db):
    token = create_user(client, "clusterCreate")

    create_data = {
      "name": "clusterCreate",
      "total_ram": 140,
      "total_cpu": 140,
      "total_gpu": 140
    }
    response = client.post(
        "/clusters/create/",
        headers={"Authorization": f"Bearer {token}"},
        json=create_data
    )

    assert response.status_code == 200
    result = response.json()
    del result['id']
    assert result == {'name': 'clusterCreate', 'total_ram': 140, 'total_cpu': 140.0, 'total_gpu': 140,
                               'available_ram': 140, 'available_cpu': 140.0, 'available_gpu': 140}

# Test for user login
def test_get_cluster(client, db):
    token = create_user(client, "GetCluster")

    create_data = {
        "name": "GetCluster",
        "total_ram": 140,
        "total_cpu": 140,
        "total_gpu": 140
    }
    response = client.post(
        "/clusters/create/",
        headers={"Authorization": f"Bearer {token}"},
        json=create_data
    )

    assert response.status_code == 200
    response = client.get(
        "/clusters/get_cluster/",
        headers={"Authorization": f"Bearer {token}"},
        params={"cluster_name": "GetCluster"}
    )

    assert response.status_code == 200
    result = response.json()
    del result['id']
    assert result == {'name': 'GetCluster', 'total_ram': 140, 'total_cpu': 140.0, 'total_gpu': 140,
                               'available_ram': 140, 'available_cpu': 140.0, 'available_gpu': 140}
