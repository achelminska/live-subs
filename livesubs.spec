# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for LiveSubs — run: tools/build.ps1

from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_data_files

project_root = Path(SPECPATH)

extra_datas = []
extra_binaries = []
extra_hiddenimports = []

for pkg in (
    "ctranslate2",
    "faster_whisper",
    "av",
    "onnxruntime",
    "pyaudiowpatch",
    "huggingface_hub",
    "tokenizers",
    "certifi",
):
    datas, binaries, hiddenimports = collect_all(pkg)
    extra_datas += datas
    extra_binaries += binaries
    extra_hiddenimports += hiddenimports

a = Analysis(
    [str(project_root / "main.py")],
    pathex=[str(project_root)],
    binaries=extra_binaries,
    datas=[
        (str(project_root / "icon.ico"), "."),
        (str(project_root / "assets" / "icon.png"), "assets"),
        (str(project_root / ".env.example"), "."),
        *extra_datas,
        *collect_data_files("certifi"),
    ],
    hiddenimports=[
        "pyaudiowpatch",
        "faster_whisper",
        "faster_whisper.assets",
        "ctranslate2",
        "av",
        "av.audio",
        "av.codec",
        "av.container",
        "onnxruntime",
        "deepl",
        "dotenv",
        "numpy",
        "huggingface_hub",
        "tokenizers",
        "certifi",
        "PyQt6.QtCore",
        "PyQt6.QtGui",
        "PyQt6.QtWidgets",
        *extra_hiddenimports,
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
