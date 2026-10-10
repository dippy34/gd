"""Regression checks against serialized native state, not builder constants.

Native portal IDs are independently taken from G.js's constants table:
SIZE_NORMAL 99, SIZE_MINI 101. In particular, do not import memory_layout.
This audit must reject the previous export that shared a wrong ID mapping.
"""
from pathlib import Path
from collections import Counter
import sys, json, bisect, hashlib
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'work/handoff/tools'))
from gmd import read_gmd, decompress


def read(path):
    f = read_gmd(path)
    parts = decompress(f['k4'][1]).split(';')
    def parse(token):
        p = token.split(',')
        return dict(zip(p[::2], p[1::2]))
    return f, parse(parts[0]), [parse(p) for p in parts[1:] if p]


def size_audit(path, plan):
    f, h, os = read(path)
    ports = sorted((float(o['2']), int(o['1'])) for o in os if o['1'] in ('99', '101'))
    xs = [p[0] for p in ports]
    def mini_at(x):
        i = bisect.bisect_right(xs, x + .0001) - 1
        return ports[i][1] == 101 if i >= 0 else h.get('kA3', '0') == '1'
    failures = Counter()
    for t, x, y, mode, radius, gravity in plan['paths']:
        intended_mini = mode == 'wave' and radius == 3
        if mini_at(x) != intended_mini:
            failures[mode] += 1
    orb_checks = []
    for e in plan['controls']:
        if e['kind'] not in ('orb', 'memory'):
            continue
        orb_checks.append(dict(time=e['time'], mode=e['mode'], mini=mini_at(e['x'])))
    rooms = [dict(section=s['name'], initial_mini=mini_at(s['x0']),
                  final_mini=mini_at(s['x1'] - .001)) for s in plan['sections']]
    return dict(mismatched_samples=dict(failures), sample_count=len(plan['paths']),
                mini_orb_inputs=sum(o['mini'] for o in orb_checks),
                orb_inputs=len(orb_checks), rooms=rooms,
                native_size_portals=[dict(x=x, id=oid, size='mini' if oid == 101 else 'normal') for x, oid in ports])


P = json.loads((ROOT / 'work/memory-plan.json').read_text())
old_dir = ROOT / 'work/revision-before-size-structure-fix'
old_plan = json.loads((old_dir / 'memory-plan.json').read_text())
current = ROOT / 'outputs/v8-1573528-refined.gmd'
f, h, os = read(current)
good = size_audit(current, P)
bad = size_audit(old_dir / 'v8-1573528-balanced.gmd', old_plan)
assert not good['mismatched_samples'], good
assert not good['mini_orb_inputs'], good
assert bad['mismatched_samples'] and bad['mini_orb_inputs'], 'Regression failed to detect original size bug'

# Reconstruct the designed wave speed on both sides of each exported size portal.
wave = next(s for s in P['sections'] if s['name'] == 'FAULTLINE')
changes = []
for o in os:
    if o['1'] not in ('99', '101'):
        continue
    x = float(o['2'])
    if not wave['x0'] + 100 < x < wave['x1'] - 260:
        continue
    t = wave['t0'] + (x - wave['x0']) / wave['speed']
    slope = 2 if o['1'] == '101' else 1
    changes.append(dict(time=t, id=int(o['1']), size='mini' if slope == 2 else 'normal', wave_slope=slope))
changes.sort(key=lambda o: o['time'])
assert [o['id'] for o in changes] == [101, 99, 101, 99], changes

# The normal reset after each wave must occur before the next room's first input.
for i, s in enumerate(P['sections'][:-1]):
    if s['mode'] != 'wave':
        continue
    resets = [o for o in os if o['1'] == '99' and s['x1'] - 250 < float(o['2']) < s['x1']]
    assert resets, s['name']

