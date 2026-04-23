# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅ Active |

## Reporting Security Issues

Email: **security@midtowntg.com**

## Security Considerations

### Screenshot Processing

This tool processes local screenshot files:
- **Input**: PNG/JPG files from `~/Pictures/Screenshots/`
- **Processing**: OCR via Azure AI Vision API
- **Output**: Markdown SOPs in `~/Documents/SOPs/`

### Azure AI Vision Security

- API calls use HTTPS/TLS 1.2+
- Images are transmitted to Azure for OCR processing
- Microsoft does not store or train on your images ([Azure AI Vision privacy](https://azure.microsoft.com/services/cognitive-services/computer-vision/))
- API key stored in environment variable or config file

### Configuration Security

Config file at `~/.config/sop-generator/config.yaml`:
```yaml
azure:
  api_key: "${AZURE_VISION_KEY}"  # Use env var, don't hardcode
  endpoint: "https://your-resource.cognitiveservices.azure.com"
```

**Never commit API keys to git.**

### Clipboard Handling

- Uses Windows `clip.exe` command via subprocess
- Input text is sanitized before clipboard copy
- No `shell=True` (secure subprocess usage)

### Output Security

Generated SOPs may contain:
- System configurations
- Internal network details
- Sensitive UI elements

**Review before sharing externally.**

## Least Privilege

Recommended Azure permissions:
- **Cognitive Services User** role only
- Single resource: Computer Vision
- No access to other Azure resources

## Input Validation

- Screenshot paths validated as existing files
- No shell expansion of user input
- Image format validation (PNG, JPG only)
- File size limits enforced

## Development

When contributing:
1. Never commit API keys
2. Use environment variables for secrets
3. Test with dummy images, not production screenshots
4. Validate all file paths
