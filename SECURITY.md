# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Active |

## Reporting Security Issues

Email: **security@midtowntg.com**

## Security Considerations

### Local Capture Processing

This tool records browser workflow metadata through a local browser extension and companion service:
- **Input**: Browser navigation, clicks, form-change markers, submits, and optional screenshot uploads to the local API.
- **Storage**: Raw capture sessions, drafts, screenshots, and exports remain under `%LOCALAPPDATA%\MTG\SOPGenerator`.
- **Output**: Halo KB-ready HTML and Bifrost publish requests after operator review.

### Local Data Boundary

- The companion service binds to `127.0.0.1` by default.
- Raw capture data is machine-local working data and should not be synced or uploaded until reviewed.
- The extension does not send raw form field values; it records `value_hint: "changed"` for form-change events.
- Review screenshots and generated HTML before publishing because screenshots may show customer or credential context.

### Configuration Security

The default style file is created at `%LOCALAPPDATA%\MTG\SOPGenerator\house-style.md`.

**Never commit API keys to git.**

### Publishing Security

- Publishing goes through Bifrost. Do not put Halo credentials in the browser extension.
- Configure Bifrost with `BIFROST_URL` and, when needed, `BIFROST_TOKEN`.
- Keep tokens in environment variables or an approved secret store, not in tracked files.

### Output Security

Generated SOPs may contain:
- System configurations
- Internal portal details
- Sensitive UI elements

**Review before sharing externally.**

## Least Privilege

Recommended integration boundaries:
- Browser extension talks only to the localhost companion API.
- Bifrost owns Halo API credentials and article publishing.
- Local captures stay on the workstation until the operator exports or publishes reviewed content.

## Input Validation

- Session IDs are contained under the configured local session directory.
- Screenshot uploads validate base64 input and write under the session screenshots directory.
- Bifrost publish responses are validated before the CLI reports success.

## Development

When contributing:
1. Never commit API keys
2. Use environment variables for secrets
3. Test with dummy screenshots or local fake payloads, not production customer captures
4. Validate all file paths
