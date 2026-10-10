"""Audit actual random branches, route clearance, and native serialization."""
from pathlib import Path
from collections import Counter
import json,sys,math,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load,parse_header,parse_ks38
from gmd import read_gmd,decompress
P=json.loads((ROOT/'work/branching-plan.json').read_text())
FILE=ROOT/'outputs/v8-1573528-branching.gmd';F=read_gmd(FILE)
raw=decompress(F['k4'][1]);head,O=load(str(ROOT/'work/v8-branching.level'))
assert raw==(ROOT/'work/v8-branching.level').read_text()
_,N=load(str(ROOT/'work/branching-native-import.level'))
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
assert len(P['phrases'])==18 and len(P['fakeouts'])==50
for s in P['sections'][9:]:
 previous=[q for q in P['sections'][:9] if q['mode']==s['mode']]
 score=lambda q:[(round(e['time']-q['t0'],4),e['kind'],e.get('hold'),e.get('orb_id')) for e in P['controls'] if q['t0']<=e['time']<q['t1'] and e['mode']==q['mode']]
 assert all(score(q)!=score(s) for q in previous)

route=json.loads((ROOT/'work/branching-route-check.json').read_text());replay=json.loads((ROOT/'work/branching-replay.json').read_text())
assert not any(r['errors'] for r in route+replay)
V=dict(file=FILE.name,sha256=hashlib.sha256(FILE.read_bytes()).hexdigest(),objects=len(O),song=1573528,seconds=P['end_time'],
 slow_percent=P['slow_percent'],rooms=15,modes=7,nominal_inputs=len(P['controls']),random_decisions=len(lock_results),
 random_checks=lock_results,distinct_flight_phrases=18,fitted_fakeouts=50,no_pulse_or_alpha_triggers=True,
 native_import=dict(objects=len(N),object_counts_match=True,claim_touch_and_random_branches_survive=True,
   random_wall_observed_present_on_attempts=[1,2],random_wall_observed_absent_on_attempts=[3]),
 nominal_path_samples=sum(r['samples'] for r in route),route_checks=route,independent_replay=replay,
 limitations=['No native damage-enabled completion verification or assigned demon rating.',
 'Native random starting states visually checked; all switch truth tables tested from serialized objects.',
 'Approximate physics replay does not fully model native triangle collision, portal entry offsets, or input buffering.'])
(ROOT/'outputs/v8-1573528-branching-validation.json').write_text(json.dumps(V,indent=2))
print(json.dumps({k:v for k,v in V.items() if k not in ('random_checks','route_checks','independent_replay')},indent=2))
