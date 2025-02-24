import pytest
import redis
import fakeredis
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

@pytest.fixture
def mock_redis_client(monkeypatch):
    """Fixture that replaces redis.StrictRedis with fakeredis.FakeStrictRedis."""
    fake_redis = fakeredis.FakeStrictRedis()
    monkeypatch.setattr(redis, "StrictRedis", lambda *args, **kwargs: fake_redis)
    return fake_redis

def create_cluster(client, username):
    user_data = {"username": username, "password": "testpassword"}
    response = client.post("/users/register", json=user_data)
    assert response.status_code == 200

    login_data = {"username": username, "password": "testpassword"}
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 200

    token = response.json().get("access_token")

    create_data = {
        "name": username,
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
    return response, token

def test_create_deployment(client, db, mock_redis_client):
    response, token = create_cluster(client, "createDeploymentUser")
    cluster_id = response.json()['id']
    create_data = {
        "name": "TestDeployment 1",
        "cluster_id": cluster_id,
        "image_path": "test_path/test",
        "ram_required": 35,
        "cpu_required": 35,
        "gpu_required": 35,
        "priority": 1
    }
    response = client.post(
        "/deployments/create/",
        headers={"Authorization": f"Bearer {token}"},
        json=create_data
    )
    assert response.status_code == 200
    result = response.json()
    del result['id']
    assert result == {'name': 'TestDeployment 1', 'cluster_id': cluster_id, 'image_path': "test_path/test",
                      'ram_required': 35, 'cpu_required': 35.0, 'gpu_required': 35, 'status': 'Running', 'priority': 1}

def test_get_deployment(client, db):
    response, token = create_cluster(client, 'getDeployment')
    cluster_id = response.json()['id']
    create_data = {
        "name": "getDeployment",
        "image_path": "test_path/test",
        "ram_required": 35,
        "cpu_required": 35,
        "gpu_required": 35,
        "priority": 1
    }
    response = client.post(
        "/deployments/create/",
        headers={"Authorization": f"Bearer {token}"},
        json=create_data
    )
    assert response.status_code == 422
