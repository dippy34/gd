"""Decorate only the approved drop, preserving original gameplay data."""
from pathlib import Path
import sys, math, json, copy, wave, hashlib
from collections import defaultdict, Counter
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gdparse,gmd
HERE=Path(__file__).parent
H,SRC=gdparse.load(HERE/'source.level')
START=16785.0; END=24660.0; ROOTGROUP=600
ADDED=[]; changes=[]; nextgroup=610; motions=[]
colors={600:(8,15,18),601:(12,24,28),602:(20,36,39),603:(30,48,49),604:(54,77,74),605:(109,135,122),606:(125,83,47),607:(194,135,74),608:(15,38,42),609:(79,100,91),610:(83,122,114),611:(5,10,12),612:(17,29,32),613:(41,61,61),614:(30,61,63),615:(132,163,143),616:(54,39,29),617:(25,49,53),618:(38,77,78),619:(9,19,22),620:(0,0,0)}
def fmt(x):return str(round(x,5)) if isinstance(x,float) else str(x)
def groups(s):return [int(v) for v in s.split('.') if v]
def group():
 global nextgroup
 nextgroup+=1;return nextgroup

def add(oid,x,y,c=603,z=-1,order=0,sx=1,sy=None,rot=0,gg=(),detail=None,ldm=False):
 o={'1':str(oid),'2':fmt(x),'3':fmt(y),'21':str(c),'22':str(c if detail is None else detail),'24':str(z),'25':str(order),'128':fmt(sx),'129':fmt(sx if sy is None else sy),'6':fmt(rot),'121':'1','134':'1','64':'1','67':'1','96':'1','20':'30','57':'.'.join(map(str,dict.fromkeys([ROOTGROUP,*gg])))}
 if ldm:o['103']='1'
 ADDED.append(o);return o

def rect(x,y,w,h,c=603,z=-1,order=0,gg=(),rot=0,ldm=False):return add(211,x,y,c,z,order,w/30,h/30,rot,gg,ldm=ldm)
def line(x1,y1,x2,y2,w=1.5,c=604,z=-1,order=1,gg=(),ldm=False):
 return rect((x1+x2)/2,(y1+y2)/2,math.hypot(x2-x1,y2-y1),w,c,z,order,gg,-math.degrees(math.atan2(y2-y1,x2-x1)),ldm)
def disc(x,y,r,c=603,z=-1,order=0,gg=(),ldm=False):
 # Native 2.2 circle sprite is 50 game units across (100px HD atlas).
 return add(3637,x,y,c,z,order,r/25,gg=gg,ldm=ldm)
def ring(x,y,r,w,c=604,z=-1,order=0,gg=(),ldm=False):
 # Polygonal rings use solid bars: predictable stroke width at any scale.
 N=36 if r>40 else 20
 for i in range(N):
  a=i*2*math.pi/N;b=(i+1)*2*math.pi/N
  line(x+r*math.cos(a),y+r*math.sin(a),x+r*math.cos(b),y+r*math.sin(b),w,c,z,order,gg,ldm)
def trigger(oid,x,**kw):
 o={'1':str(oid),'2':fmt(x),'3':str(1080+30*(len(ADDED)%8)),'36':'1','20':'34'}
 o.update({str(k):fmt(v) for k,v in kw.items()});ADDED.append(o);return o

def move(g,x,dy,duration,dx=0):
 trigger(901,x,**{'51':g,'28':dx,'29':dy,'10':duration,'30':13,'85':2});motions.append({'kind':'move','group':g,'x':x,'dy':dy,'dx':dx,'duration':duration})
def rotate(g,cg,x,deg,duration):
 trigger(1346,x,**{'51':g,'71':cg,'68':deg,'10':duration,'30':0});motions.append({'kind':'rotate','group':g,'center':cg,'x':x,'degrees':deg,'duration':duration})
def center(x,y):
 g=group();add(1764,x,y,620,-5,sx=.02,gg=(g,));return g

