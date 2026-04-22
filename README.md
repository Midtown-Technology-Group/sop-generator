# SOP Generator - Auto-generate IT documentation from Greenshot screenshots

A Python tool that watches your Greenshot folder and automatically generates step-by-step SOP documentation with **manual captions** (AI auto-caption support planned for Azure integration).

> **⚠️ AI Caption Status:** Currently using manual placeholder captions. Azure OpenAI Service (GPT-4 Vision) or Azure AI Vision integration is planned for automatic step description generation.

## The Workflow

```
1. You work through a process, taking screenshots with Greenshot (hotkeys)
2. Stop for 5 seconds → Script detects idle, prompts for title
3. Script generates Markdown SOP with:
   - Numbered steps
   - AI-generated captions (via local LLM) or manual placeholders
   - Embedded image references
   - Copied to clipboard for instant paste into Halo/ITGlue
```

## Prerequisites

### Required
- Python 3.8+
- Greenshot configured to save to a known folder
- Ditto (optional but recommended) - for clipboard history

### AI Captions (Planned - Not Currently Required)
AI-generated captions are **disabled by default**. Two implementation paths are planned:

1. **Azure OpenAI Service** (recommended for production)
   - GPT-4 Vision / GPT-4o for screenshot understanding
   - Azure AD authentication, Key Vault for secrets
   
2. **Local Ollama** (development/testing only)
   - Requires local GPU or strong CPU
   - Pull a vision model: `ollama pull llava`
   - Set `use_llm: True` in CONFIG

