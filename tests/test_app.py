from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers
from app.main import app, get_db
from app.models import Base
import pytest

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    Base.metadata.create_all(bind=engine)
    yield 
    Base.metadata.drop_all(bind=engine)
    clear_mappers()

client = TestClient(app)

def test_signup():
    response = client.post(
        "/signup",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com" 
    assert "id" in response.json()

def test_login():
    response = client.post(
        "/token",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_add_post():
    login_response = client.post(
        "/token",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/addPost",
        json={"title":"Hello","content": "Hello, world!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Hello, world!"
    assert response.json()["title"] == "Hello"

def test_get_posts():
    login_response = client.post(
        "/token",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    response = client.get(
        "/getPosts",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_post():
    login_response = client.post(
        "/token",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = login_response.json()["access_token"]
    add_response = client.post(
        "/addPost",
        json={"title":"Hello2","content": "Hello, world!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    post_id = add_response.json()["id"]
    delete_response = client.post(
        f"/deletePost?id={post_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_response.status_code == 200
