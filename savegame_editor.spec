# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ICON_ICO = PROJECT_ROOT / "fl_editor" / "images" / "icon.ico"
ICON_PNG = PROJECT_ROOT / "fl_editor" / "images" / "icon.png"
BRIDGE_SOURCE_ROOT = PROJECT_ROOT.parent / "FLAtlas" / "fl_editor"
BRIDGE_MODULE_FILES = (
    "freelancer_mesh_data.py",
    "cmp_orientation_debug.py",
    "qt3d_compat.py",
    "native_preview_style.py",
    "cmp_loader.py",
    "mat_texture_loader.py",
    "native_preview_materials.py",
    "native_preview_geometry.py",
    "native_preview_scene_data.py",
    "native_preview_qt3d.py",
)

datas = [
    (str(PROJECT_ROOT / "fl_editor" / "translations.json"), "fl_editor"),
    (str(PROJECT_ROOT / "fl_editor" / "images" / "icon.png"), "fl_editor/images"),
    (str(PROJECT_ROOT / "fl_editor" / "images" / "splash.png"), "fl_editor/images"),
]
if ICON_ICO.exists():
    datas.append((str(ICON_ICO), "fl_editor/images"))
for module_name in BRIDGE_MODULE_FILES:
    module_path = BRIDGE_SOURCE_ROOT / module_name
    if not module_path.exists():
        raise FileNotFoundError(f"Required FLAtlas bridge module not found: {module_path}")
    datas.append((str(module_path), "_flatlas_bridge/fl_editor"))

hiddenimports = [
    "pefile",
    "PySide6.Qt3DExtras",
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
