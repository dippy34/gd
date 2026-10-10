# Factory Encroached

Import **The Sinking Factory - CLOSING-FIRE.gmd**. The level's in-game name is **Factory Encroached**.

This adds the supplied concept: a dark, burning frame around the camera that gradually closes inward during the factory. Its four edges contain red fire beds, orange native looping flames, brighter tips and drifting ember chips. Dark corner masks cover the intersections. Nominal thickness grows by 1.5×, then the entire frame fades away before the next section.

The custom pressure-switch orbs, restored native portals and previous metal trim, steel spikes, factory artwork, editor organization and blue-orb group fix are preserved. Every one of the preceding export's 57,465 objects is unchanged. This export adds 3,605 effect objects, for 61,070 total. It adds no collision objects.

## Timing

Timing comes from the level's existing speed-portal schedule, with no gameplay or speed changes. Times below are level elapsed time.

| Event | Time | Level X |
| --- | ---: | ---: |
| Fade in over 0.7 seconds; begin closing | 47.93693 s | 16,785 |
| Reach final thickness | 63.87605 s | 24,600 |
| Begin fading out | 64.29272 s | 24,795 |
| Fully transparent | 64.57049 s | 24,925 |

The side borders advance 16 UI units, from nominal 32 to 48. The top and bottom advance 12, from nominal 24 to 36. Individual flame tips and embers have irregular outlines.

## Editing

Select **editor layer 2 = 96** for the entire effect. It is authored above the level around **X 17,400 / Y 3,800**; its UI reference is there. Controls are on primary layer 169 near the section's X coordinates.

| Primary editor layer | Contents |
| --- | --- |
| 160 | Fire beds and dark outer masks |
| 161 | Native animated flames |
| 162 | Soft heat light |
| 163 | Embers |
| 169 | UI reference, movement and alpha controls |

Group 1200 controls the whole effect's opacity. Groups 1201–1204 anchor the left, right, bottom and top edges. Group 1205 is the separate reference object. Groups 1220–1235 move ember cohorts. Channels 760–767 are exclusive to this effect. Existing groups and channels are unchanged.

Four UI triggers use explicit screen-edge references. The effect therefore does not rely on a particular gameplay camera zoom. The top and bottom strips extend far enough for 4:3, 16:9 and 21:9 frame dimensions. The UI applies from level initialization; alpha triggers control when the frame is visible.

## Verification and limits

The `.gmd` was decoded again and compared with the preceding export. Exact preservation, color and group isolation, UI target wiring, movement direction/duration, the 1.5× nominal expansion, fade timing, editor layers and aspect-ratio bounds pass `closing-fire-validation.json`.

The previews use the game's sprite atlases and model the UI placement and trigger transforms. The early and late views deliberately use the same ship backdrop to make the closing motion easy to compare. They are diagnostic renders, not screenshots of a native playtest. They do not verify runtime behavior, player visibility, performance or playability. Native app control returned `noWindowsAvailable`, so in-game verification remains outstanding.

The UI properties and 480×320 reference were checked against the installed game's UI positioning code and [Geode bindings](https://github.com/geode-sdk/bindings/blob/main/bindings/2.2081/GeometryDash.bro). See also [Creator School's UI guide](https://www.gdcreatorschool.com/docs/guides/triggers-1/ui-link-visible/) and the local `research/ui-native-properties.md` notes.

Build: `work/sinking-factory/build_closing_fire.py`. Check: `work/sinking-factory/validate_closing_fire.py`. Preview: `work/sinking-factory/preview_closing_fire.py`. Invoke with `rtk proxy /usr/bin/python3` from the workspace root.

Export SHA-256: `ad165aafe07f19a33bb5cb64aa8fc9230828428cccd33b2650bd1000b9926b61`.
