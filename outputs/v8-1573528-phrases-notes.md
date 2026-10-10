# v8 — reformed gameplay

Import `v8-1573528-phrases.gmd`. Internal name: **v8**. Song: **1573528**. Length: **3:25.19**. Native 0.5-speed portals cover **85.71%** of the run; the original speed-change positions and soundtrack timing are retained. All seven requested modes remain; no swing.

The new coloured inlays, moving coloured contact lights and portal brackets are removed. The earlier nearly black structural palette remains. No floating service plates or rectangular toggle-orb skins were added back.

The accepted CIPHER opening, CUTWIRE robot, SWITCHYARD ball, BLINDFOLD wave, OFFBEAT UFO, BLIND ELEVATOR spider and CROSSCODE cube keep their non-memory input scores. The first spider's 1,183 fakeout artwork objects are preserved verbatim. The second spider keeps that visual concept with new structures and timing packets. There are 25 randomized wall decisions, using the subdued circular switch display, plus two physical blind routes.

The later sections retain familiar mechanics but have separate input scores and geometry. This is a revision of the existing level's concepts, not a replacement theme.

| Time | Part | Reformed interaction |
|---|---|---|
| 1:05–1:20 | PARALLAX | Broad lift, braking and cutback arcs replace the constant hover corrections. |
| 1:46–2:00 | FAULTLINE | Normal-size wave with sustained inputs through gravity bends, manual edge pairs, suspended banks and separated crossings. |
| 2:00–2:15 | RECALL | Two-to-four-flip packets separated by longer rail runs. The original spider false-shelf language is rebuilt around these new timings. |
| 2:15–2:30 | UNDERTOW | New inverted arches, broad braking curves, detached forks and a physically carved blind continuation. |
| 2:30–2:41 | NEEDLEWORK | Long robot climbs alternate with clipped descending steps and an orb catch. Authored holds range from 0.045 to 0.300 seconds. |
| 2:41–2:55 | FALSE FLOOR | Manual ball flips alternate with automatic gravity transfers and conditional wall decisions. |
| 2:55–3:10 | COUNTERFEIT | Grouped UFO hops gain height before longer free falls into suspended catch pockets. |
| 3:10–3:25 | LAST WORD | Six dash passages with different hold lengths, two inverted releases, isolated jumps and orb catches. |

## Checks

- Export round trip, metadata, object count, spike bounds, alpha groups and 25 random-wall truth tables checked.
- All 71 physical portals are inside solid passages. Visible portal copies use normal proportions. The extended activation objects are invisible; coverage uses a conservative portal-core model.
- 49,410 swept route samples pass the exported collision check. Separate 240 Hz input replay passes all 15 rooms.
- Both blind routes have body clearance up to a real solid dead end.
- Twenty-four selected input perturbation probes pass at the planned timing and reject at least one deliberately shifted timing. This is a model sensitivity test, not a native difficulty measurement.
- All seven first/second mode counterpart scores differ. Eight rooms were reformed; seven accepted scores were deliberately preserved.
- Native-atlas previews checked for dark appearance, structural overlap and the new dash/flight/spider silhouettes.

The completed file was copied to `$HOME/Downloads/OBSIDIAN-CHOIR-HANDOFF/v8-1573528-phrases.gmd` and byte-verified. Native import could not be checked: the bridge status remained stale on the main menu. No live level was replaced.

Full damage-enabled native completion, exact engine physics and an Insane/Extreme Demon rating remain unverified. In particular, dash release and gravity transitions are approximations in the replay; native import/visual inspection alone does not prove they are beatable.

## References used

Native orb, portal and special-block behavior was checked against [GD Creator School's gameplay-object guide](https://www.gdcreatorschool.com/docs/guides/gameplay-1/gameplay-objects/) and the [RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf). Native IDs were cross-checked against the local G.js constants and schema, and rendering uses the installed game's sprite atlas. Timing placement uses the cached MP3 onset analysis for song 1573528.