def fan(x,y,r=112):
 ring(x,y,r,6,602,-3,4);ring(x,y,r-9,2,603,-3,5)
 for i in range(12):
  a=i*math.pi/6;disc(x+(r-4)*math.cos(a),y+(r-4)*math.sin(a),1.7,604,-3,6,ldm=True)
 g=group();cg=center(x,y)
 for i in range(6):
  a=i*math.pi/3
  # Broad offset blades meet the central hub, enclosed by a fixed casing.
  line(x+16*math.cos(a),y+16*math.sin(a),x+(r-22)*math.cos(a+.27),y+(r-22)*math.sin(a+.27),15,602,-3,3,(g,))
  line(x+23*math.cos(a),y+23*math.sin(a),x+(r-25)*math.cos(a+.25),y+(r-25)*math.sin(a+.25),2,603,-3,4,(g,))
 disc(x,y,18,603,-3,6);disc(x,y,7,604,-3,7)
 rotate(g,cg,max(START,x-750),-260,8)
 # Fixed mounting lugs, anchored into the rear wall.
 for s in [-1,1]:
  rect(x+s*(r+16),y,24,18,602,-3,3)
  line(x+s*r,y-35,x+s*(r+25),y-12,5,602,-3,3)

def beam(x,y,w,h,c=602,z=-3):
 rect(x,y,w,h,c,z,1)
 if h>w:
  line(x-w/2+3,y-h/2,x-w/2+3,y+h/2,2,603,z,2)
  for yy in np.arange(y-h/2+20,y+h/2,60):
   line(x-w/2+7,yy,x+w/2-7,min(yy+45,y+h/2),2,603,z,2,ldm=True)
 else:
  line(x-w/2,y+h/2-3,x+w/2,y+h/2-3,2,603,z,2)

def lamp(x,y,w=24,gg=(),z=-1):
 rect(x,y,w+7,10,611,z,7,gg);rect(x,y,w,3,607,z,8,gg)
 add(1011,x,y-8,606,z,6,w/30,.55,gg=gg,ldm=True)
 for dx in [-w/2-2,w/2+2]:disc(x+dx,y,1,609,z,9,gg,True)

def pipe(points,r=6,c=602,z=-3):
 for (x1,y1),(x2,y2) in zip(points,points[1:]):
  line(x1,y1,x2,y2,r*2+3,611,z,2);line(x1,y1,x2,y2,r*2,c,z,3)
  line(x1,y1+2,x2,y2+2,1.5,603,z,4,ldm=True)
 for x,y in points[1:-1]:disc(x,y,r+2,c,z,5)
 for x,y in points[1:-1]:ring(x,y,r+3,2,604,z,6,ldm=True)

def chain(x,y,length):
 g=group();cg=center(x,y)
 for j in range(int(length/12)):
  yy=y-j*12
  add(3050,x,yy,603,-3,8,sx=.14,sy=.22,gg=(g,),ldm=True)
 disc(x,y-length,5,603,-3,9,(g,),True)
 rotate(g,cg,max(START,x-500),3.5,1.2)
 rotate(g,cg,max(START,x-500)+600,-7,2.4)

def panel(x,y,w,h,gg=()):
 if w<22 or h<22:return
 rect(x,y,w-7,h-7,602,-1,2,gg)
 rect(x,y-1,w-11,h-11,603,-1,3,gg)
 line(x-w/2+6,y+h/2-6,x+w/2-6,y+h/2-6,1,604,-1,4,gg)
 if w>=55 and h>=45:
  for dx in [-w/2+9,w/2-9]:
   for dy in [-h/2+9,h/2-9]:add(1765,x+dx,y+dy,609,-1,6,sx=.25,gg=gg,ldm=True)
  if w>100:
   for dx in np.arange(-min(w*.3,60),min(w*.3,60),9):rect(x+dx,y,3,min(18,h-30),611,-1,5,gg,ldm=True)
 else:
  disc(x,y,1.6,609,-1,5,gg,True)

# Measure spectral onset locations; no gameplay timing is altered.
with wave.open(str(HERE/'song.wav')) as f:
 sr=f.getframerate();audio=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(float)/32768
n=1024;hop=110
frames=np.lib.stride_tricks.sliding_window_view(audio,n)[::hop]
spec=np.abs(np.fft.rfft(frames*np.hanning(n),axis=1));flux=np.maximum(np.diff(spec,axis=0),0).sum(axis=1)
ts=(np.arange(len(flux))*hop+n/2)/sr
schedule=json.loads((HERE/'inspection-plan.json').read_text())['speed_schedule']
def xt(t):return sum(max(0,min(t,schedule[i+1][0] if i+1<len(schedule) else t)-a)*v for i,(a,v) in enumerate(schedule))
def tx(x):
 for i,(t,v) in enumerate(schedule):
  if i+1==len(schedule) or x<xt(schedule[i+1][0]):return t+(x-xt(t))/v
