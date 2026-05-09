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
4. Let the extension capture clicks, navigation, form changes with value hints, and form submits.
5. Stop the session and note the session id.

## Draft, Review, Export, Publish

Create the local draft:

```powershell
python -m sop_generator draft <session-id>
```

Perform manual review of the generated draft before continuing. The current tool writes drafts and HTML, but it does not enforce approval in code before publish.

Export Halo KB-ready HTML:

```powershell
python -m sop_generator export <session-id>
```

Publish through Bifrost with environment variables:

```powershell
$env:BIFROST_URL = "https://bifrost.example"
$env:BIFROST_TOKEN = "<token>"
python -m sop_generator publish <session-id>
```

Or publish with flags:

```powershell
python -m sop_generator publish <session-id> --bifrost-url https://bifrost.example --token <token>
```

Raw capture data stays under `%LOCALAPPDATA%\MTG\SOPGenerator` on the local workstation. The extension captures browser workflow context for the local companion; it does not store direct Halo credentials.
