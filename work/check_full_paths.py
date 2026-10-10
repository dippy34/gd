"""Finite-body diagnostics using exported solids, not the builder's wall list.

This is an approximate physics model, not native completion verification.
It deliberately reports all contacts so geometry can be revised before import.
"""
import json,math,sys,bisect
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
exec((ROOT/'work/verify_balanced.py').read_text().split('f0,h0,')[0])
f,h,raw,s=read(ROOT/'outputs/v8-full.gmd')
plan=json.loads((ROOT/'work/full-plan.json').read_text())
bins=defaultdict(list);hb=defaultdict(list)
for _,o in raw:
 x,y=float(o['2']),float(o['3']);oid=int(o['1'])
 if oid==1:
  w=30*float(o.get('128',o.get('32',1)));ht=30*float(o.get('129',o.get('32',1)))
  q=(x-w/2,x+w/2,y-ht/2,y+ht/2)
  for k in range(math.floor(q[0]/120),math.floor(q[1]/120)+1):bins[k].append(q)
 if oid==8:
  r=15*float(o.get('32',1));up=float(o.get('6',0))%360==0
  q=(x-r,x+r,y-r,y+r,up)
  for k in range(math.floor(q[0]/120),math.floor(q[1]/120)+1):hb[k].append(q)
def nearby(x,r=15):
 return set(q for k in range(math.floor((x-r)/120),math.floor((x+r)/120)+1) for q in bins[k])
def solids(x,y,r=15):
 return [q for q in nearby(x,r) if q[0]<x+r-.015 and q[1]>x-r+.015 and q[2]<y+r-.015 and q[3]>y-r+.015]
def hazard(x,y,r=15):
 # Conservative full visual AABB includes the native spike rectangle.
 return [q for k in range(math.floor((x-r)/120),math.floor((x+r)/120)+1) for q in hb[k]
  if q[0]<x+r-.02 and q[1]>x-r+.02 and q[2]<y+r-.02 and q[3]>y-r+.02]
def xat(sec,t):return sec['x0']+(t-sec['t0'])*sec['speed']
def clearance(x,y,r=15):
 vals=[min(abs(y-r-q[3]),abs(q[2]-y-r)) for q in nearby(x,r) if q[0]<x+r and q[1]>x-r]
 return min(vals,default=999)
