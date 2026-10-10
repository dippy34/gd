# v8 — restored spider and wall-orb revision

- Both spider sections retain the original crossing lines, false shelves and false openings: 385 fakeout designs, copied without alteration.
- Restored all 34 randomized wall decisions. Hit the circular white orb when a wall exists; skip it when no wall exists. The underlying square trigger-orb sprite is invisible, replaced by a dim circular ring and dot.
- Removed 66 isolated rectangular plates/recesses and their old movement. Camera markers and all hidden activation objects receive explicit zero opacity.
- Visible portals have normal proportions. Forced passages and invisible activation regions enforce them; no stretched portal sprite is displayed.
- Added 84 copper/violet inlays attached to existing solid structures, with small moving contact lights. No new decoration has collision.

Internal name **v8**; song **1573528**; length **3:25.19**. All seven requested modes, the two other blind branches, slightly tightened timings and eased wave clearance remain.

Validation: all 34 random-switch truth tables pass, as do 49,408 reference-route samples and approximate input replays for all 15 rooms. The audit checks spider artwork identity, hidden square sprites, visible portal proportions, barrier coverage and moving-detail bounds. See the validation JSON for native import status. Full native completion and an exact demon rating remain unverified.

References: [RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf), [GD Creator School object settings](https://github.com/GDCreatorSchool/gdcs2/blob/main/content/docs/guides/the-editor/editing-objects.md). The sprite comparison was made against the installed game's native atlas.
