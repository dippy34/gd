# Factory Meltdown

Final file: `The Sinking Factory - MELTDOWN.gmd`
In-game name: **Factory Meltdown**.

A fresh decoration build from the original Sinking Factory, limited to the approved drop through approximately 75% (x 16785–24660). The original source file remains untouched. None of the Inferno or Containment decoration object lists is imported.

## What changed

- Furnace intake: barred furnace mouths, curved layered fire silhouettes, animated native flames, bolted pressure jackets, casing ports and warm light spill.
- Wave: heated cable trays follow the source walls; large enclosed turbines rotate behind the corridor, with connected pressure pipes and localized rupture sparks.
- Robot/cube: suspended ladles tilt over fixed catch troughs, molten streams connect nozzles to receivers, and the original moving platform carries its new metal skin.
- UFO: an extraction turbine hall with inset rotor blades, chain suspension, connected pipework, floor fires and drifting soot/embers.
- Local lighting accents use 32 measured audio onsets. Song-position estimates come from the source speed schedule; native portal activation timing has not been calibrated.
- 58 movement/rotation triggers, 15 main machinery assemblies, and 28 fire/spark emitters. The source drop shake is retained.

## Research and visual reference

I inspected the actual Flamewall reference image on [AREDL](https://aredl.net/list/126242564), especially its concentric mechanical detail, layered borders, chains, narrow hot highlights and negative space. I also inspected the [Avernus reference image](https://aredl.net/list/89496627) for silhouetted foreground depth, molten highlights and smoky red light. Avernus was a possible interpretation of “Awareness”; that name was not confirmed by the user.

The [GD Creator School pulse guide](https://www.gdcreatorschool.com/docs/guides/triggers-1/pulse/) informed channel-specific fade-in, hold and fade-out accents. All artwork uses native Geometry Dash objects, with sprites and dimensions checked against the installed game atlases. No reference level's geometry was copied.

## Validation and limits

- 36,779 total objects; 30,159 added.
- Compression/decompression round trip and object count passed.
- All original gameplay properties and source control triggers remain unchanged. 920 original structures/hazards receive color and draw-order edits only.
- One local visual inversion reset is applied and restored at the end of the section; the original glitch trigger remains.
- Every added decorative object has NoTouch and Passable enabled. New groups/channels do not collide with source IDs.
- Song remains 1569886, as in the original Sinking Factory.
- Six atlas renders were inspected and revised. Those renders simulate color, alpha, move and rotate triggers; they do not reproduce native postprocessing, camera behavior or animated-fire frames exactly.
- The native bridge was disconnected. This build has **not** been imported or playtested in Geometry Dash, and performance at this object count is unmeasured.

SHA256: `1594aee95a1b48e0ff52b497ce68e29e3e46aca6a9c0dd72aa76fa679441426d`

## Rebuild

Use the system Python that has the existing NumPy/Pillow installation:

```sh
rtk proxy /usr/bin/python3 work/sinking-factory/build_meltdown.py
rtk proxy /usr/bin/python3 work/sinking-factory/validate_meltdown.py
rtk proxy /usr/bin/python3 work/sinking-factory/preview_meltdown.py
```

The working geometry module uses the existing workspace-local Shapely dependency.
