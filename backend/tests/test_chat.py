import json

from app.main import app
from app.services import ai as ai_service
from app.services.ai import AIError


def parse_sse(text):
    events = []
    for block in text.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def test_chat_creates_conversation(client, alice, mock_ai):
    response = client.post("/api/chat", json={"message": "What is a Python generator?"}, headers=alice["headers"])
    assert response.status_code == 200
    data = response.json()
    assert data["reply"]["role"] == "assistant"
    conversations = client.get("/api/chat/conversations", headers=alice["headers"]).json()
    assert conversations[0]["id"] == data["conversation_id"]
    assert conversations[0]["title"] == "What is a Python generator?"


def test_chat_continues_conversation(client, alice, mock_ai):
    first = client.post("/api/chat", json={"message": "Hello"}, headers=alice["headers"]).json()
    client.post("/api/chat", json={"message": "Again", "conversation_id": first["conversation_id"]}, headers=alice["headers"])
    detail = client.get(f"/api/chat/conversations/{first['conversation_id']}", headers=alice["headers"]).json()
    assert [m["role"] for m in detail["messages"]] == ["user", "assistant", "user", "assistant"]


def test_conversations_are_private(client, alice, bob, mock_ai):
    conversation_id = client.post("/api/chat", json={"message": "secret"}, headers=alice["headers"]).json()["conversation_id"]
    assert client.get(f"/api/chat/conversations/{conversation_id}", headers=bob["headers"]).status_code == 404
    response = client.post("/api/chat", json={"message": "hi", "conversation_id": conversation_id}, headers=bob["headers"])
    assert response.status_code == 404
    assert client.get("/api/chat/conversations", headers=bob["headers"]).json() == []


def test_delete_conversation(client, alice, mock_ai):
    conversation_id = client.post("/api/chat", json={"message": "bye"}, headers=alice["headers"]).json()["conversation_id"]
    assert client.delete(f"/api/chat/conversations/{conversation_id}", headers=alice["headers"]).status_code == 204
    assert client.get("/api/chat/conversations", headers=alice["headers"]).json() == []


def test_chat_validation(client, alice, mock_ai):
    assert client.post("/api/chat", json={"message": ""}, headers=alice["headers"]).status_code == 422
    assert client.post("/api/chat", json={"message": "hi"}).status_code == 401


def test_stream_chat_events(client, alice, mock_ai):
    response = client.post("/api/chat/stream", json={"message": "stream please"}, headers=alice["headers"])
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    events = parse_sse(response.text)
    assert events[0][0] == "start" and events[-1][0] == "done"
    streamed = "".join(data["text"] for name, data in events if name == "delta").strip()
    conversation_id = events[0][1]["conversation_id"]
    detail = client.get(f"/api/chat/conversations/{conversation_id}", headers=alice["headers"]).json()
    assert detail["messages"][-1]["content"] == streamed


def test_stream_chat_error_event(client, alice):
    class Broken(ai_service.MockProvider):
        def stream_chat(self, history):
            yield "partial "
            raise AIError("connection lost")

    app.dependency_overrides[ai_service.get_ai_provider] = lambda: Broken()
    events = parse_sse(client.post("/api/chat/stream", json={"message": "x"}, headers=alice["headers"]).text)
    assert events[-1] == ("error", {"detail": "connection lost"})
