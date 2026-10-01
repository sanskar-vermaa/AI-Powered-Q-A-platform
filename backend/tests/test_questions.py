def test_create_question(client, alice, make_question):
    question = make_question(alice, tags=["Python", "JSON", "python"])
    assert question["author"]["username"] == "alice"
    assert question["tags"] == ["json", "python"]
    assert question["score"] == 0 and question["answer_count"] == 0


def test_create_question_requires_auth(client):
    response = client.post("/api/questions", json={"title": "A valid title here", "body": "x" * 30})
    assert response.status_code == 401


def test_create_question_validates_lengths(client, alice):
    response = client.post("/api/questions", json={"title": "short", "body": "too short"}, headers=alice["headers"])
    assert response.status_code == 422


def test_create_question_limits_tags(client, alice):
    response = client.post(
        "/api/questions",
        json={"title": "A question with many tags", "body": "x" * 30, "tags": list("abcdef")},
        headers=alice["headers"],
    )
    assert response.status_code == 422


def test_get_question_counts_views(client, alice, make_question):
    question = make_question(alice)
    client.get(f"/api/questions/{question['id']}")
    response = client.get(f"/api/questions/{question['id']}")
    assert response.json()["views"] == 2
    assert client.get(f"/api/questions/{question['id']}?count_view=false").json()["views"] == 2


def test_get_missing_question(client):
    assert client.get("/api/questions/999").status_code == 404


def test_update_question_by_author(client, alice, make_question):
    question = make_question(alice)
    response = client.patch(
        f"/api/questions/{question['id']}",
        json={"title": "How do I parse JSON safely in Python?", "tags": ["python"]},
        headers=alice["headers"],
    )
    assert response.status_code == 200
    assert response.json()["title"] == "How do I parse JSON safely in Python?"
    assert response.json()["tags"] == ["python"]


def test_update_question_forbidden_for_others(client, alice, bob, make_question):
    question = make_question(alice)
    response = client.patch(f"/api/questions/{question['id']}", json={"title": "Hijacked title here"}, headers=bob["headers"])
    assert response.status_code == 403


def test_moderator_can_edit_any_question(client, alice, make_user, make_question):
    moderator = make_user("mod", role="moderator")
    question = make_question(alice)
    response = client.patch(
        f"/api/questions/{question['id']}", json={"body": "Edited by a moderator for clarity."}, headers=moderator["headers"]
    )
    assert response.status_code == 200


def test_delete_question(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    make_answer(bob, question["id"])
    assert client.delete(f"/api/questions/{question['id']}", headers=bob["headers"]).status_code == 403
    assert client.delete(f"/api/questions/{question['id']}", headers=alice["headers"]).status_code == 204
    assert client.get(f"/api/questions/{question['id']}").status_code == 404


def test_delete_question_with_accepted_answer(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert client.delete(f"/api/questions/{question['id']}", headers=alice["headers"]).status_code == 204
