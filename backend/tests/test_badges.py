from sqlalchemy import update

from app import models


def badges(client, username):
    return client.get(f"/api/users/{username}").json()["badges"]


def test_curious_badge_for_first_question(client, alice, make_question):
    make_question(alice)
    make_question(alice, title="A second question to ask today")
    assert badges(client, "alice") == ["curious"]


def test_helper_and_teacher_badges(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    answer = make_answer(bob, question["id"])
    assert "helper" in badges(client, "bob")
    client.post(f"/api/questions/{question['id']}/accept/{answer['id']}", headers=alice["headers"])
    assert "teacher" in badges(client, "bob")


def test_enthusiast_badge_after_ten_answers(client, alice, bob, make_question, make_answer):
    question = make_question(alice)
    for i in range(10):
        make_answer(bob, question["id"], body=f"Answer number {i} with enough characters.")
    assert "enthusiast" in badges(client, "bob")


def test_trusted_badge_on_reputation(client, db, alice, bob, make_question):
    db.execute(update(models.User).where(models.User.id == alice["id"]).values(reputation=496))
    db.commit()
    question = make_question(alice)
    client.post(f"/api/questions/{question['id']}/vote", json={"value": 1}, headers=bob["headers"])
    assert "trusted" in badges(client, "alice")


def test_badge_notification(client, alice, make_question):
    make_question(alice)
    notes = client.get("/api/notifications", headers=alice["headers"]).json()
    assert any(n["kind"] == "badge" and "curious" in n["message"] for n in notes)
