# v8 — Obsidian Choir revision

The revised **v8.gmd** starts from the bare layout. The supplied decorated file was used as a visual reference for its black holes and warm-to-violet colour progression. Your original files in Downloads are unchanged.

## What changed

- Replaced the previous reticles, tick marks and machinery motifs with a continuous cosmic setting.
- Built orange, pink and purple accretion discs with black apertures. The wave includes a binary pair, a tilted lens, a broader corona and a final quasar with polar jets.
- Gave the cube sections raised platforms, step-down landings, low-ceiling pink-orb rebounds and yellow/pink orb vaults. There are 10 authored phrases and 28 planned inputs.
- Preserved all 12,173 protected wave-wall, transition and mode/speed/camera objects exactly. The wave route, song and speed schedule are unchanged.
- Used the actual collision boundaries for platform lips and wave outlines. Every added decoration has No Touch and Passable enabled. Motion groups contain decoration only.
- Included low-detail support: 53,735 objects normally, 41,786 in low detail. Core black holes, route markings and gameplay remain visible.

## Research and measurements

The attached reference has 37,430 objects. Its colour triggers begin a long amber transition near x=11,498 and a violet transition near x=15,710. Its black-hole construction separates the aperture, luminous annulus, flattened disc and rotating detail. This revision develops those ideas into a stronger orange/pink/purple palette rather than reusing the previous cool observatory palette.

The [GD Creator School gameplay guide](https://www.gdcreatorschool.com/docs/guides/gameplay-1/using-gamemodes/) explains the cube’s fixed arcs and how different orb interactions vary its patterns. The [pacing guide](https://www.gdcreatorschool.com/docs/guides/gameplay-2/pacing-progression/) informed the progression from simple terraces to combined orb vaults. Phrase starts follow the handoff’s 170 BPM grid; intermediate jumps and orb positions are placed for their arcs and landing space.

The [background guide](https://www.gdcreatorschool.com/docs/guides/deco-1/making-backgrounds/) and [polishing guide](https://www.gdcreatorschool.com/docs/guides/deco-1/polishing/) informed the depth, contrast and layer separation. Background glow was reduced after the first rendering pass so the route stays readable.

The [official editor guide](https://www.robtopgames.com/files/GDEditor.pdf) is the reference for object behaviour and editor controls. Format and local import conventions were cross-checked against [GMD API](https://github.com/HJfod/GMD-API).

## Checks and limits

The final file was read independently through a standard XML/plist parser and decompressed again. Object count, name, song, colour references, movement groups, protected source objects and the No Touch/Passable flags passed the audit. The level remains an unverified local draft.

Both rebuilt cube sections pass a continuous, independent 240 Hz ballistic clearance model. The model checks blocks, full spike triangles and orb reach, with timing and parameter sensitivity tests. Nominal normal-jump impulse is an estimate of 604.8 units/s; gravity 2727.35 units/s², yellow-orb impulse 590.85 units/s and pink-orb impulse 418.5 units/s are based on the empirical values documented by [GDForge](https://github.com/hannesgook/gdforge). Four neighbouring jump/gravity combinations also had passing input schedules. These are approximate calculations, not a reproduction of Geometry Dash’s engine.

The preview uses the installed game’s sprite and font atlases, plus approximate glow, colour-trigger and rotation rendering. A full sequence of 60 diagnostic views and low-detail comparisons was generated for review. It is not a native gameplay capture.

**Native import and a full in-game completion have not been verified.** Playtesting, performance on target devices, and moderator judgement are still required before calling this feature-ready. No rating or feature is promised.
