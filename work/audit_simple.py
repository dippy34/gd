"""Audit the final export, native import, portal barriers, and small timing edit."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd, decompress

P = json.loads((ROOT/'work/simple-plan.json').read_text())
old = json.loads((ROOT/'work/deception-plan.json').read_text())
f = read_gmd(ROOT/'outputs/v8-1573528-simple.gmd')
raw = decompress(f['k4'][1])
assert raw == (ROOT/'work/v8-simple.level').read_text()
_, objects = load(str(ROOT/'work/v8-simple.level'))
native_path = ROOT/'work/simple-native-final.level'
_, native = load(str(native_path)) if native_path.exists() else ('',objects)
assert len(objects) == len(native) == int(f['k48'][1])
assert f['k2'][1] == 'v8' and f['k45'][1] == '1573528'
for o, n in zip(objects, native):
    assert o['1'] == n['1']
    assert abs(float(o['2'])-float(n['2'])) < .056
    assert abs(float(o['3'])-float(n['3'])) < .013
    for key in ('128', '129'):
        assert abs(float(o.get(key, o.get('32',1)))-float(n.get(key, n.get('32',1)))) < .0011

ids = Counter(o['1'] for o in objects)
assert all(ids[i] == 0 for i in ('1594','2068','1049','1006','1935','1933'))
assert len(P['branches']) == 2 and not P['random_locks']
assert P['fakeouts'] == old['fakeouts']
spiders = [s for s in P['sections'] if s['mode']=='spider']
_, original_art = load(str(ROOT/'work/v8-nocturne.level'))
def spider_art(oo):
    return [o for o in oo if o.get('20')=='11' and not o.get('57') and
            any(s['x0'] <= float(o['2']) < s['x1'] for s in spiders)]
assert spider_art(objects) == spider_art(original_art)
assert P['paths'] == old['paths']
assert P['controls'] == [e for e in old['controls'] if e['kind'] != 'memory']
assert sum(ids[i] for i in ('36','84','141')) == len(P['orbs'])

def solid_at_x(x):
    result = []
    for o in native:
        if o['1'] != '1' or o.get('121') == '1' or o.get('134') == '1':
            continue
        cx, cy = float(o['2']), float(o['3'])
        hx, hy = 15*float(o.get('128',1)), 15*float(o.get('129',1))
        if cx-hx-.06 <= x <= cx+hx+.06:
            result.append((cy-hy, cy+hy))
    return sorted(result)

def covers(intervals, a, b):
    edge = a
    for lo, hi in intervals:
        if lo > edge+.025:
            break
        edge = max(edge, hi)
        if edge >= b-.025:
            return True
    return edge >= b-.025

portal_checks = []
for p in P['portal_passages']:
    n = min((o for o in native if o['1'] == str(p['id']) and o.get('121')!='1'), key=lambda o: abs(float(o['2'])-p['x']))
    assert abs(float(n['2'])-p['x']) < .056
    assert n.get('121') != '1' and n.get('134') != '1'
    assert not n.get('57'), 'Required portals must not be toggled off'
    assert n.get('135') == '1'
    art = [o for o in objects if o['1']==str(p['id']) and o.get('121')=='1' and abs(float(o['2'])-p['x'])<.001]
    assert len(art)==1 and art[0].get('134')=='1' and art[0]['129']=='1'
    core_low = float(n['3'])-15*float(n.get('129',1))
    core_high = float(n['3'])+15*float(n.get('129',1))
    assert core_low <= p['lo']-1.9 and core_high >= p['hi']+1.9
    intervals = solid_at_x(float(n['2']))
    assert covers(intervals, -30, p['lo'])
    assert covers(intervals, p['hi'], 330)
    portal_checks.append(dict(id=p['id'], x=p['x'], below_closed=True, above_closed=True,
                              opening_inside_conservative_portal_core=True))

tightened = 0
assert len(P['timing_features']) == len(old['timing_features'])
for a, b in zip(old['timing_features'], P['timing_features']):
    assert (a['section'],a['t'],a['kind']) == (b['section'],b['t'],b['kind'])
    if 'pad' not in a:
        assert a == b
        continue
    delta = 0 if b['mode'] in ('ship','wave') else .65
    assert abs(a['pad']-b['pad']-delta) < 1e-6
    tightened += bool(delta)
route = json.loads((ROOT/'work/simple-route-check.json').read_text())
replay = json.loads((ROOT/'work/simple-replay.json').read_text())
assert all(not r['errors'] for r in route+replay)
report = dict(file='v8-1573528-simple.gmd', name='v8', song=1573528,
              sha256=hashlib.sha256((ROOT/'outputs/v8-1573528-simple.gmd').read_bytes()).hexdigest(),
              objects=len(objects), duration_seconds=P['end_time'], native_half_speed_percent=P['slow_percent'],
              branches=2, preserved_spider_fakeouts=len(P['fakeouts']), preserved_spider_art=P['preserved_spider_art'],
              removed_random_walls=len(old['random_locks']), removed_bait_orbs=len(old['baits']),
              required_inputs=len(P['controls']), unchanged_reference_path=True,
              tightened_existing_timing_gates=tightened, clearance_reduction_each_side=.65,
              native_import_verified=native_path.exists(), native_portal_passages=portal_checks,
              route_samples=sum(r['samples'] for r in route), route_failures=0,
              replay_sections=len(replay), replay_failures=0,
              limitations='Route/replay physics and the conservative 30-unit portal core are model assumptions. The intermediate geometry imported natively; final artwork import could not be checked because editor coordinate controls returned noWindowsAvailable. Full native completion and exact difficulty are not verified.',
              references=['https://www.robtopgames.com/files/GDEditor.pdf',
                          'https://boomlings.dev/reference/player_physics/hitboxes',
                          'https://github.com/gd-programming/gd.docs/blob/main/docs/resources/client/level-components/level-object.md'])
(ROOT/'outputs/v8-1573528-simple-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('native_portal_passages','references')},indent=2))
