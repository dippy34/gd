# v8 — dark branching revision

[Final .gmd](v8-1573528-branching.gmd) · [31-view preview](v8-1573528-branching-preview.png) · [Validation](v8-1573528-branching-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× speed portals cover **85.71%** of the timeline. **26,934 objects**. All seven requested modes; no swing. Earlier exports remain intact.

## Changes

- Added **50 fitted fakeouts**: 25 false ledge extensions and 25 blind L-shaped recesses. Extensions attach to platform edges; recesses sit inside solid structures. Their artwork does not add colliders.
- Darkened the structures while keeping wall-switch states brighter than the surrounding geometry. Removed the blinking wave masks, pulsing trim and moving flight-room plates. The export contains no Pulse or Alpha triggers. Small moving decorative elements remain outside the playing area in other rooms.
- Reworked ship and wave into **18 structural phrases**, mixing long holds, short corrections, separated knife gates, floating barriers and enclosed ducts. Gravity changes and wave size changes vary the controls between phrases.
- Changed the later sequence to spider → ship → robot → ball → UFO → cube. These rooms have new input scores: clustered spider transfers, inverted ship movement, robot orb catches, unequal ball transfers, a different UFO contour and a cube finale with mixed-gravity orb transfers.

## Randomized white switches

There are **34 independent decisions**, each with an equal chance of starting with its wall present or absent. Each decision resolves about **0.94 seconds before its orb** and stays fixed while you approach it.

| Visible state | Correct action | Wrong action |
| --- | --- | --- |
| Wall present | Hit the white switch to remove it | Skipping leaves the wall |
| No wall | Skip the white switch | Hitting creates the wall |

The switches use Claim Touch so their activation does not also cause an ordinary jump or UFO flap. This behavior was checked against the [official RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf). Native Advanced Random branches, toggle-orb properties and collision flags were checked against [FlowVix's object schema](https://github.com/FlowVix/gd-info-explorer/blob/main/src/lib/schema.txt) and [G.js's trigger implementation](https://github.com/g-js-api/G.js/blob/main/src/lib/general-purpose.ts).

Native evidence shows the first wall [present on attempt 2](v8-1573528-branching-native-wall-present.png) and [absent on attempt 3](v8-1573528-branching-native-wall-absent.png). These are unmodified GD screenshots. The upper-left colored squares and controls belong to the installed preview interface.

## Verification and limits

- The actual .gmd imports into GD with all **26,934 objects**. Native serialization retains the random branches, Claim Touch settings and non-colliding artwork flags.
- All 34 exported switch circuits pass both correct outcomes and both wrong-choice cases. This is a serialized-logic check; every switch was not clicked through in native play.
- **49,408 finite-body route samples** pass. A separate approximate input replay passes all **15 rooms**. The reference route assumes each switch starts with a wall; branch tests check the no-wall alternative separately.
- Normal/mini states at orbs, per-room camera setup, spike bounds, group separation and absence of flight-room motion triggers pass the structural audit.
- Inspected **31 atlas-based camera views**, the [native ship](v8-1573528-branching-native-ship.png), the [native second wave](v8-1573528-branching-native-wave.png), and three opening attempts for randomization.

**Full native completion and the requested insane-to-extreme demon difficulty remain unverified.** The opening preview used Ignore Damage. Approximate physics does not fully reproduce native triangle collisions, portal entry offsets or input buffering; passing these checks is not proof of a damage-enabled completion.

Build and audit instructions are in `work/CURRENT.md`. SHA-256: `17ddb9d245f117157385613017aba45744836424356d49a25c393277dff8733a`.
