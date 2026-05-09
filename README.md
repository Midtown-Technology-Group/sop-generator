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

The browser extension captures meaningful clicks, navigation, form submits, operator notes, and screenshots. It is intentionally thin: it sends capture data to the local companion and does not hold Halo credentials or call vendor APIs directly.

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
  style\
```

This directory can contain screenshots and browser context from real customer workflows. Treat it as machine-local working data and review before publishing or sharing any exported HTML.

## Publishing

SOP Generator renders reviewed drafts into Halo KB-ready HTML. Direct Halo credentials do not belong in the browser extension. When the operator publishes, the companion sends the reviewed payload to Bifrost, and Bifrost performs the Halo KB operation.

If Bifrost is unavailable, keep the reviewed export local and retry publishing after the integration recovers.
