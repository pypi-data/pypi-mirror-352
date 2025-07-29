"""
Asset Manager for Flort

Handles loading and displaying of assets like logos, icons, and ASCII art.
"""

import os
from pathlib import Path
from typing import Optional

# ASCII Art (embedded for reliability)
FLORT_LOGO = """
███████╗██╗      ██████╗ ██████╗ ████████╗
██╔════╝██║     ██╔═══██╗██╔══██╗╚══██╔══╝
█████╗  ██║     ██║   ██║██████╔╝   ██║   
██╔══╝  ██║     ██║   ██║██╔══██╗   ██║   
██║     ███████╗╚██████╔╝██║  ██║   ██║   
╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
"""

FLORT_COMPACT = """
╭─ FLORT ─────────────────────────────────╮
│  File Concatenation & Project Overview │
╰─────────────────────────────────────────╯
"""

FLORT_MINI = """
F L O R T
═════════
"""

def get_asset_path(asset_name: str) -> Optional[Path]:
    """
    Get the path to an asset file.
    
    Args:
        asset_name: Name of the asset file (e.g., 'logo.png')
        
    Returns:
        Path to the asset file if it exists, None otherwise
    """
    # Try package assets first
    try:
        import pkg_resources
        try:
            asset_path = pkg_resources.resource_filename('flort', f'assets/{asset_name}')
            if os.path.exists(asset_path):
                return Path(asset_path)
        except (ImportError, FileNotFoundError):
            pass
    except ImportError:
        pass
    
    # Try relative to module
    module_dir = Path(__file__).parent
    asset_path = module_dir / 'assets' / asset_name
    if asset_path.exists():
        return asset_path
    
    # Try relative to project root
    project_root = module_dir.parent
    asset_path = project_root / 'assets' / asset_name
    if asset_path.exists():
        return asset_path
    
    return None

def get_logo_url() -> str:
    """
    Get the URL to the Flort logo for online display.
    
    Returns:
        str: URL to the logo image
    """
    return "https://raw.githubusercontent.com/chris17453/flort/main/assets/flort-logo.png"

def show_banner(style: str = "full") -> None:
    """
    Display a Flort banner.
    
    Args:
        style: Style of banner ("full", "compact", "mini")
    """
    if style == "full":
        print(FLORT_LOGO)
        print("File Concatenation & Project Overview Tool")
    elif style == "compact":
        print(FLORT_COMPACT)
    elif style == "mini":
        print(FLORT_MINI)
    else:
        print("FLORT - File Concatenation Tool")

def show_ascii_art() -> str:
    """
    Get ASCII art for display in help or about sections.
    
    Returns:
        str: ASCII art string
    """
    return FLORT_LOGO + "\n\nFile Concatenation & Project Overview Tool\n"

def create_logo_files():
    """
    Create logo files for the project.
    This function creates simple text-based logos that can be converted to images.
    """
    assets_dir = Path(__file__).parent.parent / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create a simple SVG logo
    svg_logo = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#2196F3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#21CBF3;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="400" height="120" fill="white" stroke="#ddd" stroke-width="2" rx="10"/>
  
  <!-- Main text -->
  <text x="50" y="50" font-family="monospace" font-size="36" font-weight="bold" fill="url(#grad1)">FLORT</text>
  
  <!-- Subtitle -->
  <text x="50" y="75" font-family="sans-serif" font-size="14" fill="#666">File Concatenation &amp; Project Overview</text>
  
  <!-- Icon elements -->
  <rect x="320" y="20" width="15" height="20" fill="#2196F3" rx="2"/>
  <rect x="340" y="15" width="15" height="25" fill="#21CBF3" rx="2"/>
  <rect x="360" y="25" width="15" height="15" fill="#42A5F5" rx="2"/>
  
  <!-- Connection lines -->
  <line x1="335" y1="30" x2="340" y2="30" stroke="#2196F3" stroke-width="2"/>
  <line x1="355" y1="27" x2="360" y2="27" stroke="#21CBF3" stroke-width="2"/>
</svg>"""
    
    svg_file = assets_dir / "flort-logo.svg"
    svg_file.write_text(svg_logo)
    
    # Create a README for assets
    readme_content = """# Flort Assets

This directory contains logos, icons, and other visual assets for Flort.

## Files:
- `flort-logo.svg` - Main logo in SVG format
- `flort-logo.png` - Main logo in PNG format (create from SVG)
- `flort-icon.ico` - Icon file for Windows
- `favicon.ico` - Favicon for documentation

## Usage:
- Use SVG for scalable applications
- Convert SVG to PNG for GitHub README
- Use ICO for Windows applications

## Converting SVG to PNG:
```bash
# Using Inkscape
inkscape flort-logo.svg --export-png=flort-logo.png --export-width=400

# Using ImageMagick
convert flort-logo.svg flort-logo.png

# Online converter
# Upload SVG to https://convertio.co/svg-png/
```
"""
    
    readme_file = assets_dir / "README.md"
    readme_file.write_text(readme_content)
    
    print(f"✅ Created logo files in {assets_dir}")
    print(f"📁 SVG logo: {svg_file}")
    print(f"📖 Asset README: {readme_file}")
    print("\n💡 To create PNG version:")
    print("   1. Open SVG in any graphics program")
    print("   2. Export as PNG (400x120 recommended)")
    print("   3. Save as flort-logo.png")

if __name__ == "__main__":
    # Demo the assets
    print("🎨 Flort Asset Demo")
    print("=" * 50)
    
    print("\n🏆 Full Banner:")
    show_banner("full")
    
    print("\n📋 Compact Banner:")
    show_banner("compact")
    
    print("\n🎯 Mini Banner:")
    show_banner("mini")
    
    print(f"\n🌐 Logo URL: {get_logo_url()}")
    
    # Check for asset files
    logo_path = get_asset_path("flort-logo.png")
    if logo_path:
        print(f"🖼️  Logo file found: {logo_path}")
    else:
        print("📝 No logo file found - run create_logo_files() to generate")
        
        create_files = input("\n❓ Create logo files now? (y/N): ")
        if create_files.lower() in ['y', 'yes']:
            create_logo_files()