# Quick Start

## Install And Start

Run these commands from the repository root:

```powershell
python -m pip install -e .[dev]
python -m sop_generator init-style
python -m sop_generator serve --host 127.0.0.1 --port 8765
```

You can also start the local companion with:

```powershell
.\Start-SOPGenerator.ps1
```

## Load The Browser Extension

Load `extension/browser` as an unpacked extension in Edge or Chrome:

1. Open `edge://extensions` or `chrome://extensions`.
2. Turn on developer mode.
3. Select "Load unpacked".
4. Choose the `extension/browser` folder from this repo.

## Record A Browser Workflow

1. Keep `python -m sop_generator serve --host 127.0.0.1 --port 8765` running.
2. Use the extension popup to start a capture session.
3. Work through the procedure in the normal browser profile.
4. Capture notes or screenshots where they clarify the SOP.
5. Stop the session and review the generated draft.
6. Export Halo KB-ready HTML or publish the reviewed payload through Bifrost.

Raw capture data stays under `%LOCALAPPDATA%\MTG\SOPGenerator` on the local workstation. The extension captures browser workflow context for the local companion; it does not store direct Halo credentials.
