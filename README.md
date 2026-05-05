# FLAtlas Savegame Editor

Standalone editor for **Freelancer** single-player savegames (`*.fl`).

The editor is built for vanilla Freelancer and modded installations. It focuses on safe save editing, readable game-data names, compatibility with encrypted saves, and visual tools for map, character, and ship changes.

Developed by **Aldenmar Odin - flathack**.

Current version: `v0.5.1`

## Features

- Open, inspect, edit, and save Freelancer savegames.
- Create a new savegame from scratch with default Trent body parts.
- Work with vanilla and modded game installations.
- Keep encrypted `FLS1` saves encrypted when saving again.
- Use automatic timestamped backups and restore previous snapshots.
- Preview pending changes before writing them to disk.
- Validate ships, equipment, cargo, factions, visited entries, and system/base values.
- Preserve incompatible or unknown entries instead of silently dropping them.
- Use translated UI text in German, English, Spanish, French, and Russian.
- Install updates from inside the editor.

## Editor Areas

### Visited

- Visual map of known and visited systems.
- Current player system marker.
- Tools to mark jump holes and jump gates as visited.
- Reveal tools for systems, visit-enabled objects, and visit-enabled zones.
- Map click workflow for moving the player ship to a system.

### Reputation

- Faction reputation table with live filtering.
- Template support for common reputation setups.
- Cleanup and validation tools.

### Trent

- Editable Trent body, head, left-hand, and right-hand parts.
- 3D character preview when the FLAtlas bridge preview modules are available.
- Costume-based saves are detected and kept read-only where needed so original `costume` and `com_costume` entries are preserved.

### Ship

- Editable ship archetype.
- Ship package templates from `goods.ini`.
- Core component editing.
- Hardpoint-aware equipment editing with invalid-hardpoint auto-fix support.
- Cargo editing.
- Compact player ship preview in the sidebar.

### Ship View

- Large ship preview for inspecting available ships from the configured game data.
- Works without a loaded savegame once a Freelancer installation is configured.
- Supports the same preview bridge used by the in-editor ship preview.

## Safety Model

The editor tries to keep savegame edits reversible and explicit.

Each save creates:

- `YourSave.fl.FLAtlasBAK`
- `YourSave.fl.FLAtlasBAK.YYYYMMDD_HHMMSS`

The restore dialog lists available backups and shows differences against the current file before restoring. Restoring a backup first snapshots the current state, so the restore operation itself remains reversible.

Story-related saves can be sensitive. The editor warns about risky `system` and `base` edits and keeps incompatible entries visible and read-only where possible.

## Requirements

- Python 3.10 or newer
- `PySide6`
- `pefile`
- `Pillow`
- `PyInstaller` for packaged builds

Install runtime dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run From Source

```bash
python start_savegame_editor.py
```

The launcher can re-execute itself with a local Python interpreter that already has `pefile` installed, which helps resolve IDS and in-game names.

Print the application version:

```bash
python start_savegame_editor.py --version
```

## Build

Install build dependencies:

```bash
python -m pip install -r requirements-build.txt
```

Build an onedir package:

```bash
python build.py --clean --mode onedir
```

Build a onefile package:

```bash
python build.py --clean --mode onefile
```

Build artifacts are written to `dist/`.

The build includes translations, icons, the splash image, and FLAtlas bridge modules used by the 3D previews. For onedir builds, the standalone updater is built and copied into the release folder when possible.

## Configuration

Local settings are stored outside the repository:

- Windows: `%APPDATA%\fl_editor\config.json`
- Linux: `~/.config/fl_editor/config.json`

Important settings include:

- `settings.savegame_path`
- `settings.savegame_game_path`
- `settings.savegame_recent_files`
- `settings.savegame_preserve_encryption`
- `settings.theme`
- `settings.language`

## Project Layout

- `start_savegame_editor.py` - source launcher.
- `fl_editor/` - application package.
- `fl_editor/savegame_editor.py` - main PySide6 editor UI and workflows.
- `fl_editor/parser.py`, `fl_editor/bini.py` - Freelancer INI and save parsing helpers.
- `fl_editor/translations.json` - UI translations.
- `build.py` - PyInstaller build helper.
- `HELP.de.md`, `HELP.en.md` - user help.
- `CHANGELOG.md` - release history.
- `ROADMAP.md` - planned work.

## Links

- Discord: <https://discord.gg/RENtMMcc>
- Issues: <https://github.com/flathack/FLAtlas---Save-Game-Editor/issues>
- Releases: <https://github.com/flathack/FLAtlas---Save-Game-Editor/releases>
