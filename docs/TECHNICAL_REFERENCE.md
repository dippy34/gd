# Technical reference

This is an observed project schema, not a complete Geometry Dash specification.
Unknown fields must be preserved. [External references](ASSETS_AND_ATTRIBUTION.md)
and local research can help, but do not infer native behavior from a field name
without verifying the relevant object type and game version.

## File format

The `.gmd` exports here are GDShare-style XML/plist dictionaries. `k4` contains a
URL-safe base64 compressed level string. Decoding gives a header, then semicolon-
separated objects. Each object is comma-separated property/value pairs.
`work/handoff/tools/gmd.py` handles this wrapper and `gdparse.py` parses the data.

Metadata includes `k2` name, `k45` song and `k48` stored object count. The original
factory source stores6619 while parsing yields6620 objects; preserve the source
file and distinguish stored metadata from measured counts. Current Factory Orbs
has57465 in both. Never discard unfamiliar metadata to simplify a rewrite.

| Property | Use in this project |
| --- | --- |
| 1 | Object ID |
| 2 / 3 | X / Y position |
| 4 / 5 / 6 | Horizontal flip / vertical flip / rotation |
| 128 / 129 | Independent X / Y scale; some older objects use32 |
| 20 / 61 | Primary / secondary editor selection layers |
| 21 / 22 | Main / detail color channels |
| 24 / 25 | Render Z layer / Z order — unrelated to editor layers |
| 57 | Dot-separated group membership |
| 51 / 71 | Target/secondary or center reference on relevant triggers; semantics vary |
| 10 | Duration on relevant triggers |
| 28 / 29 | Move offsets on Move triggers |
| 35 | Opacity on Alpha triggers |
| 56 | Enabled state on Toggle triggers |
| 121 / 134 | NoTouch / passable flags used by added decoration |
| 135 | Hidden object flag; do not substitute it for the established orb-alpha method |
| 96 / 64 / 67 | NoGlow / Don't Fade / Don't Enter flags in these builders |
| kS38 | Header color-channel definitions |

Example object IDs used here:211 filled square,693 filled right triangle,
901 Move,1007 Alpha,1049 Toggle,1346 Rotate,84 blue orb,36 yellow orb.
An ID is a native object definition, not an arbitrary label. The atlas mapping
is in [objectids.yml](../work/handoff/research/objectids.yml).

## Section boundaries and editing

| Section | X interval | Secondary layer | Primary layers |
| --- | --- | --- | --- |
| Ship |16785–18195|90|100–109|
| Wave |18195–20685|91|110–119|
| Robot |20685–21800|92|120–129|
| Press/cube |21800–22665|93|130–139|
| UFO |22665–24600|94|140–149|
| Exit |24600–24925|95|150–159|

Last primary digit:0 original collision,1 interactions/frames,2 block bodies,
3 surfaces,4 hazard skins,5 room background,6 machinery,7 fire/light,8 ash/smoke,
9 triggers/pivots. Layer 99 holds the off-playfield editor legend near(17300,2200).
Group ownership overrides simple X classification for moving assemblies; a
trigger can sit earlier than the section whose objects it controls.

## Groups and colors

- **600**: main factory visual group; fades out after the last hazards.
- **25**: existing moving press assembly. Attached art must share its motion.
- **1156**: isolated following blue orb and105 custom trim objects. No later scenery.
- **24**: original later objects/pulse. No Move should target24 in the baseline.
- **1157**: only the eight native orb cores whose appearance is replaced. Alpha0
  hides the native art; Toggle would disable interaction and is forbidden here.

Read the actual manifest for all ash, fog, rotation and other allocated groups.
Color definitions are under `colors` in the baseline manifest, extending the
original channels. Search both group membership and every trigger reference
before allocating. Field51 sometimes names a color or other target depending
on trigger type. A simple max(field 57) scan alone is insufficient.

The [group fix example](../examples/blue-orb-group-fix.json) and
[custom orb excerpt](../examples/custom-orb.json) are actual serialized objects.
They are partial excerpts, not standalone importable assemblies.

## Time and visual coverage

`inspection-plan.json` and the baseline manifest store the speed schedule as
`[start_time, world_units_per_second]` segments. Integrating each segment gives
X; inverse integration gives level time. Do not use a single X/time ratio across
speed changes. Measured decorative onsets are frozen in the baseline manifest.
Audio itself is not bundled. The active rebuild reuses those exact measurements.

Decoration coverage extends to24925, while master fade controls are at24985 and
25105. An object's center alone does not describe its rotated/scaled extent or
where it moves. Inspect both the serialized geometry and animated state before
claiming coverage. Check the source size/gravity state for gameplay work.

## Rendering limits

`render.py` uses the player's locally installed HD atlas (`GD_RESOURCES`); atlas
pixels/world units and sprite defaults matter. It is an approximation. The
preview scripts model selected colors, alpha, move and rotation triggers. They
do not implement the full engine, camera, UI anchoring, shader stack or physics.

Historical stock fire investigations found a native fill layer scaled2× relative
to its atlas frame; different old previews used different corrections. Do not
treat every historical flame screenshot as exact. The native bridge was stale;
no bridge code is silently enabled by this handoff. See the labeled native status
reports for historical context only.
