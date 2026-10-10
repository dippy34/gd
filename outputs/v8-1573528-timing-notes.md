# v8 — harder timings and deliberate fakeouts

[Final .gmd](v8-1573528-timing.gmd) · [Native opening screenshot](v8-1573528-timing-native-preview.png) · [Section previews](v8-1573528-timing-preview.png) · [Validation](v8-1573528-timing-validation.json)

This revision builds on `v8-1573528-refined.gmd`. The previous file remains intact. Internal name: **v8**. Song: **1573528**. Duration: **3:25.19**. Native 0.5× speed: **85.71%**.

## What changed

- **Cube:** restraints before takeoff catch early jumps; launch gates and orb-exit gates catch late jumps and mistimed activations. The existing musical score and recognizable platform sequences remain.
- **Robot:** takeoff and release have separate constraints. Teeth cover new divider faces so a mistimed release cannot gain an unintended landing platform. Short and long holds retain their distinct authored lengths.
- **Ball:** constrained departures and transfer throats bound both early and late gravity flips; the alternating rail structures remain.
- **UFO:** staggered intake and exit gates tighten hop timing, including the inverted section.
- **Spider:** both rooms have tighter entry and exit shoulders around each teleport. RECALL has the smaller remaining horizontal allowance.
- **Fakeouts:** **100 recessed false doorways** are attached to real wall banks and structural housings. Each leads into an actual solid dead end. Their frame language matches the real openings. Existing memory switches, misleading landing plates, room structures and moving service plates remain.

Both ship rooms and both wave rooms are unchanged, including gameplay and decoration. The corrected size portals, camera refreshes, speed schedule, all input timestamps, and intended route coordinates match the previous revision.

## Timing comparison

These are **approximate model sensitivity intervals**, not verified native click windows. One input is shifted at a time in 1/240-second steps while other inputs stay fixed. Each test stops 0.70 seconds after the input; the successful interval is capped at ±20 steps. Robot release tests change hold duration separately.

| Mode | Distinct input tests | Previous median model interval | New median model interval |
|---|---:|---:|---:|
| Cube | 11 | 112.50 ms | 33.33 ms |
| Robot | 12 | 31.25 ms | 12.50 ms |
| Ball | 6 | 91.67 ms | 8.33 ms |
| Ufo | 6 | 16.67 ms | 8.33 ms |
| Spider | 6 | 29.17 ms | 16.67 ms |

All **41** compared inputs had a smaller successful interval in the new model. The unchanged reference score passes all fifteen rooms. These figures establish a relative change under the same model; they do not assign an Insane/Extreme rating. Some intervals are asymmetric around the reference input.

## Validation and limits

- Native Geometry Dash import succeeds with **27,594 objects**. Native object ID counts match the export; size portals and camera settings survive import.
- All **49,395** nominal finite-body samples pass the exported block/spike audit. All **2,766 spikes** remain within y = 0–300.
- Continuous size-state checks pass, including orb inputs and the second wave's normal/mini alternation.
- All forty live memory decisions still control real barriers. Each added false door was checked against an actual collision bank.
- Ship and wave rooms, initial settings, camera objects and musical input score are compared directly with the previous file.
- Inspected section renders and the native opening. The native visual inspection used the existing Ignore Damage setting.

**Full native completion and exact demon difficulty remain unverified.** The replay does not fully reproduce native physics, buffering, triangle hitboxes or portal contact offsets. In particular, passing these checks is not proof of a complete damage-enabled run.

[Player hitbox reference](https://boomlings.dev/reference/player_physics/hitboxes) and [mode physics reference](https://boomlings.dev/reference/player_physics/gamemodes) informed finite-body and teleport checks. [Earlier revision notes](v8-1573528-refined-notes.md) contain the song, portal-ID and camera research.

SHA-256: `325eb46a7e1ce583694d5056185172b168ada16471ee52e13cb2d7eaf865a3bc`
