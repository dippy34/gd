> Historical v8 note. This is a separate archived project, and its sync pointer predates variety. For current factory work use root project-state.json.

# Current exported level

Latest: `outputs/v8-1573528-sync.gmd`, internal name **v8**, song **1573528**. SHA256: b4c2346e51535a356d87de9e5c8251185da51bae1c728f0a60a21a784153d131. Preserve earlier exports, including rebalance.

User requested renewed, more unique gameplay, better song sync, more orbs outside cube/robot ("words" interpreted as orbs), and a harder final cube. This revision rebuilds nine rooms: both waves, ships, UFOs, spiders, ending. Six earlier ground/ball rooms keep their non-memory controls. Dark palette and spider-only crossing-line fakeouts retained.

Raw `work/v8-sync.level`; plan `work/sync-plan.json`; final notes, validation and preview `outputs/v8-1573528-sync-*`.

Build: `sync_layout.py` imports `sync_sections.py` for replacement rooms (which imports rebalance helpers and common M). Then `clean_visuals.py` with GD_SKIN_* pointing to sync paths, then `finish_sync.py`. Each command must use rtk. Checks: `check_sync_route.py`, `replay_sync.py`, `check_sync_branches.py`, `measure_sync.py`, `audit_sync.py`. Audit binds route/replay/measurement checks to the final file SHA.

25741 objects, 352 reference inputs, 205.192 seconds, 85.714% native slow. Refined onset comb 131.044 BPM, individually measured beat guide. All new flight controls on detected attacks; total reference onset match within25ms 31.4% ->81.2%. 13 spider jump orbs, one extra UFO orb, 35 ending inputs with four green dash-release-catch passages and extra late airborne orb chains. 262 spider fakeouts, 23 random wall decisions, 61 portal passages with normal-size display copies. No coloured trim, move triggers or flashing pulse blocks.

Two added ending catches initially passed only one 240 Hz tick and were widened. Final sampled ending sensitivity 101/250 versus133/250 before, every selected new probe >=5 passing ticks. ±35 release-velocity variants pass. Full15-room swept checks and independent approximate replay pass. These are NOT native completion or demon-rating proof. Wave/ship/UFO beam solvers use measured onsets plus physical-bound constraints; opening few tenths use native floor contact. Spider mixes ordinary jump-orb arcs and teleport runs; fakeout art is rebuilt to match new geometry, not copied verbatim from old first spider.

Native bridge remains disabled: `work/sync-native-status.json`, latest Geode log September10 explicitly says matthew.gdshare_ai_decorator is not enabled, status stale. No native app settings or import performed.
