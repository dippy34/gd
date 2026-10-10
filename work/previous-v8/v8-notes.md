# v8 — Obsidian Choir

`v8.gmd` is a separate decorated copy, named **v8** inside the file. The source in Downloads is unchanged. Import the file through GDShare's import button. [GDShare documentation](https://github.com/HJfod/GDShare)

The theme is an eclipse observatory: dark metal surfaces, narrow illuminated collision boundaries, clustered stars, instrument markings, and eight eclipse landmarks. The palette develops from cyan through cool blue to warm gold. Rotation and restrained color pulses follow the handoff's timing map. The song remains [Xtrullor — Supernova, Newgrounds 593661](https://www.newgrounds.com/audio/listen/593661).

| Check | Result |
|---|---:|
| Total objects | 40,371 |
| Original layout objects and controls retained byte for byte | 12,378 |
| Old decorative objects replaced | 235 |
| New decorative objects | 27,877 |
| New visual triggers | 116 |
| Objects with low-detail mode enabled | 31,600 |
| Missing or changed layout objects | 0 |
| Hazard or interactive IDs used for new decoration | 0 |
| Opaque new decoration on positive Z layers | 0 |
| Gameplay objects in new rotation groups | 0 |
| Undefined decoration channels | 0 |

The supplied handoff checker also reports **missing 0, changed/added 0**. Its smaller baseline of 12,285 excludes 93 existing visual controls; the stricter independent check preserves those controls too. All new decorative objects have both NoTouch and Passable set. New decoration uses only IDs 211, 1764, 1888, and 3625. No new Move triggers were needed.

Placement was derived from the actual rectangles in the source. The source contains 7.5-, 15-, and 30-unit blocks, so an exact rectangle-union sweep replaced the handoff's approximate 5-unit occupancy grid for wall fills and exposed edges. The result traces 10,334 exposed segments without simplifying away collision steps. Camera centers were estimated from the actual enclosed corridor; cube decoration uses the handoff's 95-unit camera center. Timing uses the supplied 170 BPM grid and piecewise speed schedule, rather than one constant horizontal speed.

Research directly informed the construction:

- **Collision flags, groups, and detail mode:** the official editor guide distinguishes NoTouch from Passable and explains detail-mode removal. Both flags are set, and no hazard IDs were used as decoration. [RobTop's editor guide](https://www.robtopgames.com/files/GDEditor.pdf)
- **Foreground/background separation:** the background guide recommends contrasting detail and brightness so the route remains readable. Large background forms are subdued, while small boundary highlights are brighter. [Making Backgrounds](https://www.gdcreatorschool.com/docs/guides/deco-1/making-backgrounds/)
- **Layering:** blending and tilesets can take precedence over Z order. Dark aperture masks and luminous layers are separated, and all new positive-layer artwork is additive. [Editing Objects](https://www.gdcreatorschool.com/docs/guides/the-editor/editing-objects/), [Geode's Z-layer definitions](https://raw.githubusercontent.com/geode-sdk/bindings/main/bindings/include/Geode/Enums.hpp)
- **Rotation:** every new rotation uses an isolated, one-object center group. Gameplay never enters those groups. [Move & Rotate](https://www.gdcreatorschool.com/docs/guides/triggers-1/move-rotate/)
- **Organization:** background, instruments, eclipses, material fills, route edges, and panel details occupy separate editor layers 11–17. [How to Decorate](https://www.gdcreatorschool.com/docs/guides/deco-1/how-to-decorate/)
- **Optimization:** adjoining wall spans were merged, long line pieces were capped at 120 units, and optional haze, stars, and detailing were marked high detail. [Optimizing](https://www.gdcreatorschool.com/docs/guides/deco-1/optimizing/)
- **Polish:** camera cropping, brightness, layering, and low-detail continuity were inspected across the level. [Polishing](https://www.gdcreatorschool.com/docs/guides/deco-1/polishing/)
- **Serialization:** object key/value pairs, HSV values, color-trigger blending flags, group arrays, and rotation properties were cross-checked against the level-format documentation. [Level Object resource](https://github.com/gd-programming/gd.docs/blob/main/docs/resources/client/level-components/level-object.md)

The supplied KOCMOC UNLEASHED reference was decompressed and inspected at object-group level. Groups 109 and 113 each contain 36 broad glow objects with median radius about 206–207 units. Group 114 contains 62 glow objects tightly clustered around a median radius of 162.8 units, with median scale 0.49. These use the same center object, at approximately (507, 1495), but separate rotation tracks. Group 122 adds a smaller, flattened layer. That informed the new effects' separate corona, inner rim, dark aperture, and orbital layers. The reference's tiny star scale of 0.051 informed the clustered stars. No reference object geometry was pasted into v8.

Validation used two readers: the supplied handoff reader/checker and an independent conversion to standard plist parsed with Python's plistlib, followed by direct base64/gzip decoding. The final decoded data also matches the assembled level string. The original source checksum was rechecked.

The visual review includes 60 views, roughly one second apart, with at least 132 units of horizontal overlap between successive windows, plus three full-detail/low-detail comparisons. The final preview uses the game's installed sprite and font atlases. Color transitions, pulses, and the new rotation groups are evaluated for each sampled time.

**Verification limit:** these images are diagnostic renders, not screenshots from Geometry Dash. Glow-orb rendering is approximated; camera movement, engine batching/culling, collisions, music playback, and frame rate have not been verified in the engine. Attempts to connect to Geometry Dash/Steam failed or timed out. The file remains an unverified local draft. This work aims for a cohesive, readable decoration pass; a star rating is not guaranteed. [RobTop's rating FAQ](https://www.robtopgames.com/faq/answers/level/)

See `v8-validation.json` for exact counts and checksums, and `v8-preview.png` for representative views.
