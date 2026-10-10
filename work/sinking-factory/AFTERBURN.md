# Factory Afterburn

Atmosphere revision of Factory Meltdown. Import **The Sinking Factory - AFTERBURN.gmd**; the in-game name is **Factory Afterburn**. The earlier Meltdown export and the original Sinking Factory file remain unchanged.

## Changes

- Replaced the faint rising particle layer with 1,593 falling ash/cinder particles spread across the selected section. Three depth planes fall at 31, 61 and 93 world units per second, with lateral drift and locally timed starts.
- Added 50 groups of ceiling soot, exhaust haze and thin suspended-dust wisps. Darkened the wall/panel palette and reduced the even edge lighting while retaining the stronger light from fire and molten streams.
- Added fitted gauge/control boxes, extraction hoods connected to collectors, supported cable trays, mounted warning lights, and caution paint inside existing ledges. Retained the turbines, ladles and furnace artwork.
- Removed round particle halos during visual review so the ash reads as flakes and streaks.
- The original gameplay, soundtrack, speed portals and camera controls remain unchanged. Decoration stays within the previously approved drop-through-about-75% section and fades before the next section.

## Checks

- 41,641 total objects; every added visual object has NoTouch and Passable enabled.
- GMD round trip, original gameplay-property comparison, object counts, group/channel isolation, and source-file checksum passed.
- The existing trigger evaluator checks all 81 ash groups and samples motion at ship, wave, robot and UFO positions. This verifies downward motion in the diagnostic simulator, not in the native game.
- Six atlas views were inspected. The renderer uses the installed game sprites and simulates move/rotate/color/alpha triggers. It does not reproduce native camera tracking, postprocessing or looping fire frames exactly.
- **Native import/playtest and performance are unverified:** the native bridge was disconnected. No gameplay difficulty/rating claim is made.

The visual direction continues the previously inspected [Flamewall reference](https://aredl.net/list/126242564): warm firelight against dark machinery, suspended debris, and layered silhouettes. The geometry is original, using native GD objects.

SHA256: `3695e6dd472a2305bdc8b2bdb30db549a87df05c7692e8471127a7d3b3b94454`

## Rebuild

```sh
rtk proxy /usr/bin/python3 work/sinking-factory/build_atmosphere.py
rtk proxy /usr/bin/python3 work/sinking-factory/validate_atmosphere.py
rtk proxy /usr/bin/python3 work/sinking-factory/audit_atmosphere_motion.py
rtk proxy /usr/bin/python3 work/sinking-factory/preview_atmosphere.py
```
