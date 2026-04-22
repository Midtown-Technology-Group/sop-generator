"""
SOP Generator - Watches Greenshot folder and auto-generates step-by-step documentation

Usage:
    python sop_generator.py --watch                    # Watch mode (continuous)
    python sop_generator.py --process-existing          # Process all existing screenshots
    python python sop_generator.py --caption "image.png" # Generate caption for single image
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import subprocess

# Configuration
CONFIG = {
    # Where Greenshot saves screenshots - adjust this to your path
    "greenshot_folder": Path.home() / "Pictures" / "Greenshot",
    
    # Where generated SOPs will be saved
    "output_folder": Path.home() / "Documents" / "SOPs",
    
    # Time to wait after last screenshot before processing (seconds)
    "idle_timeout": 5,
    
    # Screenshot filename pattern Greenshot uses
    # Common: "greenshot_capture_001.png" or "2025-01-14_14-32-45.png"
    "filename_pattern": "*.png",
    
    # TODO: Azure AI Integration (Not Implemented)
    # Future enhancement: Use Azure OpenAI Service (GPT-4 Vision) or Azure AI Vision
    # for automatic caption generation from screenshots.
    # 
    # Candidate Azure primitives:
    #   - Azure OpenAI Service (GPT-4o / GPT-4 Vision) - Best for UI understanding
    #   - Azure AI Vision (Image Analysis 4.0) - Dense captioning, OCR
    #   - Azure Document Intelligence - Overkill for this use case
    #
    # Implementation notes:
    #   - Use DefaultAzureCredential for auth (managed identity in prod)
    #   - Consider Azure Key Vault for API key storage
    #   - Implement retry logic with exponential backoff
    #   - Cache results to reduce API calls
    #
    # For now, captions are manual placeholders. Set use_llm=True for Ollama local fallback.
    "use_llm": False,  # Set to True to use local Ollama (Azure integration TBD)
    "llm_provider": "ollama",  # "ollama" - Azure TBD
    "ollama_model": "llava",  # Local vision model (Azure GPT-4 Vision TBD)
    "ollama_url": "http://localhost:11434",
}


class SOPGenerator:
    def __init__(self, config: dict):
        self.config = config
        self.output_folder = Path(config["output_folder"])
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.known_files = set()
        
    def get_greenshot_files(self) -> List[Path]:
        """Get all screenshot files from Greenshot folder, sorted by modification time."""
        folder = Path(self.config["greenshot_folder"])
        if not folder.exists():
            print(f"⚠️  Greenshot folder not found: {folder}")
            return []
        
        files = list(folder.glob(self.config["filename_pattern"]))
        files.sort(key=lambda p: p.stat().st_mtime)
        return files
    
    def generate_caption(self, image_path: Path) -> str:
        """Generate a caption for an image using local LLM (Ollama) or fallback."""
        if not self.config["use_llm"]:
            return self._manual_caption_prompt(image_path)
        
        if self.config["llm_provider"] == "ollama":
            return self._caption_with_ollama(image_path)
        else:
            return self._manual_caption_prompt(image_path)
    
    def _caption_with_ollama(self, image_path: Path) -> str:
        """Use Ollama's llava model to generate image captions."""
        import base64
        
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Build prompt for SOP context
            prompt = """Describe what is happening in this screenshot in one clear sentence suitable for IT documentation.
Focus on: What action is being performed, what UI element is being interacted with, and what the expected result is.
Be concise (under 15 words)."""
            
            # Call Ollama API
            import requests
            response = requests.post(
                f"{self.config['ollama_url']}/api/generate",
                json={
                    "model": self.config["ollama_model"],
                    "prompt": prompt,
                    "images": [image_data],
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                caption = response.json().get("response", "").strip()
                # Clean up common artifacts
                caption = caption.replace("The image shows ", "").replace("This screenshot shows ", "")
                return caption
            else:
                return self._manual_caption_prompt(image_path)
                
        except Exception as e:
            print(f"  ⚠️  LLM caption failed: {e}")
            return self._manual_caption_prompt(image_path)
    
    def _manual_caption_prompt(self, image_path: Path) -> str:
        """Fallback: Return placeholder for manual entry.
        
        TODO: Replace with Azure AI Vision / Azure OpenAI GPT-4 Vision call.
        See CONFIG comments for implementation roadmap.
        """
        # Extract filename without extension as a hint
        hint = image_path.stem.replace("_", " ").replace("-", " ")
        return f"[TODO: Describe this step - e.g., 'Click the Settings button'] (ref: {image_path.name})"
    
    def create_sop_document(self, screenshots: List[Path], title: str) -> Path:
        """Create a Markdown SOP document from a list of screenshots."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"SOP_{title.replace(' ', '_')}_{timestamp}.md"
        output_path = self.output_folder / filename
        
        # Build document
        lines = [
            f"# {title}",
            "",
            f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Screenshots:** {len(screenshots)}",
            "",
            "---",
            "",
        ]
        
        # Process each screenshot
        for i, screenshot in enumerate(screenshots, 1):
            print(f"  📸 Processing step {i}/{len(screenshots)}: {screenshot.name}")
            
            # Generate or get caption
            caption = self.generate_caption(screenshot)
            
            # Determine relative path for image reference
            # For Halo/ITGlue: we'll embed directly, so we copy images to assets folder
            asset_name = f"step_{i:02d}_{screenshot.name}"
            asset_path = self.output_folder / "assets" / asset_name
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy image to assets (for embedding)
            import shutil
            shutil.copy2(screenshot, asset_path)
            
            # Add step to document
            lines.extend([
                f"## Step {i}",
                "",
                f"**Action:** {caption}",
                "",
                f"![Step {i}](./assets/{asset_name})",
                "",
                "<!-- Additional notes: -->",
                "",
                "---",
                "",
            ])
        
        # Write document
        content = "\n".join(lines)
        output_path.write_text(content, encoding="utf-8")
        
        print(f"\n✅ SOP saved to: {output_path}")
        print(f"📁 Assets folder: {self.output_folder / 'assets'}")
        
        # Copy to clipboard for immediate paste
        self._copy_to_clipboard(content)
        
        return output_path
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard for immediate paste."""
        try:
            # Windows
            subprocess.run(["clip"], input=text.encode(), check=True, shell=True)
            print("📋 Content copied to clipboard - ready to paste into Halo/ITGlue!")
        except Exception:
            pass
    
    def watch_mode(self):
        """Continuously watch for new screenshots and auto-generate SOPs."""
        print(f"👁️  Watching: {self.config['greenshot_folder']}")
        print(f"⏱️  Idle timeout: {self.config['idle_timeout']} seconds")
        if self.config["use_llm"]:
            print(f"🤖 LLM enabled: {self.config['llm_provider']}")
        else:
            print("✏️  Manual captions: Fill in [TODO] placeholders after generation")
            print("   (Azure AI integration planned for auto-captions)")
        print("Press Ctrl+C to stop\n")
        
        pending_screenshots = []
        last_activity = time.time()
        
        # Initialize with existing files
        self.known_files = {f.stat().st_mtime for f in self.get_greenshot_files()}
        
        try:
            while True:
                current_files = self.get_greenshot_files()
                current_mod_times = {f.stat().st_mtime for f in current_files}
                
                # Detect new files
                new_files = [f for f in current_files if f.stat().st_mtime not in self.known_files]
                
                if new_files:
                    print(f"📸 Detected {len(new_files)} new screenshot(s)")
                    pending_screenshots.extend(new_files)
                    last_activity = time.time()
                    self.known_files = current_mod_times
                
                # Check if we should generate SOP (idle timeout reached)
                if pending_screenshots and (time.time() - last_activity) > self.config["idle_timeout"]:
                    print(f"\n⏳ Idle timeout reached. Processing {len(pending_screenshots)} screenshots...")
                    
                    # Get user input for title
                    title = input("Enter SOP title (or press Enter for auto-timestamp): ").strip()
                    if not title:
                        title = f"Process_Documentation_{datetime.now().strftime('%Y-%m-%d')}"
                    
                    self.create_sop_document(pending_screenshots, title)
                    pending_screenshots = []
                    self.known_files = {f.stat().st_mtime for f in self.get_greenshot_files()}
                    print("\n👁️  Resuming watch mode...\n")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 Stopped.")
            if pending_screenshots:
                print(f"⚠️  {len(pending_screenshots)} pending screenshots not processed.")


def main():
    parser = argparse.ArgumentParser(
        description="Auto-generate SOPs from Greenshot screenshots",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sop_generator.py --watch                    # Watch mode
  python sop_generator.py --process-existing         # Process all existing screenshots
  python sop_generator.py --caption "screenshot.png"   # Caption single image
  python sop_generator.py --config                     # Show current config
        """
    )
    
    parser.add_argument("--watch", "-w", action="store_true", help="Watch mode - continuously monitor for new screenshots")
    parser.add_argument("--process-existing", "-p", action="store_true", help="Process all existing screenshots as one SOP")
    parser.add_argument("--caption", "-c", metavar="IMAGE", help="Generate caption for single image")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM caption generation")
    
    args = parser.parse_args()
    
    # Apply CLI overrides
    if args.no_llm:
        CONFIG["use_llm"] = False
    
    if args.config:
        print("Current configuration:")
        for key, value in CONFIG.items():
            print(f"  {key}: {value}")
        return
    
    generator = SOPGenerator(CONFIG)
    
    if args.caption:
        caption = generator.generate_caption(Path(args.caption))
        print(f"Caption: {caption}")
    
    elif args.process_existing:
        files = generator.get_greenshot_files()
        if not files:
            print("No screenshots found in Greenshot folder.")
            return
        
        print(f"Found {len(files)} screenshots.")
        title = input("Enter SOP title: ").strip() or "Existing_Process_Documentation"
        generator.create_sop_document(files, title)
    
    else:
        # Default to watch mode
        generator.watch_mode()


if __name__ == "__main__":
    main()
