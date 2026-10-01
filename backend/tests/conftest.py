import os

# Configure the app before it is imported. Set TEST_DATABASE_URL to run against
# another database, e.g. oracle+oracledb://user:pass@localhost:1521/?service_name=FREEPDB1
os.environ["DATABASE_URL"] = os.environ.get("TEST_DATABASE_URL", "sqlite://")
os.environ["AI_PROVIDER"] = "mock"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough-for-hs256"
os.environ["FRONTEND_DIST"] = "/nonexistent"
os.environ["BCRYPT_ROUNDS"] = "4"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, update

from app import models
from app.database import Base, SessionLocal, engine
from app.deps import ai_rate_limiter
from app.main import app
from app.services import ai as ai_service

PASSWORD = "password123"


@pytest.fixture(scope="session", autouse=True)
def _schema():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def _clean_tables():
    yield
    with engine.begin() as conn:
        conn.execute(update(models.Question).values(accepted_answer_id=None))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(delete(table))
    ai_rate_limiter.reset()
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    with SessionLocal() as session:
        yield session


@pytest.fixture
def make_user(client, db):
    def _make(username: str = "alice", role: str = "user", password: str = PASSWORD):
        response = client.post(
            "/api/auth/register",
            json={"username": username, "email": f"{username}@example.com", "password": password},
        )
        assert response.status_code == 201, response.text
        user_id = response.json()["id"]
        db.execute(update(models.User).where(models.User.id == user_id).values(role=role))
        db.commit()
        token = client.post("/api/auth/login", json={"username": username, "password": password}).json()["access_token"]
        return {"id": user_id, "username": username, "headers": {"Authorization": f"Bearer {token}"}}

    return _make


@pytest.fixture
def alice(make_user):
    return make_user("alice")


@pytest.fixture
def bob(make_user):
    return make_user("bob")


@pytest.fixture
def make_question(client):
    def _make(
        user,
        title="How do I parse JSON in Python?",
        body="I have a JSON string and need a dict from it.",
        tags=("python", "json"),
    ):
        response = client.post(
            "/api/questions", json={"title": title, "body": body, "tags": list(tags)}, headers=user["headers"]
        )
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def make_answer(client):
    def _make(user, question_id, body="Use json.loads(text) from the standard library."):
        response = client.post(f"/api/questions/{question_id}/answers", json={"body": body}, headers=user["headers"])
        assert response.status_code == 201, response.text
        return response.json()

    return _make


@pytest.fixture
def mock_ai():
    provider = ai_service.MockProvider()
    app.dependency_overrides[ai_service.get_ai_provider] = lambda: provider
    return provider
