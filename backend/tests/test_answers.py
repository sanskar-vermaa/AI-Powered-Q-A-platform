def test_create_and_list_answers(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    assert answer["author"]["username"] == "bob"
    assert answer["is_ai"] is False and answer["is_accepted"] is False
    listed = client.get(f"/api/questions/{question['id']}/answers").json()
    assert [a["id"] for a in listed] == [answer["id"]]


def test_answer_requires_auth_and_valid_body(client, alice, make_question):
    question = make_question(alice)
    assert client.post(f"/api/questions/{question['id']}/answers", json={"body": "x" * 30}).status_code == 401
    response = client.post(f"/api/questions/{question['id']}/answers", json={"body": "short"}, headers=alice["headers"])
    assert response.status_code == 422


def test_answer_on_missing_question(client, alice):
    response = client.post("/api/questions/12345/answers", json={"body": "x" * 30}, headers=alice["headers"])
    assert response.status_code == 404


def test_answers_sorted_accepted_then_score(client, alice, bob, make_user, make_question, make_answer):
    carol = make_user("carol")
    question = make_question(alice)
    first = make_answer(bob, question["id"], body="First answer with enough text in it.")
    second = make_answer(carol, question["id"], body="Second answer with enough text in it.")
    third = make_answer(bob, question["id"], body="Third answer with enough text in it.")
    client.post(f"/api/answers/{second['id']}/vote", json={"value": 1}, headers=alice["headers"])
    client.post(f"/api/questions/{question['id']}/accept/{third['id']}", headers=alice["headers"])
    order = [a["id"] for a in client.get(f"/api/questions/{question['id']}/answers").json()]
    assert order == [third["id"], second["id"], first["id"]]


def test_update_answer(client, alice, bob, make_question, make_answer):
    answer = make_answer(bob, make_question(alice)["id"])
    new_body = {"body": "Updated answer body that is long enough."}
    assert client.patch(f"/api/answers/{answer['id']}", json=new_body, headers=alice["headers"]).status_code == 403
    response = client.patch(f"/api/answers/{answer['id']}", json=new_body, headers=bob["headers"])
    assert response.status_code == 200
    assert response.json()["body"] == new_body["body"]


def test_delete_answer(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    assert client.delete(f"/api/answers/{answer['id']}", headers=alice["headers"]).status_code == 403
    assert client.delete(f"/api/answers/{answer['id']}", headers=bob["headers"]).status_code == 204
    assert client.get(f"/api/answers/{answer['id']}").status_code == 404


def test_delete_accepted_answer_clears_acceptance(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    client.delete(f"/api/answers/{answer['id']}", headers=bob["headers"])
    detail = client.get(f"/api/questions/{question['id']}").json()
    assert detail["accepted_answer_id"] is None and detail["answer_count"] == 0


def test_get_single_answer(client, alice, bob, make_question, make_answer):
    answer = make_answer(bob, make_question(alice)["id"])
    assert client.get(f"/api/answers/{answer['id']}").json()["id"] == answer["id"]
