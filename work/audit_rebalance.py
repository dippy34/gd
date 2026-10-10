"""Serialized random-branch truth tables, artwork and portal coverage audit."""
from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,decompress
P=json.loads((ROOT/'work/rebalance-plan.json').read_text())
F=ROOT/'outputs/v8-1573528-rebalance.gmd';f=read_gmd(F)
H,O=load(str(ROOT/'work/v8-rebalance.level'))
assert decompress(f['k4'][1])==(ROOT/'work/v8-rebalance.level').read_text()
assert len(O)==P['objects']==int(f['k48'][1]) and f['k2'][1]=='v8' and f['k45'][1]=='1573528'
native_path=ROOT/'work/rebalance-native-import.level'
if native_path.exists():
    _,N=load(str(native_path));assert len(N)==len(O)
    for a,b in zip(O,N):
        assert a['1']==b['1'] and abs(float(a['2'])-float(b['2']))<.056 and abs(float(a['3'])-float(b['3']))<.013
        for k in ('128','129'):
            assert abs(float(a.get(k,a.get('32',1)))-float(b.get(k,b.get('32',1))))<.0011
else:N=O
def gs(o):return {int(g) for g in o.get('57','').split('.') if g}
def active(o,state):return all(state.get(g,True) for g in gs(o))
def bounds(o):
    x,y=float(o['2']),float(o['3']);hx,hy=15*float(o.get('128',1)),15*float(o.get('129',1))
    return x-hx,x+hx,y-hy,y+hy
def covers(intervals,a,b):
    edge=a
    for lo,hi in sorted(intervals):
        if lo>edge+.025:break
        edge=max(edge,hi)
        if edge>=b-.025:return True
    return edge>=b-.025

alpha={int(o['51']):float(o['35']) for o in O if o['1']=='1007'}
assert alpha[8480]==0 and alpha[8520]==.24
assert not any(o['1']=='1049' and o.get('51') in ('8480','8520') for o in O)
checks=[]
for m in P['random_locks']:
    randoms=[o for o in O if o['1']=='2068' and o['152']==f"{m['branch_yes']}.1.{m['branch_no']}.1"]
    assert len(randoms)==1
    orbs=[o for o in O if o['1']=='1594' and int(o['51'])==m['wall']]
    assert len(orbs)==2 and all(o.get('445')=='1' and o.get('135')=='1' and 8480 in gs(o) for o in orbs)
    init=[o for o in O if o['1']=='1049' and o.get('62')!='1' and int(o['51']) in (m['wall'],m['present'],m['absent'])]
    assert len(init)==3 and all(o['56']=='0' and float(o['2'])<float(randoms[0]['2']) for o in init)
    for branch,wall_present in ((m['branch_yes'],True),(m['branch_no'],False)):
        state={m['wall']:False,m['present']:False,m['absent']:False}
        actions=[o for o in O if o['1']=='1049' and branch in gs(o)]
        assert actions and all(o.get('62')=='1' for o in actions)
        for o in actions:state[int(o['51'])]=o['56']=='1'
        live=[o for o in orbs if active(o,state)]
        assert len(live)==1 and state[m['wall']]==wall_present
        hit_result=live[0]['56']=='1';skip_result=wall_present
        assert (hit_result if wall_present else skip_result)==False
        assert (skip_result if wall_present else hit_result)==True
        skins=[o for o in O if o.get('20')=='15' and active(o,state) and abs(float(o['2'])-float(live[0]['2']))<.001]
        assert Counter(o['1'] for o in skins)=={'3636':1,'1764':1}
    wall=[bounds(o) for o in O if o['1']=='1' and m['wall'] in gs(o)]
    assert wall and covers([(r[2],r[3]) for r in wall],0,300)
    points=[p for p in P['paths'] if m['t']<p[0]<m['gate_t']+.12]
    assert any(r[0]<p[1]+p[4] and r[1]>p[1]-p[4] and r[2]<p[2]+p[4] and r[3]>p[2]-p[4] for r in wall for p in points)
    checks.append(dict(section=m['section'],time=m['t'],probability=.5,both_correct_choices_pass=True,both_wrong_choices_block=True))
assert len(checks)==25

