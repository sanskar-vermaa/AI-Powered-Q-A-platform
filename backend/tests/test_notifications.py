def kinds(client, user):
    return [n["kind"] for n in client.get("/api/notifications", headers=user["headers"]).json()]


def test_answer_notifies_question_author(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    make_answer(bob, question["id"])
    notifications = client.get("/api/notifications", headers=alice["headers"]).json()
    answer_note = next(n for n in notifications if n["kind"] == "answer")
    assert "bob answered" in answer_note["message"]
    assert answer_note["link"] == f"/questions/{question['id']}"


def test_no_notification_for_own_actions(client, alice, make_question, make_answer):
    question = make_question(alice)
    make_answer(alice, question["id"])
    assert "answer" not in kinds(client, alice)


def test_comment_and_accept_notifications(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    client.post(f"/api/answers/{answer['id']}/comments", json={"body": "Nice one"}, headers=alice["headers"])
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert {"comment", "accepted"} <= set(kinds(client, bob))


def test_unread_count_and_mark_read(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    make_answer(bob, question["id"])
    unread = client.get("/api/notifications/unread-count", headers=alice["headers"]).json()["unread"]
    assert unread >= 1
    first = client.get("/api/notifications", headers=alice["headers"]).json()[0]
    assert client.post(f"/api/notifications/{first['id']}/read", headers=alice["headers"]).status_code == 204
    after = client.get("/api/notifications/unread-count", headers=alice["headers"]).json()["unread"]
    assert after == unread - 1


def test_mark_all_read(client, alice, bob, make_question, make_answer):
    make_answer(bob, make_question(alice)["id"])
    client.post("/api/notifications/read-all", headers=alice["headers"])
    assert client.get("/api/notifications/unread-count", headers=alice["headers"]).json()["unread"] == 0
    assert client.get("/api/notifications?unread_only=true", headers=alice["headers"]).json() == []


def test_cannot_read_others_notifications(client, alice, bob, make_question, make_answer):
    make_answer(bob, make_question(alice)["id"])
    note = client.get("/api/notifications", headers=alice["headers"]).json()[0]
    assert client.post(f"/api/notifications/{note['id']}/read", headers=bob["headers"]).status_code == 404
