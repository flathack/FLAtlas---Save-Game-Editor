# FL Atlas - Savegame Editor Roadmap

## Current Status (v0.2.0)
- Standalone savegame editor is stable with:
  - conventional menu bar
  - path settings
  - language and theme switching
  - refined About and Update dialogs
  - Online Help (Wiki) link in Help menu
- Save workflow includes:
  - Save
  - Save As
  - recent savegames
  - timestamped backup history
  - restore dialog with backup list and diff preview
  - **create new savegame from scratch** with default Trent body parts
- Map tooling includes:
  - visited map first
  - current system marker
  - reveal-all visit support
  - locked gate tools
- Ship editing:
  - dedicated core/equip/cargo subtabs
  - **ship templates** from `goods.ini` `_package` entries
  - apply pre-configured ship setups with one click
- Startup is faster because game data loads lazily.
- Story-save protection blocks risky system/base writes conservatively.
- Better search/filter support is available across combo-heavy editors.
- Backup restore preview is more resilient on very large savegames.
- Incompatible save entries stay visible as locked read-only rows instead of breaking the editor.
- Incompatible `rep_group` values are preserved when applying reputation templates.
- Encrypted `FLS1` saves are preserved by default and shown with an in-editor notice.
- Costume-based Trent saves stay in their original format and lock Trent customization safely.
- Locked-gate handling now keeps `[locked_gates]` / `npc_locked_gate` data out of the writable `[Player]` lock list.
- **Auto-updater** downloads and installs updates directly from within the packaged Windows version.
- Complete help documentation available in German and English.

## Release Readiness
- Packaging assets are present:
  - `icon.png`
  - `icon.ico`
  - `splash.png`
  - `translations.json`
- PyInstaller build scripts exist for Windows and Linux.
- Build script compiles standalone updater (`FLEditorUpdater.exe`) alongside the main application.

## High Priority
- Move backup diff generation fully off the UI thread for very large saves.
- Add retention settings for backup history:
  - keep last N backups
  - optional manual cleanup action
- Add a dedicated restore confirmation step summarizing:
  - selected backup timestamp
  - diff size
  - current file that will be replaced
- Tighten save safety around location-sensitive fields beyond system/base if needed.

## Next Release Goals (v0.2.1)
- Undo/Redo for the in-memory editing session
- Clearer diff preview before save with categorized sections
- Regression coverage for savegame lock/visit serialization
- Stronger guardrails for map actions that should not rewrite read-only lock sections

## Mid-Term Goals (v0.3.x)
- Batch tools for cargo and equipment edits
- Savegame compare mode between two `.fl` files

## Long-Term Goals
- Exportable crash-report package for bug reports
- Automated release pipeline for Windows and Linux artifacts
- Backup browser with metadata and restore points

