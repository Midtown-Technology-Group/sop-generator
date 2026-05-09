from html import escape

from .models import DraftSop


def render_halo_html(draft: DraftSop) -> str:
    """Render a reviewed SOP draft as Halo-ready HTML."""
    lines = [
        "<article>",
        f"  <h1>{escape(draft.title)}</h1>",
        f"  <p>{escape(draft.summary)}</p>",
    ]

    if draft.warnings:
        lines.append("  <h2>Warnings</h2>")
        lines.append("  <ul>")
        for warning in draft.warnings:
            lines.append(f"    <li>{escape(warning)}</li>")
        lines.append("  </ul>")

    lines.append("  <ol>")
    for step in sorted(draft.steps, key=lambda item: item.order):
        lines.append(f"    <li>{escape(step.action)}")
        if step.expected_result:
            lines.append(f"      <p>{escape(step.expected_result)}</p>")
        for evidence_path in step.evidence:
            escaped_path = escape(evidence_path, quote=True)
            lines.append(f'      <img src="{escaped_path}" alt="Step {step.order} evidence">')
        lines.append("    </li>")
    lines.append("  </ol>")
    lines.append("</article>")
    return "\n".join(lines)