errors=[];checks=[];allpaths=[]
offset=float(sys.argv[1]) if len(sys.argv)>1 else 0
gravity_scale=float(sys.argv[2]) if len(sys.argv)>2 else 1
blue_impulse=float(sys.argv[3]) if len(sys.argv)>3 else None
for sec in plan['sections']:
 mode=sec['mode'];a,b=sec['t0'],sec['t1'];v=sec['speed'];t=a
 controls=[e for e in plan['controls'] if e['mode']==mode and a-1e-5<=e['time']<b]
 events=sorted([dict(e,time=e['time']+offset) for e in controls],key=lambda e:e['time']);ei=0;y=sec['incoming_y'];vy=0;grav=-1;held=False;hold_end=-1;ground=False
 count=Counter();first={};path=[];jump={1:670.8,2:685.2,3:673.8}[sec['speed_index']]
 def err(kind,**extra):
  count[kind]+=1
  if kind not in first:first[kind]=dict(time=round(t,4),x=round(xat(sec,t),2),y=round(y,3),**extra)
 # Grounded modes can fall onto a previous section's last platform.
 if mode in ['cube','robot','ball','spider']:
  if solids(xat(sec,t),y):err('entry overlap')
  if y<=15.01:y=15;ground=True
 else:
  # Author's flight dynamics are separately bounded; all actual walls are
  # still checked with full player dimensions in this export audit.
  r=12 if mode=='wave' else 15
  for t,y in sec['flight_points']:
   x=xat(sec,t)
   if solids(x,y,r):err('flight wall',boxes=solids(x,y,r)[:2])
   if hazard(x,y,r):err('flight spike')
   path.append([t,x,y])
  checks.append(dict(name=sec['name'],mode=mode,errors=dict(count),first=first,exit_y=y,samples=len(path)))
  allpaths.append(dict(name=sec['name'],mode=mode,points=path));continue
 reset=b-.68 if mode in ['ball','spider'] else math.inf
 while t<b-1e-7:
  ne=events[ei]['time'] if ei<len(events) else math.inf
  if ne<=t+1e-6:
   e=events[ei];ei+=1
   if e['kind'] in ['jump','hold']:
    if not ground:err('airborne jump')
    vy=-grav*jump*(.5 if mode=='robot' else 1);ground=False;hold_end=t+e.get('hold',0)
   elif e['kind']=='orb':
    orb=min(plan['orbs'],key=lambda o:abs(o[1]-xat(sec,t)))
    if abs(orb[2]-y)>25:err('orb out of reach',orb_y=orb[2])
    if e['orb_id']==84:grav*=-1;vy=grav*(jump*.4 if blue_impulse is None else blue_impulse)
    else:vy=-grav*jump*(.72 if e['orb_id']==141 else 1)
    ground=False
   elif e['kind']=='flip':
    if not ground:err('airborne flip')
    grav*=-1;vy=grav*jump*.3 if mode=='ball' else 0;ground=False
    if mode=='spider':
     # Teleport hits an actual surface in the exported level at this column.
     candidates=[q for q in nearby(xat(sec,t),0) if q[0]<=xat(sec,t)<=q[1] and (q[2]>=y+14 if grav>0 else q[3]<=y-14)]
     if not candidates:err('spider has no surface')
     else:
      y=min(q[2] for q in candidates)-15 if grav>0 else max(q[3] for q in candidates)+15
      ground=True
   continue
  if t>=reset-1e-7:grav=-1;ground=False;reset=math.inf
  to=min(b,t+1/240,ne,reset);dt=to-t
  if dt<1e-9:t+=1e-7;continue
  oldy=y;x=xat(sec,to)
  acc=grav*(2200 if mode=='ball' else 3110.4)*gravity_scale
  if mode=='robot' and t<hold_end:acc=0;vy=-grav*jump*.5
  if not ground:y+=vy*dt+.5*acc*dt*dt;vy+=acc*dt
  # A resting icon remains supported only while the surface exists.
  if ground:
   support=[q for q in nearby(x) if q[0]<x+15 and q[1]>x-15 and abs((q[2]-15 if grav>0 else q[3]+15)-y)<.1]
   if not support:ground=False
  boxes=nearby(x)
  landing=[q for q in boxes if q[0]<x+15-.01 and q[1]>x-15+.01 and vy<=0 and oldy-15>=q[3]-.1 and y-15<=q[3]]
  ceiling=[q for q in boxes if q[0]<x+15-.01 and q[1]>x-15+.01 and vy>=0 and oldy+15<=q[2]+.1 and y+15>=q[2]]
  if landing and grav<0:y=max(q[3] for q in landing)+15;vy=0;ground=True
  if ceiling and grav>0:y=min(q[2] for q in ceiling)-15;vy=0;ground=True
  t=to
  if solids(x,y):err('solid collision',boxes=solids(x,y)[:2])
  if hazard(x,y):err('spike collision')
  path.append([t,x,y])
 checks.append(dict(name=sec['name'],mode=mode,errors=dict(count),first=first,exit_y=y,samples=len(path)))
 allpaths.append(dict(name=sec['name'],mode=mode,points=path))
print(json.dumps([c for c in checks if c['errors']],indent=2))
suffix='' if offset==0 and gravity_scale==1 and blue_impulse is None else f'-{offset}-{gravity_scale}'+(f'-blue{blue_impulse}' if blue_impulse is not None else '')
(ROOT/f'work/full-path-checks{suffix}.json').write_text(json.dumps(checks,indent=2))
if not suffix:(ROOT/'work/checked-paths.json').write_text(json.dumps(allpaths))
print('Sections',len(checks),'with errors',sum(bool(c['errors']) for c in checks))