beats=[]
for pred in np.arange(48.064,64,.5):
 ids=np.where(abs(ts-pred)<.075)[0];j=ids[np.argmax(flux[ids])];t=float(ts[j]);x=xt(t)
 if START<=x<END-180:beats.append({'song_time':round(t,5),'x':round(x,4),'strength':round(float(flux[j]),2)})

# Background: wall bays and water confined to the approved section.
for a in np.arange(START,END,300):
 w=min(300,END-a);rect(a+w/2,320,w,1200,600,-5,-20)
 add(1011,a+w/2,30,608,-5,-10,w/30,12)
# Continuous functional architecture, with the silhouette changing at each mode.
for x in [16935,17595,18135,18555,19275,19935,20595,21135,21675,22335,22935,23655,24315]:
 beam(x,290,26,920,601,-5)
for x,y,r in [(17115,330,123),(17745,360,96),(18960,385,132),(20220,400,108)]:fan(x,y,r)
for a,b in [(16805,18170),(18230,20630),(20700,22400),(22685,24635)]:
 beam((a+b)/2,475,b-a,24,602,-3)
 pipe([(a+35,550),(a+35,515),(b-35,515),(b-35,400)],5)
for x in [17055,17895,18525,19695,20355,20925,21555,22995,23955]:
 chain(x,470,70+(int(x)//30%3)*24)
# Pressure duct: jointed runs and inspection hatches behind the wave.
pipe([(18235,25),(18885,25),(18885,-65),(19665,-65),(19665,65),(20595,65)],9,c=602)
pipe([(18315,420),(18825,420),(19005,480),(19605,480),(19815,390),(20625,390)],8,c=602)
for x,y in [(18435,340),(19155,60),(19875,430),(20445,90)]:
 ring(x,y,27,4,603,-3,8);ring(x,y,20,2,604,-3,9)
 g=group();cg=center(x,y)
 for angle in [0,60,120]:line(x-19*math.cos(math.radians(angle)),y-19*math.sin(math.radians(angle)),x+19*math.cos(math.radians(angle)),y+19*math.sin(math.radians(angle)),3,604,-3,10,(g,))
 rotate(g,cg,max(START,x-600),80,5)
# Maintenance hall: boilers of different proportions, rear ladders and braces.
for x,y,w,h in [(20835,200,126,440),(21465,260,168,500),(22125,290,100,370)]:
 rect(x,y,w,h,601,-3,0);disc(x,y+h/2,w/2,601,-3,0)
 for yy in [y-h*.3,y+h*.27]:rect(x,yy,w+10,9,602,-3,1)
 line(x-w*.32,y-h/2,x-w*.32,y+h/2,3,603,-3,2)
 ring(x,y+80,18,3,603,-3,3);lamp(x,y+80,12,z=-3)
 for yy in np.arange(y-h/2+10,y+h/2-15,18):line(x+w*.3,yy,x+w*.3+20,yy,2,603,-3,2,ldm=True)
 pipe([(x+w/2,y+100),(x+w/2+35,y+100),(x+w/2+35,y-60)],4)
# UFO: overhead segmented gantry, with anchored suspension cables.
for a,b in [(22700,23360),(23420,23990),(24050,24620)]:
 beam((a+b)/2,410,b-a,22,603,-3)
 for x in np.arange(a+10,b-15,75):line(x,402,min(x+55,b),460,3,602,-3,2)
 lamp((a+b)/2,398,35,z=-3)

# Original objects retain every physical and control property. Only colors and
# draw ordering are changed for visible structure/hazard objects in the section.
OUT=copy.deepcopy(SRC)
struct={'1','94','1338','1339','468','211','208','209','693'}
hazards={'8','216','217','458','1717','1718'}
for idx,o in enumerate(OUT):
 x=float(o.get('2',0));oid=o['1']
 if not 16875<=x<END:continue
 if oid in struct|hazards and '6' not in o.get('57','').split('.'):
  before=dict(o)
  o['21']=str(605 if oid in hazards else 604 if oid in {'1338','1339','468','208','209'} else 602)
  o['22']=str(603 if oid in hazards else 602);o['24']='-1';o['25']='10' if oid in hazards else '0'
  changes.append({'index':idx,'keys':[k for k in set(o)|set(before) if o.get(k)!=before.get(k)]})

# Fill the native slope outlines with corresponding triangle art and inset ribs.
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));oid=o['1'];gg=groups(o.get('57',''))
 if not 16875<=x<END or 6 in gg:continue
 if oid in ['1338','1339']:
  w=30 if oid=='1338' else 60
  q=add(693 if w==30 else 694,x,y,602,-1,-2,gg=gg)
  for k in ['4','5','6','32','128','129']:
   if k in o:q[k]=o[k]
  # Transform ribs with the exact original flips and rotation.
  def tr(a,b):
   if o.get('4')=='1':a=-a
   if o.get('5')=='1':b=-b
   r=-math.radians(float(o.get('6',0)));return x+a*math.cos(r)-b*math.sin(r),y+a*math.sin(r)+b*math.cos(r)
  a=tr(-w/2+5,-11);b=tr(w/2-5,-11)
  line(*a,*b,2,603,-1,1,gg)
  a=tr(w*.20,-8);b=tr(w*.20,0)
  line(*a,*b,2,604,-1,2,gg,True)
  a=tr(w*.35,-8);disc(*a,1.2,609,-1,3,gg,True)
 if oid in ['94','208','209']:
  rect(x,y,29,29,602,-1,-1,gg);panel(x,y,29,29,gg)
  if x>=22665 and oid=='94':
   # Every hanging assembly has a fixed rear suspension connection.
   if y>120:line(x,y+19,x,398,1.2,602,-3,1)
   disc(x,y,8,611,-1,4,gg);ring(x,y,6,1.2,604,-1,5,gg)
   if int(x/30)%3==0:disc(x,y,1.4,607,-1,6,gg)
 if oid in ['216','217','458']:
  # A filled core made from two exact half-triangles stays inside the outline.
  w,h=(20,20) if oid=='216' else (20,8) if oid=='217' else (8,8)
  r=-math.radians(float(o.get('6',0)))
  for side in [-1,1]:
   dx=side*w/4;dy=-2
   if o.get('4')=='1':dx=-dx
   if o.get('5')=='1':dy=-dy
   xx=x+dx*math.cos(r)-dy*math.sin(r);yy=y+dx*math.sin(r)+dy*math.cos(r)
   q=add(693,xx,yy,602,-1,9,sx=w/60,sy=h/30,gg=gg,rot=float(o.get('6',0)))
   if (side==1) != (o.get('4')=='1'):q['4']='1'
   if o.get('5')=='1':q['5']='1'

