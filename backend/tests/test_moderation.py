import pytest


@pytest.fixture
def moderator(make_user):
    return make_user("mod", role="moderator")


def flag(client, user, target_type, target_id, reason="spam"):
    return client.post(
        "/api/flags", json={"target_type": target_type, "target_id": target_id, "reason": reason}, headers=user["headers"]
    )


def test_flag_content(client, alice, bob, make_question):
    question = make_question(alice)
    response = flag(client, bob, "question", question["id"])
    assert response.status_code == 201
    assert response.json()["status"] == "open" and response.json()["reporter"]["username"] == "bob"


def test_duplicate_open_flag_rejected(client, alice, bob, make_question):
    question = make_question(alice)
    flag(client, bob, "question", question["id"])
    assert flag(client, bob, "question", question["id"]).status_code == 409


def test_flag_missing_content(client, bob):
    assert flag(client, bob, "answer", 999).status_code == 404


def test_flag_invalid_reason(client, alice, bob, make_question):
    question = make_question(alice)
    assert flag(client, bob, "question", question["id"], reason="boring").status_code == 422


def test_queue_requires_staff(client, bob, moderator):
    assert client.get("/api/moderation/flags", headers=bob["headers"]).status_code == 403
    assert client.get("/api/moderation/flags", headers=moderator["headers"]).status_code == 200


def test_dismiss_flag(client, alice, bob, moderator, make_question):
    question = make_question(alice)
    flag_id = flag(client, bob, "question", question["id"]).json()["id"]
    response = client.post(f"/api/moderation/flags/{flag_id}", json={"status": "dismissed"}, headers=moderator["headers"])
    assert response.json()["status"] == "dismissed"
    assert client.get(f"/api/questions/{question['id']}").status_code == 200
    assert client.get("/api/moderation/flags", headers=moderator["headers"]).json() == []
    assert len(client.get("/api/moderation/flags?status=all", headers=moderator["headers"]).json()) == 1


def test_resolve_and_delete_answer(client, alice, bob, make_user, moderator, make_question, make_answer):
    carol = make_user("carol")
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    first = flag(client, alice, "answer", answer["id"]).json()["id"]
    flag(client, carol, "answer", answer["id"])
    response = client.post(
        f"/api/moderation/flags/{first}", json={"status": "resolved", "delete_content": True}, headers=moderator["headers"]
    )
    assert response.status_code == 200
    assert client.get(f"/api/answers/{answer['id']}").status_code == 404
    assert client.get(f"/api/questions/{question['id']}").json()["accepted_answer_id"] is None
    assert client.get("/api/moderation/flags", headers=moderator["headers"]).json() == []


def test_resolve_and_delete_question_and_comment(client, alice, bob, moderator, make_question):
    question = make_question(alice)
    comment = client.post(
        f"/api/questions/{question['id']}/comments", json={"body": "buy cheap stuff"}, headers=bob["headers"]
    ).json()
    for target_type, target_id in (("comment", comment["id"]), ("question", question["id"])):
        flag_id = flag(client, alice if target_type == "comment" else bob, target_type, target_id).json()["id"]
        client.post(
            f"/api/moderation/flags/{flag_id}", json={"status": "resolved", "delete_content": True},
            headers=moderator["headers"],
        )
    assert client.get(f"/api/questions/{question['id']}").status_code == 404


def test_resolve_missing_flag(client, moderator):
    response = client.post("/api/moderation/flags/999", json={"status": "resolved"}, headers=moderator["headers"])
    assert response.status_code == 404
