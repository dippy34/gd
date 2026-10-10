"""v8 / NULL CHOIR: authored memory rooms for song 1573528.

No source gameplay is reused. Models are design diagnostics, not a GD verifier.
Units are GD world units; physics ticks are 1/240 s. Audio onsets come from the
user's cached MP3. Every room has its own score and structural rule.
"""
from pathlib import Path
import sys, json, math, bisect, base64, hashlib
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gmd import read_gmd, decompress, compress, write_gmd
from gdparse import parse_header,parse_ks38
B=60/131; PHASE=.0011672084571444524; G=3110.4
AUDIO=json.loads((ROOT/'work/music-1573528-analysis.json').read_text())
AT=np.array([e['time'] for e in AUDIO['onsets']])
SCORE=[
 (0,32,'cube',0,'CIPHER','selective switches / suspended terraces'),
 (32,56,'robot',0,'CUTWIRE','short and long holds / false landing plates'),
 (56,80,'ball',0,'SWITCHYARD','staggered gravity rails / blocked exits'),
 (80,112,'wave',1,'BLINDFOLD','concealed industrial channel / irregular bursts'),
 (112,144,'ufo',0,'OFFBEAT','tap omissions / ascending window sequence'),
 (144,176,'ship',1,'PARALLAX','long drift and short corrections / inverted control'),
 (176,200,'spider',0,'BLIND ELEVATOR','false teleport targets / alternating shelf depths'),
 (200,232,'cube',0,'CROSSCODE','blue orb transfers / inverted pink and yellow orbs'),
 (232,264,'wave',0,'FAULTLINE','mini wave / three displaced lanes / concealed crossings'),
 (264,288,'robot',0,'NEEDLEWORK','low ceilings / compressed holds / stepdown landings'),
 (288,320,'ufo',0,'COUNTERFEIT','inverted flight / false orb pairs / low-high chambers'),
 (320,352,'ball',0,'FALSE FLOOR','island rails / hidden solid dividers / delayed flips'),
 (352,384,'ship',0,'UNDERTOW','sustained low flight / stepped climb / staggered slits'),
 (384,416,'spider',0,'RECALL','short teleport slots / asymmetric stacked platforms'),
 (416,448,'cube',0,'LAST WORD','moving code tokens / recall locks / descending islands'),
]
SECTIONS=[]; xx=0
for i,(b0,b1,mode,sp,name,rule) in enumerate(SCORE):
 t0=0 if b0==0 else PHASE+b0*B;t1=PHASE+b1*B;v=[251.16,311.58][sp]
 SECTIONS.append(dict(index=i,beat0=b0,beat1=b1,t0=t0,t1=t1,x0=xx,x1=xx+(t1-t0)*v,mode=mode,speed=v,speed_index=sp,name=name,rule=rule))
 xx=SECTIONS[-1]['x1']
END=SECTIONS[-1]['t1']
def sec_at(t):return SECTIONS[max(0,min(len(SECTIONS)-1,bisect.bisect_right([s['t0'] for s in SECTIONS],t)-1))]
def xt(t):
 s=sec_at(t);return s['x0']+(t-s['t0'])*s['speed']
def bt(b):return 0 if b==0 else PHASE+b*B
def snap(t,rad=.18):
 near=AT[np.abs(AT-t)<=rad]
 return float(near[np.argmin(abs(near-t))]) if len(near) else t

