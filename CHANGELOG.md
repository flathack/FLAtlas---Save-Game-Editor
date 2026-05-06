# Changelog

All notable changes to FLAtlas Savegame Editor are documented in this file.

## v0.6.1 - 2026-05-06

### Improvements
- Added Multiverse sector tabs to the universe map for mods with multiple map sectors.
- Restored stable Trent 3D preview coloring with a thin mesh overlay fallback.
- Updated Discord and issue tracker links.

### Bug Fixes
- Fixed a startup crash in the universe map sector tab initialization.
- Prevented story-locked savegames from changing systems via the universe map.
- Fixed Trent 3D texture/material loading crashes on affected Qt3D/RHI setups.

## v0.6.0 - 2026-05-05

### New Features
- Added an architecture-aware auto-updater that selects the matching release asset for Windows, Linux, x64, ARM64, and ARM targets.
- Added direct update downloads from the update dialog, while preserving the existing Windows self-update flow for packaged builds.
- Added a green `Launch Freelancer` button next to Save that uses the configured game path.

### Improvements
- Optimized startup by delaying game data loading, savegame name resolving, update checks, and 3D preview initialization until after the first window is visible.
- Made the 3D preview load on demand instead of automatically during savegame loading.
- Added a Qt3D runtime safety probe before loading 3D previews to avoid native crashes on affected Python/Qt setups.
- Kept the SWAT BlackOps theme as the default and refined compact editor UI behavior.

### Bug Fixes
- Fixed savegame loading crashes caused by automatic 3D preview initialization.
- Fixed update asset selection so Linux and ARM builds are not confused with Windows x64 packages.
- Fixed several 3D preview rendering issues around double-sided ship geometry and wireframe visibility.
- Fixed universe map interaction and player position coloring.

## v0.5.2 - 2026-05-05

### Improvements
- Updated the app icon and splash screen with the Anubis shield artwork.
- Improved standalone startup when launched from another project's Python environment.

### Bug Fixes
- Disabled the Qt3D preview during standalone startup to avoid native Qt crashes on affected environments.

## v0.5.1 - 2026-03-30

### Improvements
- Updated the Windows release package for v0.5.1.

### Bug Fixes
- Fixed packaged Trent 3D preview startup failures caused by a missing `PySide6.Qt3DExtras` runtime dependency.
- Fixed `FLAtlas bridge offline` in the standalone Windows build when opening the Trent Character preview.

## v0.5.0 - 2026-03-29

### New Features
- Added a dedicated Ship View tab with large 3D preview support for ship inspection.
- Added a compact player ship 3D preview in the sidebar.
- Ship View now works even without a loaded savegame by loading ship data directly from the configured game installation.
- Added fixed light and dark theme handling for the 3D preview widgets, including the Trent preview and ship previews.
- Improved the editor workflow around ship editing, preview visibility, and no-savegame browsing.

### Improvements
- Updated the Windows release package and release metadata for v0.5.0.
- Improved ship preview presentation with flat shaded rendering and wireframe overlay support.
- Improved tab behavior so ship-related preview tools remain accessible while editing loaded savegames.
- Refined menu bar integration for more reliable startup behavior on Windows.

### Bug Fixes
- Fixed missing ship geometry in the preview caused by incomplete Qt3D vertex attribute layouts on DirectX.
- Fixed repeated Qt3D input-layout and graphics-pipeline creation failures by adding normals to shared preview geometry and wireframe renderers.
- Fixed ship hull faces appearing transparent from one side by rendering ship preview geometry double-sided where needed.
- Fixed the Ship View dropdown sometimes appearing empty when no savegame was loaded.
- Fixed 3D previews not updating correctly when the application theme changed.
- Fixed cases where the menu bar could fail to appear on startup.
- Fixed several ship preview rendering regressions around wireframe visibility and preview refresh behavior.
