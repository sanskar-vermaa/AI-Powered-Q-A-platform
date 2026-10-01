def reputation(client, username):
    return client.get(f"/api/users/{username}").json()["reputation"]


def vote(client, user, kind, target_id, value):
    return client.post(f"/api/{kind}/{target_id}/vote", json={"value": value}, headers=user["headers"])


def test_upvote_question(client, alice, bob, make_question):
    question = make_question(alice)
    response = vote(client, bob, "questions", question["id"], 1)
    assert response.json() == {"score": 1, "my_vote": 1}
    assert reputation(client, "alice") == 1 + 5


def test_upvote_answer(client, alice, bob, make_question, make_answer):
    answer = make_answer(bob, make_question(alice)["id"])
    assert vote(client, alice, "answers", answer["id"], 1).json()["score"] == 1
    assert reputation(client, "bob") == 1 + 10


def test_downvote_costs_reputation_with_floor(client, alice, bob, make_question):
    question = make_question(alice)
    vote(client, bob, "questions", question["id"], -1)
    assert reputation(client, "alice") == 1  # never drops below 1


def test_change_vote(client, alice, bob, make_question):
    question = make_question(alice)
    vote(client, bob, "questions", question["id"], 1)
    response = vote(client, bob, "questions", question["id"], -1)
    assert response.json() == {"score": -1, "my_vote": -1}


def test_retract_vote(client, alice, bob, make_question):
    question = make_question(alice)
    vote(client, bob, "questions", question["id"], 1)
    assert vote(client, bob, "questions", question["id"], 0).json() == {"score": 0, "my_vote": 0}
    assert reputation(client, "alice") == 1


def test_repeat_vote_is_idempotent(client, alice, bob, make_question):
    question = make_question(alice)
    vote(client, bob, "questions", question["id"], 1)
    assert vote(client, bob, "questions", question["id"], 1).json()["score"] == 1
    assert reputation(client, "alice") == 6


def test_cannot_vote_on_own_post(client, alice, make_question):
    question = make_question(alice)
    assert vote(client, alice, "questions", question["id"], 1).status_code == 400


def test_invalid_vote_value(client, alice, bob, make_question):
    question = make_question(alice)
    assert vote(client, bob, "questions", question["id"], 2).status_code == 422


def test_vote_requires_auth(client, alice, make_question):
    question = make_question(alice)
    assert client.post(f"/api/questions/{question['id']}/vote", json={"value": 1}).status_code == 401


def test_vote_on_missing_targets(client, bob):
    assert vote(client, bob, "questions", 999, 1).status_code == 404
    assert vote(client, bob, "answers", 999, 1).status_code == 404


def test_my_vote_reported_in_detail(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(alice, question["id"])
    vote(client, bob, "questions", question["id"], -1)
    vote(client, bob, "answers", answer["id"], 1)
    assert client.get(f"/api/questions/{question['id']}", headers=bob["headers"]).json()["my_vote"] == -1
    assert client.get(f"/api/questions/{question['id']}").json()["my_vote"] == 0
    answers = client.get(f"/api/questions/{question['id']}/answers", headers=bob["headers"]).json()
    assert answers[0]["my_vote"] == 1


def test_vote_on_ai_answer(client, alice, bob, make_question, mock_ai):
    question = make_question(alice)
    ai_answer = client.post(f"/api/ai/questions/{question['id']}/answer", headers=alice["headers"]).json()
    assert vote(client, bob, "answers", ai_answer["id"], 1).json()["score"] == 1