class Level:
 def __init__(self):
  self.objects=[];self.rects=[];self.spikes=[];self.controls=[];self.paths=[]
  self.orbs=[];self.memories=[];self.gates=[];self.moves=[];self.groups=100;self.sections=[]
 def group(self):self.groups+=1;return self.groups
 def obj(self,oid,x,y,**props):
  o={'1':oid,'2':round(x,5),'3':round(y,5),'64':1,'67':1,'96':1,'20':0}
  o.update(props);o={str(k):str(v) for k,v in o.items()};self.objects.append(o);return o
 def rect(self,a,b,lo,hi,kind='solid',group=None,visible=True):
  if b-a<.3 or hi-lo<.3:return
  assert lo>=-60 and hi<=330,(lo,hi,kind)
  rec=dict(a=a,b=b,lo=lo,hi=hi,kind=kind,group=group)
  self.rects.append(rec)
  # Small native blocks avoid large-scale collision and spider teleport quirks.
  n=math.ceil((b-a)/75);m=math.ceil((hi-lo)/75)
  for i in range(n):
   for j in range(m):
    props={'128':(b-a)/n/30,'129':(hi-lo)/m/30,'21':1,'22':2,'24':-1}
    if group:props['57']=group
    if not visible:props['135']=1
    self.obj(1,a+(i+.5)*(b-a)/n,lo+(j+.5)*(hi-lo)/m,**props)
  # Joined dark faces and restrained edge strips give structures a silhouette.
  if visible and kind not in ('foundation','roof'):
   self.artbox(a,b,lo,hi,5,group=group,z=-3)
   self.artbox(a,b,hi-1.0,hi,2,group=group,z=1)
   self.artbox(a,b,lo,lo+1.0,2,group=group,z=1)
 def artbox(self,a,b,lo,hi,ch=2,group=None,z=-3):
  if b<=a or hi<=lo:return
  p={'128':(b-a)/30,'129':(hi-lo)/30,'21':ch,'22':ch,'121':1,'134':1,'24':z,'25':-2,'20':10}
  if group:p['57']=group
  return self.obj(211,(a+b)/2,(lo+hi)/2,**p)
 def spike(self,x,base,up=True,scale=.7,group=None):
  y=base+(15*scale if up else -15*scale)
  assert 0<=y-15*scale and y+15*scale<=300,(x,y,scale)
  p={'32':scale,'6':0 if up else 180,'21':3,'22':3,'24':1}
  if group:p['57']=group
  self.obj(8,x,y,**p);self.spikes.append(dict(x=x,y=y,r=15*scale,group=group))
 def portal(self,oid,t,y=55):
  # Standard-sized portal remains inside the fixed 300-unit playfield.
  self.obj(oid,xt(t),max(55,min(245,y)),**{'13':1,'21':1004,'22':1004,'129':1,'128':1})
 def event(self,t,kind,mode,**kw):
  e=dict(time=float(t),x=xt(t),kind=kind,mode=mode);e.update(kw);self.controls.append(e);return e
 def orb(self,oid,t,y,**props):
  self.obj(oid,xt(t),y,**{'21':1004,'22':1004,**props});self.orbs.append(dict(id=oid,t=t,x=xt(t),y=y,**props))
 def label(self,text,x,y=265,scale=.22,ch=2,group=None):
  p={'31':base64.urlsafe_b64encode(text.encode()).decode(),'32':scale,'21':ch,'22':ch,'121':1,'134':1,'24':-3,'20':10}
  if group:p['57']=group
  self.obj(580,x,y,**p)
 def alpha(self,t,g,opacity,duration=0):self.obj(1007,xt(t),-430,**{'51':g,'35':opacity,'10':duration,'20':5})
 def toggle(self,t,g,active):self.obj(1049,xt(t),-460,**{'51':g,'56':int(active),'20':5})
 def move(self,t,g,dx,dy,duration):
  self.obj(901,xt(t),-490,**{'51':g,'28':dx,'29':dy,'10':duration,'30':13,'20':5})
  self.moves.append(dict(t=t,group=g,dx=dx,dy=dy,duration=duration))
 def remember(self,s,t,y,correct=True,symbol='I',gate_t=None):
  g=self.group();gt=gate_t or t+.46;gx=xt(gt)
  self.rect(gx-5,gx+5,0,300,'memory lock' if correct else 'wrong-input lock',g)
  if not correct:self.toggle(max(0,s['t0']-.2),g,False)
  self.orb(1594,t,y,**{'51':g,'56':0 if correct else 1,'32':.65,'21':4,'22':4})
  self.label(symbol,xt(t),min(282,y+27),.18,4)
  if correct:self.event(t,'memory',s['mode'],target=g,symbol=symbol,activate=False)
  self.memories.append(dict(section=s['name'],t=t,y=y,gate_t=gt,group=g,correct=correct,symbol=symbol))
 def path(self,s,pts):
  # pts: time, y, gravity (-1 down), radius, mode; use dense native-unit samples.
  s['points']=pts;s['times']=[p[0] for p in pts]
  self.paths.extend([[t,xt(t),y,mode,r,g] for t,y,g,r,mode in pts])
 def envelope(self,s,a,b,pad=0):
  pts=s['points'];ts=s['times'];v=s['speed'];t0=s['t0']+(a-s['x0'])/v;t1=s['t0']+(b-s['x0'])/v
  near=pts[max(0,bisect.bisect_left(ts,t0-18/v)-1):bisect.bisect_right(ts,t1+18/v)+1]
  near=[p for p in near if a-p[3]-.1<=xt(p[0])<=b+p[3]+.1]
  if not near:return 0,300
  return min(p[1]-p[3] for p in near)-pad,max(p[1]+p[3] for p in near)+pad
 def fit_gate(self,s,t,width,pad,kind='precision',floating=False):
  a=xt(t)-width/2;b=a+width;lo,hi=self.envelope(s,a,b,pad)
  if lo>8:self.rect(a,b,max(3,lo-22) if floating else 0,lo,kind+' lower')
  if hi<292:self.rect(a,b,hi,min(297,hi+22) if floating else 300,kind+' upper')
  self.gates.append(dict(section=s['name'],t=t,a=a,b=b,lo=lo,hi=hi,pad=pad,kind=kind))
 def safe_spike(self,s,t,base,up=True,scale=.7):
  r=15*scale;y=base+(r if up else -r);lo,hi=self.envelope(s,xt(t)-r,xt(t)+r,1.5)
  if (y+r<lo or y-r>hi) and 0<=y-r and y+r<=300:self.spike(xt(t),base,up,scale);return True
  return False

