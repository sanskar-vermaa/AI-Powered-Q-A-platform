from app import seed


def test_seed_populates_and_is_idempotent(client):
    assert seed.seed() is True
    stats = client.get("/api/stats").json()
    assert stats["users"] == len(seed.USERS)
    assert stats["questions"] == len(seed.QUESTIONS)
    assert seed.seed() is False
    login = client.post("/api/auth/login", json={"username": "admin", "password": seed.DEMO_PASSWORD})
    assert login.status_code == 200
    assert client.get("/api/tags/python").json()["description"]
