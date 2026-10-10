# v8 — structural cleanup

[Final .gmd](v8-1573528-clean.gmd) · [Before / after](v8-1573528-clean-comparison.png) · [All 15 rooms](v8-1573528-clean-preview.png) · [Native opening](v8-1573528-clean-native-preview.png) · [Validation](v8-1573528-clean-validation.json)

Internal name **v8**. Song **1573528**. Duration **3:25.19**. Native 0.5× portals for **85.71%** of the timeline. **28,984 objects**.

The visible structures have been rebuilt from the existing solid geometry. Joined platforms share an exposed outer boundary. Crossing support cages, nested platform frames, and all 100 oversized false door boxes have been removed. Seventy-one small inset faces fit within their actual platform bodies, clear of attached timing banks. Spike graphics use filled silhouettes; adjacent teeth no longer draw outlines through one another. Native spikes retain their collision settings and are hidden behind the replacement artwork.

All gameplay positions, sizes, rotations and behavior properties match the previous timing revision. The same 489 planned inputs, seven modes, forty functional memory decisions, mini/normal portals, camera locks, speed changes, moving code tokens and moving service plates remain. The earlier timing file remains intact.

Validation:

- Inspected 30 atlas-based renders, covering all fifteen rooms, with the exported camera and trigger states.
- Imported the actual .gmd in Geometry Dash. Inspected the native opening during play and the robot, spider and second-wave structures in the editor.
- Native import retains 28,984 objects; object ID counts match. Checked 15,809 collision, camera, interaction and replacement-spike-art objects against native serialization, allowing its position/scale rounding.
- All 12,328 rebuilt structural art boxes fit within the union of real solid bounds. Outside-playfield service recesses are excluded from this containment check.
- The 49,395-sample finite-body route audit passes, all 2,766 native spikes remain inside the playfield, and all forty live memory choices still control their original barriers.

The native opening check used the existing Ignore Damage setting. **Full native completion and exact demon difficulty remain unverified.** Scripted previews approximate the engine, and the route model does not prove a damage-enabled completion.

Rebuild: `rtk proxy python3 work/clean_visuals.py`, then `rtk proxy python3 work/check_clean.py`. The cleanup reads the frozen timing revision and writes its own export; `memory_layout.py` still generates the earlier timing revision. For import validation, capture the imported file to `work/clean-native-import.level`, then run `work/audit_clean_visuals.py` and `work/package_clean.py`.

SHA-256: `a2537043c426c5259abd83073d100a0aec4cf6718486e07edfa5bb55ce4814ff`
