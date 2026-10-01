def register(client, username="alice", email=None, password="password123"):
    return client.post(
        "/api/auth/register",
        json={"username": username, "email": email or f"{username}@example.com", "password": password},
    )


def test_register_returns_user_without_password(client):
    response = register(client)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "hashed_password" not in body and "password" not in body


def test_first_user_becomes_admin(client):
    assert register(client, "first").json()["role"] == "admin"
    assert register(client, "second").json()["role"] == "user"


def test_duplicate_username_is_case_insensitive(client):
    register(client, "alice")
    response = register(client, "ALICE", email="other@example.com")
    assert response.status_code == 409


def test_duplicate_email(client):
    register(client, "alice", email="same@example.com")
    assert register(client, "bob", email="SAME@example.com").status_code == 409


def test_weak_password_rejected(client):
    assert register(client, password="short1").status_code == 422
    assert register(client, password="lettersonly").status_code == 422


def test_invalid_username_rejected(client):
    assert register(client, username="no spaces").status_code == 422
    assert register(client, username="ab").status_code == 422


def test_login_with_username_or_email(client):
    register(client)
    for identifier in ("alice", "ALICE", "alice@example.com"):
        response = client.post("/api/auth/login", json={"username": identifier, "password": "password123"})
        assert response.status_code == 200, identifier
        assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    register(client)
    response = client.post("/api/auth/login", json={"username": "alice", "password": "wrong-pass1"})
    assert response.status_code == 401


def test_oauth2_token_endpoint(client):
    register(client)
    response = client.post("/api/auth/token", data={"username": "alice", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_me_requires_auth(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401


def test_me_returns_current_user(client, alice):
    response = client.get("/api/auth/me", headers=alice["headers"])
    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_change_password(client, alice):
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "password123", "new_password": "newpassword9"},
        headers=alice["headers"],
    )
    assert response.status_code == 204
    assert client.post("/api/auth/login", json={"username": "alice", "password": "newpassword9"}).status_code == 200
    assert client.post("/api/auth/login", json={"username": "alice", "password": "password123"}).status_code == 401


def test_change_password_requires_current(client, alice):
    response = client.post(
        "/api/auth/change-password",
        json={"current_password": "nope12345", "new_password": "newpassword9"},
        headers=alice["headers"],
    )
    assert response.status_code == 400
