"""Audit exported geometry and conditional gate states, independently of builder.
This checks a proposed trajectory, NOT native playability or demon difficulty.
"""
from pathlib import Path
import sys,json,math,bisect,hashlib
from collections import defaultdict,Counter
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gmd import read_gmd,decompress
f=read_gmd(ROOT/'outputs/v8-1573528-timing.gmd')
raw=decompress(f['k4'][1]);tokens=raw.split(';');objects=[]
for token in tokens[1:]:
 if not token:continue
 ps=token.split(',');assert len(ps)%2==0;objects.append(dict(zip(ps[::2],ps[1::2])))
P=json.loads((ROOT/'work/memory-plan.json').read_text())
rects=[];spikes=[];bybin=defaultdict(list);spbin=defaultdict(list)
for i,o in enumerate(objects):
 oid=int(o['1']);x=float(o['2']);y=float(o['3']);g=tuple(int(v) for v in o.get('57','').split('.') if v)
 if oid==1 and o.get('121')!='1':
  w=30*float(o.get('128',o.get('32',1)));h=30*float(o.get('129',o.get('32',1)))
  q=(x-w/2,x+w/2,y-h/2,y+h/2,g,i);rects.append(q)
  for k in range(math.floor(q[0]/100),math.floor(q[1]/100)+1):bybin[k].append(q)
 elif oid==8:
  r=15*float(o.get('32',1));q=(x-r,x+r,y-r,y+r,g,i);spikes.append(q)
  assert y-r>=-.001 and y+r<=300.001,('spike bounds',i,y,r)
  for k in range(math.floor(q[0]/100),math.floor(q[1]/100)+1):spbin[k].append(q)
assert f['k2'][1]=='v8' and f['k45'][1]=='1573528'
assert not any(o['1'] in ('1935',) for o in objects)
assert {12,13,47,111,660,745,1331}<=set(int(o['1']) for o in objects)
assert len(objects)==int(f['k48'][1])
def nearby(bins,x,r):return set(q for k in range(math.floor((x-r)/100),math.floor((x+r)/100)+1) for q in bins[k])
def overlap(q,x,y,r):return q[0]<x+r-.075 and q[1]>x-r+.075 and q[2]<y+r-.075 and q[3]>y-r+.075
# Gate state is obtained from actual serialized trigger/orb properties.
events=[]
for o in objects:
 if o['1']=='1049':events.append((float(o['2']),int(o['51']),o.get('56')=='1'))
for e in P['controls']:
 if e['kind']=='memory':
  candidates=[o for o in objects if o['1']=='1594' and int(o.get('51',0))==e['target']]
  assert len(candidates)==1
  o=candidates[0];events.append((float(o['2']),int(o['51']),o.get('56')=='1'))
events.sort();active={};ei=0;errors=defaultdict(Counter);first=defaultdict(dict);counts=Counter()
for t,x,y,mode,r,g in sorted(P['paths']):
 while ei<len(events) and events[ei][0]<=x+1e-6:
  _,grp,on=events[ei];active[grp]=on;ei+=1
 sec=P['sections'][max(0,bisect.bisect_right([s['t0'] for s in P['sections']],t)-1)]['name']
 for typ,bins in [('solid',bybin),('spike',spbin)]:
  for q in nearby(bins,x,r):
   if any(not active.get(v,True) for v in q[4]):continue
   if overlap(q,x,y,r):
    errors[sec][typ]+=1
    if typ not in first[sec]:first[sec][typ]=dict(t=t,x=x,y=y,box=q[:4],object=q[-1])
 counts[sec]+=1
results=[dict(section=s['name'],samples=counts[s['name']],errors=dict(errors[s['name']]),first=first[s['name']]) for s in P['sections']]
# Every memory choice must affect a real full-height barrier beyond its orb.
memory=[]
for m in P['memories']:
 orbs=[o for o in objects if o['1']=='1594' and int(o.get('51',0))==m['group']];assert len(orbs)==1
 gate=[q for q in rects if m['group'] in q[4]];assert gate
 assert min(q[2] for q in gate)<=.001 and max(q[3] for q in gate)>=299.99
 before=not any(e[1]==m['group'] and not e[2] and e[0]<float(orbs[0]['2']) for e in events)
 after=orbs[0].get('56')=='1'
 assert before==m['correct'] and after!=m['correct']
 memory.append(dict(section=m['section'],time=m['t'],correct=m['correct'],group=m['group'],wrong_choice_leaves_or_creates_full_wall=True,
  orb_to_wall_lead_units=min(q[0] for q in gate)-float(orbs[0]['2'])))
ids=Counter(int(o['1']) for o in objects)
summary=dict(file='v8-1573528-timing.gmd',sha256=hashlib.sha256((ROOT/'outputs/v8-1573528-timing.gmd').read_bytes()).hexdigest(),
 objects=len(objects),seconds=P['end_time'],slow_percent=P['slow_percent'],mode_count=7,rooms=len(P['sections']),input_events=len(P['controls']),
 spike_count=len(spikes),spikes_outside_playfield=0,native_timewarp_objects=ids[1935],memory_decisions=len(memory),
 nominal_path_samples=len(P['paths']),rooms_with_nominal_overlaps=sum(bool(r['errors']) for r in results),results=results,memory_checks=memory,
 limitations=['Recorded-route finite-body collision audit, not native completion verification.',
 'Ship/UFO/ball acceleration and portal contact offsets need native testing.',
 'Target difficulty is not a measured or assigned demon rating.'])
(ROOT/'outputs/v8-1573528-timing-validation.json').write_text(json.dumps(summary,indent=2))
print(json.dumps([r for r in results if r['errors']],indent=2));print('rooms with overlaps',summary['rooms_with_nominal_overlaps'])
print('memory lead min',min(m['orb_to_wall_lead_units'] for m in memory))