# Every ground score is an explicit sequence: relative beat, next ledge height,
# hold seconds (robot), orb ID and orb delay. No periodic cadence is extended.
GROUND={
 'CIPHER':[
  (2,30,0,0,0),(3.75,0,0,141,.17),(5.5,45,0,0,0),(7,15,0,0,0),
  (8.75,60,0,36,.15),(10.75,45,0,0,0),(12.25,0,0,0,0),(13.75,45,0,141,.18),
  (15.75,75,0,0,0),(17.25,30,0,0,0),(18.75,0,0,36,.16),(20.75,45,0,0,0),
  (22.25,15,0,0,0),(23.75,60,0,141,.16),(25.75,90,0,0,0),(27.25,30,0,0,0),(29,0,0,0,0)],
 'CUTWIRE':[
  (1.75,45,.19,0,0),(3.25,15,.095,0,0),(4.5,75,.245,0,0),(6.25,105,.17,0,0),
  (7.75,45,.08,0,0),(8.75,15,.12,0,0),(10.25,90,.29,0,0),(12.25,60,.10,0,0),
  (13.5,0,.075,0,0),(14.75,45,.205,0,0),(16.25,75,.16,0,0),(17.75,45,.085,0,0),
  (19,60,.21,0,0),(20.5,0,.095,0,0),(21.75,0,.145,0,0)],
 'NEEDLEWORK':[
  (1.5,30,.14,0,0),(2.75,45,.11,0,0),(4,0,.065,0,0),(5,60,.23,0,0),
  (6.75,90,.155,0,0),(8.25,30,.065,0,0),(9.25,0,.09,0,0),(10.5,30,.15,0,0),
  (11.75,60,.165,0,0),(13.25,105,.21,0,0),(15,45,.055,0,0),(16,15,.075,0,0),
  (17.25,75,.23,0,0),(19,30,.07,0,0),(20.25,0,.095,0,0),(21.5,0,.115,0,0)],
 'LAST WORD':[
  (1.75,45,0,141,.16),(3.75,75,0,0,0),(5.25,30,0,0,0),(6.75,60,0,36,.17),
  (9,90,0,0,0),(10.5,45,0,0,0),(12,15,0,141,.16),(14,60,0,0,0),
  (15.5,90,0,0,0),(17,30,0,36,.15),(19.25,0,0,0,0),(20.75,45,0,0,0),
  (22.25,75,0,141,.16),(24.25,30,0,0,0),(25.75,60,0,0,0),(27.25,15,0,0,0),(29,0,0,0,0)]}

def ground(L,s):
 t0,t1,v=s['t0'],s['t1'],s['speed'];mode=s['mode'];jump=[637.2,670.8][s['speed_index']]
 score=GROUND[s['name']];surface=0;pts=[];actions=[];last_t=t0;last_x=s['x0']
 def append_between(a,b,y):
  for t in np.arange(a,b,1/240):pts.append([float(t),y,-1,15,mode])
 for j,(beat,target,hold,oid,delay) in enumerate(score):
  t=snap(t0+beat*B);next_t=snap(t0+score[j+1][0]*B) if j+1<len(score) else t1-.38
  append_between(last_t,t,surface+15)
  L.event(t,'hold' if mode=='robot' else 'jump',mode,hold=hold)
  ot=snap(t+delay,.028) if oid else None
  y=surface+15;vy=jump*(.5 if mode=='robot' else 1);tt=t;arc=[];orb_done=False
  while tt<t+1.15:
   dt=min(1/240,t+1.15-tt)
   if oid and not orb_done and tt<=ot<tt+dt+1e-9:dt=ot-tt
   if dt<1e-8:
    L.orb(oid,ot,y);L.event(ot,'orb',mode,orb_id=oid);vy=jump*(.72 if oid==141 else 1);orb_done=True;continue
   acc=0 if mode=='robot' and tt<t+hold else -G
   if mode=='robot' and tt<t+hold:vy=jump*.5;dt=min(dt,t+hold-tt)
   y+=vy*dt+.5*acc*dt*dt;vy+=acc*dt;tt+=dt
   arc.append([tt,y,-1,15,mode])
   if vy<0 and y<=target+15 and tt>t+.15:break
  landing=tt
  arc[-1][1]=target+15
  if landing>next_t-.015:raise ValueError(('insufficient landing time',s['name'],j,landing,next_t))
  first_clear=next((a[0] for a in arc if a[1]>target+31),landing)
  left=max(xt(landing)-v*.075,xt(first_clear)+16)
  right=xt(next_t)+v*.07
  if target:
   # Actual platforms float. False plates share their artwork but no collider.
   L.rect(left,right,max(0,target-18),target,'suspended landing')
   if s['name']=='CUTWIRE':L.artbox(left-45,left-7,target-18,target,2)
   elif s['name']=='NEEDLEWORK':L.artbox(right+14,right+60,target-18,target,2)
  actions.append(dict(t=t,landing=landing,target=target,source=surface,hold=hold,orb=oid,orb_time=ot,left=left,right=right))
  pts.extend(arc);surface=target;last_t=landing
 append_between(last_t,t1,surface+15)
 L.path(s,pts);s['actions']=actions
 for j,e in enumerate(actions):
  # Narrow caps test both tap timing and robot release length; ground spikes
  # are placed only where their entire visual boxes clear the nominal path.
  tt=e['t']+(e['hold']+.06 if mode=='robot' else (.29 if e['orb'] else .21))
  L.fit_gate(s,tt,10 if mode=='cube' else 12,5.5 if mode=='cube' else 6,'arc slot',True)
  L.safe_spike(s,e['t']+.22,e['source'],True,.7)
  if e['target']>0:
   L.safe_spike(s,(e['t']+e['landing'])/2,0,True,.75)
  if s['name'] in ('CIPHER','LAST WORD') and j in ([1,4,8,12] if s['name']=='CIPHER' else [0,5,9,13]):
   mt=e['t']+(.38 if e['orb'] else .21)
   p=min(pts,key=lambda p:abs(p[0]-mt));symbol={1:'II',4:'I',8:'IV',12:'III',0:'II',5:'IV',9:'I',13:'III'}[j]
   L.remember(s,mt,p[1],True,symbol,gate_t=min(e['landing']+.05,mt+.32))
  if s['name']=='CIPHER' and j in (3,6,10,14):
   mt=e['t']+(.40 if e['orb'] else .20);p=min(pts,key=lambda p:abs(p[0]-mt));L.remember(s,mt,p[1],False,{3:'III',6:'IV',10:'II',14:'I'}[j])
  if s['name']=='LAST WORD' and j in (2,7,11,15):
   mt=e['t']+.20;p=min(pts,key=lambda p:abs(p[0]-mt));L.remember(s,mt,p[1],False,'V')
 # Prevent simply remaining below the suspended platform chain.
 for t in np.arange(t0+1,t1-.7,.13):L.safe_spike(s,float(t),0,True,.72)

