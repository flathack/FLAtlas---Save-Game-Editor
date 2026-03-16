# FL Atlas - Savegame Editor

Standalone editor for **Freelancer** singleplayer save files (`*.fl`).

Developed by **Aldenmar Odin - flathack**.

## Version
- Current: `v0.2.0`

## Core Features
- Open and edit Freelancer savegames with `filename - in-game name` display
- Works with vanilla Freelancer and modded installs
- Fast startup with lazy loading of game data
- `Open Recent` workflow for previously used savegames
- `Save As...` support for branch saves and experiments
- **Create new savegame from scratch** with default Trent body parts
- Safe save workflow with automatic backup history
- Built-in backup restore dialog with backup list and diff preview
- Story-save protection for risky `system` / `base` edits
- Encrypted `FLS1` saves stay encrypted by default when saved again
- Better compatibility handling for foreign or partially incompatible saves
- **Auto updater** — download and install updates directly from within the editor

## Editor Tabs
- `Visited`
  - visited map comes first
  - current player system is marked with a red dot
  - `Mark all JH/JG as visited`
  - `Reveal everything` for systems, visit-enabled objects, and visit-enabled zones
- `Locked Gates`
  - visualize and clear locked jump connections
- `Reputation`
  - faction reputation table
  - template support
  - cleanup and validation support
- `Trent`
  - editable Trent appearance parts
  - costume-based saves are detected and kept read-only to preserve original `costume` / `com_costume` entries
- `Ship`
  - ship archetype
  - **ship templates** — apply pre-configured ship packages from `goods.ini`
  - subtabs for `Core Components`, `Equip Entries`, and `Cargo Entries`
  - core equipment
  - hardpoint-aware equipment editing
  - cargo editing
  - live filters for equipment, cargo, and faction tables

## Validation and Safety
- `Check savegame` validates:
  - ships
  - equipment
  - cargo
  - factions
  - system/base
  - visited entries
- hardpoint auto-fix is available for invalid equipment assignments
- save preview shows a compact list of pending changes before write
- plain-text save writing preserves file formatting correctly
- every save creates a new timestamped backup snapshot
- incompatible numeric IDs stay visible in the UI instead of breaking the load flow
- incompatible entries are shown as locked/read-only and are preserved on save
- a visible compatibility warning is shown when the loaded save does not fully match the configured game data
- a visible encryption notice shows whether the current save is encrypted and whether it will be saved encrypted again

## Backup Workflow
- Each save creates:
  - latest alias: `YourSave.fl.FLAtlasBAK`
  - history snapshot: `YourSave.fl.FLAtlasBAK.YYYYMMDD_HHMMSS`
- `Restore Backup` opens a dialog with:
  - left side: available backups
  - right side: differences to the current save
- restoring a backup preserves the current state as a new history snapshot first

## UI / UX
- conventional menu structure:
  - `File`
  - `Edit`
  - `View`
  - `Tools`
  - `Help`
- refined `About` dialog using `icon.png`
- improved update dialogs with clearer status states
- hidden technical saves are excluded from picker lists:
  - `Restart.fl`
  - `AutoSave.fl`
  - `AutoStart.fl`
- translations available for:
  - `de`
  - `en`
  - `es`
  - `fr`
  - `ru`
- Online Help (Wiki) accessible directly from the Help menu
- Complete help documentation available in German and English

## Requirements
- Python 3.10+
- PySide6
- `pefile`
- PyInstaller for packaged builds

## Start
```bash
python start_savegame_editor.py
```

The launcher can re-exec with a Python interpreter that already has `pefile` available.

## Build
This project includes a complete PyInstaller setup for Windows and Linux.

Relevant files:
- `requirements-build.txt`
- `build.py`
- `savegame_editor.spec`
- `build.bat`
- `build.sh`

Install build dependencies:
```bash
python -m pip install -r requirements-build.txt
```

Build onedir package:
```bash
python build.py --clean --mode onedir
```

Build onefile package:
```bash
python build.py --clean --mode onefile
```

Artifacts are written to:
- `dist/`

Included build assets:
- `fl_editor/translations.json`
- `fl_editor/images/icon.png`
- `fl_editor/images/icon.ico`
- `fl_editor/images/splash.png`

## Configuration
Local config file:
- Windows: `%APPDATA%\\fl_editor\\config.json`
- Linux: `~/.config/fl_editor/config.json`

Relevant settings:
- `settings.savegame_path`
- `settings.savegame_game_path`
- `settings.savegame_recent_files`
- `settings.savegame_preserve_encryption`
- `settings.theme`
- `settings.language`

## Notes
- Savegame changes are written only when clicking `Save`
- Story-related saves can still be sensitive; keep original backups for major edits
- Backup history can grow over time; prune old snapshots manually if needed

## Links
- Discord: https://discord.gg/RENtMMcc
- Report bugs: https://github.com/flathack/FLAtlas---Save-Game-Editor/issues
- Releases: https://github.com/flathack/FLAtlas---Save-Game-Editor/releases
