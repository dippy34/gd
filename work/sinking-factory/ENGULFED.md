# Factory Engulfed

Import **The Sinking Factory - ENGULFED.gmd**. In-game name: **Factory Engulfed**.

Replaces the rejected thin border with large overlapping Geometry Dash preset flames. Their native looping animation runs continuously with randomized starting frames. The fire closes progressively inward, accelerates near the end, and fully engulfs the screen before the factory section finishes.

The factory, gameplay, custom orbs, restored native portals, steel spikes, blue-orb group fix and previous editor organization remain unchanged. All 57,465 objects from CUSTOM-ORBS are preserved exactly. The old CLOSING-FIRE additions are absent. This export adds 289 objects, including 227 native animated flames, for 57,754 total objects.

## Timing and editing

The fire fades in at X 16,785 (47.93693 seconds of level time). Its fronts advance continuously throughout the part. Full engulfment occurs at 64.43049 seconds; it holds until the factory boundary at X 24,925 / 64.57049 seconds, where the screen clears for the next part. There is no early fade-out.

Select **secondary editor layer 96** for the whole effect. The UI setup is authored around X 17,400 / Y 3,800.

| Primary layer | Contents |
| --- | --- |
| 160 | Fire backing fills |
| 161 | Native flame fronts |
| 162 | Heat light |
| 163 | Final full-screen fire |
| 169 | UI, alpha and movement controls |

Group 1200 controls all effect opacity. Groups 1201–1204 are the four moving fronts; 1205 is the separate UI reference; 1210 is the final fire layer. Channels 760–771 belong to this effect. The full-coverage geometry supports 4:3, 16:9 and 21:9 screens.

## Research and checks

The large flame treatment draws on the [late section of Flamewall's original showcase](https://www.youtube.com/watch?v=wZbqwUv5NI8&t=400s). See `research/engulfed-design.md` for the visual observations, native preset inspection and implementation decisions.

`engulfed-validation.json` confirms the GMD roundtrip, exact base preservation, native animation settings, uniform sprite scaling, group/color isolation, inward movement and full-screen coverage. The preview uses real native atlas frames with corrected fire fill scaling. Its phases use one fixed backdrop to make the closing movement clear.

**Native playtesting remains unverified:** app screenshots work, but native input returns `noWindowsAvailable`. The previews model appearance and geometry, not engine performance or player physics.

Build with `rtk proxy /usr/bin/python3 work/sinking-factory/build_engulfed.py`; validate with `validate_engulfed.py`; render with `preview_engulfed.py` in the same directory.
