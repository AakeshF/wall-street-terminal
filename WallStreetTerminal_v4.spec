# -*- mode: python ; coding: utf-8 -*-
"""
Wall Street Terminal v4.0 PyInstaller Spec File
===============================================
Creates a standalone windowed application with Textual
"""

import sys
from pathlib import Path

block_cipher = None

# Get the absolute path to the project
project_dir = Path.cwd()

a = Analysis(
    ['main_app_launcher.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        # Include data files
        ('screener_list.json', '.'),
        ('.env.example', '.'),
        ('README.md', '.'),
        # Include watchlist and portfolio if they exist
        ('watchlist.json', '.'),
        ('portfolio.json', '.'),
    ],
    hiddenimports=[
        # Core dependencies
        'dotenv',
        'aiohttp',
        'anthropic',
        'numpy',
        'colorama',
        'asyncio',
        'json',
        'dataclasses',
        'pathlib',
        # Textual and rich
        'textual',
        'textual.app',
        'textual.widgets',
        'textual.containers',
        'textual.screen',
        'textual.reactive',
        'textual.css',
        'rich',
        'rich.text',
        'rich.table',
        'rich.console',
        'rich.markup',
        'markdown_it',
        'pygments',
        # Our modules
        'cache_manager',
        'data_fetcher',
        'ai_analyzer',
        'portfolio_manager',
        'market_screener',
        'visualizer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude test files
        'test_*',
        'simple_curses_test',
        # Exclude legacy code
        '_legacy_code',
        'simple_terminal_v2',
        # Exclude git files
        '.git',
        # Exclude build artifacts
        'build',
        'dist',
        '__pycache__',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WallStreetTerminal_v4',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Textual requires a console on Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add an icon file if you want
    version_file=None,
)

# Optional: Create a folder distribution instead of single file
# Uncomment below if you prefer folder distribution
"""
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WallStreetTerminal_v4',
)
"""