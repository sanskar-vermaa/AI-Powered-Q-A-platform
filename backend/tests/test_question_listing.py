def seed(client, alice, bob, make_question, make_answer):
    q1 = make_question(
        alice, title="How do I sort a list in Python?", body="I need to sort numbers ascending.", tags=["python"]
    )
    q2 = make_question(
        alice, title="What is a closure in JavaScript?", body="Explain closures with an example.", tags=["javascript"]
    )
    q3 = make_question(
        bob,
        title="Why is my SQL query so slow?",
        body="A SELECT with joins takes ten seconds.",
        tags=["sql", "performance"],
    )
    make_answer(bob, q1["id"])
    client.post(f"/api/questions/{q2['id']}/vote", json={"value": 1}, headers=bob["headers"])
    return q1, q2, q3


def titles(response):
    return [item["title"] for item in response.json()["items"]]


def test_list_newest_first(client, alice, bob, make_question, make_answer):
    q1, q2, q3 = seed(client, alice, bob, make_question, make_answer)
    response = client.get("/api/questions")
    assert response.status_code == 200
    assert [i["id"] for i in response.json()["items"]] == [q3["id"], q2["id"], q1["id"]]
    assert response.json()["total"] == 3


def test_sort_by_votes(client, alice, bob, make_question, make_answer):
    _, q2, _ = seed(client, alice, bob, make_question, make_answer)
    assert client.get("/api/questions?sort=votes").json()["items"][0]["id"] == q2["id"]


def test_unanswered_filter(client, alice, bob, make_question, make_answer):
    q1, _, _ = seed(client, alice, bob, make_question, make_answer)
    ids = [i["id"] for i in client.get("/api/questions?sort=unanswered").json()["items"]]
    assert q1["id"] not in ids and len(ids) == 2


def test_filter_by_tag(client, alice, bob, make_question, make_answer):
    seed(client, alice, bob, make_question, make_answer)
    assert titles(client.get("/api/questions?tag=SQL")) == ["Why is my SQL query so slow?"]


def test_filter_by_author(client, alice, bob, make_question, make_answer):
    seed(client, alice, bob, make_question, make_answer)
    assert client.get("/api/questions?author=bob").json()["total"] == 1


def test_search_matches_title_and_body(client, alice, bob, make_question, make_answer):
    seed(client, alice, bob, make_question, make_answer)
    assert titles(client.get("/api/questions?q=closure")) == ["What is a closure in JavaScript?"]
    assert titles(client.get("/api/questions?q=joins")) == ["Why is my SQL query so slow?"]
    assert client.get("/api/questions?q=nothing-matches-this").json()["total"] == 0


def test_pagination(client, alice, make_question):
    for i in range(5):
        make_question(alice, title=f"Pagination question number {i}", body="Body text long enough to pass.")
    page = client.get("/api/questions?page=2&page_size=2").json()
    assert page["page"] == 2 and page["page_size"] == 2 and page["pages"] == 3 and page["total"] == 5
    assert len(page["items"]) == 2


def test_page_size_is_capped(client):
    assert client.get("/api/questions?page_size=1000").json()["page_size"] == 100


def test_summary_fields(client, alice, bob, make_question, make_answer):
    q1, _, _ = seed(client, alice, bob, make_question, make_answer)
    item = next(i for i in client.get("/api/questions").json()["items"] if i["id"] == q1["id"])
    assert item["answer_count"] == 1
    assert item["excerpt"].startswith("I need to sort")
    assert item["has_accepted_answer"] is False
