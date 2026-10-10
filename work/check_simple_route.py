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
f=read_gmd(ROOT/'outputs/v8-1573528-simple.gmd')
raw=decompress(f['k4'][1]);tokens=raw.split(';');objects=[]
for token in tokens[1:]:
 if not token:continue
 ps=token.split(',');assert len(ps)%2==0;objects.append(dict(zip(ps[::2],ps[1::2])))
P=json.loads((ROOT/'work/simple-plan.json').read_text())
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
 if o['1']=='1049' and o.get('62')!='1':events.append((float(o['2']),int(o['51']),o.get('56')=='1'))
for e in P['controls']:
 if e['kind']=='memory':
  candidates=[o for o in objects if o['1']=='1594' and int(o.get('51',0))==e['target']]
  candidates=[o for o in candidates if o.get('56')=='0'];assert len(candidates)==1
  o=candidates[0];events.append((float(o['2']),int(o['51']),o.get('56')=='1'))
events.extend((m['roll']*0+next(e['x'] for e in P['controls'] if e.get('target')==m['wall'])-.1,int(m['wall']),True) for m in P['random_locks']);events.sort();active={};ei=0;errors=defaultdict(Counter);first=defaultdict(dict);counts=Counter()
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

print(json.dumps(results,indent=2));(ROOT/'work/simple-route-check.json').write_text(json.dumps(results,indent=2))
