# Repository guidance

SOP Generator records human-led browser workflows locally, renders reviewed drafts as Halo KB-ready HTML, and publishes through Bifrost. Read `README.md` before changing capture, storage, export, or publish behavior. Python code lives in `src/`; the unpacked Edge/Chrome extension is `extension/browser`; `tests/` holds Python tests.

## Critical boundaries

Raw browser events, screenshots, drafts, and exports remain under `%LOCALAPPDATA%/MTG/SOPGenerator` unless the operator explicitly exports or publishes a reviewed result. Use synthetic sessions for development; never sweep, upload, or publish real customer captures as a test shortcut. Preserve the operator's normal browser profile and conditional-access context.

The extension currently records clicks, navigation, form changes/value hints, and submits; it does not expose screenshot or note controls. Storage APIs are not proof of an implemented capture UI. Keep documentation aligned with observable behavior.

Publishing belongs in Bifrost so Halo credentials, retries, category mapping, and article creation stay in the integration layer. Direct Halo credentials do not belong in the extension. The CLI expects manual review but does not enforce approval in code: confirm the reviewed payload and explicit publish intent before invoking publish. If Bifrost is unavailable, retain the reviewed export locally for later retry.

## Verification

CI uses Python 3.11. From the repository root:

```sh
python -m pip install -e .[dev]
python -m pytest -q
python -m ruff check src tests
```

For local browser verification, follow the localhost companion and unpacked-extension setup in `README.md`; use disposable session data. Distinguish Python test results, interactive capture evidence, and actual downstream Halo publication. Never log Bifrost tokens or captured sensitive field values.

## Secret gate before publication

Before publishing the current PR branch, commit the complete candidate and run
`python3 scripts/secret_gate.py --base origin/main` (native Windows: `python`). Require exit 0;
missing tooling/authentication, scan errors and skipped scans block publication.
Then run the existing repository gates. Repeat after changing outgoing commits.
Push exactly the scanned HEAD. This PR scan covers the current branch against its
fetched intended base; other refs, multi-ref pushes and rewritten history require
`--pre-push` with Git's complete ref-update stream. Stop if any pushed ref is
uncovered. See [secret scanning](SECRET-SCANNING.md) for base selection, new branches,
pre-push input and prerequisites. Preserve GitGuardian App, CI and Gitleaks checks.

For a non-default PR target, fetch its destination and pass that exact ref to
`--base`; the remote default is not a substitute for a release/maintenance base.

The secret gate requires Python 3.11+ and approved ggshield >=1.56.1,<2.
