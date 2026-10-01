def test_profile(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    make_answer(bob, question["id"])
    profile = client.get("/api/users/alice").json()
    assert profile["question_count"] == 1 and profile["answer_count"] == 0
    assert "email" not in profile
    assert client.get("/api/users/BOB").json()["answer_count"] == 1


def test_profile_not_found(client):
    assert client.get("/api/users/ghost").status_code == 404


def test_update_me(client, alice):
    response = client.patch("/api/users/me", json={"bio": "I like Python."}, headers=alice["headers"])
    assert response.status_code == 200
    assert response.json()["bio"] == "I like Python."
    assert client.get("/api/users/alice").json()["bio"] == "I like Python."


def test_update_email_conflict(client, alice, bob):
    response = client.patch("/api/users/me", json={"email": "bob@example.com"}, headers=alice["headers"])
    assert response.status_code == 409
    ok = client.patch("/api/users/me", json={"email": "new@example.com"}, headers=alice["headers"])
    assert ok.json()["email"] == "new@example.com"


def test_list_users_by_reputation(client, alice, bob, make_question):
    question = make_question(alice)
    client.post(f"/api/questions/{question['id']}/vote", json={"value": 1}, headers=bob["headers"])
    assert [u["username"] for u in client.get("/api/users").json()] == ["alice", "bob"]
    assert [u["username"] for u in client.get("/api/users?q=bo").json()] == ["bob"]


def test_user_answers(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    assert [a["id"] for a in client.get("/api/users/bob/answers").json()] == [answer["id"]]
