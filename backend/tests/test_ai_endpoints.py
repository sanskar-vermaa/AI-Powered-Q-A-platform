from app.deps import ai_rate_limiter
from app.main import app
from app.services import ai as ai_service
from app.services.ai import AIError


class FailingProvider(ai_service.MockProvider):
    name = "failing"

    def answer_question(self, *args):
        raise AIError("upstream unavailable")

    def suggest_tags(self, *args):
        raise AIError("upstream unavailable")


def test_status(client, mock_ai):
    assert client.get("/api/ai/status").json() == {"provider": "mock", "live": False}


def test_generate_ai_answer(client, alice, bob, make_question, mock_ai):
    question = make_question(alice)
    response = client.post(f"/api/ai/questions/{question['id']}/answer", headers=bob["headers"])
    assert response.status_code == 201
    body = response.json()
    assert body["is_ai"] is True and body["author"] is None
    assert question["title"] in body["body"]
    notes = client.get("/api/notifications", headers=alice["headers"]).json()
    assert any(n["kind"] == "ai_answer" for n in notes)


def test_only_one_ai_answer_per_question(client, alice, make_question, mock_ai):
    question = make_question(alice)
    client.post(f"/api/ai/questions/{question['id']}/answer", headers=alice["headers"])
    assert client.post(f"/api/ai/questions/{question['id']}/answer", headers=alice["headers"]).status_code == 409


def test_ai_answer_requires_auth_and_question(client, alice, mock_ai):
    assert client.post("/api/ai/questions/1/answer").status_code == 401
    assert client.post("/api/ai/questions/999/answer", headers=alice["headers"]).status_code == 404


def test_ai_answer_permissions(client, alice, bob, make_user, make_question, mock_ai):
    moderator = make_user("mod", role="moderator")
    question = make_question(alice)
    answer = client.post(f"/api/ai/questions/{question['id']}/answer", headers=alice["headers"]).json()
    edit = {"body": "Corrected AI answer with enough length."}
    assert client.patch(f"/api/answers/{answer['id']}", json=edit, headers=alice["headers"]).status_code == 403
    assert client.patch(f"/api/answers/{answer['id']}", json=edit, headers=moderator["headers"]).status_code == 200
    assert client.delete(f"/api/answers/{answer['id']}", headers=bob["headers"]).status_code == 403
    # The asker may remove an AI answer from their own question.
    assert client.delete(f"/api/answers/{answer['id']}", headers=alice["headers"]).status_code == 204


def test_accepting_ai_answer(client, alice, make_question, mock_ai):
    question = make_question(alice)
    answer = client.post(f"/api/ai/questions/{question['id']}/answer", headers=alice["headers"]).json()
    response = client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert response.json()["accepted_answer_id"] == answer["id"]


def test_suggest_tags(client, alice, mock_ai):
    response = client.post(
        "/api/ai/suggest-tags",
        json={"title": "FastAPI with SQLAlchemy in Python", "body": "Using docker too"},
        headers=alice["headers"],
    )
    assert response.status_code == 200
    assert set(response.json()["tags"]) == {"python", "docker", "fastapi"}


def test_improve_question(client, alice, mock_ai):
    response = client.post(
        "/api/ai/improve-question",
        json={"title": "my code broken", "body": "it does not work at all"},
        headers=alice["headers"],
    )
    data = response.json()
    assert data["title"].endswith("?") and "What I tried" in data["body"] and data["tips"]


def test_summary(client, alice, bob, make_question, make_answer, mock_ai):
    question = make_question(alice)
    make_answer(bob, question["id"])
    response = client.post(f"/api/ai/questions/{question['id']}/summary", headers=alice["headers"])
    assert response.status_code == 200
    assert "Answers so far:** 1" in response.json()["summary"]


def test_provider_errors_become_502(client, alice, make_question):
    app.dependency_overrides[ai_service.get_ai_provider] = lambda: FailingProvider()
    question = make_question(alice)
    response = client.post(f"/api/ai/questions/{question['id']}/answer", headers=alice["headers"])
    assert response.status_code == 502
    assert response.json()["detail"] == "upstream unavailable"
    assert client.get(f"/api/questions/{question['id']}/answers").json() == []


def test_ai_rate_limit(client, alice, mock_ai):
    payload = {"title": "Python question title", "body": ""}
    for _ in range(ai_rate_limiter.limit):
        assert client.post("/api/ai/suggest-tags", json=payload, headers=alice["headers"]).status_code == 200
    assert client.post("/api/ai/suggest-tags", json=payload, headers=alice["headers"]).status_code == 429
