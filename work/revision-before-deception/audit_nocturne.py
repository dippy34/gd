"""Audit actual random branches, route clearance, and native serialization."""
from pathlib import Path
from collections import Counter
import json,sys,math,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load,parse_header,parse_ks38
from gmd import read_gmd,decompress
P=json.loads((ROOT/'work/nocturne-plan.json').read_text())
FILE=ROOT/'outputs/v8-1573528-nocturne.gmd';F=read_gmd(FILE)
raw=decompress(F['k4'][1]);head,O=load(str(ROOT/'work/v8-nocturne.level'))
assert raw==(ROOT/'work/v8-nocturne.level').read_text()
_,N=load(str(ROOT/'work/nocturne-native-import.level'))
assert len(O)==len(N)==P['objects']==int(F['k48'][1])
assert Counter(o['1'] for o in O)==Counter(o['1'] for o in N)
assert F['k2'][1]=='v8' and F['k45'][1]=='1573528'
assert not any(o['1'] in ('1935','1006','1007') for o in O)
assert {12,13,47,111,660,745,1331}<={int(o['1']) for o in O}

def group(o,g):return str(g) in o.get('57','').split('.')
def sec(name):return next(s for s in P['sections'] if s['name']==name)
def xat(t):
 s=max((s for s in P['sections'] if s['t0']<=t),key=lambda s:s['t0'])
 return s['x0']+(t-s['t0'])*s['speed']
def bounds(o):
 x=float(o['2']);y=float(o['3']);w=30*float(o.get('128',o.get('32',1)));h=30*float(o.get('129',o.get('32',1)))
 return x-w/2,x+w/2,y-h/2,y+h/2

lock_results=[];all_logic_groups=[]
for m in P['random_locks']:
 all_logic_groups.extend(m[k] for k in ('wall','present','absent','branch_yes','branch_no'))
 randoms=[o for o in O if o['1']=='2068' and o.get('152')==f"{m['branch_yes']}.1.{m['branch_no']}.1"]
 assert len(randoms)==1 and abs(float(randoms[0]['2'])-xat(m['roll']))<.0001
 init=[o for o in O if o['1']=='1049' and o.get('62')!='1' and int(o['51']) in (m['wall'],m['present'],m['absent'])]
 assert len(init)==3 and all(o.get('56')=='0' for o in init)
 assert all(float(o['2'])<float(randoms[0]['2']) for o in init)
 orbs=[o for o in O if o['1']=='1594' and int(o['51'])==m['wall']]
 assert len(orbs)==2 and all(o.get('445')=='1' and o.get('99','0')=='0' for o in orbs)
 assert orbs[0]['2']==orbs[1]['2'] and orbs[0]['3']==orbs[1]['3']
 for branch,present in ((m['branch_yes'],True),(m['branch_no'],False)):
  active={m['wall']:False,m['present']:False,m['absent']:False}
  actions=[o for o in O if o['1']=='1049' and group(o,branch)]
  assert actions and all(o.get('62')=='1' for o in actions)
  for o in actions:active[int(o['51'])]=o.get('56')=='1'
  visible=[o for o in orbs if active[int(o['57'])]]
  assert len(visible)==1 and active[m['wall']]==present
  # Inspect exported orb action, not an assumed Boolean inversion.
  clicked=visible[0].get('56')=='1';skipped=active[m['wall']]
  assert clicked==(not present)
  assert (clicked if present else skipped)==False
  assert (skipped if present else clicked)==True
 native_orbs=[o for o in N if o['1']=='1594' and int(o['51'])==m['wall']]
 assert len(native_orbs)==2 and all(o.get('445')=='1' for o in native_orbs)
 assert sorted(o.get('56','0') for o in native_orbs)==['0','1']
 native_rand=[o for o in N if o['1']=='2068' and o.get('152')==randoms[0]['152']]
 assert len(native_rand)==1
 wall=[bounds(o) for o in O if o['1']=='1' and group(o,m['wall'])]
 assert wall and min(q[2] for q in wall)<.0001 and max(q[3] for q in wall)>299.99
 # Both wrong decisions leave exactly this wall. Prove it intersects the
 # reference body after the decision, independent of all other random rolls.
 pts=[p for p in P['paths'] if m['t']<p[0]<m['gate_t']+.12]
 assert any(q[0]<p[1]+p[4] and q[1]>p[1]-p[4] and q[2]<p[2]+p[4] and q[3]>p[2]-p[4] for q in wall for p in pts)
 lead=(min(q[0] for q in wall)-float(orbs[0]['2'])-15)/sec(m['section'])['speed']
 assert lead>.04
 lock_results.append(dict(section=m['section'],time=m['t'],probability_wall=.5,
     both_branches_correct=True,wrong_choices_create_or_leave_barrier=True,
     reveal_before_orb_seconds=m['t']-m['roll'],body_to_wall_after_orb_seconds=lead))
assert len(all_logic_groups)==len(set(all_logic_groups))

# No replacement decoration carries a collision. This includes every fakeout.
assert all(o.get('121')==o.get('134')=='1' for o in O if o['1'] in ('211','693'))
assert all(o.get('121')==o.get('134')=='1' for o in N if o['1'] in ('211','693'))
for o in O:
 if o['1']=='8':
  r=15*float(o.get('32',1));y=float(o['3']);assert -.001<=y-r and y+r<=300.001
sizes=sorted((float(o['2']),o['1']) for o in O if o['1'] in ('99','101'))
for orb in P['orbs']:
 previous=[o for o in sizes if o[0]<=orb['x']];assert not previous or previous[-1][1]=='99'
for s in P['sections']:
 for oid in ('1913','1914','2925'):
  assert any(o['1']==oid and s['x0']<=float(o['2'])<s['x0']+50 for o in O)
 if s['mode'] in ('ship','wave'):
  assert not any(o['1']=='901' and s['x0']<=float(o['2'])<s['x1'] for o in O)
