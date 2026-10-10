"""Distinct flight phrases and randomized wall decisions for v8."""
from pathlib import Path
import sys, json, math, bisect, base64, inspect
import numpy as np
import memory_layout as M
ROOT=M.ROOT
B=M.B

# Keep the accepted opening score. The back half changes its mode order and
# receives new scores; it is not a second pass through the opening rooms.
M.SCORE=M.SCORE[:9]+[
 (264,296,'spider',0,'RECALL','teleport packets / missing rungs'),
 (296,328,'ship',0,'UNDERTOW','inverted lift / separated knife gates'),
 (328,352,'robot',0,'NEEDLEWORK','orb catches / clipped holds'),
 (352,384,'ball',0,'FALSE FLOOR','unequal rail transfers / reaction locks'),
 (384,416,'ufo',0,'COUNTERFEIT','inverted chambers / delayed taps'),
 (416,448,'cube',0,'LAST WORD','ceiling recall / mixed gravity orb transfers')]
M.SECTIONS=[];xx=0
for i,(b0,b1,mode,sp,name,rule) in enumerate(M.SCORE):
 t0=0 if b0==0 else M.PHASE+b0*B;t1=M.PHASE+b1*B;v=[251.16,311.58][sp]
 M.SECTIONS.append(dict(index=i,beat0=b0,beat1=b1,t0=t0,t1=t1,x0=xx,x1=xx+(t1-t0)*v,mode=mode,speed=v,speed_index=sp,name=name,rule=rule));xx=M.SECTIONS[-1]['x1']
M.END=M.SECTIONS[-1]['t1']
M.GROUND['NEEDLEWORK']=[
 (1.5,60,.23,0,0),(3.25,15,.065,141,.18),(5.25,105,.32,0,0),
 (7,45,.075,0,0),(8.75,75,.15,36,.23),(11,0,.055,0,0),
 (12.25,45,.22,0,0),(14.25,90,.13,141,.21),(16.25,30,.065,0,0),
 (17.75,105,.28,0,0),(19.5,45,.075,0,0),(21,0,.10,0,0),(22,0,.075,0,0)]
M.RAILS['FALSE FLOOR']=(
 [1.75,3.5,5.75,7.25,9.75,11.5,14,15.5,17.75,19.25,21.75,23.5,25.75,27.5,29.5],
 [180,75,270,15,210,90,255,45,165,0,240,60,195,30,270])
M.RAILS['RECALL']=(
 [1.5,2.25,2.875,4.5,5.25,6,7.75,8.375,9.25,11,11.75,12.375,14.25,15,15.625,17.5,18.125,19,20.75,21.375,22.25,24,24.625,25.5,27.25,28,28.625,29.375],
 [195,60,255,15,180,45,270,90,210,0,240,30,165,75,225,0,270,45,195,90,255,15,180,60,240,30,210,0])
M.FLIGHT['PARALLAX']=[(0,35),(3,170),(8,170),(12,65),(16,55),(21,235),(25,235),(29,135),(32,45)]
M.FLIGHT['UNDERTOW']=[(0,30),(4,215),(7,140),(11,140),(15,240),(19,65),(24,65),(28,190),(32,35)]
M.FLIGHT['COUNTERFEIT']=[(0,45),(3,225),(7,95),(12,250),(16,160),(19,65),(23,220),(28,100),(32,35)]

# Use the existing ground solver for the finale's gravity transfers, with its
# own score and lower ceiling. This replaces the former CIPHER-like islands.
src=inspect.getsource(M.crosscode)
src=src.replace('roof=270','roof=240')
start=src.index(' score=[');end=src.index('\n events=[]',start)
src=src[:start]+''' score=[(1.75,84,.16),(3.75,36,.18),(6,84,.17),(8.25,141,.15),
   (10.5,84,.18),(12.75,141,.16),(14.75,36,.19),(17,84,.16),
   (19.25,36,.15),(21.5,84,.18),(23.75,141,.17),(26,84,.16),(28.25,36,.17)]'''+src[end:]
ns=dict(M.__dict__);exec(src,ns);finale=ns['crosscode']

