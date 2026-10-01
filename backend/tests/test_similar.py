def test_similar_finds_duplicates(client, alice, make_question):
    original = make_question(alice, title="How do I sort a list of dictionaries by value in Python?")
    make_question(alice, title="What is the difference between Docker and a VM?", tags=["docker"])
    response = client.get("/api/questions/similar", params={"title": "Sort list of dictionaries by a value python"})
    results = response.json()
    assert results and results[0]["id"] == original["id"]
    assert all(r["id"] != 0 for r in results)


def test_similar_empty_for_unrelated(client, alice, make_question):
    make_question(alice)
    assert client.get("/api/questions/similar", params={"title": "kubernetes ingress tls"}).json() == []


def test_similar_ignores_stopwords_only(client, alice, make_question):
    make_question(alice)
    assert client.get("/api/questions/similar", params={"title": "how do I"}).json() == []


def test_related_excludes_self(client, alice, make_question):
    q1 = make_question(alice, title="How to parse JSON in Python quickly?")
    q2 = make_question(alice, title="Parse nested JSON in Python")
    related = client.get(f"/api/questions/{q1['id']}/related").json()
    assert [r["id"] for r in related] == [q2["id"]]
    assert client.get("/api/questions/999/related").status_code == 404
