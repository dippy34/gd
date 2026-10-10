# Visual design guide

**Target:** a dark, scary factory burning down, with the intensity of a furnace.
The owner named Awareness, Flamewall and a furnace as mood references. Those are
references for atmosphere and intensity, not permission to copy another level.

## What the feedback means in practice

| Owner feedback | Practical design interpretation | Failure to avoid |
| --- | --- | --- |
| “random things just sticking out” | Every assembly has a support, mounting point and industrial function | Decorative rods, brackets and cabinets scattered in open space |
| Cube/UFO too minimal, later too crowded | Detail existing structures; keep their silhouettes and negative space coherent | Treating density as a substitute for composition |
| Block and spike design too basic | Fitted plate faces, seams, bevels, controlled edge light and a readable cutting edge | Bare triangular outlines with a glow halo |
| Darker, realistic burning ash | Small irregular dim flakes, varied drift and occasional hot embers, behind interactions | Uniform bright confetti or thick white squares |
| Keep custom orbs, undo custom portals | Orbs can be pressure-switch machinery; native portal language stays recognizable | Replacing portals with large custom rings/cages |
| Liked old ship, wave and robot | Preserve those designs while fixing identified weak areas | Redesigning accepted sections to make everything match a new experiment |
| More atmosphere and factory identity | A coherent room with furnaces, vents, ductwork and structural supports | Generic fire color applied to unrelated geometric decorations |

These implementation ideas are interpretations of feedback, not invented proof
that the owner approved any particular new asset.

## Build an assembly, then a room

Start with the collision silhouette. It is the boundary of a platform, blade,
beam or housing. Fit a dark body inside it. Add a restrained metal rim, surface
seams that obey the body, and fasteners at plausible joints. Pick one focal
detail: a vent, heat slit, gauge, access plate or actuator. Connect it to the
room's structural logic. Stop before every empty patch is filled.

A suspended block needs a purposeful suspension or reads as an intentional
gameplay platform with a complete casing. A pipe ends at a coupling, wall or
machine. A press head connects to its guide/support and all attached art shares
the relevant movement group. A fan's rotating blades sit inside a fixed casing
around one pivot. Do not stack unrelated functions into the same small object.

## Depth and contrast

Keep masonry/structure darkest, machinery a little clearer, playable surfaces
distinct, and heat sources brightest. Use orange/red light near furnaces or hot
metal rather than evenly distributed decorative lights. A few warm highlights
carry the factory mood; bright white rectangles or rainbow trim fight it.

Dark atmosphere still needs intentional silhouettes. The older v8 request for
very difficult visibility does **not** justify hiding this factory's hazards.
Inspect at the actual camera scale, not only zoomed out in the editor.

## Motion has a cause

Good candidates are turning fans, swaying suspended parts, falling ash, fire at
vents and a press following its original motion. Use sync accents selectively:
a pressure release, heat bloom or mechanical stroke can answer a strong beat.
Constant flashing blocks make the visual rhythm monotonous and distracting.

Keep foreground effects away from essential interactions except where a new
explicitly approved mechanic calls for occlusion. Inspect the beginning, middle
and extreme positions of each moving assembly, including camera transitions.

## Custom interactions

The approved custom-orb concept is an industrial pressure switch. Keep its native
hitbox, functional settings and source groups. Hide only the visual core if using
the existing alpha method. Attach the replacement art to the same motion groups.
Its frame must communicate an interaction without becoming a bright white dot.

Portals use their original appearances with the previous restrained trim. Do not
stretch them or add large replacement frames. The earlier demand for enforced
portals belongs to v8 gameplay; preserve factory portals as supplied.

## Critique before increasing object count

For every changed screenshot, answer:

1. What is the focal assembly, and what factory function does it express?
2. Which pieces are attached to it, and where are their endpoints/mounts?
3. Is the gameplay silhouette distinguishable from the background?
4. Is added detail concentrated on useful surfaces or cluttering open air?
5. Does the warm light have a plausible source? Does the scene retain darkness?
6. Does the section keep its identity rather than repeating a prefab?
7. Do all movement extremes and the final exit remain complete and coherent?
8. What did a native test prove, and what is only a diagnostic estimate?

Use [the critique template](../examples/critique-template.md). Compare with the
owner's actual [negative examples](VISUAL_EXAMPLES.md), not just an earlier
assistant's self-assessment. “Rate worthy” and “feature worthy” are aspirations,
not guarantees an automated checker can award.