class BranchLevel(M.Level):
 def __init__(self):
  super().__init__();self.random_locks=[];self.phrases=[]
 def panel(self,a,b,lo,hi,group=None,kind='panel'):
  # Static art is rebuilt after collision geometry is complete. Conditional
  # walls keep their group-aware skin.
  if group:
   self.artbox(a,b,lo,hi,7,group,z=5)
   for y in (lo+3,hi-4):self.artbox(a,b,y,y+1,4,group,z=5)
 def timing_door(self,s,t,width,pad,kind,decoy=False,side=1):
  super().timing_door(s,t,width,pad,kind,False,side)
 def remember(self,s,t,y,correct=True,symbol='I',gate_t=None):
  # Two mutually exclusive copies of the same native toggle orb implement
  # one decision: when the wall exists, the active orb removes it; otherwise
  # the active orb creates it. Equal weighted branches roll before approach.
  wall=self.group();present=self.group();absent=self.group()
  branch_yes=self.group();branch_no=self.group()
  gt=gate_t or t+.46;gx=M.xt(gt)
  self.rect(gx-5,gx+5,0,300,'random reaction wall',wall)
  init=max(s['t0']+.002,t-.95);roll=init+.008
  for grp in (wall,present,absent):self.toggle(init,grp,False)
  self.obj(2068,M.xt(roll),-550,**{'152':f'{branch_yes}.1.{branch_no}.1','20':5})
  def spawned(group,target,on):
   self.obj(1049,M.xt(roll),-580,**{'57':group,'51':target,'56':int(on),'62':1,'87':1,'20':5})
  spawned(branch_yes,wall,True);spawned(branch_yes,present,True)
  spawned(branch_no,absent,True)
  for visible,on in ((present,False),(absent,True)):
   self.orb(1594,t,y,**{'51':wall,'56':int(on),'57':visible,'32':.65,
            '445':1,'99':0,'21':1004,'22':1004,'24':7})
  # The recorded reference takes the wall-present branch for collision checks.
  self.event(t,'memory',s['mode'],target=wall,activate=False,randomized=True)
  self.memories.append(dict(section=s['name'],t=t,y=y,gate_t=gt,group=wall,correct=True,symbol='?',randomized=True))
  self.random_locks.append(dict(section=s['name'],t=t,y=y,gate_t=gt,wall=wall,present=present,absent=absent,
      branch_yes=branch_yes,branch_no=branch_no,init=init,roll=roll,probability=.5,claim_touch=445))

HEIGHTS={
 'BLINDFOLD':[230,184,253,146,211,43,115,63,260,208,248,120,180,46,241,192,254,71,130,85,226,173,257,39,106,68,196,142,248,205,266,60,152,100,230,44,95,55,256,183,238,140,209,49,126,77,247,191,259,103,174,40,225,168,249,62,139,91,265,206,244,48,117,69,217,145,252,92,182,45,246,187,258,73,142,99,234,161,261,57],
 'FAULTLINE':[150,76,246,190,260,98,171,130,235,58,126,70,255,207,248,137,198,44,240,156,262,110,179,64,221,172,253,42,111,68,256,194,241,101,168,48,228,173,260,73,149,105,252,196,266,60,119,79,235,160,246,48,140,89,257,188,242,97,175,44,226,167,259,67,145,98,249,185,261,53,121,78,239,174,256,42,132,88,246,183,260,69,152,108,228,165,257,47,115,73,250,190,262,56,137,92,231,171,255,64]}

def wave_path(L,s):
 t0,t1=s['t0'],s['t1'];tail=t1-.8;t=t0;y=15.;v=s['speed'];g=-1;mini=False;direction=1;pts=[];idx=0
 sizes=[(t0+b*B,state) for b,state in ([(8,True),(12,False),(21,True),(25,False)] if s['name']=='FAULTLINE' else [(17,True),(20,False)])]
 gravs=[(t0+b*B,gg) for b,gg in ([(5,1),(14,-1),(23,1),(28,-1)] if s['name']=='FAULTLINE' else [(11,1),(23,-1)])]
 changes=sorted([(t,'size',state) for t,state in sizes]+[(t,'gravity',gg) for t,gg in gravs]);ci=0
 def held():return direction>0 if g<0 else direction<0
 L.event(t,'turn','wave',down=held())
 while t<tail-1e-7:
  assert idx<len(HEIGHTS[s['name']]),('wave score too short',s['name'],t-t0)
  goal=HEIGHTS[s['name']][idx];sv=v*(2 if mini else 1)
  if (goal-y)*direction<sv*.06:
   goal=min(269,y+sv*.14) if direction>0 else max(31,y-sv*.14)
  ideal=t+(goal-y)/(direction*sv)
  candidates=[float(z) for z in M.AT if z>t+.065 and abs(z-ideal)<.052 and 29<y+direction*sv*(z-t)<271]
  nt=min(candidates,key=lambda z:abs(z-ideal)) if candidates else ideal
  nt=min(nt,tail);kind='turn'
  if ci<len(changes) and changes[ci][0]<=nt:nt=changes[ci][0];kind=changes[ci][1]
  assert nt>t+1e-8,(s['name'],idx,t,nt,y,goal)
  for tt in np.arange(t,nt,1/240):pts.append([float(tt),y+direction*sv*(tt-t),g,3 if mini else 5,'wave'])
  y+=direction*sv*(nt-t);t=nt
  if kind=='turn':
   idx+=1;direction*=-1
  else:
   state=changes[ci][2];ci+=1
   if kind=='size':mini=state;L.portal(101 if mini else 99,t,y)
   else:g=state;L.portal(11 if g>0 else 10,t,y)
  L.event(t,'turn','wave',down=held(),gravity=g)
 L.portal(10,tail,y);L.portal(99,tail,y);L.portal(12,tail+.06,y)
 for tt in np.arange(tail,t1,1/240):pts.append([float(tt),max(15,y-.5*M.G*(tt-tail)**2),-1,15,'cube'])
 L.path(s,pts)
 return tail

