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
    screenshot_response = client.post(
        f"/api/sessions/{session_id}/screenshots",
        json={
            "filename": "one.png",
            "screenshot_base64": base64.b64encode(b"png").decode("ascii"),
        },
    )
    screenshot_path = screenshot_response.json()["path"]
    client.post(
        f"/api/sessions/{session_id}/events",
        json={"type": "click", "label": "Users", "screenshot_path": screenshot_path},
    )

    draft = client.post(f"/api/sessions/{session_id}/draft").json()
    draft_model = DraftSop.model_validate(draft)
    html = render_halo_html(draft_model)

    assert screenshot_response.status_code == 200
    assert screenshot_path.endswith("one.png")
    assert (tmp_path / "sessions" / session_id / "screenshots" / "one.png").read_bytes() == b"png"
    assert draft["title"] == "Reset MFA"
    assert draft["steps"][0]["action"] == "Open Admin Portal."
    assert draft_model.steps[1].evidence == [screenshot_path]
    assert "Reset MFA" in html
    assert "Open Admin Portal." in html
    assert screenshot_path in html
