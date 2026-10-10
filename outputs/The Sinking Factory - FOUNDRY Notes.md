# Factory Foundry

Import **The Sinking Factory - FOUNDRY.gmd**. The in-game name is **Factory Foundry**.

The approved drop remains the decoration scope (x16785–24660). The ship design has been restored from Afterburn. Cinder’s darker soot and irregular drifting ash remain. The accepted wave and earlier robot artwork remain; the moving press and cube transition shown in the user screenshot receive the targeted detail pass.

## Changes

- Restored all 3,477 Afterburn ship foreground skin objects and its original visual retints.
- Retained 7,122 wave/earlier robot foreground skin objects.
- Rebuilt the moving press head and cube cabinet with fitted steel panels, internal ribs, inset mechanical channels, fastening plates and solid bevelled teeth. Added press guides, sliding shoes, connected pipe banks, valve wheels and a control cabinet.
- Expanded the UFO machinery with guide-track carriages, bearing details, generator/coolant/exhaust cabinets, collector pipes and turbine mounting hardware.
- Added trim for every visible native orb/portal/speed location in the decorated section: 8 orb housings, 5 mode/size portal housings, and 6 speed brackets. Co-located mode/size portals share one frame. Native centers, openings, art and hitboxes remain intact. Trim follows the source groups, including moving orbs.
- Kept 1,144 irregular ash particles and their existing movement controls.

## Fixed following-orb group conflict

The supplied original level has 30 objects in group 24: the blue orb at (22065,75), plus 29 later objects. The Move trigger at the orb location targets group 24, with its player-lock flags enabled, unintentionally moving the later objects too.

This version assigns the blue orb and its 86 trim objects to unused group **1156**, and retargets that one Move trigger. The original follow duration, offsets and player-lock flags are retained exactly. The 29 later objects remain byte-for-byte unchanged in their original group 24, and the later group-24 pulse is preserved. There is no remaining Move trigger targeting group 24.

## Checks and limitations

GMD compression/metadata round-trip, source preservation, decoration scope, added-object passability, artwork restoration, native-interaction frame coverage and the group-conflict regression all passed. The original source .gmd is unchanged. All source gameplay data is retained except the two expressly requested group corrections (orb membership and Move target).

The file contains 60,143 objects. Performance has not been measured in-game. The preview uses actual local sprite atlases plus scripted move/rotate/alpha/color evaluation. It does not reproduce all native shader, camera, player-lock or physics behavior; pit-slope default tilt is approximated from the known source slopes and earlier native screenshot. The native bridge status was stale, so this file has not been natively imported or playtested by this agent.

## Rebuild

From the workspace, use the required `rtk proxy` command prefix with `/usr/bin/python3` and these scripts:

1. `work/sinking-factory/build_foundry.py`
2. `work/sinking-factory/validate_foundry.py`
3. `work/sinking-factory/audit_foundry.py`
4. `work/sinking-factory/preview_foundry.py`

Output SHA-256: `9e032c46a22aab66daef611f610855e066a507583afb422e070c8ccb9ae764b9`
