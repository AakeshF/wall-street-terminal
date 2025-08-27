#!/usr/bin/env python3
"""
GitHub Release Preparation Script
=================================
Prepares release notes and checklist for Wall Street Terminal
"""

import os
import json
from pathlib import Path
from datetime import datetime

def get_file_size(filepath):
    """Get file size in MB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    return "Not found"

def create_release_notes():
    """Generate release notes for GitHub"""
    
    # Check if executable exists
    exe_path = Path("dist/WallStreetTerminal.exe")
    exe_size = get_file_size(exe_path)
    
    release_notes = f"""# Wall Street Terminal v3.0

## First Official Release!

### Quick Install
Download `WallStreetTerminal.exe` ({exe_size}) and double-click to run. No installation required!

### What's New in v3.0

#### Major Features
- **ASCII Price Charts**: Beautiful sparkline visualizations
- **Custom Market Screener**: Define your own screening criteria  
- **Web Search AI**: Real-time sentiment analysis
- **Performance Tracking**: Track win rate and best/worst trades
- **Professional Terminal**: Fast, clean, and powerful

#### Key Improvements
- Removed mock data for 100% real market information
- Enhanced AI predictions with web context
- Transaction reasoning for every trade
- Intelligent 4-hour caching system
- Multi-source data (Finnhub, Polygon, Alpha Vantage)

### Setup Instructions

1. Download `WallStreetTerminal.exe`
2. Run the executable
3. On first run, it creates `.env.example`
4. Copy to `.env` and add your free API keys:
   - [Finnhub](https://finnhub.io) - 60 calls/min
   - [Polygon](https://polygon.io) - 5 calls/min  
   - [Alpha Vantage](https://alphavantage.co) - 5 calls/min
   - [Anthropic](https://anthropic.com) - For AI analysis
   - [Tavily](https://tavily.com) - Optional web search

### For Developers

```bash
git clone https://github.com/yourusername/wall-street-terminal.git
cd wall-street-terminal
pip install -r requirements.txt
python simple_terminal_v2.py
```

### Commands
- `A` - Add stock to watchlist
- `K` - Run market screener
- `V` - View performance metrics
- `B/S` - Buy/Sell with AI reasoning
- `1-9` - Detailed analysis with charts
- `Q` - Quit

### Trading Strategies
- Use the screener to find oversold stocks (RSI < 30)
- Monitor alerts for exit signals
- Track your win rate with performance view
- Let AI guide your decisions

### Disclaimer
For educational and simulation purposes only. Not financial advice.

### Credits
Built with Claude AI assistance for the ultimate trading experience.

---

**Windows Defender Note**: You may need to allow the app through Windows Defender on first run.
"""
    
    return release_notes

def create_github_cli_command():
    """Create GitHub CLI command for release"""
    
    commands = """
# GitHub Release Commands
# =======================

# 1. Create a new release with GitHub CLI (if installed)
gh release create v3.0 \\
  --title "Wall Street Terminal v3.0 - Professional Trading Terminal" \\
  --notes-file RELEASE_NOTES.md \\
  dist/WallStreetTerminal.exe

# 2. Or manually:
# - Go to: https://github.com/yourusername/wall-street-terminal/releases/new
# - Tag: v3.0
# - Title: Wall Street Terminal v3.0 - Professional Trading Terminal
# - Upload: dist/WallStreetTerminal.exe
# - Paste the release notes
# - Publish release

# 3. Update README download link after release:
# Change line 49 in README.md to point to your actual release URL
"""
    
    return commands

def main():
    """Main function"""
    print("Wall Street Terminal Release Preparation")
    print("=" * 50)
    
    # Check executable
    exe_path = Path("dist/WallStreetTerminal.exe")
    if exe_path.exists():
        print(f"[OK] Executable found: {exe_path}")
        print(f"   Size: {get_file_size(exe_path)}")
    else:
        print("[ERROR] Executable not found! Run: pyinstaller WallStreetTerminal.spec")
        return
    
    # Generate release notes
    release_notes = create_release_notes()
    
    # Save release notes
    with open("RELEASE_NOTES.md", "w") as f:
        f.write(release_notes)
    print("\n[OK] Created RELEASE_NOTES.md")
    
    # Save GitHub commands
    commands = create_github_cli_command()
    with open("GITHUB_RELEASE_COMMANDS.txt", "w") as f:
        f.write(commands)
    print("[OK] Created GITHUB_RELEASE_COMMANDS.txt")
    
    # Checklist
    print("\nRelease Checklist:")
    print("1. [ ] Review RELEASE_NOTES.md")
    print("2. [ ] Check exe is in dist/ folder")
    print("3. [ ] Push all changes to GitHub")
    print("4. [ ] Create release on GitHub")
    print("5. [ ] Update README with actual release URL")
    print("6. [ ] Test download link")
    
    print("\nReady to release! Follow the checklist above.")
    print("\nTip: Use GitHub CLI or web interface to create the release")

if __name__ == "__main__":
    main()