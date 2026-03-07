# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ICON_ICO = PROJECT_ROOT / "fl_editor" / "images" / "icon.ico"
ICON_PNG = PROJECT_ROOT / "fl_editor" / "images" / "icon.png"

datas = [
    (str(PROJECT_ROOT / "fl_editor" / "translations.json"), "fl_editor"),
    (str(PROJECT_ROOT / "fl_editor" / "images" / "icon.png"), "fl_editor/images"),
    (str(PROJECT_ROOT / "fl_editor" / "images" / "splash.png"), "fl_editor/images"),
]
if ICON_ICO.exists():
    datas.append((str(ICON_ICO), "fl_editor/images"))

hiddenimports = [
    "pefile",
]

a = Analysis(
    ["start_savegame_editor.py"],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="FLAtlas-Savegame-Editor",
    icon=str(ICON_ICO if ICON_ICO.exists() else ICON_PNG if ICON_PNG.exists() else ""),
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="FLAtlas-Savegame-Editor",
)
