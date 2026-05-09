from sop_generator.models import DraftSop, SopStep
from sop_generator.render_halo import render_halo_html


def test_render_halo_html_escapes_text():
    draft = DraftSop(
        title="Reset <MFA>",
        summary="Use the portal.",
        warnings=["Remove secrets."],
        steps=[SopStep(order=1, action="Click <Reset>", evidence=["screenshots/one.png"])],
    )
    html = render_halo_html(draft)
    assert "&lt;MFA&gt;" in html
    assert "&lt;Reset&gt;" in html
    assert "screenshots/one.png" in html