def crosscode(L,s):
 # A single continuous, mixed-gravity orb score, not repeated floor jumps.
 t0,t1=s['t0'],s['t1'];roof=270;L.rect(s['x0'],s['x1'],roof,300,'crosscode ceiling')
 score=[(2,84,.17),(4.25,141,.17),(6.25,36,.16),(8.5,84,.18),(10.75,141,.17),(12.75,84,.16),
  (15,36,.16),(17.25,141,.15),(19.25,84,.18),(21.5,36,.16),(23.75,84,.17),(26,141,.17),(28.25,84,.16)]
 events=[]
 for b,oid,dt in score:
  t=snap(t0+b*B);events.extend([(t,'jump',0),(snap(t+dt,.025),'orb',oid)])
 events.sort();t=t0;y=15;vy=0;g=-1;grounded=True;ei=0;pts=[]
 while t<t1-1e-8:
  if ei<len(events) and events[ei][0]<=t+1e-7:
   et,kind,oid=events[ei];ei+=1
   if kind=='jump':
    assert grounded,('crosscode airborne',et,y);vy=-g*637.2;grounded=False
    L.event(et,'jump','cube',gravity=g)
   else:
    L.orb(oid,et,y,**{'6':180 if g>0 else 0});L.event(et,'orb','cube',orb_id=oid,gravity=g)
    if oid==84:g*=-1;vy=g*637.2*.4
    else:vy=-g*637.2*(.72 if oid==141 else 1)
    grounded=False
   continue
  to=min(t1,t+1/240,events[ei][0] if ei<len(events) else t1);dt=to-t
  if not grounded:
   y+=vy*dt+.5*g*G*dt*dt;vy+=g*G*dt
   if g<0 and y<=15:y=15;vy=0;grounded=True
   if g>0 and y>=roof-15:y=roof-15;vy=0;grounded=True
  t=to;pts.append([t,y,g,15,'cube'])
 assert g==-1,'must end down'
 L.path(s,pts)
 for j,(b,oid,dt) in enumerate(score):
  t=snap(t0+b*B);L.fit_gate(s,t+.27,10,6,'gravity keyhole',True)
  p=min(pts,key=lambda p:abs(p[0]-t));L.safe_spike(s,t+.23,0 if p[2]<0 else roof,p[2]<0,.7)
  if oid==84:L.fit_gate(s,t+.53,14,9,'transfer divider')
  if j in (1,4,7,10):
   mt=t+.37;p=min(pts,key=lambda p:abs(p[0]-mt));L.remember(s,mt,p[1],False,'X')

RAILS={
 'SWITCHYARD':([2,3.75,5.25,6.75,8.25,10,11.5,13.25,14.75,16.25,18,19.5,21],
  [240,45,210,0,270,60,225,30,195,0,255,45,210]),
 'FALSE FLOOR':([1.75,3.25,5,6.5,8.25,9.75,11.5,13.25,15,16.5,18,19.75,21.5,23.25,25,26.5,28.25],
  [195,30,255,75,225,15,180,0,240,60,270,30,210,0,255,45,225]),
 'BLIND ELEVATOR':([1.75,2.5,3.75,4.25,5.75,6.5,7.5,8.75,9.25,10.75,12,12.75,14.25,15,16.5,17.25,18.25,19.75,20.5,21.25],
  [210,45,270,0,180,60,240,30,195,0,255,75,225,15,270,45,180,0,240,30]),
 'RECALL':([1.5,2.25,3.5,4.5,5.25,6.75,7.25,8.5,9.75,10.5,12,12.75,13.25,14.75,15.5,16.75,17.75,18.5,20,20.5,21.75,23,23.75,25,26.5,27.25,28.5,29.25],
  [270,30,195,75,240,0,210,45,180,15,255,60,225,0,195,45,270,75,210,30,180,0,240,60,270,15,225,0])}
