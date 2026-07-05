# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for LiveSubs — run: tools/build.ps1

from pathlib import Path

project_root = Path(SPECPATH)

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(project_root / "icon.ico"), "."),
        (str(project_root / "assets" / "icon.png"), "assets"),
        (str(project_root / ".env.example"), "."),
    ],
    hiddenimports=[
        "pyaudiowpatch",
        "faster_whisper",
        "faster_whisper.assets",
        "ctranslate2",
        "av",
        "av.audio",
        "onnxruntime",
        "deepl",
        "dotenv",
        "numpy",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="LiveSubs",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / "icon.ico"),
)