See [Azure AI Roadmap](#azure-ai-roadmap) for implementation notes.

## Installation

```bash
# Clone or download sop_generator.py
git clone <repo>  # or just download the file
cd sop_generator

# Install dependencies
pip install requests

# Configure
# Edit sop_generator.py CONFIG dict or create config.json
```

## Configuration

Edit the `CONFIG` dict at the top of `sop_generator.py`:

```python
CONFIG = {
    "greenshot_folder": Path("C:/Users/You/Pictures/Greenshot"),  # Your Greenshot output folder
    "output_folder": Path.home() / "Documents" / "SOPs",         # Where SOPs are saved
    "idle_timeout": 5,   # Seconds to wait after last screenshot
    "use_llm": False,   # Set True for Ollama local LLM (Azure integration TBD)
    # Azure AI integration - see roadmap below
}
```

## Usage

### Watch Mode (Recommended)
Continuously watches for new screenshots:

```bash
python sop_generator.py --watch
```

1. Work through your process, hitting Greenshot hotkeys
2. Pause for 5 seconds
3. Script prompts: "Enter SOP title:"
4. Markdown document generated, copied to clipboard
5. Paste directly into Halo KB or ITGlue

### Process Existing Screenshots

```bash
python sop_generator.py --process-existing
```

### Single Image Caption Test

```bash
python sop_generator.py --caption "path/to/screenshot.png"
```

### Disable AI Captions

```bash
python sop_generator.py --watch --no-llm
```

## Output Format

Generated Markdown looks like:

```markdown
# How to Configure MFA in Azure AD

**Created:** 2025-01-14 14:32
**Screenshots:** 5

---

## Step 1

**Action:** [TODO: Describe this step - e.g., 'Click the Settings button'] (ref: 2025-01-14_14-30-22.png)

![Step 1](./assets/step_01_greenshot_capture_001.png)

<!-- Additional notes: -->

---

## Step 2

**Action:** [TODO: Describe this step - e.g., 'Click the Settings button'] (ref: 2025-01-14_14-31-15.png)

![Step 2](./assets/step_02_greenshot_capture_002.png)

<!-- Additional notes: -->

---
```

## Integration with Halo/ITGlue

### For Halo:
1. Generate SOP with the script
2. Copy is automatically in clipboard
3. Paste into Halo KB article (Markdown supported)
4. Upload images from `assets/` folder to Halo
5. Or convert to HTML for better control

### For ITGlue:
1. Generate SOP
2. ITGlue accepts direct image paste - open the assets folder
3. Drag images into ITGlue editor
4. Copy the text content manually

## Pro Tips

### With Ditto
- Configure Ditto to keep 50+ clipboard items
- Your last 50 screenshots are always available
- Can re-paste if you accidentally overwrite clipboard

### Naming Conventions
Configure Greenshot filename pattern:
- `${capturetime:d"yyyy-MM-dd_HH-mm-ss"}` for timestamps
- Makes chronological sorting automatic

### Batch Processing
If you have folders of existing screenshots:

```python
# Add to sop_generator.py or run separately
import os
from pathlib import Path

folders = Path("C:/OldDocs").glob("*")
for folder in folders:
    images = sorted(folder.glob("*.png"))
    if images:
        # Process each folder as one SOP
        pass
```

## Troubleshooting

### Captions show `[TODO: Describe this step...]`
This is **expected behavior** - AI captions are disabled by default. Options:
1. Fill in descriptions manually (paste into Halo/ITGlue, then edit)
2. Enable local Ollama: Set `use_llm: True` in CONFIG (requires local GPU)
3. Wait for Azure integration (roadmap item)

### Ollama connection errors (if using local LLM)
- Ensure Ollama is running: `ollama serve`
- Test: `curl http://localhost:11434/api/tags`
- Try a smaller model if llava is slow: `ollama pull llava-phi3`

### No screenshots detected
- Verify `greenshot_folder` path exists
- Check Greenshot output filename pattern matches `filename_pattern` in config

### Images not embedding
- Ensure you're using the full asset path or uploading images to your PSA
- Consider using base64 embedded images (add `--embed-base64` flag if implemented)

## Azure AI Roadmap

Planned Azure integration for automatic screenshot captioning:

### Candidate Services

| Service | Use Case | Pros | Cons |
|---------|----------|------|------|
| **Azure OpenAI Service** (GPT-4 Vision) | Generate natural language descriptions of UI actions | Best accuracy, understands context | Higher cost, requires careful prompt engineering |
| **Azure AI Vision** (Image Analysis 4.0) | Dense captioning, OCR for text extraction | Purpose-built for images, cheaper | Less contextual understanding |
| Azure Document Intelligence | Structured data extraction from forms | Not applicable here | Overkill for UI screenshots |

### Implementation Plan

```python
# TODO: Add to sop_generator.py - Azure OpenAI Vision integration
def _caption_with_azure_openai(self, image_path: Path) -> str:
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential
    
    client = AzureOpenAI(
        azure_endpoint="https://YOUR_RESOURCE.openai.azure.com/",
        credential=DefaultAzureCredential(),  # Managed Identity
        api_version="2024-02-15-preview"
    )
    
    # Encode image
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()
    
    response = client.chat.completions.create(
        model="gpt-4-vision",  # Deployment name
        messages=[{
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                {"type": "text", "text": "Describe the UI action in one sentence for IT documentation"}
            ]
        }]
    )
    return response.choices[0].message.content
```

### Design Decisions Needed

1. **Authentication**: DefaultAzureCredential (development) → Managed Identity (production)
2. **Key Storage**: Azure Key Vault for API keys / endpoint URLs
3. **Cost Control**: Implement caching (hash image → store caption) to avoid re-processing
4. **Fallback**: Keep manual placeholder if Azure call fails or quota exceeded

## Future Enhancements

Possible additions:
- [x] Core Greenshot → Markdown workflow
- [ ] Azure OpenAI Service integration (GPT-4 Vision) for auto-captions
- [ ] Azure Key Vault integration for secrets management
- [ ] Direct Halo API integration (auto-upload)
- [ ] Windows notification toast when SOP is ready
- [ ] GUI version with preview
- [ ] Template system for different doc types (runbook vs SOP vs KB)

## License

MIT - Use freely in your MSP/IT operations
