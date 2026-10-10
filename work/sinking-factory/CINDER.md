# Factory Cinder

Import `The Sinking Factory - CINDER.gmd`. The level name is **Factory Cinder**.

This revision keeps the liked wave and robot structures and reworks the ship and UFO materials within the previously approved drop section. The ship uses joined steel casings, recessed reinforcement, bolted inspection covers and rails fitted to the original slope boundaries. The UFO has chamfered mechanical housings and solid, bevelled crusher teeth. The old glowing outlines in these sections have been replaced.

The atmosphere has deeper soot shadows and cooler, darker dust. Ash consists of irregular carbon flakes in four depth layers, with three stages of wind drift, tumbling larger flakes, fading, and occasional hot edges. 1,144 particles use 104 wind cohorts; 362 have ember edges. There are no round particle halos.

## Preservation and validation

- The original source file remains unchanged.
- All 6,620 source objects are retained. All source gameplay properties, positions, groups, portals, hazards, timing controls and song data are retained. Original visual-only changes are confined to the approved section.
- 753 original wave/robot objects match the previous AFTERBURN export exactly. All 7,815 foreground skin objects in that interval are retained exactly.
- Added visual objects have NoTouch and Passable enabled. No new collision objects were added. The existing robot moving-platform group is retained.
- The GMD compression and metadata round-trip passed. Serialized motion checks passed for all 104 ash cohorts, with 64 sampled moving objects and exit controls checked.
- Final file contains 52,437 objects. In-game performance has not been measured. Fine atmospheric details are marked high detail where appropriate.

## Preview limits

The preview uses local Geometry Dash sprite atlases and an evaluator for move, rotate, alpha and color/pulse triggers. It is a diagnostic, not a recording from the game. It does not simulate the native glitch shader, precise native camera behavior or physics. Pit-slope sprite tilt is approximated from source geometry and the earlier native screenshot; the actual GMD uses the unchanged native pit-slope objects.

A live screenshot confirmed Geometry Dash was on the Factory Afterburn level menu, but editor clicks failed with `noWindowsAvailable`. The native bridge was disconnected. This revision has therefore not been imported or playtested through the bridge.

## Rebuild

Use `/usr/bin/python3 work/sinking-factory/build_refinery.py`, then `validate_refinery.py`, `audit_refinery.py` and `preview_refinery.py` from the same folder. Shell commands in this workspace use the required `rtk proxy` prefix.

Output SHA-256: `3bd32c99f94a858c36d1fa5ce7cfc10fa375f0ec8d17f642cd32ae941fca164f`
