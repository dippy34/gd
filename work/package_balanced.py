"""Package the ship-balance and structural-art revision without replacing v8 memory."""
from pathlib import Path
import json,hashlib,csv,shutil
ROOT=Path(__file__).resolve().parent.parent
stem='v8-1573528-balanced'
p=json.loads((ROOT/'work/memory-plan.json').read_text())
v=json.loads((ROOT/f'outputs/{stem}-validation.json').read_text())
r=json.loads((ROOT/'work/memory-replay.json').read_text())
ships=json.loads((ROOT/'work/ship-rebalance-checks.json').read_text())
preserved=json.loads((ROOT/'work/nonship-preservation.json').read_text())
assert v['rooms_with_nominal_overlaps']==0 and not any(q['errors'] for q in r)
assert len(preserved)==13
assert v['sha256']==hashlib.sha256((ROOT/f'outputs/{stem}.gmd').read_bytes()).hexdigest()
v.update(independent_model_replay=r,ship_balance_checks=ships,nonship_gameplay_preserved=preserved,
 native_verification={'completed':False,'reason':'Local native editor bridge reports disconnected; no native completion run is claimed.'},
 previous_file='v8-1573528-memory.gmd')
(ROOT/f'outputs/{stem}-validation.json').write_text(json.dumps(v,indent=2))
with (ROOT/f'outputs/{stem}-inputs.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=['time','x','mode','kind','hold','down','orb_id','gravity','target','symbol','activate'],extrasaction='ignore');w.writeheader();w.writerows(p['controls'])
stamp=lambda t:f'{int(t)//60}:{t%60:05.2f}'
lines=[
 '# v8 — ship balance and structure revision','',
 f'[Final .gmd]({stem}.gmd) · [Preview]({stem}-preview.png) · [Validation]({stem}-validation.json)','',
 'The internal level name remains **v8**. The previous memory version is preserved as `v8-1573528-memory.gmd`.','',
 '## Gameplay changes','',
 '| Ship section | Old thrust changes | New thrust changes | Change |',
 '|---|---:|---:|---|',
 '| PARALLAX | 79 | 39 | Smoother climbs, broader galleries, gravity reversal removed |',
 '| UNDERTOW | 86 | 50 | Longer corrections, steadier height changes, wider slits |','',
 'The reference score uses longer correction intervals. Narrow ship gates receive 24 units of extra space around the finite-body route instead of 11; drift galleries receive 27 instead of 14. Ship rail spikes are kept at least 22 additional units away from the sampled route. These are design-model clearances, not native click-window measurements.','',
 'All thirteen non-ship sections retain identical gameplay objects and input scores. The level still has forty live memory decisions, all seven requested game modes, and no swing or black holes. Gravity changes remain in the cube and UFO sections.','',
 '## Structure and visibility','',
 'Joined panel faces, inset borders, collars, brackets and supports replace isolated block outlines and unrelated floating motifs. Frames join into larger bays. False landings and real platforms use the same panel design, so the composition is more coherent without labelling the correct route. Continuous wave walls retain dark faces. Background bay frames still move; collision surfaces stay aligned with their visible skins.','',
 f'Song: **1573528**. Duration: **{stamp(p["end_time"])}**. Native 0.5× speed: **{p["slow_percent"]:.2f}%**. Objects: **{p["objects"]:,}**. No timewarp.','',
 '## Checks and limits','',
 f'- Exported geometry: {v["nominal_path_samples"]:,} finite-body path samples, zero nominal block/spike overlaps; all {v["spike_count"]} spikes fit inside y = 0–300.',
 '- Independent input-model replay passes all fifteen sections.',
 '- Compared exported gameplay objects and input scores with the previous .gmd: all thirteen non-ship rooms match.',
 '- Audited all forty memory switches and their full-height gates.',
 '- Ran separate whole-score timing-shift checks on both ship sections. These indicate sensitivity under the approximate model; they are not individual input windows or difficulty ratings.',
 '- Inspected atlas-based renders of both ship sections and representative cube, robot, UFO, ball, spider and wave sections.','',
 '**Native completion and exact Insane/Extreme difficulty remain unverified.** The local editor bridge is disconnected. Ship/UFO/ball dynamics and native portal contact offsets still require in-game testing.','',
 '[Original research references and memory notes](v8-1573528-memory-notes.md)','',
 f'SHA-256: `{v["sha256"]}`','']
(ROOT/f'outputs/{stem}-notes.md').write_text('\n'.join(lines))
print(json.dumps({'file':str((ROOT/f'outputs/{stem}.gmd').resolve()),'bytes':(ROOT/f'outputs/{stem}.gmd').stat().st_size,'objects':p['objects'],'native_verified':False},indent=2))
