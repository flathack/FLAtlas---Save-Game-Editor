# FL Atlas - Savegame Editor

## Current Status (v0.1.0)
- Standalone savegame editor is running with menu bar, path settings, language switch, theme switch, and help menu.
- Savegame load/save flow is stable with backup creation (`.FLAtlasBAK`) and delayed write-until-save behavior.
- Map tabs (`Locked Gates`, `Visited`) are integrated and theme-aware.
- Reputation tab includes template application and neutral template.
- Ship tab includes hardpoint-aware filtering and AutoFix.
- `Check savegame` validates key sections and now also applies hardpoint AutoFix in the same action.
- Manual update check now always returns a result message (update available, up to date, or check failed).

## Open Issues
- Validation can still report many unresolved numeric IDs depending on mod data completeness and hash mapping coverage.
- Savegame safety checks should be expanded further for edge-case ship/equipment combinations.
- Some UI translations still need continuous review when new strings are added.

## Completed Since v0.1.0 Tag

### Added
- Help menu entries:
  - Quick Help
  - Check for Updates
  - Reset Program Config
- Config reset action removes local config file after confirmation.
- Explicit update-check feedback messages for manual checks.
- Theme-adaptive map palette for better contrast in light themes.

### Changed
- README updated to match current standalone scope and feature set.
- Savegame validation flow now includes automatic hardpoint cleanup.

### Fixed
- Dark map rendering on bright themes.
- Missing user feedback when no update was available.

## Next Release Goals (target: v0.1.1)
- Add optional strict pre-save validation mode with blocker warnings.
- Add clear validation result breakdown by category with counts.
- Add map legend (locked, visited, unknown) for both map tabs.
- Improve unresolved ID diagnostics to separate:
  - unknown in game data
  - known but unresolved display name

## Mid-Term Goals (v0.2.x)
- Add undo/redo for in-memory editing session.
- Add batch tools for cargo/equipment edits.
- Add compatibility presets for `Customize Trent`.

## Long-Term Goals
- Build clean standalone release bundles for Linux and Windows.
- Add optional crash-report helper export for reproducible bug reports.
