# Quick Start Guide

## 5-Minute Setup

### 1. Install Python Dependencies
```bash
cd sop_generator
pip install requests
```

### 2. Configure Greenshot
Open Greenshot → Preferences → Output:
- Set "Storage location" to something like `C:\Users\You\Pictures\Greenshot`
- Enable "Copy file path to clipboard" (optional but helpful)
- Filename pattern: `${capturetime:d"yyyy-MM-dd_HH-mm-ss"}` or default

### 3. Configure SOP Generator
Edit `sop_generator.py` and update:
```python
"greenshot_folder": Path("C:/Users/YourName/Pictures/Greenshot"),  # <- Your path
"output_folder": Path("C:/Users/YourName/Documents/SOPs"),         # <- Where you want docs
```

### 4. AI Captions (Not Required - Placeholders for Now)

**Current behavior:** Step descriptions are manual placeholders like `[TODO: Describe this step]`

**Future:** Azure OpenAI Service (GPT-4 Vision) integration planned

**Optional local workaround:**
```powershell
# Windows with winget - for local Ollama fallback only
winget install Ollama.Ollama
ollama pull llava
# Then set use_llm: True in sop_generator.py CONFIG
```

### 5. Run It
Double-click `start_watch.bat` or run:
```bash
python sop_generator.py --watch
```

## Your First SOP

1. **Start the script** → You'll see "Watching: C:\Users\...\Greenshot"
2. **Do your process** → Hit Greenshot hotkey (default: `PrtScn`) at each step
   - Step 1: Open settings → Screenshot
   - Step 2: Click option → Screenshot
   - Step 3: Enter value → Screenshot
3. **Pause** → Wait 5 seconds after your last screenshot
4. **Enter title** → Script prompts: `Enter SOP title: `
5. **Paste into Halo/ITGlue** → Content is already in your clipboard!

## File Structure After Running

```
C:\Users\You\Documents\SOPs\
├── SOP_How_to_Reset_Password_2025-01-14_14-32-15.md
└── assets\
    ├── step_01_2025-01-14_14-30-22.png
    ├── step_02_2025-01-14_14-30-45.png
    └── step_03_2025-01-14_14-31-10.png
```

## Advanced: Making It Even Faster

### Auto-start with Windows
1. Press `Win+R` → type `shell:startup`
2. Create shortcut to `start_watch.bat`

### Pin to Taskbar
1. Right-click `start_watch.bat` → Create shortcut
2. Right-click shortcut → Properties → Change icon
3. Pin to taskbar for one-click launch

### Keyboard Shortcut
Create an AutoHotkey script (`sop_hotkey.ahk`):
```autohotkey
#s::  ; Win+S to toggle SOP generator
Run, C:\Path\To\sop_generator\start_watch.bat
return
```

## Troubleshooting

**"No module named 'requests'"**
```bash
pip install requests
```

**"Greenshot folder not found"**
- Double-check path in config (use forward slashes: `C:/Users/...`)
- Ensure folder exists and Greenshot is saving there

**"Ollama connection error"**
- Ensure Ollama is running in background (system tray icon)
- Or disable LLM: `--no-llm` flag

**Script doesn't detect screenshots**
- Check that `filename_pattern` matches your Greenshot output (usually `*.png`)
- Try running with `--process-existing` to test file detection

## Tips for Halo/ITGlue Integration

### Halo PSA
1. Generate SOP (clipboard auto-copied)
2. In Halo: New KB Article
3. Paste (Ctrl+V) - Markdown renders automatically
4. For images: Drag from `assets/` folder or use Halo's image upload

### ITGlue
1. Generate SOP
2. ITGlue's editor is HTML-based
3. Either:
   - Option A: Paste text, then drag images individually
   - Option B: Use an online Markdown-to-HTML converter first
   - Option C: Upload to a wiki that ITGlue can iframe/embed

### Pro Tip: Base64 Embedding
If you want single-file portability (image data embedded in the Markdown):

```bash
# Add this flag (requires updating script)
python sop_generator.py --watch --embed-images
```

This makes the `.md` file completely self-contained but much larger.

---

**Questions?** The script is just a starting point - customize it for your specific PSA workflow!
