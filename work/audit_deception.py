"""Audit actual random branches, route clearance, and native serialization."""
from pathlib import Path
from collections import Counter
import json,sys,math,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load,parse_header,parse_ks38
from gmd import read_gmd,decompress
P=json.loads((ROOT/'work/deception-plan.json').read_text())
FILE=ROOT/'outputs/v8-1573528-deception.gmd';F=read_gmd(FILE)
raw=decompress(F['k4'][1]);head,O=load(str(ROOT/'work/v8-deception.level'))
assert raw==(ROOT/'work/v8-deception.level').read_text()
native_path=ROOT/'work/deception-native-import.level'
N=load(str(native_path))[1] if native_path.exists() else []
assert len(O)==P['objects']==int(F['k48'][1])
if N:
 assert len(N)==len(O)
 assert Counter(o['1'] for o in O)==Counter(o['1'] for o in N)
assert F['k2'][1]=='v8' and F['k45'][1]=='1573528'
assert not any(o['1'] in ('1935','1006') for o in O)
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
 if N:
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

route=json.loads((ROOT/'work/deception-route-check.json').read_text());replay=json.loads((ROOT/'work/deception-replay.json').read_text())
assert not any(r['errors'] for r in route+replay)

old_plan=json.loads((ROOT/'work/nocturne-plan.json').read_text())
_,old_objects=load(str(ROOT/'work/v8-nocturne.level'))
assert P['controls']==old_plan['controls'] and P['paths']==old_plan['paths']
assert P['random_locks']==old_plan['random_locks']
spider_results=[]
for s in P['sections']:
 if s['mode']!='spider':continue
 sig=lambda objects:Counter(tuple(sorted(o.items())) for o in objects if s['x0']<=float(o['2'])<s['x1'])
 assert sig(O)==sig(old_objects)
 spider_results.append(dict(section=s['name'],objects=sum(sig(O).values()),all_objects_identical=True))
assert len(P['fakeouts'])==385 and all(sec(d['section'])['mode']=='spider' for d in P['fakeouts'])
assert P['removed_nonspider_decoys']==592
switch_groups={str(m[k]) for m in P['random_locks'] for k in ('present','absent')}
for o in O:
 if o.get('20')!='11':continue
 assert o.get('57') in switch_groups or any(s['mode']=='spider' and s['x0']<=float(o['2'])<s['x1'] for s in P['sections'])

affected={b['section'] for b in P['branches']}
def unaffected_collision(objects):
 return Counter(tuple(sorted(o.items())) for o in objects if o['1'] in ('1','8') and not any(sec(n)['x0']<=float(o['2'])<sec(n)['x1'] for n in affected))
assert unaffected_collision(O)==unaffected_collision(old_objects)

alphas=[o for o in O if o['1']=='1007']
assert len(alphas)==1 and alphas[0]['51']=='8500' and float(alphas[0]['2'])==0
assert float(alphas[0]['35'])==.13 and float(alphas[0]['10'])==0
for o in O:
 if o['1'] in ('36','84','141'):
  assert o.get('57')=='8500' and float(o.get('32',1))==1
  assert o.get('121')!='1' and o.get('135')!='1'
  assert o.get('507')=='1' and o.get('96')=='1'
for b in P['baits']:
 matches=[o for o in O if o['1']==str(b['id']) and abs(float(o['2'])-b['x'])<.0001 and abs(float(o['3'])-b['y'])<.0001]
 assert len(matches)==1 and matches[0].get('20')=='12'
 assert b['wrong_hit_collides']
 assert any(k in b['first_collision'] for k in ('solid collision','spike collision'))
 inputs=[e for e in P['controls'] if sec(b['section'])['t0']<=e['time']<sec(b['section'])['t1']]
 assert all(abs(e['time']-b['t'])>=.2799 for e in inputs)
 assert all(not(e['kind']=='hold' and e['time']-.26<b['t']<e['time']+e.get('hold',0)+.26) for e in inputs)
assert len(P['baits'])==17

branches=json.loads((ROOT/'work/deception-branch-checks.json').read_text())
assert len(branches)==4
for b in branches:
 assert b['first_collision'] and b['first_collision'][0]>=b['length']-b['body_radius']-2
 assert b['first_collision'][0]<=b['length']+8
 assert 'solid' in b['first_collision'][1]
assert all(b['removed_solid_area']>150 for b in P['branches'])
for portal in P['branch_portals']:
 assert portal['route_separation']>45
 assert any(o['1']==str(portal['id']) and abs(float(o['2'])-portal['x'])<.0001 and abs(float(o['3'])-portal['y'])<.0001 for o in O)

V=dict(file=FILE.name,sha256=hashlib.sha256(FILE.read_bytes()).hexdigest(),objects=len(O),song=1573528,
 seconds=P['end_time'],slow_percent=P['slow_percent'],rooms=15,modes=7,nominal_inputs=len(P['controls']),
 unchanged_input_score=True,spider_sections=spider_results,spider_visual_decoys=385,
 removed_nonspider_visual_decoys=592,unchanged_collision_outside_four_flight_rooms=True,
 live_bait_orbs=len(P['baits']),bait_checks=P['baits'],real_blind_branches=4,branch_checks=branches,
 gravity_portals_in_wrong_branches=len(P['branch_portals']),random_decisions=len(lock_results),random_checks=lock_results,
 matched_required_and_bait_orb_display=dict(scale=1,constant_opacity=.13,no_glow=True),
 no_flashing_triggers=True,native_import_checked=bool(N),
 native_check_note='Fresh import not completed because GD was being used concurrently; older native screenshots do not verify this revision.' if not N else 'Object count and random logic checked against fresh native serialization.',
 atlas_camera_views=18,nominal_path_samples=sum(r['samples'] for r in route),route_checks=route,independent_replay=replay,
 limitations=['Full native completion and exact demon difficulty remain unverified.',
 'Wrong-orb tests use approximate native-physics parameters; live input buffering and collision details require player testing.',
 'Branch checks verify geometric access and solid dead ends, not a full alternate-input native run.'])
(ROOT/'outputs/v8-1573528-deception-validation.json').write_text(json.dumps(V,indent=2)+'\n')
print(json.dumps({k:v for k,v in V.items() if k not in ('bait_checks','random_checks','route_checks','independent_replay')},indent=2))
