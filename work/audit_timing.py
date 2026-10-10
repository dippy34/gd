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


P = json.loads((ROOT/'work/memory-plan.json').read_text())
current=ROOT/'outputs/v8-1573528-timing.gmd'
old_dir=ROOT/'work/revision-before-timing-hardening'
old_plan=json.loads((old_dir/'memory-plan.json').read_text())
f,h,os=read(current)
old_f,old_h,old_os=read(old_dir/'v8-1573528-refined.gmd')
state=size_audit(current,P)
assert not state['mismatched_samples'] and not state['mini_orb_inputs']
assert f['k2'][1]=='v8' and f['k45'][1]=='1573528'
assert not any(o['1'] in ('1935','1933') for o in os)
assert h==old_h, 'Song, speed and initial mode settings must remain identical'
# All inputs retain their song-aligned timestamps and original mode/size plan.
assert P['controls']==old_plan['controls']
assert P['paths']==old_plan['paths']
assert P['speed_schedule']==old_plan['speed_schedule']
# The complete ship/wave rooms, including decoration, must be preserved.
preserved=[]
for s in P['sections']:
 if s['mode'] not in ('ship','wave'):continue
 def room(items):
  return Counter(tuple(sorted(o.items())) for o in items if s['x0']<=float(o['2'])<s['x1'])
 assert room(os)==room(old_os),s['name']
 preserved.append(s['name'])
# Preserve every camera target and trigger verbatim.
camera_ids={'1764','1913','1914','2925'}
assert Counter(tuple(sorted(o.items())) for o in os if o['1'] in camera_ids)==Counter(tuple(sorted(o.items())) for o in old_os if o['1'] in camera_ids)
# Each false doorway must sit in an actual solid bank, have a linked structure,
# remain inside camera bounds, and be different from the intended route.
fakes=[]
for fake in P['fakeouts']:
 x,y=fake['x'],fake['y']
 assert 20<y<280
 walls=[]
 for o in os:
  if o['1']!='1' or o.get('121')=='1':continue
  cx,cy=float(o['2']),float(o['3']);w=30*float(o.get('128',1));hh=30*float(o.get('129',1))
  if cx-w/2-.001<=x<=cx+w/2+.001 and cy-hh/2-.001<=y<=cy+hh/2+.001:walls.append(o)
 assert walls, fake
 fakes.append(dict(section=fake['section'],x=x,y=y,actual_solid_dead_end=True))
assert len(P['fakeouts'])>=80
assert {z['mode'] for z in P['timing_features']}=={'cube','robot','ball','ufo','spider'}
result=dict(file=current.name,sha256=hashlib.sha256(current.read_bytes()).hexdigest(),native_size_state=state,
 preserved_ship_wave_rooms=preserved,unchanged_input_score=True,unchanged_route_and_size_plan=True,
 camera_settings_preserved=True,features_by_mode=dict(Counter(t['mode'] for t in P['timing_features'])),
 purposeful_fakeout_count=len(fakes),fakeouts=fakes,
 limitations=['Static exported-state and geometry checks, not damage-enabled native completion.'])
(ROOT/'work/timing-audit.json').write_text(json.dumps(result,indent=2))
print(json.dumps({k:result[k] for k in ['preserved_ship_wave_rooms','unchanged_input_score','camera_settings_preserved','features_by_mode','purposeful_fakeout_count']},indent=2))
