# Earlier v8 gameplay lessons — separate project

These preferences came from the OBSIDIAN-CHOIR/v8 layout iterations. They are
retained so an agent can understand the archive, **not** to authorize replacing
The Sinking Factory gameplay. Song1573528 belongs to v8; factory uses 1569886.

## What the owner was asking for

- Insane Demon to easy Extreme ambition, with balanced difficulty across modes.
- Every mode except swing, with recognizably different sections and structures.
- Mostly native0.5× speed portals, with deliberate song-driven changes; time warp
  was not an acceptable substitute for the requested portal speed.
- A long level extending beyond the second song drop, around3:20 in that request.
- Memory/fakeouts inspired by Limbo, difficult visibility inspired by VSC, but
  purposeful structures instead of random overlapping pass-through objects.
- Retain the spider-specific crossing-line fakeouts; do not apply that treatment
  to every mode. Later feedback asked for fewer, more purposeful false routes.
- Random wall/orb decisions were requested: pressing the trigger orb toggles a
  wall, and its initial state varies. Preserve solvability and readable state.

## Repeated failures and useful corrections

| Observed complaint | What to check |
| --- | --- |
| Ship too easy, later ship far too hard | Timing/trajectory margin within each mode; do not assume difficulty from tight-looking spacing |
| Mini cube cannot reach big-cube orbs | Actual size state through every portal and the corresponding jump/interaction reach |
| Second wave has reversed size assumptions | Portal sequence and collision envelope for both big and mini wave |
| Spikes offscreen or positioned too high | Native camera bounds, not just world coordinates |
| “Up and down” wave/ship, boring repeated clicking | Distinct action phrases: sustained control, releases, direction changes and varied intervals |
| Second half repeats first half | Compare full room geometry and input sequences, not just decoration/random seed |
| Mode order repeats mechanically | Assign modes by musical role and local concept, rather than cycling all modes in order |
| Ending cube impossible or trivial | Check entry state, dash release/catch conditions, then adjust real timing windows |
| Portal can be skipped or looks stretched | Enforce the route through a normally proportioned portal; prove all possible paths cross it |
| Fakeouts look accidental | False corridors still need a beginning, structure and a coherent visual rule |

These are testing targets, not evidence that all historical versions solved them.

## What counts as evidence

The archive contains approximate route solvers, reference input CSVs, swept-path
checks, timing-window sensitivity reports and some historical native captures.
They are useful for finding impossible timings, size mismatches and duplicated
patterns. They do not replicate every native mechanic and cannot certify a demon
difficulty. The archived reports explicitly contain native verification limits.

Measure onset timing and derive X from the speed schedule. Examine more than one
successful input trace; a single reference route can hide an unreasonably narrow
window or bypass. Check wrong-input branches and random-state alternatives.
Do not claim “studied and possible” from decorative screenshots alone.

The saved sequence ends with `v8-1573528-variety.gmd`. An older CURRENT note points
to sync; that is historical and stale. Both are archived. The last request in that
project concerned differentiating the two ships and UFOs; saved files and reports
document the attempted revisions, not final native acceptance.
