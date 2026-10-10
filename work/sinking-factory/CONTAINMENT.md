# Factory Containment — current revision

Current deliverable: `outputs/The Sinking Factory - CONTAINMENT.gmd`.
In-game name: Factory Containment. 11,871 objects; 5,251 added. Source remains untouched.

The user rejected the prior Inferno pass as disconnected and nonsensical. This revision discards its entire added-object list and builds again from source geometry. No free-floating flames, sparks, smoke balls, collapsing beams, or diagonal exhaust bars remain.

Ship and main-wave armor follow the native slope hypotenuses. Their outward sides connect to full metal walls; panels and cooling vents are geometrically clipped inside those walls with an 11-unit edge setback. The 10 intersecting wave-intro chevrons remain shallow so their existing openings are not visually filled. Straight wave lips mount into outward wall bodies. Robot plates use unions of the actual occupied grid cells, separated by movement group. UFO assemblies attach to rear rails via thin dim cables. Eight framed furnace apertures supply heat and 16 contained sliding shutters supply motion. Existing source UFO distortion and camera movement remain.

Original objects change only color/draw-order properties, apart from one explicit visual inversion reset at the drop. Its original steady state is restored at the section boundary. All original collision, timing, mode, speed, gravity, orb, music, and gameplay-trigger properties remain unchanged. New visible objects have both NoTouch and Passable. New art is on editor layer0/secondary30 so it can be inspected with the original layer visible. All new object centers stay in the drop–75% region. Scenery is spatially confined and fades at the exit; it can naturally be seen ahead as the camera approaches.

Checks: source SHA; exact GMD roundtrip; physical property comparison; dedicated IDs; no new collidable/decorative hazard objects; clipped polygon tessellation area coverage; shutter travel stays within frames; 10 intro chevrons preserved. The tessellation check caught a missing concave panel region; the renderer now clips intersecting triangles and fills the complete polygon.

Preview sheet uses native sprite atlases and approximate procedural outlines/camera centers. It does not reproduce native shaders. This revision was not imported or playtested in the game: UI click calls were failing, native bridge was disconnected, and the optional request to leave GD at the main menu had not received a reply at export time. Do not claim native verification.

Files: build_structured.py, structured.level, structured-manifest.json, validate_structured.py, structured-validation.json, preview_structured.py, structured-sheet.png, and audit/slope-boundaries.json.
