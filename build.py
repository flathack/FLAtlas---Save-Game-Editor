#!/usr/bin/env python3
"""Build helper for FLAtlas Savegame Editor (PyInstaller)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
ENTRYPOINT = PROJECT_ROOT / "start_savegame_editor.py"
UPDATER_SCRIPT = PROJECT_ROOT / "fleditor_updater.py"
ICON_FILE = PROJECT_ROOT / "fl_editor" / "images" / "icon.png"
ICON_ICO_FILE = PROJECT_ROOT / "fl_editor" / "images" / "icon.ico"
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


def _detect_version() -> str:
    ns: dict[str, object] = {}
    code = ENTRYPOINT.read_text(encoding="utf-8")
    exec(compile(code, str(ENTRYPOINT), "exec"), ns, ns)
    ver = str(ns.get("APP_VERSION", "") or "").strip()
    return ver or "v0.0.0"


def _ensure_clean_dirs() -> None:
    for name in ("build", "dist"):
        p = PROJECT_ROOT / name
        if p.exists():
            shutil.rmtree(p)


def _build_data_args(sep: str) -> list[str]:
    data_files = [
        PROJECT_ROOT / "fl_editor" / "translations.json",
        PROJECT_ROOT / "fl_editor" / "images" / "icon.png",
        PROJECT_ROOT / "fl_editor" / "images" / "splash.png",
    ]
    if ICON_ICO_FILE.exists():
        data_files.append(ICON_ICO_FILE)
    args: list[str] = []
    for path in data_files:
        target = "fl_editor" if path.name == "translations.json" else "fl_editor/images"
        args.extend(["--add-data", f"{path}{sep}{target}"])
    for module_name in BRIDGE_MODULE_FILES:
        module_path = BRIDGE_SOURCE_ROOT / module_name
        if not module_path.exists():
            raise FileNotFoundError(f"Required FLAtlas bridge module not found: {module_path}")
        args.extend(["--add-data", f"{module_path}{sep}_flatlas_bridge/fl_editor"])
    return args


def _assert_no_config_in_dist(dist_path: Path, app_name: str) -> None:
    package_root = dist_path / app_name
    if not package_root.exists():
        return
    blocked_names = {
        "config.json",
        ".fl_editor",
        "fl_editor.ini",
    }
    blocked_parts = {
        "appdata",
        ".config",
    }
    bad_paths: list[Path] = []
    for path in package_root.rglob("*"):
        low_name = path.name.lower()
        low_parts = {part.lower() for part in path.parts}
        if low_name in blocked_names or blocked_parts.intersection(low_parts):
            bad_paths.append(path)
    if bad_paths:
        lines = "\n".join(str(p) for p in bad_paths[:20])
        raise RuntimeError(f"Build contains config artifacts and is not releasable:\n{lines}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Build FLAtlas Savegame Editor")
    ap.add_argument(
        "--mode",
        choices=("onedir", "onefile"),
        default="onedir",
        help="PyInstaller packaging mode (default: onedir)",
    )
    ap.add_argument(
        "--clean",
        action="store_true",
        help="Delete previous build/dist before building",
    )
    args = ap.parse_args()

    if not ENTRYPOINT.exists():
        print(f"Entrypoint not found: {ENTRYPOINT}", file=sys.stderr)
        return 2

    version = _detect_version()
    app_name = f"FLAtlas-Savegame-Editor-{version}"

    if args.clean:
        _ensure_clean_dirs()

    sep = ";" if sys.platform.startswith("win") else ":"
    pyinstaller_cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name",
        app_name,
        "--hidden-import",
        "pefile",
        "--hidden-import",
        "PySide6.Qt3DExtras",
        "--windowed",
    ]
    pyinstaller_cmd.extend(_build_data_args(sep))
    icon_for_exe: Path | None = None
    if sys.platform.startswith("win"):
        if ICON_ICO_FILE.exists():
            icon_for_exe = ICON_ICO_FILE
    elif ICON_FILE.exists():
        icon_for_exe = ICON_FILE
    if icon_for_exe is not None:
        pyinstaller_cmd.extend(["--icon", str(icon_for_exe)])
    if args.mode == "onefile":
        pyinstaller_cmd.append("--onefile")
    else:
        pyinstaller_cmd.append("--onedir")
    pyinstaller_cmd.extend([str(ENTRYPOINT)])

    print("Running:", " ".join(pyinstaller_cmd))
    proc = subprocess.run(pyinstaller_cmd, cwd=str(PROJECT_ROOT))
    if proc.returncode != 0:
        return proc.returncode

    # Build the standalone updater exe
    if UPDATER_SCRIPT.exists() and args.mode == "onedir":
        updater_cmd = [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--clean",
            "--name",
            "FLEditorUpdater",
            "--onefile",
            "--windowed",
        ]
        if icon_for_exe is not None:
            updater_cmd.extend(["--icon", str(icon_for_exe)])
        updater_cmd.append(str(UPDATER_SCRIPT))
        print("Building updater:", " ".join(updater_cmd))
        proc2 = subprocess.run(updater_cmd, cwd=str(PROJECT_ROOT))
        if proc2.returncode != 0:
            print("Warning: updater build failed", file=sys.stderr)
        else:
            updater_exe = PROJECT_ROOT / "dist" / "FLEditorUpdater.exe"
            target_dir = PROJECT_ROOT / "dist" / app_name
            if updater_exe.exists() and target_dir.exists():
                shutil.copy2(updater_exe, target_dir / "FLEditorUpdater.exe")
                print(f"Updater copied to {target_dir / 'FLEditorUpdater.exe'}")

    dist_path = PROJECT_ROOT / "dist"
    _assert_no_config_in_dist(dist_path, app_name)
    print(f"Build completed: {dist_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