def rails(L,s):
 bs,targets=RAILS[s['name']];mode=s['mode'];r=13.75 if mode=='spider' else 15
 # Spider uses its documented smaller red box; solid contact uses 15-unit
 # support centre to match the native icon's standing offset conservatively.
 r=15
 events=[snap(s['t0']+b*B,.12) for b in bs]
 if mode=='spider':
  # Joint onset matching prevents two short offbeat flips snapping to one hit.
  # The minimum separation comes from the finite-width shelf/teleport setup.
  states=[(0,[])]
  for b in bs:
   intended=s['t0']+b*B
   candidates=sorted(set([intended]+[float(t) for t in AT if abs(t-intended)<=.12]))
   nxt=[]
   for c in candidates:
    eligible=[(cost,path) for cost,path in states if not path or c-path[-1]>=.22]
    if eligible:
     cost,path=min(eligible,key=lambda q:q[0]);cost+=float(min(abs(AT-c)))+.05*abs(c-intended)
     nxt.append((cost,path+[c]))
   states=nxt
  events=min(states,key=lambda q:q[0])[1]
 surfaces=[0]+targets;platforms=[]
 L.rect(s['x0'],xt(events[0]) + 26,-30,0,'starting rail')
 for j,(t,target) in enumerate(zip(events,targets)):
  nt=events[j+1] if j+1<len(events) else s['t1']-.45
  upper=(j%2==0);left=xt(t)-24 if mode=='spider' else xt(t)+26
  right=xt(nt)+29
  if upper:L.rect(left,right,target,target+18,'teleport shelf' if mode=='spider' else 'upper rail')
  else:L.rect(left,right,max(0,target-18),target,'island rail')
  platforms.append((left,right,target,upper))
  # False landing faces occupy genuinely different heights and are no-touch.
  if mode=='spider':
   fake=target-54 if upper else target+54
   L.artbox(left+4,right-4,fake,fake+10,2)
  elif s['name']=='FALSE FLOOR':L.artbox(left-80,left-28,target-12,target,2)
 t=s['t0'];y=15;vy=0;g=-1;grounded=True;ei=0;pts=[]
 reset=s['t1']-.90
 while t<s['t1']-1e-8:
  if ei<len(events) and events[ei]<=t+1e-7:
   et=events[ei];target=targets[ei];ei+=1
   assert grounded,('airborne rail flip',s['name'],ei,t,y)
   g*=-1;L.event(et,'flip',mode,gravity=g,target=target)
   if mode=='spider':y=target-15 if g>0 else target+15;vy=0;grounded=True
   else:vy=g*637.2*.3;grounded=False
   continue
  if t>=reset-1e-7:
   if g>0:L.portal(10,reset,y);g=-1;grounded=False
   reset=math.inf
  to=min(s['t1'],t+1/240,events[ei] if ei<len(events) else s['t1'],reset);dt=to-t;x=xt(to);old=y
  # A ledge can end, so standing does not imply permanent support.
  support=[p for p in platforms if p[0]<x+15 and p[1]>x-15 and abs((p[2]-15 if p[3] else p[2]+15)-y)<.01]
  if grounded and y>15 and not support:grounded=False
  if not grounded:
   acc=g*(2200 if mode=='ball' else G);y+=vy*dt+.5*acc*dt*dt;vy+=acc*dt
   for l,rr,h,up in platforms:
    if not(l<x+15 and rr>x-15):continue
    if g>0 and up and old+15<=h+.1 and y+15>=h:y=h-15;vy=0;grounded=True
    if g<0 and not up and old-15>=h-.1 and y-15<=h:y=h+15;vy=0;grounded=True
   if g<0 and y<=15:y=15;vy=0;grounded=True
  t=to;pts.append([t,y,g,r,mode])
 L.path(s,pts)
 for j,t in enumerate(events):
  old=surfaces[j];up=(j%2==0);delay=.065 if mode=='spider' else .25
  # Old rail ends in a spike. Tight flanking faces bound the teleport slot.
  L.safe_spike(s,t+delay,old,up,.6)
  if mode=='spider':
   L.fit_gate(s,t+.092,8,5,'teleport exit')
   L.fit_gate(s,t-.092,8,5,'teleport entry')
  else:L.fit_gate(s,t+.32,12,7,'ball transfer',True)
 # Add forbidden extra flips through live switches in otherwise quiet rail runs.
 if mode=='ball':
  for j in ([2,6,10] if s['name']=='SWITCHYARD' else [1,5,9,13]):
   mt=events[j]+.48;p=min(pts,key=lambda p:abs(p[0]-mt));L.remember(s,mt,p[1],False,'X')

FLIGHT={
 'BLINDFOLD':[(0,125),(3,245),(6,80),(10,190),(14,140),(17,255),(20,65),(23,180),(26,95),(29,200),(32,120)],
 'FAULTLINE':[(0,165),(4,230),(7,115),(10,70),(14,200),(17,250),(20,140),(23,80),(27,205),(32,110)],
 'OFFBEAT':[(0,70),(3,150),(6,230),(10,110),(14,205),(18,95),(22,180),(26,250),(30,80),(32,30)],
 'COUNTERFEIT':[(0,120),(4,230),(8,180),(12,70),(16,90),(20,245),(24,175),(28,85),(32,25)],
 'PARALLAX':[(0,110),(4,110),(7,235),(11,235),(14,95),(18,95),(22,190),(25,245),(28,110),(32,20)],
 'UNDERTOW':[(0,85),(5,70),(8,70),(12,150),(16,230),(19,230),(23,135),(27,80),(30,165),(32,15)]}
