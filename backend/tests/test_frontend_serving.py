from fastapi.testclient import TestClient

from app.main import _mount_frontend, create_app


def test_spa_fallback_and_assets(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "app.js").write_text("console.log('hi')")
    (tmp_path / "index.html").write_text("<html>spa</html>")
    (tmp_path / "favicon.svg").write_text("<svg/>")
    app = create_app()
    _mount_frontend(app, tmp_path)
    client = TestClient(app)
    assert client.get("/assets/app.js").text == "console.log('hi')"
    assert client.get("/favicon.svg").text == "<svg/>"
    assert client.get("/questions/42").text == "<html>spa</html>"
    assert client.get("/../../etc/passwd").text == "<html>spa</html>"
    assert client.get("/api/health").json()["status"] == "ok"


def test_no_frontend_build_is_fine(tmp_path):
    app = create_app()
    _mount_frontend(app, tmp_path)
    assert TestClient(app).get("/").status_code == 404
