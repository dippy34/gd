# Factory Meltdown v2

File: `~/Downloads/The Sinking Factory - MELTDOWN v2.gmd`. In-game name: **Factory Meltdown v2**.
It is built on the shipped MELTDOWN file, which is left untouched in Downloads.

## What changed

The goal was a Flamewall/Avernus look with more atmosphere, and parts that blend together. Everything added is decoration.

- **Lighting pass over the existing MELTDOWN decoration.** Every MELTDOWN deco object now takes its brightness from a light map built from the real heat sources: fires, furnaces, lava streams, lamps and glowing corridor seams. Metal far from heat drops to near-black, and vents only glow when they're close to fire. This is what removes the flat "wallpaper" look.
- **Darker metal colours.** The metal colour channels were retuned toward near-black. The glowing corridor seams are stronger.
- **Background haze** sits behind the machinery, brightest at the bottom. Distant stacks, girder towers and cranes stand in the fog behind it.
- **Glow at every heat source**, a warm glow down the ship and wave corridors, and a lava sea with Flamewall-style fire tongues under the UFO hall.
- **Embers and smoke.** About 1,050 embers rise across the whole drop (moved by triggers), plus about 100 blurry out-of-focus embers in front and drifting smoke.
- **Avernus-style swinging maces on chains** and **Flamewall-style hanging lit panels**, behind all gameplay.
- **Black foreground edges** with hot glowing rims and lava drips. They only appear where the player can never be.
- **A dark soft backing behind every spike cluster and orb**, so orange outlines stay readable over the brighter background.
- **Section edges fixed.**
  - The entry no longer shows a hard wall edge when the camera zooms out at the drop.
  - The exit no longer cuts from dark to white. The foundry now burns out into white-hot light that meets the original white segment.
- **Lights pulse** on the same 32 measured beats MELTDOWN already used.

## How it was matched to the references (measured, not eyeballed)

1. Flamewall (126242564) and Avernus (89496627) were downloaded from the game's level API. Their layers, colours and glow-orb sizes were measured object by object.
2. Frames were sampled from both verification videos: 84 from Flamewall and 50 from Avernus. Each frame was measured for dark share, brightness, contrast and top-to-bottom light. Every preview of this build was measured the same way.

The table uses the 7 gameplay shots. The exit flare shot is left out.

| Measure | Avernus video | Flamewall video | MELTDOWN before | MELTDOWN v2 |
|---|---|---|---|---|
| Near-black share of screen | 0.573 | 0.512 | 0.361 | 0.453 |
| Bright share | 0.033 | 0.039 | 0.027 | 0.035 |
| Average brightness | 0.099 | 0.116 | 0.144 | 0.123 |
| Contrast | 0.145 | 0.160 | 0.125 | 0.142 |
| Bottom vs top brightness | 2.29x | 1.69x | 1.00x | 1.81x |

The ship section (the furnace intake) stays brighter than the references because of MELTDOWN's big furnace windows. The other sections sit at 0.45–0.60 near-black.

## Gameplay safety (checked by `validate_v2.py`, all passed)

- All 6,620 original objects are identical to MELTDOWN's copies. MELTDOWN itself only changed their colours and draw order.
- MELTDOWN's decoration objects only gained a brightness (HSV) value. The header settings and song (1569886) are unchanged.
- 5,864 objects were added. Every one is decoration with NoTouch and Passable.
  - Only decoration object types are used, with no hazards or blocks.
  - They use new colour channels 650–682 and new groups 700 and up, so nothing collides with existing IDs.
- No solid object drawn in front of gameplay overlaps any gameplay object.
- No solid object drawn in front of gameplay covers any space the player can reach. This was checked by flood-filling each gamemode's free space from its portal, dead ends included.
- The .gmd decodes back to the exact level string. Object count: 42,643.
- Most heavy decoration is marked high-detail, so Low Detail Mode hides it.

## Limits

- **Not imported or playtested in Geometry Dash.** The in-game check needed control of the game, and that was declined, so every screenshot is an atlas render.
- The renders use the game's real sprites, colours, layers, pulses and movement. They don't reproduce shaders, animated fire frames or exact camera behaviour.
- Glow orbs (objects 1886–1888) are drawn by the game itself, so their exact size in the previews is estimated. Their sizes and density follow Avernus's measured usage, so in-game they should look like Avernus's glows.
- Frame rate at 42.6k objects has not been measured.

## Files

- `The Sinking Factory - MELTDOWN v2 Preview.png`: eight gameplay shots.
- `... Before-After.png`: MELTDOWN versus v2 at the same camera positions.
- `... vs References.png`: v2 next to Avernus and Flamewall rendered with the same renderer.
- `... Full Section.png`: the whole drop end to end, at the camera's height.
- `... Measurements.png` and `... Validation.json`.

Rebuild: `/usr/bin/python3 work/sinking-factory/v2/v2_export.py`. Previews: `v2_preview.py`, `v2_strips.py`, `present.py`.

SHA256: `92e802586c6513bc1ae8caaea704014a9e1fa97bdbb6625b9a020115fa944629`