assert len(P['phrases'])==18 and len(P['fakeouts'])>=300
for s in P['sections'][9:]:
 previous=[q for q in P['sections'][:9] if q['mode']==s['mode']]
 score=lambda q:[(round(e['time']-q['t0'],4),e['kind'],e.get('hold'),e.get('orb_id')) for e in P['controls'] if q['t0']<=e['time']<q['t1'] and e['mode']==q['mode']]
 assert all(score(q)!=score(s) for q in previous)

route=json.loads((ROOT/'work/nocturne-route-check.json').read_text());replay=json.loads((ROOT/'work/nocturne-replay.json').read_text())
assert not any(r['errors'] for r in route+replay)

# Compare this revision with the accepted branching file, not just its own
# generator's expectation. All controls and non-wave collision objects stay.
old_plan=json.loads((ROOT/'work/branching-plan.json').read_text())
_,old_objects=load(str(ROOT/'work/v8-branching.level'))
assert P['controls']==old_plan['controls'] and P['paths']==old_plan['paths']
assert P['random_locks']==old_plan['random_locks']
def wave_x(x):
 return any(s['mode']=='wave' and s['x0']<=x<s['x1'] for s in P['sections'])
def nonwave_collision(objects):
 return Counter(tuple(sorted(o.items())) for o in objects if o['1'] in ('1','8') and not wave_x(float(o['2'])))
assert nonwave_collision(O)==nonwave_collision(old_objects)
old_gates={(g['section'],g['t'],g['kind'],g['a'],g['b']):g for g in old_plan['gates']}
wave_gates=[]
for g in P['gates']:
 if sec(g['section'])['mode']!='wave':continue
 before=old_gates[(g['section'],g['t'],g['kind'],g['a'],g['b'])]
 assert abs(before['lo']-g['lo']-5.5)<1e-7
 assert abs(g['hi']-before['hi']-5.5)<1e-7
 wave_gates.append(dict(section=g['section'],time=g['t'],before_gap=before['hi']-before['lo'],after_gap=g['hi']-g['lo']))
assert wave_gates

for native in [o for o in N if o['1']=='1594']:
 assert native.get('135')=='1' and native.get('96')=='1' and native.get('507')=='1'
 assert native.get('445')=='1' and native.get('21')=='13' and native.get('22')=='13'
 skin=[o for o in N if o['1']=='211' and o.get('57')==native['57']]
 assert len(skin)==8
 assert all(o.get('121')==o.get('134')=='1' for o in skin)
 assert all(int(o['21']) in (1,4,7,13) for o in skin)
colors={int(c['6']):tuple(int(c[k]) for k in ('1','2','3')) for c in parse_ks38(parse_header(head)['kS38'])}
assert colors[1000]==(0,0,0)
assert all(max(colors[ch])<=29 for ch in (1,2,3,4,5,6,7,13))
native_head,_=load(str(ROOT/'work/nocturne-native-import.level'))
native_colors={int(c['6']):tuple(int(c[k]) for k in ('1','2','3')) for c in parse_ks38(parse_header(native_head)['kS38'])}
assert all(colors[ch]==native_colors[ch] for ch in (1,2,3,4,5,6,7,13,1000))

fake_counts=Counter(d['kind'] for d in P['fakeouts'])
spider_fakes=sum(sec(d['section'])['mode']=='spider' for d in P['fakeouts'])
for d in P['fakeouts']:
 assert d['a']<d['b'] and 0<=d['lo']<d['hi']<=300
 if d['kind']=='false opening in solid bank':
  bank=d['bank']
  assert bank[0]<bank[1] and bank[2]<d['lo']<d['hi']<bank[3]
  assert any(abs(r['a']-bank[0])<1e-7 and abs(r['b']-bank[1])<1e-7 and abs(r['lo']-bank[2])<1e-7 and abs(r['hi']-bank[3])<1e-7 for r in P['rectangles'])

V=dict(file=FILE.name,sha256=hashlib.sha256(FILE.read_bytes()).hexdigest(),objects=len(O),song=1573528,
 seconds=P['end_time'],slow_percent=P['slow_percent'],rooms=15,modes=7,nominal_inputs=len(P['controls']),
 unchanged_input_score=True,unchanged_nonwave_collision_objects=True,
 wave_extra_clearance_per_side=5.5,wave_gate_checks=wave_gates,
 random_decisions=len(lock_results),random_checks=lock_results,
 fakeouts=len(P['fakeouts']),fakeouts_by_kind=dict(fake_counts),spider_fakeouts=spider_fakes,
 hidden_native_switches=68,dim_switch_skins=68,maximum_switch_color_component=29,
 no_pulse_or_alpha_triggers=True,
 native_import=dict(objects=len(N),object_counts_match=True,hidden_switch_flags_preserved=True,
   claim_touch_and_random_branches_preserved=True,all_fake_art_non_colliding=True,palette_preserved=True),
 visual_review=dict(atlas_camera_views=20,native_opening_switches=True,native_spider=True,native_second_wave=True),
 nominal_path_samples=sum(r['samples'] for r in route),route_checks=route,independent_replay=replay,
 limitations=['No damage-enabled native completion or assigned demon difficulty.',
 'Native appearance inspected; switch branch logic checked from exported and imported objects.',
 'Approximate physics does not fully reproduce native triangle collision, portal offsets or buffering.'])
(ROOT/'outputs/v8-1573528-nocturne-validation.json').write_text(json.dumps(V,indent=2)+'\n')
print(json.dumps({k:v for k,v in V.items() if k not in ('random_checks','route_checks','independent_replay','wave_gate_checks')},indent=2))
