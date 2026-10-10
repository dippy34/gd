# Fire takeover research and decisions

## Visual reference

Reviewed OneAlphaHelix's original [Flamewall showcase](https://www.youtube.com/watch?v=wZbqwUv5NI8), including the orange mechanical section around 5:33 and the large flame backdrop near 6:40. The latter uses large overlapping flame silhouettes, red/orange depth and bright fire behind dark structures. The relevant takeaway for this project is the scale and mass of the fire. This is visual interpretation of the showcase, not a claim about the creator's construction method. No artwork or objects were copied from Flamewall.

Also inspected [GEAR III gameplay](https://www.youtube.com/watch?v=ryzLR-eQQ0k) around 0:41 as a secondary contrast reference. Its subdued red fog and black silhouettes are useful atmosphere references, but it was not the main reference for the engulfment.

## Why the preceding effect failed

- Tiny repeated flames outlined a rectangle. They did not read as an approaching wall of fire.
- The previous movement advanced only 12–16 UI units and faded out before its endpoint; it could never engulf the player.
- Independent X/Y scale distorted preset proportions.
- The diagnostic renderer used the fire detail sprite's half-resolution atlas dimensions without the game's 2× detail scale. That made the preview look hollow. This was a preview defect, separate from the user's valid design criticism.

## Native preset evidence

Examined the installed game's `FireSheet_01-hd.plist` and corresponding atlas. Preset IDs 920, 923 and 924 map to `Fire_03_looped`, `Fire_01_looped` and `Fire_02_looped`. Each has nine looping native frames. Detail names use `Fire_03_2_looped`, etc. Their source sizes are about half the outline sizes; the native `GameObject::setupCustomSprites` routine includes the 2× child scale at arm64 address `0x1003b6090`. See `fire-spritesetup-disasm.txt`. The new diagnostic preview uses the actual outline and detail frames, aligns their centers, and models that detail scale. No replacement sprite asset is installed in the level.

[Geode's 2.2081 bindings](https://github.com/geode-sdk/bindings/blob/main/bindings/2.2081/GeometryDash.bro), `EnhancedGameObject`, documents these saved fields:

| Property | Function | Export setting |
| --- | --- | --- |
| 106 | Randomized animation start | Enabled |
| 107 / 122 | Animation speed / use speed | 1× / enabled |
| 123 | Animate on trigger | Disabled; continuous native animation |
| 126 | Disable delayed loop | Enabled |
| 127 | Disable animation shine | Enabled |
| 214 | Animate only when active | Disabled |
| 462 | Single frame | Omitted |

The native UI settings were already verified separately in `ui-native-properties.md`. The new front groups are 1201–1204; 1205 is the separate UI reference. A fifth centered UI group, 1210, supplies the final full-screen native flame layer.

## Replacement

Rebuild from CUSTOM-ORBS, removing the rejected effect entirely. Use three overlapping rows of broad native preset 920, with occasional taller 923/924 tongues. Every preset uses uniform scale. The visible boundary consists of animated fire. The rectangular backing fills start offscreen behind the fire and guarantee closure near the end.

Move the fronts progressively inward, from small peripheral flames to substantial intrusion. Travel increases over four continuous segments, reaching 330 UI units for top/bottom and slightly more on the sides. The top and bottom backing fills overlap vertically by 74 units at the endpoint. A 0.36-second late crossfade adds a centered screenful of larger native flames over an opaque red fire backing. Full engulfment is reached 0.14 seconds before the factory boundary, then cuts to the next part at X 24,925. The old 1.5× limit is superseded by the user's request for complete engulfment.

## Verification limits

Reviewed real atlas renders at start, middle, closing, full engulfment, wide aspect and exit. The randomized frame samples illustrate possible native frames; they are not a deterministic replay of the engine's random seed. The render does not simulate player physics or certify gameplay visibility.

The current native game can be screenshotted and shows the preceding Factory Encroached import. Native clicks still return `noWindowsAvailable`, so the new import has not been playtested. The `.gmd` data, UI wiring, animation settings, collisions, group isolation and full-screen coverage geometry were checked independently.
