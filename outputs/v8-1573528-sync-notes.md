# v8 — song 1573528, revised gameplay and sync

Import **v8-1573528-sync.gmd** as a new local copy. Its in-game name is **v8**. Earlier exports are preserved.

- Nine rooms have new input scores: both waves, both ships, both UFOs, both spiders, and the final cube. CIPHER, CUTWIRE, SWITCHYARD, CROSSCODE, NEEDLEWORK and FALSE FLOOR retain their accepted non-memory inputs.
- The flight solvers select their thrust changes, wave turns and UFO actions from measured attacks in the cached recording. Attack proximity across the whole reference score improved from 31.4% to 81.2% within 25 ms. This measures the planned inputs against the recording, not audio latency inside GD.
- The spectral comb refines the pulse estimate to approximately 131.044 BPM; the editor beat guide follows individually detected attacks. Existing native speed portals remain: 85.714% of the level is at 0.5 speed. No time-warp triggers.
- Spider now has **13 native jump orbs** across its two rooms. Orb arcs clear mounted teeth before returning to the current rail; teleport inputs reach the opposite shelf. The crossing-line and false-shelf style is rebuilt around these routes. There are 262 spider fake-out features.
- The final cube has **35 reference inputs**, up from 27: four dash releases and catches, extra airborne orb chains, and tighter departure/exit gates. The two over-tight late catches found in testing were widened. Its 10 sampled timing probes passed 101/250 shifted inputs versus 133/250 before; these are approximate model sensitivities, not native frame windows.
- Dark structural colours remain. Native helper rectangles are hidden at runtime, displayed portals have normal proportions, and conditional switches use the existing dim circular skin. There are 23 random wall decisions; all were checked for both hit/skip outcomes.

The level contains **25,741 objects**, uses all seven requested modes except swing, and lasts **205.192 seconds (3:25.2)**. The source and all earlier exports are untouched.

## Validation and limits

The final serialized GMD round-trips correctly. All 15 rooms pass both a swept reference-route check and an independent 240 Hz input replay against exported collision objects. The checks include normal/mini state, orb reach, spider support faces, fixed-screen spike bounds, conditional wall logic, portal divider coverage, and dash-release momentum variations of ±35 world units/second. Room comparisons confirm distinct input scores in each pair of flight/spider rooms; the song's recurring musical beat remains intentional.

Eight native-sprite diagnostic views were rendered and visually inspected. These are script renders, not native gameplay footage. Full damage-enabled completion, native audio latency, exact demon difficulty and a rating remain unverified. The installed Native Editor Bridge is disabled in the latest Geode log, and its status is stale; this revision was not imported through it.

The numeric assumptions are documented in `work/sync_sections.py` and `work/replay_sync.py`. Detailed results are in `v8-1573528-sync-validation.json` and `work/sync-measurements.json`.

References used for the gameplay mechanisms and sync approach: [GD Creator School: Gameplay Objects](https://www.gdcreatorschool.com/docs/guides/gameplay-1/gameplay-objects/), [GD Creator School: Making Sync](https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-sync/), and the [official editor guide](https://www.robtopgames.com/files/GDEditor.pdf). The recording, existing object schemas and local native sprite atlas supplied the project-specific measurements.

SHA-256: `b4c2346e51535a356d87de9e5c8251185da51bae1c728f0a60a21a784153d131`