# Reuse the physical flight integrator, not its old corridor or blinking masks.
src=inspect.getsource(M.flight);src=src[:src.index(' if mode==\'wave\':\n  # Two geometrically')]
src=src.replace("inv=(t0+10*B,t0+22*B) if s['name']=='COUNTERFEIT' else None", "inv=(t0+10*B,t0+22*B) if s['name']=='COUNTERFEIT' else (t0+12*B,t0+23*B) if s['name']=='PARALLAX' else (t0+7*B,t0+24*B)")
ns=dict(M.__dict__);exec(src,ns);flight_integrator=ns['flight']

def flight(L,s):
 t0,t1,v=s['t0'],s['t1'],s['speed'];tail=t1-.8
 if s['mode']=='ufo':return M.flight(L,s)
 if s['mode']=='wave':wave_path(L,s)
 else:flight_integrator(L,s)
 # Distinct structural phrases replace the continuous oscillating tube.
 styles=({'BLINDFOLD':[(1,7,'duct'),(7,15,'knives'),(15,22,'blades'),(22,30,'split')],
          'FAULTLINE':[(1,6,'split'),(6,13,'blades'),(13,20,'knives'),(20,26,'duct'),(26,30,'blades')],
          'PARALLAX':[(1.7,8,'duct'),(8,14,'knives'),(14,21,'blades'),(21,30,'duct')],
          'UNDERTOW':[(1.7,7,'blades'),(7,13,'knives'),(13,19,'duct'),(19,25,'split'),(25,30,'blades')]}[s['name']])
 events=[e for e in L.controls if e['mode']==s['mode'] and t0+.3<e['time']<tail-.2 and e['kind'] in ('turn','thrust')]
 for ba,bb,style in styles:
  L.phrases.append(dict(section=s['name'],beat0=ba,beat1=bb,style=style))
  a=M.xt(t0+ba*B);end=M.xt(min(t0+bb*B,tail-.18))
  if style in ('duct','blades'):
   step=12 if s['mode']=='wave' else 24;pad=8.5 if s['mode']=='wave' else 18
   for x in np.arange(a,end,step):
    b=min(x+step,end);lo,hi=L.envelope(s,x,b,pad)
    lower=0 if style=='duct' else max(0,lo-33);upper=300 if style=='duct' else min(300,hi+33)
    if lo>3:L.rect(float(x),float(b),lower,lo,f'{style} lower')
    if hi<297:L.rect(float(x),float(b),hi,upper,f'{style} upper')
    if s['mode']=='ship':
     for xx in (x+6,x+18):
      if xx+6>b:continue
      tt=t0+(xx-s['x0'])/v
      if lo>3:L.safe_spike(s,tt,lo,True,.35,2)
      if hi<297:L.safe_spike(s,tt,hi,False,.35,2)
   if style=='blades':
    for b in np.arange(ba+.6,bb,2.35):L.timing_door(s,t0+float(b)*B,10,6.0,'blade checkpoint')
  else:
   local=[e for e in events if ba<=(e['time']-t0)/B<bb];last=-1e9
   for j,e in enumerate(local):
    tt=e['time']+.07
    if tt-last<.13:continue
    last=tt;w=8 if s['mode']=='wave' else 12
    L.timing_door(s,tt,w,4.5 if s['mode']=='wave' else 5.5,'flight knife')
    if style=='split':L.fit_gate(s,tt+.19,32,6,'offset false junction',True)
  # Each discontinuous phrase has an actual gate at entry and exit.
  if style!='duct':
   for beat in (ba+.12,bb-.12):L.timing_door(s,t0+beat*B,10,6,'phrase gate')

