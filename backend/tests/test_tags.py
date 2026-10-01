def test_list_tags_with_counts(client, alice, make_question):
    make_question(alice, tags=["python", "json"])
    make_question(alice, title="Python decorators explained please", tags=["python"])
    tags = client.get("/api/tags").json()
    assert [(t["name"], t["question_count"]) for t in tags] == [("python", 2), ("json", 1)]


def test_list_tags_by_name_and_search(client, alice, make_question):
    make_question(alice, tags=["python", "json", "django"])
    assert [t["name"] for t in client.get("/api/tags?sort=name").json()] == ["django", "json", "python"]
    assert [t["name"] for t in client.get("/api/tags?q=jan").json()] == ["django"]


def test_get_tag(client, alice, make_question):
    make_question(alice, tags=["python"])
    assert client.get("/api/tags/Python").json()["question_count"] == 1
    assert client.get("/api/tags/unknown").status_code == 404


def test_update_tag_description_requires_staff(client, alice, make_user, make_question):
    make_question(alice, tags=["python"])
    regular = make_user("regular")
    admin = make_user("admin", role="admin")
    payload = {"description": "A general-purpose programming language."}
    assert client.patch("/api/tags/python", json=payload, headers=regular["headers"]).status_code == 403
    response = client.patch("/api/tags/python", json=payload, headers=admin["headers"])
    assert response.status_code == 200
    assert response.json()["description"] == payload["description"]


def test_tags_are_reused_across_questions(client, alice, make_question):
    make_question(alice, tags=["python"])
    make_question(alice, title="Second question about python", tags=["PYTHON"])
    assert len(client.get("/api/tags").json()) == 1