# Camera targets are read from exported objects, with a local refresh in every room.
camera = []
for s in P['sections']:
    cams = [o for o in os if o['1'] == '1914' and s['x0'] - .01 <= float(o['2']) < s['x0'] + 100]
    assert len(cams) == 1, (s['name'], len(cams))
    cam = cams[0]
    assert cam['101'] == '2' and cam['36'] == '1' and float(cam['10']) == 0
    targets = [o for o in os if cam['71'] in o.get('57', '').split('.')]
    assert len(targets) == 1 and float(targets[0]['3']) == 150
    zooms = [o for o in os if o['1'] == '1913' and s['x0'] - .01 <= float(o['2']) < s['x0'] + 100]
    assert len(zooms) == 1 and float(zooms[0]['371']) == .82
    free = [o for o in os if o['1'] == '2925' and s['x0'] - .01 <= float(o['2']) < s['x0'] + 100]
    assert len(free) == 1 and free[0]['111'] == '1'
    camera.append(dict(section=s['name'], target_y=150, zoom=.82,
                       trigger_x=float(cam['2']), target_group=int(cam['71'])))

# Preserve accepted gameplay outside ship, including the opening cube, exactly.
# Size/camera fixes and passable structural backing are checked separately.
_, _, old_os = read(old_dir / 'v8-1573528-balanced.gmd')
def gameplay_objects(objects, section):
    chosen = []
    for o in objects:
        if not section['x0'] - .0001 <= float(o['2']) < section['x1'] - .0001:
            continue
        if o['1'] in ('99', '101'):
            continue
        if o['1'] not in ('1', '8', '10', '11', '12', '13', '47', '111', '660', '745', '1331', '36', '84', '141', '1594', '1049'):
            continue
        # Group numbers are allocation details. Their toggle states are audited elsewhere.
        chosen.append(tuple(sorted((k, v) for k, v in o.items() if k not in ('57', '51'))))
    return Counter(chosen)
preservation = []
for s in P['sections']:
    if s['mode'] == 'ship':
        continue
    old_s = next(z for z in old_plan['sections'] if z['name'] == s['name'])
    native_match = gameplay_objects(os, s) == gameplay_objects(old_os, old_s)
    def score(plan):
        return [{k:v for k,v in e.items() if k != 'target'} for e in plan['controls']
                if s['t0'] <= e['time'] < s['t1']]
    score_match = score(P) == score(old_plan)
    assert native_match and score_match, (s['name'], native_match, score_match)
    preservation.append(dict(section=s['name'], native_gameplay_preserved=True, inputs_preserved=True))

ships = []
for s in P['sections']:
    if s['mode'] != 'ship':
        continue
    gates = [g for g in P['gates'] if g['section'] == s['name']]
    assert all(g['kind'] == 'lined ship corridor' for g in gates)
    # Each new corridor has an actual floor-connected lower bank and roof-connected upper bank.
    local = [r for r in P['rectangles'] if s['x0'] <= r['a'] < s['x1'] and r['kind'].startswith('ship duct')]
    assert all(r['lo'] == 0 if r['kind'].endswith('lower') else r['hi'] == 300 for r in local)
    widths = [g['hi'] - g['lo'] for g in gates]
    ships.append(dict(section=s['name'], continuous_bank_segments=len(gates),
                      solid_bank_gap_min=min(widths), solid_bank_gap_max=max(widths),
                      spike_projection_per_bank=12,
                      note='World-unit geometric gaps, not a measured native input window or difficulty rating.'))

result = dict(file=current.name, sha256=hashlib.sha256(current.read_bytes()).hexdigest(),
              native_size_state=good, old_file_regression=bad,
              second_wave_size_changes=changes, camera_refreshes=camera,
              nonship_preservation=preservation, ships=ships,
              limitations=['No damage-enabled native completion run is claimed.',
                           'State trace uses portal centre positions. Exact native contact offsets remain unmeasured.',
                           'The camera probe was visually inspected in cube, ship and wave; final complete-level framing is not a full native recording.'])
(ROOT / 'work/refined-audit.json').write_text(json.dumps(result, indent=2))
print(json.dumps(dict(size_errors=good['mismatched_samples'], orb_inputs_checked=good['orb_inputs'],
                      old_size_errors=sum(bad['mismatched_samples'].values()),
                      preserved_rooms=len(preservation), cameras=len(camera), ships=ships), indent=2))
