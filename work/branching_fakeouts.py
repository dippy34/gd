"""Fit deliberate false landings and blind side branches to authored structures."""
from pathlib import Path
import sys,json,math,base64,hashlib
from collections import defaultdict
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,compress,write_gmd
P=json.loads((ROOT/'work/branching-plan.json').read_text())
H,O=load(str(ROOT/'work/v8-branching-skinned.level'));decoys=[];added=[]
R=[r for r in P['rectangles'] if not r.get('group')];bins=defaultdict(list)
sections={s['name']:s for s in P['sections']}
wall_x=[sections[m['section']]['x0']+(m['gate_t']-sections[m['section']]['t0'])*sections[m['section']]['speed'] for m in P['memories']]
for r in R:
 for b in range(math.floor(r['a']/100),math.floor(r['b']/100)+1):bins[b].append(r)
def nearby(a,b):return list({id(r):r for i in range(math.floor(a/100),math.floor(b/100)+1) for r in bins[i]}.values())
def overlap(a,b,lo,hi,r,pad=0):return a<r['b']+pad and b>r['a']-pad and lo<r['hi']+pad and hi>r['lo']-pad
def contains(q):
 clips=[(max(q[0],r['a']),min(q[1],r['b']),max(q[2],r['lo']),min(q[3],r['hi'])) for r in nearby(q[0],q[1]) if overlap(*q,r)]
 xs=sorted({x for a,b,lo,hi in clips for x in (a,b)});area=0
 for a,b in zip(xs,xs[1:]):
  mid=(a+b)/2;end=-1e9;length=0
  for lo,hi in sorted((lo,hi) for aa,bb,lo,hi in clips if aa<=mid<=bb):length+=max(0,hi-max(lo,end));end=max(end,hi)
  area+=(b-a)*length
 return area>=(q[1]-q[0])*(q[3]-q[2])-.0001
def art(a,b,lo,hi,ch=1):
 assert b>a and hi>lo
 o={'1':'211','2':str((a+b)/2),'3':str((lo+hi)/2),'128':str((b-a)/30),'129':str((hi-lo)/30),
    '21':str(ch),'22':str(ch),'24':'5','25':'-1','20':'10','64':'1','67':'1','96':'1','121':'1','134':'1'}
 O.append(o);added.append(o)
def avoid_interactions(a,b,lo,hi):
 return not any(a-35<o['x']<b+35 and lo-35<o['y']<hi+35 for o in P['orbs']) and not any(a-15<x<b+15 for x in wall_x)
for s in P['sections']:
 local=[r for r in R if s['x0']<=r['a'] and r['b']<=s['x1'] and r['kind'] in ('suspended landing','island rail','upper rail','teleport shelf')]
 last=-1e9
 for i,r in enumerate(local):
  if r['a']-last<90 or r['hi']-r['lo']<10 or not(10<r['lo'] and r['hi']<290):continue
  for side in (1,-1):
   for w in (56,43,31):
    a,b=(r['b'],r['b']+w) if side>0 else (r['a']-w,r['a']);lo,hi=r['lo'],r['hi']
    if not(s['x0']+130<a and b<s['x1']-180):continue
    if any(overlap(a+.05,b-.05,lo,hi,q) for q in nearby(a,b)):continue
    if any(a-3<q['x']+q['r'] and b+3>q['x']-q['r'] and lo-3<q['y']+q['r'] and hi+3>q['y']-q['r'] for q in P['spikes']):continue
    if not avoid_interactions(a,b,lo,hi):continue
    if any(overlap(a,b,lo,hi,q,10) for q in decoys):continue
    art(a,b,lo,hi);art(a,b,hi-.9,hi,2);art(a+3,b-3,lo+3,hi-3,5)
    decoys.append(dict(section=s['name'],kind='false extension of real ledge',a=a,b=b,lo=lo,hi=hi,host=r));last=r['a'];break
   else:continue
   break
 # Blind passages are L-shaped recesses inside a real wall mass. Their mouth
 # is adjacent to the wall contour, with a closed end, and no flashing mask.
 last=-1e9
 for j,beat in enumerate([2.0,3.6,5.3,7.1,8.8,10.6,12.3,14.1,15.8,17.6,19.3,21.1,22.8,24.6,26.3,28.1]):
  t=s['t0']+beat*(60/131)
  if t>s['t1']-.9:continue
  x=s['x0']+(t-s['t0'])*s['speed'];width=[56,71,48,64][j%4]
  if x-last<100:continue
  a=x-width/2;b=x+width/2
  if s['mode'] not in ('ship','wave') and j%2:continue
  choices=[]
  for cy in (38,65,92,119,146,173,200,227,254):
   q=(a,b,cy-11,cy+11)
   if contains(q) and avoid_interactions(*q) and not any(overlap(*q,d,12) for d in decoys):choices.append(q)
  if not choices:continue
  # Pick the closest contained recess to the route, not an arbitrary deep box.
  p=min(s['points'],key=lambda p:abs(p[0]-t));q=min(choices,key=lambda q:abs((q[2]+q[3])/2-p[1]))
  a,b,lo,hi=q;cy=(lo+hi)/2
  art(a,b-4,cy-5,cy+5,5)
  if p[1]<cy:art(a,a+11,lo,cy+5,5)
  else:art(a,a+11,cy-5,hi,5)
  art(b-5,b-3,cy-5,cy+5,6)
  decoys.append(dict(section=s['name'],kind='blind L-shaped side passage',a=a,b=b,lo=lo,hi=hi));last=x

ser=lambda o:','.join(f'{k},{v}' for k,v in o.items());raw=';'.join([H]+[ser(o) for o in O])+';'
f=read_gmd(ROOT/'work/branching-skinned.gmd');f['k4']=('s',compress(raw));f['k48']=('i',str(len(O)))
f['k3']=('s',base64.urlsafe_b64encode(b'Song 1573528. Dark branching memory. Wall switches randomize each attempt: press for a wall, skip for no wall. Seven modes, different second half.').decode())
out=ROOT/'outputs/v8-1573528-branching.gmd';write_gmd(out,f);(ROOT/'work/v8-branching.level').write_text(raw)
P['objects']=len(O);P['fakeouts']=decoys;(ROOT/'work/branching-plan.json').write_text(json.dumps(P,separators=(',',':')))
audit=dict(objects=len(O),added_art_objects=len(added),fakeouts=len(decoys),by_kind={k:sum(d['kind']==k for d in decoys) for k in set(d['kind'] for d in decoys)},
           sha256=hashlib.sha256(out.read_bytes()).hexdigest())
(ROOT/'work/branching-fakeout-audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