# Tile-aligned robot panels, packed into occupied cells only. Separate each move
# group, so artwork on the moving block platform follows the source exactly.
bygroup=defaultdict(set)
for o in SRC:
 if o['1'] in ['211','208','209'] and 20685<=float(o['2'])<22665 and 6 not in groups(o.get('57','')):
  bygroup[tuple(groups(o.get('57','')))].add((round(float(o['2']),3),round(float(o['3']),3)))
for gg,cells in bygroup.items():
 left=set(cells)
 while left:
  x,y=min(left,key=lambda p:(p[1],p[0]));nw=1
  while nw<6 and (x+30*nw,y) in left:nw+=1
  nh=1
  while nh<4 and all((x+30*i,y+30*nh) in left for i in range(nw)):nh+=1
  for i in range(nw):
   for j in range(nh):left.remove((x+30*i,y+30*j))
  panel(x+(nw-1)*15,y+(nh-1)*15,nw*30,nh*30,gg)
 for x,y in cells:
  for dx,dy in [(0,30),(0,-30),(-30,0),(30,0)]:
   if (x+dx,y+dy) in cells:continue
   if dx==0:line(x-15,y+dy/2,x+15,y+dy/2,1.5,604,-1,7,gg)
   else:line(x+dx/2,y-15,x+dx/2,y+15,1.5,604,-1,7,gg)

