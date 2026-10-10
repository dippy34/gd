# Current project state

The selected baseline is [CUSTOM-ORBS.gmd](../outputs/The%20Sinking%20Factory%20-%20CUSTOM-ORBS.gmd),
internal name **Factory Orbs**, song ID **1569886**, **57,465 parsed objects**.
SHA-256: `802bc6c3ed846833bac104d893f3002918e3d170db00f80bb2e0ff161643380c`.

This is a conservative handoff choice: it retains the user's custom-orb/native-
portal decision and predates the discarded border experiments. It is not a claim
that the user gave final approval to all cube/UFO detail. Do not choose a file by
modification time or assume a previous assistant's “passed” means visually good.

## Scope

Original source: [The Sinking Factory.gmd](../inputs/The%20Sinking%20Factory.gmd).
Its metadata credits **ricewithmaggi**. Preserve that provenance and the work of
other contributors. Source SHA-256:
`9429ecc3df11cd6d0aab4b573b4bb0da9560240da78ec92223f2f92436b9386a`.

The owner selected roughly **51–75%**, then clarified that the beat drop should
determine the actual boundary. The established decoration interval is **X16785
through X24925**. Speed-schedule conversion places it at approximately **47.94–
64.57 seconds of level time**. Do not equate percent, song time and level time;
native activation/camera details require a game check.

This is decoration of supplied gameplay. Keep positions, collisions, portals,
orb behavior and collaborator sections intact unless the owner requests changes.

## Retain

| Component | Evidence and constraint |
| --- | --- |
| Ship | Owner requested restoration of the old look; Afterburn ship skins retained in the baseline |
| Wave and early robot | Owner explicitly liked them; regression checks retain their accepted skins |
| Custom orbs | Keep eight pressure-switch orb designs, original gameplay behavior and follow motion |
| Portals | Latest explicit preference: undo custom portals; native sprites and earlier restrained trim restored |
| Spikes | 84 custom steel spike skins; no plain outlined triangles passed off as finished design |
| Ash/darkness | Darker atmosphere, restrained ember light and falling ash; ash geometry retained |
| Exit | Complete the previously white/unskinned tail through X24925; no early fade exposing hazards |
| Editing | Secondary layers90–95; primary100–159 by section and purpose; legend99 |

## Important regression

The blue orb at **(22065,75)** originally shared group 24 with later objects.
A follow Move intended for that orb also moved the later objects forward, making
them appear to disappear. The fix isolates the orb and its **105 current trim
objects** in group 1156. Its Move settings stay intact apart from the target.
The **29 later group 24 objects** and their pulse are unchanged. Do not merge these
groups. Older Refined notes mention86 trim objects; Custom-Orbs is the current105.

Native orb cores remain active but visually hidden through alpha group 1157.
Only those eight cores use that group; custom orb art and restored portals do not.

## Disregarded and historical

The owner said to ignore the custom-art part. **CUSTOM-FIRE / Factory Wildfire is
excluded**, including its generated artwork and implementation. Do not rebuild
it. CLOSING-FIRE and ENGULFED are kept as labeled historical experiments; neither
is selected or endorsed. A closing-fire concept may be reconsidered only in a
future explicit task.

The full earlier **v8 / OBSIDIAN-CHOIR** history is retained separately. Its song
1573528, memory gameplay, VSC/Limbo references and demon difficulty goals are not
requirements for The Sinking Factory. See [history](HISTORY.md).

## Verification status

Data regression and GMD parsing/roundtrip checks pass locally. A GitHub Actions
template is included in docs/ci; automated CI is not installed.
Native playtesting of Factory Orbs was not completed. The earlier native bridge
was unavailable; screenshots from other versions do not substitute for this test.
No difficulty rating, feature outcome or native frame-rate claim is established.
