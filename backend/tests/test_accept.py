def reputation(client, username):
    return client.get(f"/api/users/{username}").json()["reputation"]


def test_only_author_can_accept(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    response = client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=bob["headers"])
    assert response.status_code == 403


def test_accept_awards_reputation(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    response = client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert response.status_code == 200
    assert response.json()["accepted_answer_id"] == answer["id"]
    assert reputation(client, "bob") == 1 + 15
    assert reputation(client, "alice") == 1 + 2


def test_accept_again_toggles_off(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    url = f"/api/questions/{question['id']}/accept/{answer['id']}"
    client.post(url, headers=alice["headers"])
    assert client.post(url, headers=alice["headers"]).json()["accepted_answer_id"] is None
    assert reputation(client, "bob") == 1
    assert reputation(client, "alice") == 1


def test_switching_accepted_answer_moves_reputation(client, alice, bob, make_user, make_question, make_answer):
    carol = make_user("carol")
    question = make_question(alice)
    first = make_answer(bob, question["id"])
    second = make_answer(carol, question["id"])
    client.post(f"/api/questions/{question['id']}/accept/{first['id']}", headers=alice["headers"])
    client.post(f"/api/questions/{question['id']}/accept/{second['id']}", headers=alice["headers"])
    assert reputation(client, "bob") == 1
    assert reputation(client, "carol") == 16
    assert reputation(client, "alice") == 3


def test_self_answer_accept_gives_no_reputation(client, alice, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(alice, question["id"])
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert reputation(client, "alice") == 1


def test_accept_answer_from_other_question(client, alice, bob, make_question, make_answer):
    q1 = make_question(alice)
    q2 = make_question(alice, title="Another question about Python lists")
    answer = make_answer(bob, q2["id"])
    assert client.post(f"/api/questions/{q1['id']}/accept/{answer['id']}", headers=alice["headers"]).status_code == 404


def test_accepted_flag_in_answer_list(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert client.get(f"/api/questions/{question['id']}/answers").json()[0]["is_accepted"] is True
    summary = client.get("/api/questions").json()["items"][0]
    assert summary["has_accepted_answer"] is True
