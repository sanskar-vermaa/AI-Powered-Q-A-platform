def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_openapi_schema_lists_core_routes(client):
    paths = client.get("/openapi.json").json()["paths"]
    for path in ("/api/questions", "/api/auth/login", "/api/ai/suggest-tags", "/api/chat/stream"):
        assert path in paths


def test_unknown_api_route_returns_404(client):
    assert client.get("/api/does-not-exist").status_code == 404
