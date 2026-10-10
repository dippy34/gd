# v8 — chapter and motion revision

Final level: **v8.gmd**, internally named **v8**. Song: Xtrullor — Supernova (593661). Approximately **4:20**, beyond the requested second-drop area; native editor displays about 4:21. Original source files and the previous v8 have been preserved.

This revision adds a recurring floor-to-ceiling “gravity loom”: blue orbs transfer the cube onto a ceiling route, with inverted jumps and yellow/pink orb combinations before returning to the floor. It appears in the opening, returns as an expanded sequence around 1:19, and comes back around 2:38. Six inverted flight windows use visible upside-down and normal-gravity portals in ship, UFO and wave passages.

The opening develops through cube, robot and ship into a faster wave drop around 0:34. Later speed lifts reach the faster 3× setting; the quiet ship/spider stretch around 3:17–3:34 provides a reset before the returning wave drop. All seven classic modes remain, with no swing. There are 27 sections and no repeated three-mode sequence.

The scenery now moves with the music: paired fins draw inward and release, five split gates open on drop accents, and suspended crystal lanterns swing in the quiet chapters. There are 58 scenery features driven by 192 Move and 34 Rotate triggers. Every moving target is noncolliding decoration. All black holes remain removed. The orange/pink/purple nebula, beveled structures and solid crystal spikes remain.

## Musical chapters

| Time | Chapter | Identity |
| --- | --- | --- |
| 0:00–0:34 | IGNITION | Learn the gravity loom; robot vaults build into inverted ship flight. |
| 0:34–1:19 | BREACH | Fast wave release, then ball/UFO sync and a spider punctuation. |
| 1:19–1:41 | THE LOOM | The opening gravity mechanic returns as a longer ceiling-orb sequence. |
| 1:41–2:04 | RECHARGE | Wave tension and spider timing lead into the next speed lift. |
| 2:04–3:17 | OVERDRIVE | Faster ship and wave passages, with gravity callbacks between them. |
| 3:17–3:34 | SUSPENSION | Normal-speed ship and a spider count-in create breathing room. |
| 3:34–3:57 | RETURN | The drop gate reopens; wave, inverted UFO and ball build the final phrase. |
| 3:57–4:19 | RELEASE | The fastest wave/ship payoff resolves into the final cube landing. |

## Checks and limits

Music positions use spectral attacks measured from the cached song and a 170 BPM grid starting at 0.128 seconds. The editor beat guidelines now cover the whole level. Jump and orb impulse estimates were corrected against the physics reference, including robot hold behavior, UFO lift and ball's initial flip impulse.

The exported geometry passes all 27 nominal section checks. Approximate grounded-mode checks also pass with inputs shifted ±25 ms, gravity varied ±3%, and alternative blue-orb impulses. Five wave sections pass 331 nominal and individual-turn timing variants, including reversed input mapping during the inverted passage. Object counts, portal/speed placements, decoration collision flags, motion targets and the ending are audited from the exported file.

**These are approximate models, not a native completion proof.** Ship/UFO routes use approximate control models and clearance checks. Native import and visual playback are checked separately. The user's editor has Ignore Damage enabled; visual playback under that setting does not verify gameplay completion. A full damage-enabled playthrough and difficulty balance remain unverified. The GMD is marked unverified, and no rating or feature is promised.

49,645 objects; 16,145 high-detail objects; 33,500 remain in low detail mode. The song is referenced by ID and is not embedded. Preview images are atlas-based diagnostic renders, not gameplay screenshots.

## References

[Music credit](https://www.newgrounds.com/audio/listen/593661), [game-mode physics](https://boomlings.dev/reference/player_physics/gamemodes), [orb behavior](https://boomlings.dev/reference/player_physics/orbs_and_pads), [sync guidance](https://www.gdcreatorschool.com/docs/guides/gameplay-1/making-sync/), [readable decoration](https://www.gdcreatorschool.com/docs/guides/deco-1/how-to-decorate/), and the [official editor guide](https://www.robtopgames.com/files/GDEditor.pdf).

SHA-256: 5c4637238daf2aabb31327ceb9aad94ae025d3e8acc385a727cb216ce68b67b7
