# SOP Generator

SOP Generator is a local-first SOP recorder for human-led browser workflows. A technician starts a recording, works through the real process in Edge or Chrome, reviews the generated draft, and publishes only the approved SOP artifact.

The raw capture boundary is local by design. Browser events, screenshots, drafts, and reviewed exports stay on the workstation under `%LOCALAPPDATA%\MTG\SOPGenerator` unless the operator explicitly exports or publishes a reviewed result.

## Browser-First Workflow

1. Run the Python companion service on localhost.
2. Load the browser extension from `extension/browser`.
3. Start a capture session from the extension.
4. Perform the workflow in the normal browser profile.
5. Review the generated draft and Halo KB-ready HTML.
6. Publish the reviewed payload through Bifrost.

The browser extension captures meaningful clicks, navigation, form changes with value hints, and form submits. It does not provide operator note or screenshot controls in the current UI. The companion service has screenshot storage APIs for future capture paths, but the extension does not currently expose a screenshot button or automatic screenshot flow.

The Python companion owns local session storage, draft generation, Halo KB-ready HTML rendering, and publish requests. Publishing goes through Bifrost so Halo authentication, retries, category mapping, and article creation stay in the integration layer instead of the extension.

## Install

```powershell
python -m pip install -e .[dev]
python -m sop_generator init-style
python -m sop_generator serve --host 127.0.0.1 --port 8765
```

Or start the companion with:

```powershell
.\Start-SOPGenerator.ps1
```

## Browser Extension

Load `extension/browser` as an unpacked extension in Microsoft Edge or Google Chrome:

1. Open `edge://extensions` or `chrome://extensions`.
2. Enable developer mode.
3. Choose "Load unpacked".
4. Select the repository's `extension/browser` folder.

Keep the companion service running while recording. The extension posts to the localhost companion API and preserves the operator's normal browser context, including existing profiles, conditional access state, bookmarks, and policy-managed settings.

## Local Data

Capture sessions are stored below `%LOCALAPPDATA%\MTG\SOPGenerator`:

```text
%LOCALAPPDATA%\MTG\SOPGenerator\
  sessions\
  house-style.md
```

This directory can contain screenshots and browser context from real customer workflows. Treat it as machine-local working data and review before publishing or sharing any exported HTML.

## Draft, Export, And Publish

After recording, use the session id returned by the extension or companion API:

```powershell
python -m sop_generator draft <session-id>
python -m sop_generator export <session-id>
```

The `draft` command writes a local draft from captured events. The `export` command renders the current draft as Halo KB-ready HTML. Perform manual review before publishing; the current CLI expects the operator to review the draft or exported HTML first, but publish does not enforce an approval gate in code.

Publish through Bifrost with environment variables:

```powershell
$env:BIFROST_URL = "https://bifrost.example"
$env:BIFROST_TOKEN = "<token>"
python -m sop_generator publish <session-id>
```

Or pass the values as flags:

```powershell
python -m sop_generator publish <session-id> --bifrost-url https://bifrost.example --token <token>
```

## Publishing

SOP Generator renders reviewed drafts into Halo KB-ready HTML. Direct Halo credentials do not belong in the browser extension. When the operator publishes, the companion sends the reviewed payload to Bifrost, and Bifrost performs the Halo KB operation.

If Bifrost is unavailable, keep the reviewed export local and retry publishing after the integration recovers.