def build():
 L=BranchLevel()
 for orig in M.SECTIONS:
  s=dict(orig);a,b=s['x0'],s['x1']
  L.rect(a,b,-30,0,'foundation');L.rect(a,b,300,330,'roof')
  if s['index']:L.portal(99,s['t0']+.025);L.portal({'cube':12,'robot':745,'ball':47,'wave':660,'ufo':111,'ship':13,'spider':1331}[s['mode']],s['t0']+.09)
  if s['index']==0 or s['speed_index']!=M.SECTIONS[s['index']-1]['speed_index']:L.portal(200 if not s['speed_index'] else 201,s['t0'])
  if s['name']=='LAST WORD':finale(L,s)
  elif s['name'] in M.GROUND:M.ground(L,s)
  elif s['name']=='CROSSCODE':M.crosscode(L,s)
  elif s['mode'] in ('ball','spider'):M.rails(L,s)
  else:flight(L,s)
  cg=900+s['index'];L.obj(1764,a+70,150,**{'57':cg,'121':1,'134':1,'135':1,'20':5})
  L.obj(2925,a+46 if s['index'] else 0,-420,**{'111':1,'112':1,'113':10,'114':.5,'370':1,'20':5})
  L.obj(1913,a+46 if s['index'] else 0,-420,**{'371':.82,'10':0,'20':5})
  L.obj(1914,a+47 if s['index'] else 1,-420,**{'71':cg,'101':2,'155':1,'36':1,'10':0,'20':5})
  L.label(s['name'],a+170,284,.16,6)
  # Quiet moving hardware stays outside flight rooms and outside the route.
  if s['mode'] not in ('wave','ship'):
   for beat in (3,12,21):
    x=M.xt(s['t0']+beat*B);gg=L.group();L.artbox(x-18,x+18,310,315,6,gg,z=-3)
    L.move(s['t0']+(beat-1)*B,gg,25,0,B);L.move(s['t0']+beat*B,gg,-25,0,2*B)
  L.sections.append(s)
 L.obj(3600,M.xt(M.END),150,**{'20':5})
 return L

def export(L):
 from gmd import read_gmd,compress,write_gmd
 from gdparse import load,parse_header,parse_ks38
 rawhead,_=load(str(ROOT/'work/v8-clean.level'));H=parse_header(rawhead)
 colors={1:(12,14,12),2:(26,28,22),3:(31,34,26),4:(80,82,60),5:(3,5,4),6:(17,19,15),7:(65,69,49)}
 channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
 for ch,rgb in colors.items():
  channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':'0','6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
 H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
 ser=lambda o:','.join(f'{k},{v}' for k,v in o.items())
 raw=';'.join([ser(H)]+[ser(o) for o in L.objects])+';'
 f=read_gmd(ROOT/'outputs/v8-1573528-clean.gmd');f['k4']=('s',compress(raw));f['k48']=('i',str(len(L.objects)));f['k14']=('f',False)
 write_gmd(ROOT/'work/branching-base.gmd',f);(ROOT/'work/v8-branching-base.level').write_text(raw)
 P=dict(sections=L.sections,controls=sorted(L.controls,key=lambda e:e['time']),paths=L.paths,rectangles=L.rects,spikes=L.spikes,
  orbs=L.orbs,memories=L.memories,gates=L.gates,moves=L.moves,timing_features=L.timing_features,fakeouts=[],random_locks=L.random_locks,phrases=L.phrases,
  speed_schedule=[[s['t0'],s['speed']] for s in L.sections],end_time=M.END,end_x=M.xt(M.END),bpm=131,song=1573528,phase=M.PHASE,objects=len(L.objects),
  slow_percent=100*sum(s['t1']-s['t0'] for s in L.sections if not s['speed_index'])/M.END,
  validation_limit='Approximate route model. Native completion remains unverified.')
 (ROOT/'work/branching-plan.json').write_text(json.dumps(P,separators=(',',':')))
 print(json.dumps(dict(base_objects=len(L.objects),inputs=len(L.controls),random_locks=len(L.random_locks),phrases=len(L.phrases))))

if __name__=='__main__':export(build())
