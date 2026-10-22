# Check whether an agent understood the pictures

Open the corresponding pictures in [the guide](../docs/VISUAL_EXAMPLES.md).
These are critique exercises with reference answers, not proof that an AI has
been trained. The reference answers state the intended lesson, not a universal
rule for every Geometry Dash level.

| Picture | Ask the agent | What a grounded answer should notice |
| --- | --- | --- |
| 01 | Which addition would you reconsider first, and what would you preserve? | The tall rod bundle / neighboring cabinet compete with the orb and existing machinery. Preserve coherent platform casing and useful surface detail. |
| 02 | Why does a finished center frame not prove the part is decorated? | The default exit and bare final hazards reveal missing coverage. Check the end and the runtime fade, not only geometry centers. |
| 03–04 | Why preserve these sections without copying every object? | The owner liked their identity. Continuous fitted edges and recognizable machines work; that is not approval of every old orb/spike or renderer artifact. |
| 05 | What must be classified before removing objects? | Source gameplay hazards, their decorative skins, background machinery and editor UI are different things. Do not delete hazards to cure decorative clutter. |
| 06 | Why did closing the fire border not solve the visual problem? | Coverage is functional; the repetitive rectangular border and oversized flame motifs still flatten the scene. A static atlas image does not prove animation quality. |
| 07 | What changed besides the outline color? | Steel faces, restrained rims, inset detail and attachment to the casing. Collision geometry should remain unchanged. |
| 08 | How can an orb look custom without becoming a different mechanic? | Retain the native orb logic; alpha-hide only its old visual core and carry custom art with the same movement. Do not Toggle off the orb. |
| 09 | Did the owner reject all custom interactions? | No. They first requested both, then reverted custom portals while keeping custom orbs. Follow the latest component-level decision. |
| 10 | Why did distant objects appear to vanish? | A moving orb shared group 24 with later objects. The saved fix targets 1156 for the orb/trim and preserves later group 24 and its pulse. |
| 11–12 | Are these completed improvements? What would make them convincing? | They are unbuilt diagrams. Test a single purposeful assembly and motion states in the game, then inspect readability, attachments, coverage and performance. |

For a later change, have the agent answer in this form:

> Picture and marker: …
> What I can actually see: …
> Owner decision versus my interpretation: …
> Specific local change: …
> Components I will preserve: …
> Evidence I need before calling it successful: …

Red flags: “add more objects,” “make everything custom,” “copy this entire good
screenshot,” “the data validator proves it looks good,” or treating a future
diagram as new approval to edit the level. Use the [critique template](critique-template.md)
to record an actual subsequent review.