portals=[]
for p in P['portal_passages']:
    physical=[o for o in N if o['1']==str(p['id']) and o.get('121')!='1' and abs(float(o['2'])-p['x'])<.056]
    display=[o for o in N if o['1']==str(p['id']) and o.get('121')=='1' and abs(float(o['2'])-p['x'])<.056]
    assert len(physical)==len(display)==1
    o=physical[0];art=display[0]
    assert o.get('135')=='1' and 8480 in gs(o)
    assert float(art.get('128',1))==float(art.get('129',1))==1 and art.get('135')!='1' and 8480 not in gs(art)
    low=float(o['3'])-15*float(o['129']);high=float(o['3'])+15*float(o['129'])
    assert low<p['lo']-1.9 and high>p['hi']+1.9
    intervals=[]
    for q in N:
        if q['1']!='1' or q.get('121')=='1':continue
        a,b,lo,hi=bounds(q)
        if a-.06<=float(o['2'])<=b+.06:intervals.append((lo,hi))
    assert covers(intervals,-30,p['lo']) and covers(intervals,p['hi'],330)
    portals.append(dict(id=p['id'],x=p['x'],visible_scale=1,extended_activation_invisible=True,bypass_closed=True))
assert len(portals)==68

_,original=load(str(ROOT/'work/v8-nocturne.level'))
spiders=[s for s in P['sections'] if s['mode']=='spider']
first=next(s for s in spiders if s['name']=='BLIND ELEVATOR')
def first_spider_art(oo):return [o for o in oo if o.get('20')=='11' and not o.get('57') and first['x0']<=float(o['2'])<first['x1']]
assert first_spider_art(O)==first_spider_art(original)
assert len(first_spider_art(O))==1183
assert set(d['section'] for d in P['fakeouts'])=={'BLIND ELEVATOR','RECALL'}
assert not any(o.get('20')=='14' or o['1']=='901' for o in O)
assert not P['decor_inlays'] and not P['decor_fixtures']
for s in spiders:
    assert any(o.get('20')=='11' and s['x0']<float(o['2'])<s['x1'] for o in O)
assert all(o.get('121')=='1' and o.get('134')=='1' for o in O if o.get('20') in ('14','15') and o['1'] in ('211','1764','3636'))
assert not any(o['1'] in ('1006','1935') for o in O)
assert all(o.get('135')=='1' and 8480 in gs(o) for o in O if o['1']=='1764' and gs(o)&set(range(900,915)))
route=json.loads((ROOT/'work/rebalance-route-check.json').read_text())
replay=json.loads((ROOT/'work/rebalance-replay.json').read_text())
assert not any(r['errors'] for r in route+replay)
measurements=json.loads((ROOT/'work/rebalance-measurements.json').read_text())
previous=json.loads((ROOT/'work/phrases-plan.json').read_text())
earlier=json.loads((ROOT/'work/restored-plan.json').read_text())
for s in P['sections']:
    def controls(plan):return [e for e in plan['controls'] if s['t0']<=e['time']<s['t1'] and e['kind']!='memory']
    if s['index']<8 and s['name']!='BLINDFOLD':assert controls(P)==controls(earlier)
    if 8<=s['index']<14:assert controls(P)==controls(previous) and controls(P)!=controls(earlier)
assert len(P['sections'][3]['ground_glides'])>=3
assert sum(o['1']=='1704' for o in O)==4
assert not any(o['1']=='1751' for o in O)
assert len(P['sections'][-1]['dash_windows'])==4
assert len(P['sections'][-1]['dash_robust_points'])>6000
assert {s['mode'] for s in P['sections']}=={'cube','robot','ball','ufo','spider','wave','ship'}
for d in measurements['dash_releases']:
    assert any(q['passes'] for q in d['tests']) and any(not q['passes'] for q in d['tests'])
V=dict(file=F.name,sha256=hashlib.sha256(F.read_bytes()).hexdigest(),objects=len(O),song=1573528,
       seconds=P['end_time'],slow_percent=P['slow_percent'],summary=P['finish_summary'],balance_measurements=measurements['balance'],
       random_checks=checks,portal_checks=portals,unchanged_first_spider_art=True,
       route_samples=sum(r['samples'] for r in route),route_failures=0,replay_sections=15,replay_failures=0,
       native_import_verified=native_path.exists(),
       limitations='Route physics and conservative portal cores are model assumptions. Full damage-enabled native completion and an exact demon rating remain unverified.',
       references=['https://www.robtopgames.com/files/GDEditor.pdf',
       'https://github.com/GDCreatorSchool/gdcs2/blob/main/content/docs/guides/the-editor/editing-objects.md'])
(ROOT/'outputs/v8-1573528-rebalance-validation.json').write_text(json.dumps(V,indent=2)+'\n')
print(json.dumps({k:v for k,v in V.items() if k not in ('random_checks','portal_checks','references')},indent=2))
