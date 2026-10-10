# v8 — darker false routes and eased wave

[Final .gmd](v8-1573528-nocturne.gmd) · [Preview](v8-1573528-nocturne-preview.png) · [More rooms](v8-1573528-nocturne-more-views.png) · [Validation](v8-1573528-nocturne-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× speed for **85.71%** of the timeline. **34,010 objects**. All seven requested modes, excluding swing.

## This revision

**Wave:** Added 5.5 world units of clearance on each side of the reference path, widening the openings by 11 units. This applies to both waves' ducts, knife gates, floating barriers and phrase boundaries. Their input timings, speed portals, gravity changes and mini/normal transitions remain the same.

**Spider:** Restored the older spider's rows of framed landing shelves, with multiple false shelves at different heights and apparent openings cut across still-solid banks. Real and false shelves share the same dim frame treatment. False rails terminate at actual pillars so the linework follows the structures. Both spider sections retain their existing collision geometry and timings.

**Fakeouts:** There are 244 false teleport shelf segments, 136 false landing rails and 597 apparent openings in solid banks across the level. The two spider rooms contain 385 of these individual visual decoys. False shelf artwork is non-colliding; a false opening masks a bank whose original collision remains active. These visual choices replace the previous sparse, small recesses.

**Darkness and switches:** The background is black. Structural fills use RGB (5, 6, 5); contact edges use (12, 14, 10). The white randomized-orb artwork is hidden and replaced with small, dim olive switch plates, without glow, particles or pulses. Their brightest channel is (26, 29, 20). Ordinary colored gameplay orbs and mode/size/gravity portals retain their native designs.

The 34 independent random decisions keep the same rule: **wall present → hit the switch; wall absent → skip it.** A wrong hit creates the wall. The native input objects, Claim Touch setting, groups and random trigger branches remain intact. The relevant native properties were checked against [FlowVix's schema](https://github.com/FlowVix/gd-info-explorer/blob/main/src/lib/schema.txt); the [official editor guide](https://www.robtopgames.com/files/GDEditor.pdf) documents trigger-orb and group behavior.

## Checks

- Imported the final .gmd into GD with **34,010 objects**; native object counts and the new palette match the export.
- Inspected the [dim switches during native play](v8-1573528-nocturne-native-switches.jpg), the [first spider room](v8-1573528-nocturne-native-spider.jpg), and the [second wave](v8-1573528-nocturne-native-wave.jpg). The opening preview used the existing Ignore Damage setting. The bright magenta squares and controls at the upper left belong to the installed preview interface.
- Inspected 20 atlas-based camera views spanning all 15 rooms.
- All **49,408 route samples** pass; independent approximate replay passes all **15 rooms**.
- Verified all non-wave collision objects and the complete input score against the preceding branching export. Verified the 11-unit increase at each wave gate.
- All 34 switch circuits pass both starting-state cases. Native import preserves hidden-orb, Claim Touch and non-colliding switch-art properties.

**A full damage-enabled native completion and exact demon difficulty remain unverified.** The physics model approximates triangle collisions, portal offsets and buffering. The darker presentation and extra false routes still need player feedback for final balance.

Earlier exports remain intact. Rebuild details are in `work/CURRENT.md`.

SHA-256: `9475e0337baeb567baf6fa5719a9dadd85f3b43b51786d9ed6e91c07636706cc`
