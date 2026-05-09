import base64

from fastapi.testclient import TestClient

from sop_generator.paths import SopPaths
from sop_generator.service import create_app


def test_health_endpoint(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    assert TestClient(app).get("/health").json()["ok"] is True


def test_create_session_and_append_event(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    client = TestClient(app)
    session = client.post("/api/sessions", json={"title": "Reset MFA"}).json()
    response = client.post(
        f"/api/sessions/{session['id']}/events",
        json={"type": "navigation", "url": "https://portal.test"},
    )
    assert response.status_code == 200


def test_upload_screenshot(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    client = TestClient(app)
    session = client.post("/api/sessions", json={"title": "Screenshot"}).json()
    payload = {"filename": "one.png", "screenshot_base64": base64.b64encode(b"png").decode("ascii")}
    response = client.post(f"/api/sessions/{session['id']}/screenshots", json=payload)
    assert response.status_code == 200
    assert response.json()["path"].endswith("one.png")
