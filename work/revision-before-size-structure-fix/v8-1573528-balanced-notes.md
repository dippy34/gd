# v8 — ship balance and structure revision

[Final .gmd](v8-1573528-balanced.gmd) · [Preview](v8-1573528-balanced-preview.png) · [Validation](v8-1573528-balanced-validation.json)

The internal level name remains **v8**. The previous memory version is preserved as `v8-1573528-memory.gmd`.

## Gameplay changes

| Ship section | Old thrust changes | New thrust changes | Change |
|---|---:|---:|---|
| PARALLAX | 79 | 39 | Smoother climbs, broader galleries, gravity reversal removed |
| UNDERTOW | 86 | 50 | Longer corrections, steadier height changes, wider slits |

The reference score uses longer correction intervals. Narrow ship gates receive 24 units of extra space around the finite-body route instead of 11; drift galleries receive 27 instead of 14. Ship rail spikes are kept at least 22 additional units away from the sampled route. These are design-model clearances, not native click-window measurements.

All thirteen non-ship sections retain identical gameplay objects and input scores. The level still has forty live memory decisions, all seven requested game modes, and no swing or black holes. Gravity changes remain in the cube and UFO sections.

## Structure and visibility

Joined panel faces, inset borders, collars, brackets and supports replace isolated block outlines and unrelated floating motifs. Frames join into larger bays. False landings and real platforms use the same panel design, so the composition is more coherent without labelling the correct route. Continuous wave walls retain dark faces. Background bay frames still move; collision surfaces stay aligned with their visible skins.

Song: **1573528**. Duration: **3:25.19**. Native 0.5× speed: **85.71%**. Objects: **17,904**. No timewarp.

## Checks and limits

- Exported geometry: 49,395 finite-body path samples, zero nominal block/spike overlaps; all 839 spikes fit inside y = 0–300.
- Independent input-model replay passes all fifteen sections.
- Compared exported gameplay objects and input scores with the previous .gmd: all thirteen non-ship rooms match.
- Audited all forty memory switches and their full-height gates.
- Ran separate whole-score timing-shift checks on both ship sections. These indicate sensitivity under the approximate model; they are not individual input windows or difficulty ratings.
- Inspected atlas-based renders of both ship sections and representative cube, robot, UFO, ball, spider and wave sections.

**Native completion and exact Insane/Extreme difficulty remain unverified.** The local editor bridge is disconnected. Ship/UFO/ball dynamics and native portal contact offsets still require in-game testing.

[Original research references and memory notes](v8-1573528-memory-notes.md)

SHA-256: `9b1607b9e2a7915fb53add71bd61930547929a1b3c81e118dee8f7766a3cf497`
