import base64

from fastapi.testclient import TestClient

from sop_generator.models import DraftSop
from sop_generator.paths import SopPaths
from sop_generator.render_halo import render_halo_html
from sop_generator.service import create_app


def test_capture_draft_and_render_flow(tmp_path):
    paths = SopPaths(
        root=tmp_path,
        sessions=tmp_path / "sessions",
        house_style=tmp_path / "house-style.md",
    )
    paths.ensure_default_style()
    client = TestClient(create_app(paths))

    session = client.post("/api/sessions", json={"title": "Reset MFA"}).json()
    session_id = session["id"]
    client.post(
        f"/api/sessions/{session_id}/events",
        json={"type": "navigation", "title": "Admin Portal"},
    )
    client.post(
        f"/api/sessions/{session_id}/events",
        json={"type": "click", "label": "Users"},
    )
    client.post(
        f"/api/sessions/{session_id}/screenshots",
        json={
            "filename": "one.png",
            "screenshot_base64": base64.b64encode(b"png").decode("ascii"),
        },
    )

    draft = client.post(f"/api/sessions/{session_id}/draft").json()
    draft_model = DraftSop.model_validate(draft)
    html = render_halo_html(draft_model)

    assert draft["title"] == "Reset MFA"
    assert draft["steps"][0]["action"] == "Open Admin Portal."
    assert "Reset MFA" in html
    assert "Open Admin Portal." in html
