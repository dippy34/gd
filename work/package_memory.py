from pathlib import Path
import json,csv,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parent.parent
P=json.loads((ROOT/'work/memory-plan.json').read_text())
V=json.loads((ROOT/'outputs/v8-1573528-memory-validation.json').read_text())
R=json.loads((ROOT/'work/memory-replay.json').read_text())
T=json.loads((ROOT/'work/memory-timing-sweep.json').read_text())
S=json.loads((ROOT/'work/memory-sync.json').read_text())
assert V['rooms_with_nominal_overlaps']==0 and not any(r['errors'] for r in R)
assert V['sha256']==hashlib.sha256((ROOT/'outputs/v8-1573528-memory.gmd').read_bytes()).hexdigest()
V['independent_model_replay']=R;V['timing_sweep']=T;V['audio_sync_by_input_kind']=S
V['native_verification']={'completed':False,'reason':'Two Computer Use calls to Geometry Dash timed out. No native completion or difficulty verification was obtained.'}
(ROOT/'outputs/v8-1573528-memory-validation.json').write_text(json.dumps(V,indent=2))
with (ROOT/'outputs/v8-1573528-memory-inputs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['time','x','mode','kind','hold','down','orb_id','gravity','target','symbol','activate'],extrasaction='ignore');w.writeheader();w.writerows(P['controls'])
def stamp(t):return f'{int(t)//60}:{t%60:05.2f}'
lines=[
 '# v8 — song 1573528 — memory rebuild',
 '',
 '[Import the final .gmd](v8-1573528-memory.gmd). The internal level name is **v8**. Previous versions and the original handoff are preserved.',
 '',
 f'This is a new {stamp(P["end_time"])} layout containing {P["objects"]:,} objects and fifteen authored rooms. It targets Insane Demon to entry Extreme, but that difficulty and native completion are **unverified**.',
 '',
 'The palette uses near-black shapes, faint olive/grey edges and brighter orbs. The two wave rooms use concealed crossings and different normal/mini arrangements. The other rooms use selective toggle-orb locks, false landing plates, false teleport targets, inverted orb transfers, and code recall. There are no black holes or swing sections.',
 '',
 f'Native 0.5× speed covers {P["slow_percent"]:.2f}% of the duration. Native 1× speed covers the two accented phrases at {stamp(P["sections"][3]["t0"])}–{stamp(P["sections"][3]["t1"])} and {stamp(P["sections"][5]["t0"])}–{stamp(P["sections"][5]["t1"])}. No timewarp is used. The ending is after 3:20.',
 '',
 '## Room score',
 '',
 '| Time | Room | Mode | Main setup |',
 '|---|---|---|---|',
 ]
for s in P['sections']:lines.append(f'| {stamp(s["t0"])}–{stamp(s["t1"])} | {s["name"]} | {s["mode"]} | {s["rule"]} |')
lines += [
 '',
 '## Research used',
 '',
 '- [VSC, legitimate verifier Yossarian](https://www.youtube.com/watch?v=ewlMbTR-c_w): directly inspected the dark industrial playfield, limited edge visibility and clear wave trail. Its challenge difficulty is not the target here.',
 '- [LIMBO, MindCap creator showcase](https://www.youtube.com/watch?v=ryBbuH_SPbs): directly inspected the early false route geometry and symbol-based section. The design borrows the idea of distinct memory rules; it does not copy the level or its randomized key ending.',
 '- [GD Docs: hitboxes](https://boomlings.dev/reference/player_physics/hitboxes): the wave red box is 10 units normally and 6 units in mini. The previous build had used a much larger wave collision envelope.',
 '- [GD Docs: gamemode physics](https://boomlings.dev/reference/player_physics/gamemodes) and [orbs](https://boomlings.dev/reference/player_physics/orbs_and_pads): movement units, jump velocities and orb impulses informed the design models.',
 '- [Level serialization reference](https://boomlings.dev/resources/client/level-components/level-string) and [RobTop editor guide](https://www.robtopgames.com/files/GDEditor.pdf): native groups, custom/toggle orbs, alpha, move and toggle triggers.',
 '- Local audio analysis used the actual cached **1573528.mp3**, not the old song. MP3 metadata reports 131 BPM; spectral onset-comb analysis independently returned approximately 131 BPM. The file lasts 231.915 seconds and yielded 637 detected attacks. No song title or artist is assumed.',
 '',
 '## What was checked',
 '',
 f'- Re-read the exported .gmd, decoded its compressed level string, checked object count, song ID, name, native speed objects and all seven mode portals.',
 f'- Checked {V["nominal_path_samples"]:,} finite-body route samples against exported solid blocks and conservative full spike boxes: zero nominal overlaps. All {V["spike_count"]} spikes remain inside y = 0–300.',
 '- Independently replayed the input score against the exported collision geometry: all fifteen rooms pass under the stated model assumptions. This caught and led to fixes for UFO ceiling overshoot and overlapping spider transfers.',
 '- Audited all 40 toggle-orb decisions: 13 required switches remove full-height barriers; 27 decoys enable full-height barriers. Group links and initial toggle states were read from the actual exported objects.',
 '- Ran 135 room replays across nine whole-score timing shifts from −40 to +40 ms. These are sensitivity checks, not individual click windows or proof of a demon rating.',
 '- Main jump, robot launch, gravity-flip and wave-turn categories each have a median distance of zero from a detected audio attack. Some subdivisions, orb follow-ups and ship corrections intentionally fall between detected attacks; not every input is claimed to hit an onset.',
 '- Rendered all fifteen rooms using the local game sprite atlas, with conditional group visibility and movement. These are diagnostic views rather than native screenshots.',
 '',
 '**Limit:** ship/UFO/ball dynamics remain approximate; native portal contact offsets, full-run input behaviour and final difficulty need in-game verification. The local Geometry Dash UI connection timed out twice, so no native pass is claimed.',
 '',
 '[Detailed checks](v8-1573528-memory-validation.json) · [Input score](v8-1573528-memory-inputs.csv) · [Diagnostic preview](v8-1573528-memory-preview.png)',
 '',
 '## Memory notes / spoilers',
 '',
 'CIPHER introduces the order II → I → IV → III. Its other marked orbs are decoys. LAST WORD displays II → IV → I → III and asks for the **first** order, before the tokens move. It is an authored recall sequence, not a random shuffle system. Required UFO switches appear between normal hops; their custom-orb activation is a separate input. False spider platforms have decoration but no collider, so teleportation passes through them to the real shelf.',
 '',
 f'Final SHA-256: `{V["sha256"]}`',
 ]
(ROOT/'outputs/v8-1573528-memory-notes.md').write_text('\n'.join(lines)+'\n')
print('Packaged final GMD, input score, notes and validation. Native verification remains outstanding.')
