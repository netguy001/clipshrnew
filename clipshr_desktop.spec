# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['clipshr_desktop.py'],
    pathex=[],
    # Add config.json file to the package
    datas=[('config.json', '.')], 
    hiddenimports=[
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'PyQt5',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'subprocess',
        'json',
        'pathlib',
        'datetime',
        'urllib.request', # Added for thumbnail download
        'io',             # Added for thumbnail processing
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='ClipShr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window - pure desktop app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)