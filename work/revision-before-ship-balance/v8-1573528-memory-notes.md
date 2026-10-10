# v8 — song 1573528 — memory rebuild

[Import the final .gmd](v8-1573528-memory.gmd). The internal level name is **v8**. Previous versions and the original handoff are preserved.

This is a new 3:25.19 layout containing 12,412 objects and fifteen authored rooms. It targets Insane Demon to entry Extreme, but that difficulty and native completion are **unverified**.

The palette uses near-black shapes, faint olive/grey edges and brighter orbs. The two wave rooms use concealed crossings and different normal/mini arrangements. The other rooms use selective toggle-orb locks, false landing plates, false teleport targets, inverted orb transfers, and code recall. There are no black holes or swing sections.

Native 0.5× speed covers 85.71% of the duration. Native 1× speed covers the two accented phrases at 0:36.64–0:51.30 and 1:05.96–1:20.61. No timewarp is used. The ending is after 3:20.

## Room score

| Time | Room | Mode | Main setup |
|---|---|---|---|
| 0:00.00–0:14.66 | CIPHER | cube | selective switches / suspended terraces |
| 0:14.66–0:25.65 | CUTWIRE | robot | short and long holds / false landing plates |
| 0:25.65–0:36.64 | SWITCHYARD | ball | staggered gravity rails / blocked exits |
| 0:36.64–0:51.30 | BLINDFOLD | wave | concealed industrial channel / irregular bursts |
| 0:51.30–1:05.96 | OFFBEAT | ufo | tap omissions / ascending window sequence |
| 1:05.96–1:20.61 | PARALLAX | ship | long drift and short corrections / inverted control |
| 1:20.61–1:31.60 | BLIND ELEVATOR | spider | false teleport targets / alternating shelf depths |
| 1:31.60–1:46.26 | CROSSCODE | cube | blue orb transfers / inverted pink and yellow orbs |
| 1:46.26–2:00.92 | FAULTLINE | wave | mini wave / three displaced lanes / concealed crossings |
| 2:00.92–2:11.91 | NEEDLEWORK | robot | low ceilings / compressed holds / stepdown landings |
| 2:11.91–2:26.57 | COUNTERFEIT | ufo | inverted flight / false orb pairs / low-high chambers |
| 2:26.57–2:41.22 | FALSE FLOOR | ball | island rails / hidden solid dividers / delayed flips |
| 2:41.22–2:55.88 | UNDERTOW | ship | sustained low flight / stepped climb / staggered slits |
| 2:55.88–3:10.54 | RECALL | spider | short teleport slots / asymmetric stacked platforms |
| 3:10.54–3:25.19 | LAST WORD | cube | moving code tokens / recall locks / descending islands |

## Research used

- [VSC, legitimate verifier Yossarian](https://www.youtube.com/watch?v=ewlMbTR-c_w): directly inspected the dark industrial playfield, limited edge visibility and clear wave trail. Its challenge difficulty is not the target here.
- [LIMBO, MindCap creator showcase](https://www.youtube.com/watch?v=ryBbuH_SPbs): directly inspected the early false route geometry and symbol-based section. The design borrows the idea of distinct memory rules; it does not copy the level or its randomized key ending.
- [GD Docs: hitboxes](https://boomlings.dev/reference/player_physics/hitboxes): the wave red box is 10 units normally and 6 units in mini. The previous build had used a much larger wave collision envelope.
- [GD Docs: gamemode physics](https://boomlings.dev/reference/player_physics/gamemodes) and [orbs](https://boomlings.dev/reference/player_physics/orbs_and_pads): movement units, jump velocities and orb impulses informed the design models.
- [Level serialization reference](https://boomlings.dev/resources/client/level-components/level-string) and [RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf): native groups, custom/toggle orbs, alpha, move and toggle triggers.
- Local audio analysis used the actual cached **1573528.mp3**, not the old song. MP3 metadata reports 131 BPM; spectral onset-comb analysis independently returned approximately 131 BPM. The file lasts 231.915 seconds and yielded 637 detected attacks. No song title or artist is assumed.

## What was checked

- Re-read the exported .gmd, decoded its compressed level string, checked object count, song ID, name, native speed objects and all seven mode portals.
- Checked 49,395 finite-body route samples against exported solid blocks and conservative full spike boxes: zero nominal overlaps. All 841 spikes remain inside y = 0–300.
- Independently replayed the input score against the exported collision geometry: all fifteen rooms pass under the stated model assumptions. This caught and led to fixes for UFO ceiling overshoot and overlapping spider transfers.
- Audited all 40 toggle-orb decisions: 13 required switches remove full-height barriers; 27 decoys enable full-height barriers. Group links and initial toggle states were read from the actual exported objects.
- Ran 135 room replays across nine whole-score timing shifts from −40 to +40 ms. These are sensitivity checks, not individual click windows or proof of a demon rating.
- Main jump, robot launch, gravity-flip and wave-turn categories each have a median distance of zero from a detected audio attack. Some subdivisions, orb follow-ups and ship corrections intentionally fall between detected attacks; not every input is claimed to hit an onset.
- Rendered all fifteen rooms using the local game sprite atlas, with conditional group visibility and movement. These are diagnostic views rather than native screenshots.

**Limit:** ship/UFO/ball dynamics remain approximate; native portal contact offsets, full-run input behaviour and final difficulty need in-game verification. The local Geometry Dash UI connection timed out twice, so no native pass is claimed.

[Detailed checks](v8-1573528-memory-validation.json) · [Input score](v8-1573528-memory-inputs.csv) · [Diagnostic preview](v8-1573528-memory-preview.png)

## Memory notes / spoilers

CIPHER introduces the order II → I → IV → III. Its other marked orbs are decoys. LAST WORD displays II → IV → I → III and asks for the **first** order, before the tokens move. It is an authored recall sequence, not a random shuffle system. Required UFO switches appear between normal hops; their custom-orb activation is a separate input. False spider platforms have decoration but no collider, so teleportation passes through them to the real shelf.

Final SHA-256: `b06b022c0bb8cb9dd56e6acb7c2e9a9659792ca8d39f3b746371ce9c19da2197`
