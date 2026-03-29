# Changelog

All notable changes to FLAtlas Savegame Editor are documented in this file.

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