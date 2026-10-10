# Factory Inferno

Current export: `outputs/The Sinking Factory - INFERNO.gmd`, also copied to `$HOME/Downloads/The Sinking Factory - INFERNO.gmd`.

The prior flooded/teal art is discarded for this build. All geometry starts from the original source; no flooded-pass added object list is reused.

The ship travels past broken furnace doors; the wave runs through ruptured pressure conduits; robot/cube platforms are scorched press machinery; the UFO section crosses a burning crane trench. The palette is soot, ember red, orange and pale heat. Animated flame silhouettes, rising sparks, smoke and rotating/falling rear beams replace water, quiet fans and clean teal plates. The original UFO glitch effect remains.

There are 4,316 added objects, 10,936 total, and 151 new move/rotate triggers. Original gameplay objects, hitbox properties, orbs, speed/mode/gravity portals, music and gameplay triggers remain unchanged. 920 original objects have color/draw-order changes; one visual inversion trigger is made explicitly neutral in the section and its source state is restored at the end. Every added visible object uses NoTouch and Passable; moving groups affect new background art only except skins inheriting existing platform groups.

The section remains x16785–24660 (approximately drop through75%). New artwork is visible by default for editor inspection and fades out at the exit. As with ordinary decoration, scenery can be seen ahead as the camera approaches the drop. The initial global hiding trigger was removed from the final file.

32 musical accents are measured from the cached song and placed with the decoded speed schedule. Portal activation offsets are not calibrated in native playback.

Validation: GMD roundtrip, source hash, gameplay property preservation, ID separation, no new collisions, rotation centers, original UFO shader preservation. A candidate differing only by the final removed initial hide trigger imported successfully through Native Editor Bridge and reported10,937 objects. The final export has10,936 objects. Native editor screenshots were captured, but UI click calls failed with noWindowsAvailable and play preview could not be completed. Temporary start-position test object was undone; the exported file contains no test additions. The open native candidate is not identical to the final export; import the final INFERNO.gmd to get the editor visibility change.

Atlas previews are approximate: native procedural geometry, camera tracking and shaders are not reproduced exactly. The displayed sheet is not a native playthrough or proof of feature-worthiness.
