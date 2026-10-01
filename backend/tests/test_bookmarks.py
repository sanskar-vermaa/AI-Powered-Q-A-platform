def test_bookmark_flow(client, alice, bob, make_question):
    question = make_question(alice)
    url = f"/api/questions/{question['id']}/bookmark"
    assert client.put(url, headers=bob["headers"]).status_code == 204
    assert client.put(url, headers=bob["headers"]).status_code == 204  # idempotent
    assert client.get(f"/api/questions/{question['id']}", headers=bob["headers"]).json()["bookmarked"] is True
    assert [q["id"] for q in client.get("/api/me/bookmarks", headers=bob["headers"]).json()] == [question["id"]]

    assert client.delete(url, headers=bob["headers"]).status_code == 204
    assert client.get("/api/me/bookmarks", headers=bob["headers"]).json() == []


def test_bookmark_requires_auth_and_existing_question(client, alice):
    assert client.put("/api/questions/1/bookmark").status_code == 401
    assert client.put("/api/questions/999/bookmark", headers=alice["headers"]).status_code == 404


def test_bookmarks_removed_with_question(client, alice, bob, make_question):
    question = make_question(alice)
    client.put(f"/api/questions/{question['id']}/bookmark", headers=bob["headers"])
    client.delete(f"/api/questions/{question['id']}", headers=alice["headers"])
    assert client.get("/api/me/bookmarks", headers=bob["headers"]).json() == []
