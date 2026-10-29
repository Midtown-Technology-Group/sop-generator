from html import escape
from pathlib import PureWindowsPath
from urllib.parse import urlsplit

from .models import DraftSop


def _safe_evidence_source(source: str) -> str:
    """Allow image locations, never active or unknown URI schemes."""
    if any(ord(char) < 32 or ord(char) == 127 for char in source):
        raise ValueError("Unsafe evidence source: control character")
    # Captures on Windows use absolute drive paths rather than URI schemes.
    windows_path = PureWindowsPath(source)
    if (
        not (windows_path.drive and windows_path.is_absolute())
        # Do not rely on urlsplit's patch-version-dependent space stripping.
        and urlsplit(source.lstrip(" ")).scheme.lower() not in {"", "http", "https", "file"}
    ):
        raise ValueError("Unsafe evidence source: unsupported URI scheme")
    return escape(source, quote=True)


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
            escaped_path = _safe_evidence_source(evidence_path)
            lines.append(f'      <img src="{escaped_path}" alt="Step {step.order} evidence">')
        lines.append("    </li>")
    lines.append("  </ol>")
    lines.append("</article>")
    return "\n".join(lines)
