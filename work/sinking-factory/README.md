> Historical initial-decoration notes. The current handoff starts at Factory Orbs; read the repository root README and docs/PROJECT_STATE.md first.

# The Sinking Factory — Flooded Drop

Approved scope: decorate the drop through approximately 75%, preserving gameplay.

## Deliverable
`outputs/The Sinking Factory - Flooded Drop.gmd`
In-game name: `Sinking Factory Deco`. Original author retained; source level ID recorded as 148876671. Original download untouched.

## Build
- Decoration window: x=16785 through x=24660, around the 4x ship entrance through the UFO section. This is an approximate percentage boundary based on the source geometry, not an exact native progress measurement.
- Original visible structural color/order edits start at x=16875. Every other original property, including all triggers and gameplay objects, is preserved.
- Dark teal factory wall, rotating rear turbines, pressure piping/valves, boiler maintenance hall, overhead suspension gantries, fitted metal panels and amber fixtures.
- Decorative water rises 32 units behind the gameplay. Chains rotate and steam drifts. New motion targets only new objects. Platform skin inherits the original platform movement group.
- 32 lighting accents selected from spectral-flux peaks of the cached 1569886 song. Mapping uses decoded speed-portal positions; exact native portal activation offsets have not been calibrated.
- 5,306 added objects; 11,926 total. 31 new motion triggers. Dedicated colors 600–620 and groups 600–649 avoid existing IDs.
- All new visible objects use NoTouch plus Passable. Master alpha group hides the new decoration before the section and after its exit. Fine texture/steam/chain details support Low Detail Mode.

## Validation and limitations
The GMD decodes back to the exact generated level string. The source SHA-256 is unchanged. Original gameplay properties, header gameplay settings, song, portals, and triggers compare equal. No new collision objects or ID conflicts were found. Master-group visibility was evaluated immediately before and after the section; fan positions differ at two animation times.

The native bridge status was stale during final checks. No native import or completion run is claimed. Previews use the game's sprite atlases, with diagnostic substitutes for procedurally drawn legacy outlines; they approximate camera centers and do not reproduce the source's shaders. Existing global inversion/glitch and color triggers remain original; the new opaque rear wall shields background color flashes, but shader behavior still needs native inspection.

## Files
- `source.level`: decoded original.
- `build.py`: deterministic decoration builder.
- `decorated.level`: exported raw level string.
- `build-manifest.json`: objects, colors, groups, motions, measured onsets, hashes.
- `validate.py` / `validation.json`: preservation and export checks.
- `preview.py` / `preview-sheet.png`: approximate visual review.

References studied: GD Creator School decoration and pulse guides; Newgrounds audio 1569886 (Pathetic - Society Remix, HelliXScream). No public host-specific brief was found.
