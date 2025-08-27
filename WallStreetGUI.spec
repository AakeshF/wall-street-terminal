# -*- mode: python ; coding: utf-8 -*-
"""
Wall Street Terminal GUI - PyInstaller Spec
===========================================
Creates a true Windows GUI application with no console
"""

import sys
from pathlib import Path

block_cipher = None

# Get the absolute path to the project
project_dir = Path.cwd()

a = Analysis(
    ['gui_app.py'],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[
        # Include data files
        ('screener_list.json', '.'),
        ('.env.example', '.'),
        ('watchlist.json', '.'),
        ('portfolio.json', '.'),
        # You can add an icon file here if you have one
        # ('icon.ico', '.'),
    ],
    hiddenimports=[
        # Core dependencies
        'dotenv',
        'aiohttp',
        'anthropic',
        'numpy',
        'asyncio',
        'json',
        'dataclasses',
        'pathlib',
        'decimal',
        'threading',
        # Tkinter (usually included automatically)
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
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
        # Exclude unnecessary modules
        'matplotlib',  # Not using charts yet
        'pandas',      # Not needed
        'scipy',       # Not needed
        # Exclude test files
        'test_*',
        # Exclude other apps
        'main_app',
        'simple_terminal_v2',
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
    name='WallStreetTerminal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # FALSE = No console window! True GUI app!
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Uncomment and add path to icon file
    version_file=None,
    uac_admin=False,
    uac_uiaccess=False,
)

# Optional: If you want app info
"""
# Create version info file first:
# pyi-makespec --version-file version.txt gui_app.py

# version.txt example:
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Wall Street Terminal'),
        StringStruct(u'FileDescription', u'Professional Stock Trading Application'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'WallStreetTerminal'),
        StringStruct(u'LegalCopyright', u'Copyright 2024'),
        StringStruct(u'OriginalFilename', u'WallStreetTerminal.exe'),
        StringStruct(u'ProductName', u'Wall Street Terminal'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""