# Small copper inlays follow the real solid slope transform, tying each beat
# to an attached component instead of an unanchored flash in the flight path.
for i,o in enumerate(SRC):
 x=float(o.get('2',0));y=float(o.get('3',0))
 if not 16875<=x<20685 or o['1']!='1339' or i%4:continue
 dx,dy=17,-10
 if o.get('4')=='1':dx=-dx
 if o.get('5')=='1':dy=-dy
 r=-math.radians(float(o.get('6',0)));xx=x+dx*math.cos(r)-dy*math.sin(r);yy=y+dx*math.sin(r)+dy*math.cos(r)
 rect(xx,yy,6,2,607,-1,5,groups(o.get('57','')),float(o.get('6',0)))
# Visible inspection consoles and wire conduits in the rear wall bays.
for x,y in [(17040,290),(18030,285),(18540,330),(19710,140),(21180,365),(22410,320),(23100,310),(24000,285)]:
 rect(x,y,54,34,611,-3,4);rect(x,y,49,29,602,-3,5)
 for dx in [-17,-9,-1]:rect(x+dx,y+7,4,2,606,-3,6,ldm=True)
 lamp(x+9,y-5,13,z=-3)
 pipe([(x-25,y),(x-42,y),(x-42,y+90)],2,c=602)

# Lights are mounted at known rail locations, not distributed through gameplay.
for x,y in [(16935,480),(17715,480),(18435,480),(19515,480),(20355,480),(20835,475),(21675,475),(22335,475)]:lamp(x,y,32,z=-3)
# Flood water and drifting steam remain behind the collision geometry.
water=group()
for a in np.arange(START+10,END-20,300):
 w=min(290,END-a-10);add(1011,a+w/2,-70,614,-3,-3,w/30,5,gg=(water,),ldm=True)
 line(a,-10,a+w,-10,.7,617,-3,-2,(water,),True)
move(water,START,32,max(1,tx(END)-tx(START)))
for x,y in [(17600,370),(19330,55),(21020,410),(23800,355)]:
 g=group()
 for i in range(7):add(1011,x+i*17,y+i*4,610,-3,5,sx=1.6,sy=.35,rot=-12,gg=(g,),ldm=True)
 move(g,max(START,x-450),35,2.8,25)

# New lighting uses dedicated channels. Original global color and shader logic
# remains intact; the opaque factory rear wall shields the old BG flashes.
for b in beats:
 trigger(1006,b['x'],**{'51':607,'45':.012,'46':.035,'47':.20,'7':236,'8':175,'9':101,'52':0})
 trigger(1006,b['x'],**{'51':604,'45':.015,'46':.01,'47':.16,'7':68,'8':96,'9':89,'52':0})
# Hard boundaries are visibility gates, with a short fade before the exit.
trigger(1007,START,**{'51':ROOTGROUP,'10':0,'35':1})
trigger(1007,END-150,**{'51':ROOTGROUP,'10':(150/468),'35':0})
# Start hidden even if the following section is within the pre-drop camera.
trigger(1007,0,**{'51':ROOTGROUP,'10':0,'35':0})
trigger(1007,END,**{'51':ROOTGROUP,'10':0,'35':0})

# Extend header with unused channels; retain original header values verbatim.
head=gdparse.parse_header(H)
cs=head.get('kS38','')
for cid,rgb in colors.items():
 op=0 if cid==620 else .12 if cid==610 else 1
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1'
head['kS38']=cs.strip('|')
newH=','.join(k+','+v for k,v in head.items())
ALL=OUT+ADDED
raw=newH+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in ALL)
(HERE/'decorated.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Sinking Factory Deco');fields['k48']=('i',str(len(ALL)))
fields['k1']=('i','0');fields['kCEK']=('i','4');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - Flooded Drop.gmd';out.parent.mkdir(exist_ok=True);gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(ALL),'scope':[START,END],'modified_original_objects':changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'notes':['Original gameplay and original triggers retained. Structural original edits restricted to colors and draw ordering.','Timing based on decoded portal positions; native activation offsets have not been calibrated.','New visible decorations use NoTouch and an independent master alpha group.']}
(HERE/'build-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:manifest[k] for k in ['source_objects','added_objects','total_objects','scope','groups']},indent=2));print(out)
