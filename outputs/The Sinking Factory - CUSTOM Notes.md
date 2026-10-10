# Factory Custom

Import **The Sinking Factory - CUSTOM.gmd**; in-game name **Factory Custom**.

This revision addresses the two supplied spike screenshots and replaces the visible native orb and portal artwork throughout the factory section, x16785–24925.

- **84 full-height and short spikes** now have opaque, two-tone steel faces, a center bevel, mounting foot and paired fasteners. This includes the floor row below the cube portal and the ceiling/floor spikes around the yellow orb. These replace both bare outlines and previous faces that were too dark to read. Existing UFO crusher blades remain.
- **8 custom orb switches** use octagonal pressure-switch castings, recessed button faces, small function-colored accents, screws and electrical contacts. The blue and black switches have different center symbols. The native white rings and cores are hidden.
- **5 custom mode/size gate locations** use segmented steel housings, inset contact strips and small mode glyphs. Co-located mode/size portals share a gate.
- **6 custom speed locations** use machined chevrons and mounting rails. The slow portal points backward, while faster speeds use increasing forward chevrons.

The 21 native interactive objects remain active at their original coordinates, scales and rotations. Their original behavior and settings remain; their drawing is hidden using an isolated zero-opacity group, **1157**. Alpha controls visibility, rather than disabling the objects. See [Creator School's Alpha documentation](https://www.gdcreatorschool.com/docs/guides/triggers-1/alpha/). The custom artwork is not in that hidden group. Inspect in play mode or with editor effect preview enabled to evaluate the final appearance.

The following blue orb and its **105 custom artwork objects** stay together in **group 1156**. Its Move trigger is unchanged from Refined. The 29 later group-24 objects and their pulse are still preserved. No Move trigger targets group 24.

Editor organization is retained: whole-section layers **90–95**, detailed layers **100–159**, and the in-editor guide on **99**. Interaction artwork stays on the section's layer ending in **1**; new spike skins stay on the layer ending in **4**. The original gameplay and its skins remain separately selectable.

## Verification

The final file contains **57,502 objects**. Automated checks passed for GMD round-trip, metadata, source preservation, exact original gameplay properties, complete eligible spike coverage, all visible interaction locations, hidden-group separation, passable art, editor assignments, the ending group regression and preserved ash/wall artwork. Source data outside the factory is untouched. Only authorized spike color fields and native visibility group membership change relative to Refined's original gameplay objects.

Previews use actual game sprite atlases and scripted effects. They show the supplied spike locations, cube floor, press switches, wave gate, UFO gate and exit. They are diagnostic renders rather than native game screenshots. Native playtesting, particle behavior and performance remain unverified.

Rebuild with `rtk proxy /usr/bin/python3 work/sinking-factory/build_custom.py`, validate with `validate_custom.py`, and render with `preview_custom.py` in the same directory.

SHA-256: `18085b4f8c0256b5af275ab2db99458f97e3f5b7c01702f800c54c69a25b7179`
