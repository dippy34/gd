# Current exported level

Latest: `outputs/v8-1573528-nocturne.gmd`, internal name **v8**. Read `outputs/v8-1573528-nocturne-notes.md` and its validation JSON before editing. This revision darkens the branching build, restores layered spider fakeouts and adds 5.5 units of clearance on each side of both wave paths.

Raw: `work/v8-nocturne.level`. Plan: `work/nocturne-plan.json`. Native snapshot: `work/nocturne-native-import.level`. Preserve earlier exports and `work/revision-before-nocturne/`.

The current file has 34,010 objects, 34 random wall decisions, 977 individual visual decoy features, and the unchanged 550-input reference score. Song 1573528; duration 205.192 seconds; native 0.5 speed covers 85.714% of the timeline. Normal portal is 99; mini is 101. Keep the camera resets, native speed portals and all seven modes except swing.

Native 1594 switch input objects are hidden with 135 and retain Claim Touch 445, No Glow 96 and No Particle 507. Eight pieces of non-colliding dark artwork follow each active-orb group. Do not remove the hidden inputs or merge the mutually exclusive visible groups. The 34 wall decisions are unchanged from branching.

## Build

Run sequentially from the workspace root:

```sh
rtk proxy python3 work/nocturne_layout.py
rtk proxy env GD_SKIN_SOURCE=work/nocturne-base.gmd GD_SKIN_TARGET=work/nocturne-skinned.gmd GD_SKIN_PLAN=work/nocturne-plan.json GD_SKIN_RAW=work/v8-nocturne-base.level GD_SKIN_OUTPUT_RAW=work/v8-nocturne-skinned.level GD_SKIN_AUDIT=work/nocturne-skin-audit.json python3 work/clean_visuals.py
rtk proxy python3 work/nocturne_fakeouts.py
rtk proxy python3 work/check_nocturne_route.py
rtk proxy python3 work/replay_nocturne.py
```

Import the new file through the native bridge and refresh `work/nocturne-native-import.level`, then run `rtk proxy python3 work/audit_nocturne.py`. Its native visual-review entries describe the inspected current screenshots; refresh those observations after further edits.

Use `GD_PREVIEW_LEVEL=work/v8-nocturne.level` and `GD_PREVIEW_PLAN=work/nocturne-plan.json` with `work/preview_memory.py`. Current inspected camera positions are in `nocturne-review-*` and `nocturne-rest-*` under `work/previews`. Package with `rtk proxy python3 work/package_nocturne.py` after the audit and visual review.

The new generator imports `branching_layout.py`, which imports `memory_layout.py`; neither older generator's default export is the current level. `clean_visuals.py` also defaults to an older export unless the environment arguments above are provided.

Full native completion and exact demon difficulty remain unverified. Native artwork and import were inspected; all room replays pass an approximate physics model.
