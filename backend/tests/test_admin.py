def test_admin_can_promote_and_suspend(client, make_user):
    admin = make_user("root", role="admin")
    bob = make_user("bob")
    response = client.patch(f"/api/admin/users/{bob['id']}", json={"role": "moderator"}, headers=admin["headers"])
    assert response.status_code == 200 and response.json()["role"] == "moderator"

    client.patch(f"/api/admin/users/{bob['id']}", json={"is_active": False}, headers=admin["headers"])
    # Suspended users lose access with existing tokens and cannot log in.
    assert client.get("/api/auth/me", headers=bob["headers"]).status_code == 401
    assert client.post("/api/auth/login", json={"username": "bob", "password": "password123"}).status_code == 403


def test_non_admin_forbidden(client, make_user):
    moderator = make_user("mod", role="moderator")
    bob = make_user("bob")
    assert (
        client.patch(f"/api/admin/users/{bob['id']}", json={"role": "admin"}, headers=moderator["headers"]).status_code
        == 403
    )


def test_admin_cannot_change_self(client, make_user):
    admin = make_user("root", role="admin")
    response = client.patch(f"/api/admin/users/{admin['id']}", json={"role": "user"}, headers=admin["headers"])
    assert response.status_code == 400


def test_admin_update_missing_user(client, make_user):
    admin = make_user("root", role="admin")
    assert client.patch("/api/admin/users/999", json={"role": "user"}, headers=admin["headers"]).status_code == 404


def test_invalid_role(client, make_user):
    admin = make_user("root", role="admin")
    bob = make_user("bob")
    assert (
        client.patch(f"/api/admin/users/{bob['id']}", json={"role": "god"}, headers=admin["headers"]).status_code == 422
    )