def flight(L,s):
 mode=s['mode'];t0,t1,v=s['t0'],s['t1'],s['speed'];tail=t1-.8
 keys=FLIGHT[s['name']];kt=[t0+k[0]*B for k in keys];ky=[k[1] for k in keys]
 def target(t):return float(np.interp(t,kt,ky))
 inv=(t0+10*B,t0+22*B) if s['name'] in ('PARALLAX','COUNTERFEIT') else None
 def gravity(t):return 1 if inv and inv[0]<=t<inv[1] else -1
 pts=[];t=t0;y=15.;vy=0;held=False;events=[]
 if mode=='wave':
  # Authored contour is followed using measured audio attacks. The first room
  # has long traverses and uneven bursts; the second alternates normal/mini.
  direction=1;mini=False;flip_count=0
  changes=[(t0+8*B,True),(t0+16*B,False),(t0+23*B,True),(t0+29*B,False)] if s['name']=='FAULTLINE' else []
  ci=0;L.event(t,'turn',mode,down=True)
  while t<tail-1e-7:
   speed_y=v*(2 if mini else 1);horizon=(.36 if mini else .72)
   candidates=AT[(AT>t+.115)&(AT<min(t+horizon,tail))]
   desired=target(t+.3)+(60 if direction>0 else -60)
   good=[]
   for tt in candidates:
    yy=y+direction*speed_y*(tt-t)
    if 42<yy<260:good.append((abs(yy-desired),float(tt)))
   nt=min(good)[1] if good else t+max(.06,min(horizon,abs((245 if direction>0 else 50)-y)/speed_y))
   boundary=t+((272 if direction>0 else 28)-y)/(direction*speed_y)
   nt=min(nt,boundary,tail);is_size=False
   if ci<len(changes) and changes[ci][0]<nt:nt=changes[ci][0];is_size=True
   if nt<=t+1e-7:raise ValueError(('wave stalled',t,y,direction))
   for tt in np.arange(t,nt,1/240):pts.append([float(tt),y+direction*speed_y*(tt-t),-1,3 if mini else 5,mode])
   y+=direction*speed_y*(nt-t);t=nt
   if is_size:
    mini=changes[ci][1];ci+=1;L.portal(99 if mini else 101,t,y)
   else:
    direction*=-1;L.event(t,'turn',mode,down=direction>0);flip_count+=1
  L.portal(101,tail,y);L.portal(12,tail+.06,y)
  # Conservative transition model: clear area and cube fall, no tail hazards.
  for tt in np.arange(tail,t1,1/240):pts.append([float(tt),max(15,y-.5*G*(tt-tail)**2),-1,15,'cube'])
 else:
  next_control=t0+.04;next_hop=t0+.10;prev_g=-1
  while t<tail:
   g=gravity(t);dt=min(1/240,tail-t)
   if g!=prev_g:
    L.portal(11 if g>0 else 10,t,y);prev_g=g
   if mode=='ship':
    if t>=next_control:
     up=target(t+.18)-y-vy*.19>0;newheld=up if g<0 else not up
     if newheld!=held or t< t0+.1:L.event(t,'thrust',mode,down=newheld)
     held=newheld
     choices=AT[(AT>t+.065)&(AT<t+.17)]
     next_control=float(choices[0]) if len(choices) else t+.115
    acc=(-g if held else g)*1000
    # Keep design model comfortably inside bounds; corrective controls become
    # part of the recorded score, never unrecorded position clamping in midair.
    predicted=y+vy*abs(vy)/2000
    if predicted<32 and acc<0:
     held=g<0;L.event(t,'thrust',mode,down=held);acc=1000;next_control=t+.11
    if predicted>268 and acc>0:
     held=g>0;L.event(t,'thrust',mode,down=held);acc=-1000;next_control=t+.11
    y+=vy*dt+.5*acc*dt*dt;vy=max(-300,min(300,vy+acc*dt))
   else:
    norm=y if g<0 else 300-y
    if t>=next_hop:
     if norm>205:next_hop=t+.05
     else:
      vy=-g*420;L.event(t,'hop',mode,gravity=g)
      choices=AT[(AT>t+.30)&(AT<t+.73)]
      goal=target(t+.5);candidates=[]
      for tt in choices:
       yy=y+vy*(tt-t)+.5*g*1244.16*(tt-t)**2
       if 40<yy<260:candidates.append((abs(yy-goal),float(tt)))
      next_hop=min(candidates)[1] if candidates else t+.53
    y+=vy*dt+.5*g*1244.16*dt*dt;vy+=g*1244.16*dt
   if y<15:y=15;vy=0
   if y>285:y=285;vy=0
   t+=dt;pts.append([t,y,g,15,mode])
  L.portal(10,tail,y);L.portal(12,tail+.06,y)
  for tt in np.arange(tail,t1,1/240):pts.append([float(tt),max(15,min(285,y+min(0,vy)*(tt-tail)-.5*G*(tt-tail)**2)),-1,15,'cube'])
 L.path(s,pts)
 if mode=='wave':
  # Two geometrically different rooms: continuous milled channel, then
  # disconnected paired teeth and long longitudinal barriers around mini lanes.
  step=12 if s['name']=='BLINDFOLD' else 22
  for a in np.arange(s['x0']+140,xt(tail-.12),step):
   b=min(a+step,xt(tail-.12));lo,hi=L.envelope(s,a,b,8 if step==12 else 9)
   if step==12:
    if lo>4:L.rect(a,b,0,lo,'milled wave lower')
    if hi<296:L.rect(a,b,hi,300,'milled wave upper')
   else:
    if lo>20:L.rect(a,b,max(0,lo-42),lo,'fractured lower blade')
    if hi<280:L.rect(a,b,hi,min(300,hi+42),'fractured upper blade')
  # Fake connectors obscure remembered bends but have no touch/collision.
  for b in ([6.5,13.5,20.5,27] if step==12 else [5,11.75,19.5,25.5]):
   tt=t0+b*B;p=min(pts,key=lambda p:abs(p[0]-tt));g=L.group()
   L.artbox(xt(tt)-15,xt(tt)+19,p[1]-34,p[1]+34,1,g,z=1)
   L.alpha(tt-.58,g,.13,.12);L.alpha(tt-.10,g,.92,.1)
 elif mode=='ship':
  spans=[(2.7,4.5,False),(6.7,6.9,True),(8.5,11.2,False),(13.5,13.7,True),(16,18.4,False),(20,20.2,True),(23,25.4,False),(27.6,27.8,True),(29.4,29.6,True)] if s['name']=='PARALLAX' else [(2.8,7,False),(9,9.2,True),(10.8,11.0,True),(13,15.5,False),(18,20,False),(22,22.2,True),(24,26.5,False),(28.5,28.7,True)]
  for aa,bb,narrow in spans:
   ta=t0+aa*B;tb=t0+bb*B;L.fit_gate(s,(ta+tb)/2,(tb-ta)*v,11 if narrow else 14,'offset slit' if narrow else 'drift gallery',narrow)
  for tt in np.arange(t0+1.1,tail-.4,.28):
   L.safe_spike(s,float(tt),0,True,.8);L.safe_spike(s,float(tt),300,False,.8)
 else:
  hops=[e for e in L.controls if e['mode']=='ufo' and t0<e['time']<tail-.4]
  for j,e in enumerate(hops):
   L.fit_gate(s,e['time']+.19,13,5,'ufo tap window',s['name']=='COUNTERFEIT')
   if j in (3,8,14,19):
    tt=e['time']+.26;p=min(pts,key=lambda p:abs(p[0]-tt));L.remember(s,tt,p[1],False,'X')
   if j in ((1,11,17) if s['name']=='OFFBEAT' else (5,10,16)):
    tt=e['time']+.28
    if j+1<len(hops) and hops[j+1]['time']-tt>.21:
     p=min(pts,key=lambda p:abs(p[0]-tt));L.remember(s,tt,p[1],True,'I' if s['name']=='OFFBEAT' else 'II')
  spans=[(3.5,105,True),(7,185,False),(11.5,80,True),(16,145,True),(21.5,215,False),(27,100,True)] if s['name']=='OFFBEAT' else [(4,190,True),(8.5,75,False),(13,130,True),(17.5,230,True),(22.5,90,False),(27.5,160,True)]
  for b,w,floating in spans:
   tt=t0+b*B;L.fit_gate(s,tt,w,10,'suspended ufo chamber',floating)
   lo,hi=L.envelope(s,xt(tt)-w/2,xt(tt)+w/2,10)
   # Offset false doorway is an intentional route decoy, with no touch.
   fake=max(40,min(255,(lo+hi)/2+(80 if b<16 else -80)))
   L.artbox(xt(tt)-24,xt(tt)+24,fake-2,fake+2,2)
   L.artbox(xt(tt)-24,xt(tt)-21,fake-22,fake+22,2)
   L.artbox(xt(tt)+21,xt(tt)+24,fake-22,fake+22,2)
  for tt in np.arange(t0+1.1,tail-.4,.19):
   L.safe_spike(s,float(tt),0,True,.72);L.safe_spike(s,float(tt),300,False,.72)

