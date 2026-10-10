# v8 — size, camera, ship and structure fixes

[Final .gmd](v8-1573528-refined.gmd) · [Native opening screenshot](v8-1573528-refined-native-preview.png) · [Section previews](v8-1573528-refined-preview.png) · [Validation](v8-1573528-refined-validation.json)

This revises the existing accepted level. The internal name remains **v8**, with song **1573528**, a **3:25.19** duration, seven modes excluding swing, and native 0.5× speed for **85.71%** of the level. Previous .gmd files are preserved.

- **Preserved gameplay:** all thirteen non-ship sections keep the same gameplay objects and input timings, with size portals corrected separately. This includes the opening cube, orb arrangements, memory decisions, speed schedule and section order.
- **Fixed size state:** the earlier generator reversed normal-size portal 99 and mini portal 101; its checker repeated the same error. Both are corrected. Wave exits and room transitions explicitly restore normal size. The second wave now follows normal → mini → normal → mini → normal, matching its intended wave slopes.
- **Harder ships:** PARALLAX and UNDERTOW now use different continuous, spike-lined flight contours, replacing broad galleries and bypassable floating dividers. Their wall shapes demand controlled climbs, dives and height changes. This is a geometric difficulty increase; the exact demon rating remains unverified.
- **Camera correction:** free-camera, zoom and vertical lock are refreshed after each mode entry. The separate native probe reproduced a 67.5-pixel vertical shift at ship entry, then confirmed matching reference positions in ship and wave after the correction. The entire y = 0–300 playfield fits in the tested view. The final opening was also inspected in Geometry Dash.
- **Purposeful structures:** suspended platforms have columns or ceiling supports; precision caps form piston heads; rail and spider shelves sit inside connected housings; the second wave's blades share continuous backing and lane-change supports. False routes retain the same visual construction as real routes. Small service plates move inside wall recesses. Existing collision faces remain aligned with their visible skins.

The empty level shown during testing was **v8 CAMERA TEST**, a separate diagnostic copy. It is not the final artifact.

## Checks

- Native import succeeded with **21,228 objects**. The native snapshot matches all exported object ID counts, size portals and camera settings.
- A continuous size-state trace passes **49,395 route samples** and all **36 required orb inputs**. The same check rejects the earlier file's size-state bug.
- Serialized second-wave portal order is checked independently of the generator constants.
- Approximate input replay and finite-body geometry checks pass all fifteen rooms, with no nominal block/spike overlaps.
- All **1,851 spikes** lie within the designed playfield. All forty memory choices still affect real gates.
- The first cube and the other twelve non-ship gameplay scores match the previous version.

**Full native completion and an Insane/Extreme difficulty rating are not verified.** Ship/UFO/ball dynamics and exact portal contact offsets remain approximate in the replay model. Native visual checks used the existing Ignore Damage setting.

## Research used for the corrections

- [G.js native object constants](https://github.com/g-js-api/G.js/blob/main/src/constants.ts): normal and mini portal IDs.
- [G.js camera implementation](https://github.com/g-js-api/G.js/blob/main/src/lib/general-purpose.ts): free camera, static vertical targets and zoom properties.
- [GD player-physics reference](https://boomlings.dev/reference/player_physics/gamemodes): mode behaviour and the limits of documented ship physics.
- [Earlier song and memory research](v8-1573528-memory-notes.md).

SHA-256: `b43677e77912843af1e36e1be617e609163feb41fb44971b6ad3001aa59e6177`
