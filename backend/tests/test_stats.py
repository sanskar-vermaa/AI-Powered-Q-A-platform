def test_empty_stats(client):
    stats = client.get("/api/stats").json()
    assert stats == {"users": 0, "questions": 0, "answers": 0, "ai_answers": 0, "tags": 0, "answered_ratio": 0.0}


def test_stats_counts(client, alice, bob, make_question, make_answer, mock_ai):
    q1 = make_question(alice)
    make_question(alice, title="Another question that is unanswered", tags=["misc"])
    make_answer(bob, q1["id"])
    client.post(f"/api/ai/questions/{q1['id']}/answer", headers=alice["headers"])
    stats = client.get("/api/stats").json()
    assert stats["users"] == 2 and stats["questions"] == 2
    assert stats["answers"] == 2 and stats["ai_answers"] == 1
    assert stats["tags"] == 3 and stats["answered_ratio"] == 0.5


def test_leaderboard(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    client.post(f"/api/answers/{answer['id']}/vote", json={"value": 1}, headers=alice["headers"])
    board = client.get("/api/stats/leaderboard").json()
    assert board[0] == {"username": "bob", "reputation": 11, "answer_count": 1}
    assert len(client.get("/api/stats/leaderboard?limit=1").json()) == 1
