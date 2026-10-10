# Factory Refined

Import **The Sinking Factory - REFINED.gmd**. Its in-game name is **Factory Refined**.

The cube/UFO composition has been simplified: the extra cabinets, pipe bundles, press guide frames and UFO carriage racks have been removed. The 84 older thin hanger pieces have also been removed. Fitted block panels, hazard skins and the main factory machinery remain. Orb and portal housings remain attached to their native interactions. The accepted Afterburn ship, wave and earlier robot skins are retained.

The factory now continues to **x24925**, through the two previously uncovered UFO obstacles and into the entrance of the supplied next section. Those obstacles have matching steel housings and blades, with a dark masonry background, exit lintel and sill. The factory fade starts after the final hazards rather than exposing them halfway through the exit.

The original file is untouched. The export contains **56,066 objects**, 4,077 fewer than Foundry. This is a decoration and editor-organization change; it does not redesign the gameplay.

## Editor layers

The entire factory build, including its original gameplay objects, is organized by section and function. Other collaborators' objects outside x16785–24925 retain their original editor layers and data. Editor layers change selection and visibility while editing; they are separate from render Z layers. This scheme uses a detailed primary layer and a secondary layer for selecting a whole section, following the editor's two-layer system. [Editor layer documentation](https://www.gdcreatorschool.com/docs/guides/the-editor/editing-objects/)

| Section | Select whole section | Detailed layers |
|---|---:|---:|
| Ship | 90 | 100–109 |
| Wave | 91 | 110–119 |
| Robot | 92 | 120–129 |
| Press and cube transition | 93 | 130–139 |
| UFO | 94 | 140–149 |
| Factory exit | 95 | 150–159 |

The last digit of each detailed layer identifies its contents:

| Last digit | Contents |
|---:|---|
| 0 | Original gameplay collision objects |
| 1 | Portals, orbs, speed portals and their frames |
| 2 | Block bodies |
| 3 | Block surface detail |
| 4 | Spike and hazard skins |
| 5 | Room background |
| 6 | Machinery and supports |
| 7 | Fire, glow and lights |
| 8 | Ash, smoke and soot |
| 9 | Triggers and rotation pivots |

Examples: **131** selects the cube/press interactions and their frames; **144** selects the UFO hazard skins; **93** selects the complete press/cube assembly. Use **All** to view the complete level. Some categories are empty in short sections. Moving press pieces, orb frames, rotating machinery and ash clouds stay assigned to their owning section even when they span a section boundary. Triggers can be positioned earlier than the objects they control.

There is also a guide inside the editor on **layer 99**, above the play area at approximately **(17300,2200)**. It has no gameplay collision or trigger group. The guide is not part of the visible playfield.

Organizing major elements and documenting the layer plan follows the Creator School decoration workflow. The serialized layer fields are **20** and **61**; render fields **24** and **25** are independent. [Decoration workflow](https://www.gdcreatorschool.com/docs/guides/deco-1/how-to-decorate/) · [GD object property reference](https://github.com/gd-programming/gd.docs/blob/main/docs/resources/client/level-components/level-object.md)

## Following blue orb

The previous group-conflict fix is retained. The blue orb at **(22065,75)** and its 86 trim objects use **group 1156**. Its original following Move trigger targets 1156 with its duration, movement offsets and player-lock settings preserved. The 29 later objects remain unchanged in group 24. Their later pulse remains intact, and no Move trigger targets group 24.

## Validation and limits

The validation script checks GMD decoding and metadata, unchanged source data outside the factory, preserved gameplay properties, passable decoration, retained accepted skins and ash, interaction coverage, the blue-orb regression, exit hazard coverage, and layer assignments. See the accompanying validation JSON for results.

The seven preview views use actual game sprite atlases and scripted move/rotate/alpha/color evaluation. They are diagnostic renders, not screenshots of this export running in Geometry Dash. Native shaders, camera behavior, player locks and physics are not fully simulated. The native bridge was stale, so native import, playtesting and performance remain unverified.

## Rebuild

Run from this workspace:

```sh
rtk proxy /usr/bin/python3 work/sinking-factory/build_refined.py
rtk proxy /usr/bin/python3 work/sinking-factory/validate_refined.py
rtk proxy /usr/bin/python3 work/sinking-factory/preview_refined.py
```

Build metadata and the final file hash are in `refined-manifest.json` and `refined-validation.json`.
