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


def test_draft_session_returns_sop_and_writes_draft(tmp_path):
    paths = SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    paths.house_style.write_text("Do not include raw secrets.", encoding="utf-8")
    app = create_app(paths)
    client = TestClient(app)
    session = client.post("/api/sessions", json={"title": "Reset MFA"}).json()
    client.post(
        f"/api/sessions/{session['id']}/events",
        json={"type": "click", "label": "Reset MFA"},
    )
    response = client.post(f"/api/sessions/{session['id']}/draft")
    assert response.status_code == 200
    assert response.json()["steps"][0]["action"] == "Select Reset MFA."
    assert (tmp_path / "sessions" / session["id"] / "draft.json").exists()


def test_append_event_unknown_session_returns_404(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    response = TestClient(app).post(
        "/api/sessions/not-created/events",
        json={"type": "navigation", "url": "https://portal.test"},
    )
    assert response.status_code == 404


def test_draft_unknown_session_returns_404_without_orphan_directory(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    response = TestClient(app).post("/api/sessions/not-created/draft")
    assert response.status_code == 404
    assert not (tmp_path / "sessions" / "not-created").exists()


def test_upload_screenshot_unknown_session_returns_404_without_orphan_directory(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    payload = {"filename": "one.png", "screenshot_base64": base64.b64encode(b"png").decode("ascii")}
    response = TestClient(app).post("/api/sessions/not-created/screenshots", json=payload)
    assert response.status_code == 404
    assert not (tmp_path / "sessions" / "not-created").exists()


def test_upload_screenshot_invalid_base64_returns_json_error(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    client = TestClient(app)
    session = client.post("/api/sessions", json={"title": "Screenshot"}).json()
    response = client.post(
        f"/api/sessions/{session['id']}/screenshots",
        json={"filename": "one.png", "screenshot_base64": "not base64"},
    )
    assert response.status_code in {400, 422}
    assert response.headers["content-type"].startswith("application/json")


def test_cors_preflight_allows_browser_extension_origin(tmp_path):
    app = create_app(
        SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    )
    response = TestClient(app).options(
        "/api/sessions",
        headers={
            "Origin": "chrome-extension://example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "*"
