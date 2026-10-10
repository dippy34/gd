# v8 — balance revision

Import **v8-1573528-rebalance.gmd**. Internal level name: **v8**. Song **1573528**. Duration **3:25.19**. The speed schedule is unchanged: native 0.5-speed portals cover **85.71%** of the run. All seven requested modes remain; no swing.

## Source selection

The first-half scores come from the earlier `restored` revision, including the earlier PARALLAX ship. The exception is BLINDFOLD, which has a new manual wave score: unequal tap sequences, grounded glides, low rest canopies and separate aerial structures. It does not reuse the later wave's sustained-gravity-input pattern.

From FAULTLINE onward, the newer `phrases` revision remains the base. The second wave, spider, ball and UFO retain their input scores. The second ship retains its curved route but receives more clearance. The last robot retains its short/long holds and stairs with additional takeoff and release constraints. LAST WORD is rebuilt as a distinct finale.

The dark palette, 25 randomized wall-toggle decisions and spider-only crossing fakeout lines remain. No colourful trim, floating white rectangular plates or moving decorative hardware was added. Visible portals retain normal proportions; their extended activation objects are invisible.

## Balance changes

- **Second ship:** corridor envelopes allow 12 more world units on each side; portal openings in this room also have more clearance. Its broad curves and deliberate braking remain.
- **Last robot:** takeoff restraints and separate release checks make the existing holds matter. An initially harsher setting was backed off after sensitivity testing.
- **Final cube:** four green dash passages replace the former six mixed green/pink dashes. Dash entries sit near the jump apex with broader approach space. Each release leads to a pink, yellow or blue catch orb; separate blue-orb inputs handle gravity changes. The challenge is release timing and the following catch rather than a long free hold. The geometry includes an envelope for modest variation in post-release vertical momentum.

## Verification

The exported object string round-trips correctly. All 15 rooms pass the independent 240 Hz replay and swept-route collision check. All spikes remain inside the authored 300-unit playfield. The conditional-wall truth tables, full-height walls, portal passages and preserved first-spider artwork are checked separately. Eight native-atlas preview frames were visually reviewed.

The following probes shift the same three selected inputs in each category by -50 to +50 ms in 1/240-second increments. More passing probes means more forgiving in this model; these totals are not native difficulty ratings.

| Model probe | Previous | Revised |
|---|---:|---:|
| UNDERTOW input time | 25/75 | 56/75 |
| NEEDLEWORK input time | 51/75 | 29/75 |
| NEEDLEWORK hold duration | 44/75 | 17/75 |

All four final dash releases reject some early/late input probes. The final cube also passes the replay with assumed post-release vertical velocities of -50, 0 and +50 world units/second. That is an uncertainty check, not a measurement of native dash physics.

The first-half selection and second-half retention are checked directly against the two previous plans. Shared game modes remain intentional; the corresponding first/second scores differ. The first spider's 1,183 fakeout-art objects are unchanged, and the second spider retains its newer 1,317-art-object design.

**Native completion remains unverified.** The installed Native Editor Bridge mod is disabled according to the latest Geode startup log, and its status is stale. Its settings were not changed, the game was not restarted, and no live level was replaced. The previous ending failed in real play despite passing an idealized model, so the new ending should be treated as a reworked candidate until checked in-game. No exact Insane/Extreme Demon classification is claimed.

## References

Orb, dash, gravity and ground-contact behavior was cross-checked against [GD Creator School's gameplay-object guide](https://www.gdcreatorschool.com/docs/guides/gameplay-1/gameplay-objects/) and the [RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf). Object IDs were checked against the local G.js constants/schema. Previews use the installed game's sprite atlas. Timing uses the cached analysis of song 1573528.

Saved to `$HOME/Downloads/OBSIDIAN-CHOIR-HANDOFF/v8-1573528-rebalance.gmd` and byte-verified. SHA256: `0d7b732dc69870b4e805d6add850b52a43971188e15a9bb6231c33645073dfb7`.
