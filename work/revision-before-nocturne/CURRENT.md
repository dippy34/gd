# Current exported level

Latest: `outputs/v8-1573528-branching.gmd`, internal name **v8**. Read its `-notes.md` and `-validation.json` before editing. This revision follows the accepted structural cleanup and changes flight patterns, later room order, visibility and randomized wall decisions.

Current raw: `work/v8-branching.level`. Current plan: `work/branching-plan.json`. Current native import snapshot: `work/branching-native-import.level`. Keep prior exports intact, especially `outputs/v8-1573528-clean.gmd`.

The latest export has 26,934 objects, 34 independent randomized wall choices, 50 fitted fakeouts and 18 flight phrases. Song 1573528; duration 205.192 seconds. All seven modes except swing. Native 0.5 speed covers 85.714% of the timeline; no time warp. Normal size portal is 99; mini is 101. Retain per-room camera resets after mode portals and Claim Touch 445 on the randomized toggle orbs.

## Rebuild

Run sequentially from the workspace root:

```sh
rtk proxy python3 work/branching_layout.py
rtk proxy env GD_SKIN_SOURCE=work/branching-base.gmd GD_SKIN_TARGET=work/branching-skinned.gmd GD_SKIN_PLAN=work/branching-plan.json GD_SKIN_RAW=work/v8-branching-base.level GD_SKIN_OUTPUT_RAW=work/v8-branching-skinned.level GD_SKIN_AUDIT=work/branching-skin-audit.json python3 work/clean_visuals.py
rtk proxy python3 work/branching_fakeouts.py
rtk proxy python3 work/check_branching_route.py
rtk proxy python3 work/replay_branching.py
```

Import the resulting .gmd through the native bridge and refresh `work/branching-native-import.level`. Then run `rtk proxy python3 work/audit_branching.py`. Native random-state observations in that audit refer to screenshots from this revision, not automated native gameplay tests; refresh them if the logic changes.

Preview with `GD_PREVIEW_LEVEL=work/v8-branching.level` and `GD_PREVIEW_PLAN=work/branching-plan.json` when calling `work/preview_memory.py`. Existing final views use prefix `branching-final`; 31 camera positions are recorded by their filenames. `work/package_branching.py` packages those inspected previews and copies the final .gmd to Downloads after checking the audited hash.

`work/memory_layout.py` still describes an older score. `work/branching_layout.py` imports it and overrides the revised portions. Running `work/clean_visuals.py` without the environment arguments rebuilds the older clean artifact. Do not treat either default output as the latest revision.

Full native completion and exact demon difficulty remain unverified. The script checks use an approximate physics model. Native random starting states and ship/wave artwork were inspected; the complete level was not played through with damage enabled.