def decorate(L,s):
 # Per-room architectural motifs move slowly behind the colliders. No circles,
 # random particles or foreground death-obscuring masks are introduced.
 a,b=s['x0'],s['x1'];idx=s['index'];g=L.group()
 motif=['brackets','cables','switches','ribs','windows','diagonals','lifts','crosses','faults','needles','tiles','shelves','steps','slots','tokens'][idx]
 for n,x in enumerate(np.arange(a+90,b-30,110 if motif=='ribs' else 180)):
  if motif in ('brackets','windows','tiles','slots'):
   L.artbox(x-28,x+28,82,85,6,g);L.artbox(x-28,x-25,85,213,6,g);L.artbox(x+25,x+28,85,213,6,g);L.artbox(x-28,x+28,213,216,6,g)
  elif motif in ('cables','ribs','needles','lifts'):
   L.artbox(x-2,x+2,18,282,6,g);L.artbox(x-18,x+18,95,98,6,g);L.artbox(x-12,x+12,205,208,6,g)
  elif motif in ('diagonals','faults','crosses'):
   o=L.artbox(x-2,x+2,80,220,6,g);o['6']='35' if motif!='crosses' else '45'
   if motif=='crosses':o=L.artbox(x-2,x+2,80,220,6,g);o['6']='-45'
  else:
   L.artbox(x-42,x+42,62,65,6,g);L.artbox(x-23,x+23,148,151,6,g);L.artbox(x-32,x+32,234,237,6,g)
 L.move(s['t0'],g,0,6,2*B);L.move(s['t0']+2*B,g,0,-12,4*B);L.move(s['t0']+6*B,g,0,6,2*B)
 L.move(s['t0']+12*B,g,-18,0,5*B);L.move(s['t0']+20*B,g,18,0,5*B)
 L.label(s['name'],a+170,284,.18,4)
 # The code is shown ahead of the test, then fades. It has a real gate effect.
 if s['name']=='CIPHER':
  cg=L.group();L.label('II  I  IV  III',a+180,240,.22,4,cg);L.alpha(0,cg,1);L.alpha(bt(3),cg,0,.25)
 if s['name']=='LAST WORD':
  # Four tokens cross in two authored swaps. Their identifying glyphs move
  # with them, and the remembered order is asked by the later switch locks.
  L.label('FIRST ORDER',a+223,192,.14,4)
  order=['II','IV','I','III'];gs=[]
  for j,sym in enumerate(order):
   gg=L.group();gs.append(gg);cx=a+140+j*55
   L.artbox(cx-16,cx+16,210,242,1,gg);L.label(sym,cx,225,.18,4,gg)
  for gg,dx in zip(gs,[55,-55,55,-55]):L.move(s['t0']+.25,gg,dx,0,.42)
  for gg,dx in zip(gs,[110,110,-110,-110]):L.move(s['t0']+.75,gg,dx,0,.55)
  for gg in gs:L.alpha(s['t0']+1.5,gg,0,.2)
 # Pulses follow actual measured attacks; use a dim channel to avoid whiteout.
 for o in AUDIO['onsets']:
  if s['t0']<=o['time']<s['t1'] and o['strength']>.20:
   L.obj(1006,xt(o['time']),-520,**{'51':2,'52':0,'45':.015,'46':.025,'47':.16,'7':71,'8':66,'9':47,'20':5})

