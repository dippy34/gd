# v8 — spider-only linework and mechanical fakeouts

[Final .gmd](v8-1573528-deception.gmd) · [18-view preview](v8-1573528-deception-preview.png) · [Validation](v8-1573528-deception-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× speed for **85.71%** of the timeline. **30,508 objects**.

## Scope corrected

Both spider sections are identical to the preceding nocturne file: **2,262 objects** in BLIND ELEVATOR and **3,293 objects** in RECALL. Their 385 visual decoys and dense shelf linework remain.

Removed all **592** copied false shelf and painted-gap features outside those spider rooms. The other rooms use their earlier clean structural surfaces, the dark palette and the eased wave geometry. Randomized switches retain their dim olive artwork and original behavior.

## Different kinds of wrong choices

**17 live bait orbs.** These use native yellow-jump or blue-gravity orb mechanics. They occupy deliberately selected gaps between required inputs, with at least 0.28 seconds from each required click and additional exclusion around robot holds. Hitting each retained bait creates a collision in the approximate replay; skipping it preserves the original input score. A candidate that did not produce a collision was removed.

Required and bait orbs share the same normal size and a constant 13% opacity, with glow and particles disabled. This avoids identifying the bait through a different size or brighter outline. The opacity is set once at the start and never flashes.

**Four genuine blind branches.** Collision geometry is cut to form real openings:

| Room | Tempting wrong move | Result |
| --- | --- | --- |
| BLINDFOLD | Continue downward through a required wave turn | The lower branch ends against a solid cap |
| FAULTLINE | Continue the mini-wave climb | The upper branch closes while the real route turns away |
| PARALLAX | Dive into a lower service duct | A live gravity portal sits inside the detour, followed by a solid end |
| UNDERTOW | Maintain altitude past the required descent | The straight branch ends while the intended route drops |

These branches share the existing wall surfaces. Their entries have actual open space and their ends have actual collision. [Ship branch preview](v8-1573528-deception-ship-branch.png).

The existing **34 randomized wall decisions** remain: wall present → hit; wall absent → skip. All seven modes and the original 550-input reference score are retained.

## LIMBO study

Inspected MindCap's original showcase at [0:22](https://www.youtube.com/watch?v=ryBbuH_SPbs&t=22s), [0:45](https://www.youtube.com/watch?v=ryBbuH_SPbs&t=45s) and [1:08](https://www.youtube.com/watch?v=ryBbuH_SPbs&t=68s). The references show grouped orb choices, alternate destinations around coherent platform masses, and distinct visual framing for each room. The design takeaway used here is to give a misleading object a specific relationship to the player's next decision. The new geometry and timings were authored for this level.

## Verification

- Exact serialized-object comparisons confirm that both spider sections are unchanged.
- All non-spider shelf overlays are removed; remaining layer-11 artwork belongs to the spider rooms or the existing randomized switch skins.
- The **49,408-sample** route check passes, and approximate independent replay passes all **15 rooms**.
- Each of the **17 bait inputs** produces a solid or spike collision in the wrong-input model. All four branch approaches have body clearance up to their solid caps.
- The 34 randomized switch circuits pass both starting-state cases.
- Inspected 18 atlas-based camera views spanning all 15 rooms.

**A fresh native import/playtest was not completed because GD was being used concurrently. Full native completion and exact demon difficulty remain unverified.** The scripted models approximate native orb physics, input buffering and portal collision. Branch checks establish geometric access and solid endpoints, rather than a native alternate-input completion.

Earlier exports remain intact. Rebuild details are in `work/CURRENT.md`.

SHA-256: `8d859faea28782d7cd1798102fd7884d2cfaac420d04dd20291e2ec3f2efb4d6`
