def test_comment_on_question(client, alice, bob, make_question):
    question = make_question(alice)
    response = client.post(
        f"/api/questions/{question['id']}/comments", json={"body": "Which Python version?"}, headers=bob["headers"]
    )
    assert response.status_code == 201
    assert response.json()["author"]["username"] == "bob"
    comments = client.get(f"/api/questions/{question['id']}/comments").json()
    assert [c["body"] for c in comments] == ["Which Python version?"]


def test_comment_on_answer(client, alice, bob, make_question, make_answer):
    answer = make_answer(bob, make_question(alice)["id"])
    response = client.post(f"/api/answers/{answer['id']}/comments", json={"body": "Thanks!"}, headers=alice["headers"])
    assert response.status_code == 201
    assert response.json()["answer_id"] == answer["id"]
    assert len(client.get(f"/api/answers/{answer['id']}/comments").json()) == 1


def test_comment_validation_and_auth(client, alice, make_question):
    question = make_question(alice)
    url = f"/api/questions/{question['id']}/comments"
    assert client.post(url, json={"body": "hi there"}).status_code == 401
    assert client.post(url, json={"body": "x"}, headers=alice["headers"]).status_code == 422
    assert client.post(url, json={"body": "x" * 601}, headers=alice["headers"]).status_code == 422


def test_comment_on_missing_targets(client, alice):
    assert client.post("/api/questions/999/comments", json={"body": "hello"}, headers=alice["headers"]).status_code == 404
    assert client.post("/api/answers/999/comments", json={"body": "hello"}, headers=alice["headers"]).status_code == 404


def test_delete_comment(client, alice, bob, make_question):
    question = make_question(alice)
    comment = client.post(
        f"/api/questions/{question['id']}/comments", json={"body": "A comment"}, headers=bob["headers"]
    ).json()
    assert client.delete(f"/api/comments/{comment['id']}", headers=alice["headers"]).status_code == 403
    assert client.delete(f"/api/comments/{comment['id']}", headers=bob["headers"]).status_code == 204
    assert client.delete(f"/api/comments/{comment['id']}", headers=bob["headers"]).status_code == 404
