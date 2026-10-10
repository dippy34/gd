# v8 — moving singularities and mixed modes

Final revision: 8 September 2026. Import **v8.gmd** with GDShare. Its in-game name is **v8**. Your original files in Downloads were preserved; the preceding v8 is backed up in `work/revision-before-mixed-modes`.

## Changes

Eleven black holes now drift and bob as complete groups. The black aperture, rim and disc move together. The previous crossing bands, rotating fragments and jets were removed, and the center uses the game's larger, smoother circle sprite. The orange, pink and purple palette remains, with restrained pulses and a continuous dark nebula.

All gameplay was rebuilt following your latest permission to change every mode. This supersedes the handoff document's earlier instruction to preserve the original layout.

| Time | Mode | Role |
|---|---|---|
| 0:00–0:11.43 | Wave | Introduces the later wave's speed and turn spacing |
| 0:11.43–0:22.72 | Ball | Alternating gravity flips with varied intervals and single/double gates |
| 0:22.72–0:34.02 | Spider | Shorter taps and immediate rail changes leading into the drop |
| 0:34.02–0:45.31 | Wave | Similar input pace, slightly closer walls |
| 0:45.31–0:50.96 | Ship | Broad curved flight corridor with a gradual exit |
| 0:50.96–0:59.10 | Ball | Return to familiar inputs, then an open finish |

The speed stays normal throughout. Both wave sections use turn intervals of approximately **0.44–0.62 seconds**. Their nominal vertical gaps are 144 and 136 units, with extra space around transitions. These measurements replace the old slow-cube-to-fast-wave difficulty jump. They are design targets, not a verified star rating.

The original Xtrullor **Supernova**, Newgrounds song **593661**, is retained. The drop remains at **34.016 seconds**, aligned with the supplied 170 BPM timing grid. The opening and drop wave turns follow the same rhythmic pattern lengths. All new solid-edge decoration follows actual collision geometry.

## Research used

- The supplied decorated level was decoded as a visual reference for black apertures, colored light and disc proportions. The installed game's own sprite atlas was inspected to compare the small ball against the larger smooth circle.
- [GD Creator School: Pacing & Progression](https://www.gdcreatorschool.com/docs/guides/gameplay-2/pacing-progression/) informed the consistent challenge, recognizable patterns and allowance for timing errors. My application was to establish the wave's input pace before the drop and vary the modes around it.
- [GD Creator School: Move & Rotate](https://www.gdcreatorschool.com/docs/guides/triggers-1/move-rotate/) documents relative group movement, easing and rotation behavior. Each complete black hole now uses one Move group with eased motion. No gameplay object belongs to those groups.
- [G.js group implementation](https://github.com/g-js-api/G.js/blob/main/types/group.js), [its property mapping](https://github.com/g-js-api/G.js/blob/main/properties/obj_props.js) and [camera helpers](https://github.com/g-js-api/G.js/blob/main/lib/general-purpose.js) were checked against the serialized movement and camera settings. The camera holds its vertical framing while the level scrolls horizontally.
- [gd.py header implementation](https://github.com/nekitdev/gd.py/blob/main/gd/api/header.py) was checked for starting mode, normal speed, gravity and song-offset fields.

## Validation

The exported file was parsed independently as XML/plist, decoded and decompressed. Its name, song, object count and level data round-trip correctly. Every decorative object has No Touch and Passable enabled, and none uses a hazard ID. Positive-layer decoration uses additive colors. All 33 movement triggers target decoration only.

The 240 Hz clearance model reads collision geometry from the final exported level. It checks finite player bodies, complete spike triangles and section boundaries. Both wave routes pass 39 variants each, including one turn shifted by ±40 ms. Ball and spider pass 36 combinations of timing offsets and gravity estimates. Ship passes four acceleration estimates with a bounded controller and no input-state changes closer than 0.24 seconds. The first wave exit and the ship-to-ball entrance were enlarged after the checks exposed transition risks.

The renderer produced 60 diagnostic views across the level and low-detail comparisons. The motion preview uses one fixed viewport at three times so the actual translation is visible. It uses the game's sprite and font atlases; glow and trigger rendering are approximations, and multipart portal art is incomplete in these previews.

**Native import and in-game completion remain unverified.** The app-control connection repeatedly timed out. The clearance model is not Geometry Dash's engine and does not establish exact difficulty, native appearance, device performance or a feature rating.

Final object count: **18,627**; low detail: **15,300**. File size: **279,700 bytes**.

SHA-256: `41fe17ebff95378fb6b9ff402cf876a1f5baf237ce0846e9ceecdb7922d9ba0e`.
