"""FLAtlas Savegame Editor standalone updater.

This script is compiled to FLEditorUpdater.exe and shipped alongside the main
application.  After the user downloads a new release, the main app spawns this
process, exits, and the updater waits for the main PID to terminate before
copying files and relaunching.

Usage (invoked programmatically by FLAtlas Savegame Editor):
    FLEditorUpdater.exe --mode zip|installer --wait-pid <PID>
        --install-root <dir> --archive-path <file> --exe-path <exe>
        [--extract-root <dir>]
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
DETACHED_PROCESS = getattr(subprocess, "DETACHED_PROCESS", 0)
MB_TOPMOST = 0x00040000
MB_SETFOREGROUND = 0x00010000


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _message_box(text: str, title: str = "FLAtlas Savegame Editor Update", flags: int = 0x40) -> None:
    """Show a Win32 MessageBox (best-effort, silent fail on non-Windows)."""
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(None, str(text), str(title), int(flags) | MB_TOPMOST | MB_SETFOREGROUND)
    except Exception:
        pass


def _pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        result = subprocess.run(
            ["tasklist", "/FI", f"PID eq {int(pid)}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            creationflags=CREATE_NO_WINDOW,
            timeout=5,
        )
        output = ((result.stdout or "") + "\n" + (result.stderr or "")).lower()
        if "no tasks" in output or "keine aufgaben" in output:
            return False
        return f'"{int(pid)}"' in output or f",{int(pid)}," in output or f" {int(pid)} " in output
    except Exception:
        return False


def _wait_for_pid(pid: int, timeout_seconds: float) -> bool:
    """Block until *pid* disappears from the process list. Return True when gone."""
    if pid <= 0:
        return True
    deadline = time.time() + max(1.0, float(timeout_seconds))
    while time.time() < deadline:
        if not _pid_exists(pid):
            return True
        time.sleep(0.5)
    return not _pid_exists(pid)


def _terminate_pid_tree(pid: int) -> None:
    if pid <= 0 or not _pid_exists(pid):
        return
    try:
        subprocess.run(
            ["taskkill", "/PID", str(int(pid)), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW,
            timeout=15,
        )
    except Exception:
        pass


def _resolve_source_root(extract_root: Path) -> Path:
    """If the archive had a single top-level folder, step into it."""
    entries = [p for p in extract_root.iterdir()]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_root


def _copy_tree_contents(src: Path, dst: Path) -> None:
    """Recursively copy *src* contents into *dst*."""
    dst.mkdir(parents=True, exist_ok=True)
    for child in src.iterdir():
        target = dst / child.name
        if child.is_dir():
            shutil.copytree(child, target, dirs_exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(child, target)


def _apply_zip_update(install_root: Path, extract_root: Path) -> None:
    source_root = _resolve_source_root(extract_root)
    _copy_tree_contents(source_root, install_root)


def _launch_exe(exe_path: Path, workdir: Path) -> bool:
    if not exe_path.exists():
        return False
    try:
        subprocess.Popen(
            [str(exe_path)],
            cwd=str(workdir),
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
            close_fds=True,
        )
        return True
    except Exception:
        return False


def _launch_installer(installer_path: Path) -> bool:
    if not installer_path.exists():
        return False
    try:
        subprocess.Popen(
            [str(installer_path)],
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
            close_fds=True,
        )
        return True
    except Exception:
        return False


def _cleanup(paths: list[Path]) -> None:
    for path in paths:
        try:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists():
                path.unlink()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("zip", "installer"), required=True)
    parser.add_argument("--wait-pid", type=int, default=0)
    parser.add_argument("--install-root", required=True)
    parser.add_argument("--extract-root", default="")
    parser.add_argument("--archive-path", required=True)
    parser.add_argument("--exe-path", required=True)
    args = parser.parse_args(argv)

    install_root = Path(args.install_root).resolve()
    extract_root = Path(args.extract_root).resolve() if args.extract_root else None
    archive_path = Path(args.archive_path).resolve()
    exe_path = Path(args.exe_path).resolve()

    wait_pid = int(args.wait_pid)
    if not _wait_for_pid(wait_pid, 12.0):
        _terminate_pid_tree(wait_pid)
        _wait_for_pid(wait_pid, 30.0)
    time.sleep(0.8)

    try:
        if args.mode == "installer":
            started = _launch_installer(archive_path)
            if not started:
                _message_box(
                    "FLAtlas Savegame Editor konnte das Update-Installationsprogramm nicht starten.\n"
                    "Bitte fuehre das heruntergeladene Update manuell aus."
                )
                return 1
            return 0

        if extract_root is None or not extract_root.exists():
            raise RuntimeError("Extract root is missing")
        _apply_zip_update(install_root, extract_root)
        time.sleep(1.0)
        started = _launch_exe(exe_path, install_root)
        if not started:
            _message_box(
                "FLAtlas Savegame Editor wurde aktualisiert.\n"
                "Bitte starte das Programm manuell neu."
            )
            return 2
        return 0
    except Exception as exc:
        _message_box(f"FLAtlas Savegame Editor Update fehlgeschlagen.\n\n{exc}", flags=0x10)
        return 1
    finally:
        cleanup_paths: list[Path] = [archive_path]
        if extract_root is not None:
            cleanup_paths.append(extract_root)
        _cleanup(cleanup_paths)


if __name__ == "__main__":
    sys.exit(main())