def build():
 L=Level()
 for orig in SECTIONS:
  s=dict(orig);a,b=s['x0'],s['x1'];start=len(L.objects)
  L.rect(a,b,-30,0,'foundation');L.rect(a,b,300,330,'roof')
  if s['index']:L.portal({'cube':12,'robot':745,'ball':47,'wave':660,'ufo':111,'ship':13,'spider':1331}[s['mode']],s['t0']+.09)
  if s['index']==0 or s['speed_index']!=SECTIONS[s['index']-1]['speed_index']:L.portal(200 if not s['speed_index'] else 201,s['t0'])
  if s['name'] in GROUND:ground(L,s)
  elif s['name']=='CROSSCODE':crosscode(L,s)
  elif s['mode'] in ('ball','spider'):rails(L,s)
  else:flight(L,s)
  decorate(L,s);s['object_count']=len(L.objects)-start;L.sections.append(s)
 # Camera stays fixed so no hazard can be placed above a changing mode roof.
 L.obj(2925,0,-420,**{'111':1,'112':1,'113':10,'114':.5,'370':1,'20':5})
 L.obj(1764,0,150,**{'57':900,'121':1,'134':1,'135':1,'20':5})
 L.obj(1913,0,-420,**{'371':.9,'10':0,'20':5})
 L.obj(1914,1,-420,**{'71':900,'101':2,'155':1,'10':0,'20':5})
 L.obj(3600,xt(END),150,**{'20':5})
 return L

def export(L):
 f=read_gmd(ROOT/'work/handoff/OBSIDIAN-CHOIR.gmd');H=parse_header(decompress(f['k4'][1]).split(';')[0])
 H.update({'kA2':'0','kA4':'1','kA3':'0','kA8':'0','kA10':'0','kA11':'0','kA32':'1','kA22':'0'})
 H['kA14']=''.join(f'{bt(i):.5f}~{1 if i%4==0 else .6}~' for i in range(449))
 colors={1:(25,25,21),2:(49,47,35),3:(59,56,39),4:(127,117,77),5:(10,11,10),6:(19,20,17),60:(0,0,0),1000:(3,4,3),1001:(3,4,3),1002:(22,23,18),1004:(255,255,255)}
 channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
 for ch,rgb in colors.items():channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':'0','6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
 H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
 ser=lambda o:','.join(f'{k},{v}' for k,v in o.items())
 raw=';'.join([ser(H)]+[ser(o) for o in L.objects])+';'
 desc='Song 1573528. Dark memory layout; seven modes, mostly native 0.5x. Fifteen different rooms. Insane/Extreme target; requires native verification.'
 f.update({'k2':('s','v8'),'k3':('s',base64.urlsafe_b64encode(desc.encode()).decode()),'k4':('s',compress(raw)),'k48':('i',str(len(L.objects))),'k45':('i','1573528'),'k14':('f',False),'k23':('i','4'),'k72':('f',False)})
 write_gmd(ROOT/'outputs/v8-1573528-memory.gmd',f);(ROOT/'work/v8-memory.level').write_text(raw)
 plan=dict(sections=L.sections,controls=sorted(L.controls,key=lambda e:e['time']),paths=L.paths,rectangles=L.rects,spikes=L.spikes,orbs=L.orbs,memories=L.memories,gates=L.gates,moves=L.moves,
  speed_schedule=[[s['t0'],s['speed']] for s in L.sections],end_time=END,end_x=xt(END),bpm=131,song=1573528,phase=PHASE,objects=len(L.objects),slow_percent=100*sum(s['t1']-s['t0'] for s in L.sections if not s['speed_index'])/END,
  validation_limit='Approximate design models. Native physics, portal contact offsets and completion remain unverified.')
 (ROOT/'work/memory-plan.json').write_text(json.dumps(plan,separators=(',',':')))
 print(json.dumps({k:plan[k] for k in ['objects','end_time','slow_percent']}));print('inputs',len(L.controls),'memory decisions',len(L.memories),'gates',len(L.gates))
if __name__=='__main__':export(build())
