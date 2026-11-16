# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ZimbraViewer 3.2.py'],
    pathex=[],
    binaries=[('C:/Python315/abi3t-compat/python3t.dll', '.')],
    datas=[],
    hiddenimports=['PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'unittest', 'matplotlib', 'numpy', 'scipy', 'pandas', 'PIL'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ZimbraViewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=['zimbra_icon.ico'],
)
