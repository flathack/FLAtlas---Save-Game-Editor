# FL Atlas - Savegame Editor Roadmap

## Current Status (v0.1.2)
- Standalone savegame editor is stable with:
  - conventional menu bar
  - path settings
  - language and theme switching
  - refined About and Update dialogs
- Save workflow includes:
  - Save
  - Save As
  - recent savegames
  - timestamped backup history
  - restore dialog with backup list and diff preview
- Map tooling includes:
  - visited map first
  - current system marker
  - reveal-all visit support
  - locked gate tools
- Startup is faster because game data loads lazily.
- Story-save protection blocks risky system/base writes conservatively.

## Release Readiness
- Packaging assets are present:
  - `icon.png`
  - `icon.ico`
  - `splash.png`
  - `translations.json`
- PyInstaller build scripts exist for Windows and Linux.
- Current priority is stabilizing the new backup-history workflow under large savegames.

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

## Next Release Goals (v0.1.3)
- Undo/Redo for the in-memory editing session
- Better search/filter support for combo-heavy editors
- Clearer diff preview before save with categorized sections
- Improved backup restore preview for large files
- Additional DE/EN translation cleanup

## Mid-Term Goals (v0.2.x)
- Batch tools for cargo and equipment edits
- Savegame compare mode between two `.fl` files
- Safer advanced relocation workflow for non-story saves
- Optional background loading for expensive editor lookups
- Better validation diagnostics for unresolved numeric IDs

## Long-Term Goals
- Exportable crash-report package for bug reports
- Automated release pipeline for Windows and Linux artifacts
- Backup browser with metadata and restore points
- Expert mode for advanced save manipulation with stronger guardrails
