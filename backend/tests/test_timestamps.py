from datetime import datetime


def test_timestamps_are_timezone_aware(client, alice, make_question):
    question = make_question(alice)
    for value in (question["created_at"], client.get(f"/api/questions/{question['id']}").json()["updated_at"]):
        assert datetime.fromisoformat(value).utcoffset() is not None
