from dataclasses import dataclass
import os
from pathlib import Path


DEFAULT_STYLE = """# MTG SOP House Style

Write for MTG technicians performing the work later.

- Start with a concise purpose and scope.
- Use numbered procedural steps.
- Preserve exact product and portal names.
- Call out decision points and verification evidence.
- Do not include raw passwords, MFA codes, API keys, session tokens, or recovery secrets.
- Replace sensitive customer-specific values with clear placeholders.
"""


@dataclass(frozen=True)
class SopPaths:
    root: Path
    sessions: Path
    house_style: Path

    @classmethod
    def default(cls) -> "SopPaths":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".local" / "share")
        root = base / "MTG" / "SOPGenerator"
        return cls(
            root=root,
            sessions=root / "sessions",
            house_style=root / "house-style.md",
        )

    def ensure(self) -> "SopPaths":
        self.sessions.mkdir(parents=True, exist_ok=True)
        return self

    def ensure_default_style(self) -> Path:
        self.ensure()
        if not self.house_style.exists():
            self.house_style.write_text(DEFAULT_STYLE, encoding="utf-8")
        return self.house_style
