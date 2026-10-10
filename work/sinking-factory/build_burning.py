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
colors={600:(12,4,5),601:(25,7,8),602:(18,14,15),603:(39,25,25),604:(104,57,45),605:(202,137,94),606:(137,27,12),607:(255,132,40),608:(84,10,5),609:(125,89,73),610:(41,25,27),611:(5,5,7),612:(50,9,9),613:(67,27,20),614:(153,35,12),615:(255,215,136),616:(250,54,7),617:(76,24,20),618:(195,47,13),619:(7,6,8),620:(0,0,0),621:(255,158,56),622:(65,14,9),623:(241,190,119),624:(145,22,11)}

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


# The flooded pass is discarded. This pass starts from the unmodified source.
import random,base64
rng=random.Random(140914)

def triangle(a,b,c,color,z,order=0,gg=(),ldm=False):
 pts=[a,b,c];i=max(range(3),key=lambda i:math.dist(pts[i],pts[(i+1)%3]))
 a,b,c=pts[i],pts[(i+1)%3],pts[(i+2)%3]
 ux,uy=b[0]-a[0],b[1]-a[1];length=math.hypot(ux,uy)
 if length<.001:return
 q=((c[0]-a[0])*ux+(c[1]-a[1])*uy)/(length*length)
 r=(a[0]+q*ux,a[1]+q*uy)
 for end in [a,b]:
  u=(end[0]-r[0],end[1]-r[1]);v=(c[0]-r[0],c[1]-r[1]);w=math.hypot(*u);h=math.hypot(*v)
  if min(w,h)<.01:continue
  theta=math.atan2(-u[1],-u[0]);dy=(-math.sin(theta),math.cos(theta))
  o=add(693,r[0]+(u[0]+v[0])/2,r[1]+(u[1]+v[1])/2,color,z,order,w/30,h/30,-math.degrees(theta),gg,ldm=ldm)
  if v[0]*dy[0]+v[1]*dy[1]<0:o['5']='1'

def poly(points,c,z,order=0,gg=(),ldm=False):
 for i in range(1,len(points)-1):triangle(points[0],points[i],points[i+1],c,z,order,gg,ldm)

def glow(x,y,w,h,c=616,z=-5,gg=()):
 # Native round glow, safely stretched and kept behind the scenery.
 add(1887,x,y,c,z,-2,w/10,h/10,gg=gg,ldm=True)

def hotframe(x,y,w,h):
 rect(x,y,w+20,h+20,611,-3,3)
 rect(x,y,w,h,606,-3,4)
 add(1011,x,y,616,-3,5,w/30,h/30)
 rect(x,y-h*.18,w-12,h*.32,607,-3,6)
 rect(x,y-h*.36,w-12,h*.12,615,-3,7)
 for xx in np.arange(x-w/2+9,x+w/2-3,18):rect(xx,y,6,h+10,611,-3,8)
 for yy in [y-h/2,y+h/2]:rect(x,yy,w+32,12,602,-3,9)
 for dx in [-w/2-12,w/2+12]:
  rect(x+dx,y,12,h+30,602,-3,9)
  for yy in [y-h*.35,y+h*.35]:disc(x+dx,yy,2,609,-3,10)
 glow(x,y,w*2.2,h*1.7,624)

def flame(x,y,w,h,phase=0):
 # A rising, curling flame silhouette, three nested heat contours.
 g=group();t0=max(START,x-700)
 for j,(size,c) in enumerate([(1,616),(.65,607),(.28,615)]):
  ww=w*size;hh=h*(.5+.5*size);shift=(1-size)*w*.1
  pts=[(x-ww/2,y),(x-ww*.55,y+hh*.23),(x-ww*.28,y+hh*.60),(x+ww*.14,y+hh),(x+ww*.2,y+hh*.63),(x+ww*.47,y+hh*.38),(x+ww/2,y)]
  poly(pts,c,-3,11+j,(g,),ldm=j==2)
 glow(x,y+h*.25,w*2.4,h*1.3,624,gg=(g,))
 move(g,t0,12+phase*3,.6)
 move(g,t0+310,-9,.48)
 move(g,t0+570,15,.7)
 # Each plume has its own flicker, separate from the strong musical impacts.
 for i in range(5):
  trigger(1007,t0+i*150,**{'51':g,'10':.08,'35':(.64 if i%2 else 1)})
 return g

def smoke(x,y,w,h):
 g=group();t0=max(START,x-600)
 for i in range(7):
  xx=x+math.sin(i*1.4)*w*.23;yy=y+i*h/7
  disc(xx,yy,w*(.32+i*.018),619,-3,25,(g,),True)
  disc(xx-6,yy+8,w*.22,610,-3,26,(g,),True)
 move(g,t0,55,3,dx=-28)
 return g

def sparks(x,y,amount=18,spread=60):
 for k in range(3):
  g=group();t0=max(START,x-580)+k*85
  for i in range(amount//3):
   xx=x+rng.uniform(-spread/2,spread/2);yy=y+rng.uniform(-15,60)
   line(xx,yy,xx+4,yy+9,1.1 if i%3 else 1.8,615 if i%3 else 607,-3,31,(g,),True)
  move(g,t0,100+k*22,1.4,dx=40-k*13)
  trigger(1007,t0+600,**{'51':g,'10':.25,'35':0})

def truss(a,b,y,h=45):
 line(a,y,b,y,10,611,-3,20);line(a,y+h,b,y+h,8,602,-3,21)
 for x in np.arange(a,b-20,55):
  line(x,y,min(x+55,b),y+h,5,602,-3,21)
  line(x,y+h,min(x+55,b),y,3,603,-3,22,ldm=True)

def broken_beam(x,y,length,angle,collapse=False):
 g=group() if collapse else None;gg=(g,) if g else ()
 line(x,y,x+length*math.cos(angle),y+length*math.sin(angle),18,611,-3,28,gg)
 line(x,y+5,x+length*math.cos(angle),y+length*math.sin(angle)+5,2,604,-3,29,gg)
 if g:
  cg=center(x,y);rotate(g,cg,max(START,x-500),-18,.8);move(g,max(START,x-500)+380,-45,.6)

def sign(x,y,text):
 rect(x,y,115,29,611,-3,15);line(x-57,y+15,x+57,y+15,2,606,-3,16)
 o=add(580,x,y,607,-3,17,sx=.18)
 o['31']=base64.urlsafe_b64encode(text.encode()).decode()

# Soot-black architecture silhouetted against a continuous deep red inferno.
for a in np.arange(START,END,270):
 w=min(270,END-a);rect(a+w/2,230,w,1050,600,-5,-30)
 add(1011,a+w/2,65,612,-5,-25,w/30,19)
 # Furnace wash is strongest underneath, fading into a smoke-filled ceiling.
 add(1011,a+w/2,-55,606,-5,-24,w/30,8)
for i,x in enumerate([16920,17400,17985,18570,19290,19950,20550,21180,21810,22440,23070,23790,24390]):
 beam(x,240,32 if i%3 else 48,810,611,-3)
 line(x-18,-140,x-18,520,2,613,-3,3)
 # Torn electric harness, always anchored to a support.
 line(x+14,360,x+28,290,2,604,-3,4)
 line(x+28,290,x+13,250,2,604,-3,4)
 if i%2==0:sparks(x+13,250,9,18)

# SHIP: blast doors have failed; their grilles reveal a white-hot furnace.
for x,y,w,h in [(17070,250,145,270),(17610,240,185,250),(18060,210,94,190)]:
 hotframe(x,y,w,h)
 truss(x-w/2-45,x+w/2+45,y+h/2+30)
 flame(x-w*.18,y-h/2-50,w*.50,140,1)
 smoke(x+35,y+h/2-20,125,220);sparks(x,y,21,85)
sign(17265,360,'CORE BREACH')
broken_beam(17530,405,210,-.4,True)
broken_beam(17910,445,150,-1.05,True)

# WAVE: ruptured pressure line and jagged, backlit structural ribs.
pipe([(18240,390),(18440,390),(18510,330)],13,c=602)
pipe([(18645,355),(19005,410),(19410,410)],13,c=602)
pipe([(19770,420),(20235,420),(20595,330)],13,c=602)
for x,y in [(18510,330),(19410,410),(19770,420),(20595,330)]:
 ring(x,y,18,5,604,-3,12);flame(x,y-15,70,155,2);sparks(x,y,18,45);smoke(x,y+70,120,170)
# Hot diagonal exhaust flue behind the middle wave, visibly mounted to ribs.
for a,b in [((18945,350),(19350,65)),((19680,100),(20100,395))]:
 line(*a,*b,60,611,-3,5)
 line(*a,*b,40,608,-3,6)
 line(*a,*b,14,606,-3,7)
 dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);nx=-dy/length;ny=dx/length
 for q in [.12,.38,.65,.88]:
  x=a[0]+dx*q;y=a[1]+dy*q
  line(x-nx*32,y-ny*32,x+nx*32,y+ny*32,9,602,-3,8)
for a,b,y in [(18330,18720,30),(18870,19380,-10),(19560,19890,60),(20100,20550,40)]:
 hotframe((a+b)/2,y, b-a-100,110)
 truss(a,b,y-90,40)
for x,y,ang in [(18480,450,-1.1),(19200,470,-.4),(19860,430,-.8),(20400,480,-1.35)]:broken_beam(x,y,180,ang,True)
sign(19040,335,'PRESSURE CRITICAL')

# ROBOT: a buckled press hall. Large cracked housings replace the quiet boilers.
for x,y,w,h in [(20900,240,170,300),(21570,275,190,400),(22200,250,140,340)]:
 rect(x,y,w+18,h+25,611,-3,4);rect(x,y,w,h,602,-3,5)
 # A furnace-colored crack snakes through the machine, held within its body.
 crack=[(x-25,y+h/2),(x+7,y+70),(x-18,y+5),(x+28,y-75),(x+10,y-h/2)]
 for a,b in zip(crack,crack[1:]):line(*a,*b,8,616,-3,6);line(*a,*b,2,615,-3,7)
 for yy in [y+h*.3,y-h*.3]:rect(x,yy,w+30,17,603,-3,8)
 hotframe(x,y-55,w*.50,70)
 flame(x+30,y+60,75,160);smoke(x,y+120,145,180);sparks(x,y+35,18,100)
 truss(x-w*.8,x+w*.8,y+h/2+10)
broken_beam(21700,470,240,-.55,True)
sign(21185,365,'EVACUATE')

# UFO: burning cargo crane over an open combustion trench.
for a,b,y in [(22700,23260,390),(23320,23930,430),(23990,24610,375)]:
 truss(a,b,y,48)
 hotframe((a+b)/2,-5,b-a-100,90)
 for x in [a+80,b-80]:chain(x,y-5,125)
 broken_beam(b-90,y+25,130,-1.2,True)
for x,y,w,h in [(22800,-25,95,190),(23370,-30,120,230),(23880,-20,85,155),(24420,-10,115,220)]:
 flame(x,y,w,h,1);smoke(x+20,y+h-20,135,170);sparks(x,y+50,24,90)
sign(23630,345,'SYSTEM FAILURE')

# Original geometry is recolored only. Every gameplay field remains unchanged.
OUT=copy.deepcopy(SRC)
struct={'1','94','1338','1339','468','211','208','209','693'}
hazards={'8','216','217','458','1717','1718'}
for idx,o in enumerate(OUT):
 x=float(o.get('2',0));oid=o['1']
 if not 16875<=x<END:continue
 if oid in struct|hazards and '6' not in o.get('57','').split('.'):
  before=dict(o)
  o['21']=str(605 if oid in hazards else 604 if oid in {'1338','1339','468','208','209'} else 602)
  o['22']='602';o['24']='-1';o['25']='10' if oid in hazards else '0'
  changes.append({'index':idx,'keys':[k for k in set(o)|set(before) if o.get(k)!=before.get(k)]})

# Broken solid metal follows the original slopes exactly, including flips.
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));oid=o['1'];gg=groups(o.get('57',''))
 if not 16875<=x<END or 6 in gg:continue
 if oid in ['1338','1339']:
  w=30 if oid=='1338' else 60
  q=add(693 if w==30 else 694,x,y,602,-1,-2,gg=gg)
  for k in ['4','5','6','32','128','129']:
   if k in o:q[k]=o[k]
  def tr(a,b):
   if o.get('4')=='1':a=-a
   if o.get('5')=='1':b=-b
   r=-math.radians(float(o.get('6',0)));return x+a*math.cos(r)-b*math.sin(r),y+a*math.sin(r)+b*math.cos(r)
  a=tr(-w/2+3,-12);b=tr(w/2-3,-12);line(*a,*b,2,603,-1,2,gg)
  a=tr(w*.26,-9);b=tr(w*.35,-2);line(*a,*b,1.4,606,-1,3,gg)
  a=tr(w*.30,-10);disc(*a,1.2,609,-1,4,gg,True)
 if oid=='94':
  rect(x,y,29,29,611,-1,1,gg);rect(x,y,23,23,603,-1,2,gg)
  line(x-9,y-9,x+9,y+9,3,602,-1,3,gg);line(x-9,y+9,x+9,y-9,2,602,-1,3,gg)
  disc(x,y,3,607,-1,4,gg)
  if x>=22665 and y>120:line(x,y+20,x,390,1.3,603,-3,2)
 if oid in ['216','217','458']:
  w,h=(20,20) if oid=='216' else (20,8) if oid=='217' else (8,8)
  r=-math.radians(float(o.get('6',0)))
  for side in [-1,1]:
   dx=side*w/4;dy=-2
   if o.get('4')=='1':dx=-dx
   if o.get('5')=='1':dy=-dy
   xx=x+dx*math.cos(r)-dy*math.sin(r);yy=y+dx*math.sin(r)+dy*math.cos(r)
   q=add(693,xx,yy,602,-1,9,sx=w/60,sy=h/30,gg=gg,rot=float(o.get('6',0)))
   if (side==1)!=(o.get('4')=='1'):q['4']='1'
   if o.get('5')=='1':q['5']='1'

# Scorched platform skin: larger coherent plates, one crack per plate.
bygroup=defaultdict(set)
for o in SRC:
 if o['1'] in ['211','208','209'] and 20685<=float(o['2'])<22665 and 6 not in groups(o.get('57','')):
  bygroup[tuple(groups(o.get('57','')))].add((round(float(o['2']),3),round(float(o['3']),3)))
for gg,cells in bygroup.items():
 left=set(cells)
 while left:
  x,y=min(left,key=lambda p:(p[1],p[0]));nw=1
  while nw<7 and (x+30*nw,y) in left:nw+=1
  nh=1
  while nh<5 and all((x+30*i,y+30*nh) in left for i in range(nw)):nh+=1
  for i in range(nw):
   for j in range(nh):left.remove((x+30*i,y+30*j))
  xx=x+(nw-1)*15;yy=y+(nh-1)*15;w=nw*30;h=nh*30
  rect(xx,yy,w-3,h-3,602,-1,1,gg)
  line(xx-w/2+4,yy+h/2-3,xx+w/2-4,yy+h/2-3,2,604,-1,3,gg)
  if nw>2 and nh>1:
   pts=[(xx-13,yy+h/2-5),(xx+8,yy+2),(xx-4,yy-h/2+5)]
   for a,b in zip(pts,pts[1:]):line(*a,*b,2,606,-1,4,gg)
   for dx in [-w/2+10,w/2-10]:add(1765,xx+dx,yy,609,-1,4,sx=.30,gg=gg,ldm=True)
  elif nw>1:
   for dx in np.arange(-w/2+8,w/2-3,14):line(xx+dx,yy-4,xx+dx+5,yy+4,3,606,-1,4,gg)
 for x,y in cells:
  for dx,dy in [(0,30),(0,-30),(-30,0),(30,0)]:
   if (x+dx,y+dy) in cells:continue
   if dx==0:line(x-15,y+dy/2,x+15,y+dy/2,1.5,604,-1,7,gg)
   else:line(x+dx/2,y-15,x+dx/2,y+15,1.5,604,-1,7,gg)

# Dramatic lighting follows selected measured beats, with a strong impact every
# four accents and lighter incandescent flicker between them.
for i,b in enumerate(beats):
 major=i%4==0
 trigger(1006,b['x'],**{'51':606,'45':.008,'46':.045 if major else .015,'47':.24 if major else .13,'7':240 if major else 178,'8':62 if major else 33,'9':12,'52':0})
 trigger(1006,b['x'],**{'51':604,'45':.008,'46':.025,'47':.17,'7':206 if major else 140,'8':119 if major else 65,'9':59 if major else 41,'52':0})
 if major:
  trigger(1006,b['x'],**{'51':600,'45':.01,'46':.025,'47':.22,'7':44,'8':10,'9':8,'52':0})
# Source shader targets are explicitly neutralized inside this visual section.
# Existing camera shakes, speeds, music and interactive triggers are retained.
visual_trigger_changes=[]
for i,o in enumerate(OUT):
 if o['1']=='2921' and float(o['2'])==16875:
  visual_trigger_changes.append({'index':i,'original':dict(o)})
  o['176']='0';o['10']='0';o['188']='0'
# Restore the source's visual shader state at the precise end boundary.
for entry in visual_trigger_changes:
 orig=entry['original'];o=dict(orig);o['2']=str(END);o['3']='1440';o['20']='34';o['10']='0'
 if o['1']=='2909':
  elapsed=tx(END)-tx(float(orig['2']));o['176']=fmt(min(1,elapsed/float(orig['10']))*float(orig['176']))
 ADDED.append(o)
 if orig['1']=='2909':
  finish=dict(orig);finish['2']=fmt(END+.01);finish['3']='1470';finish['20']='34';finish['10']=fmt(max(.001,float(orig['10'])-elapsed));ADDED.append(finish)

# No start-of-level hide: the artwork remains inspectable in the editor.
# Its actual geometry starts at the drop; activate/fade are local to the section.
trigger(1007,START,**{'51':ROOTGROUP,'10':0,'35':1})
trigger(1007,END-90,**{'51':ROOTGROUP,'10':90/468,'35':0})
trigger(1007,END,**{'51':ROOTGROUP,'10':0,'35':0})
head=gdparse.parse_header(H);cs=head.get('kS38','').rstrip('|')
for cid,rgb in colors.items():
 op=0 if cid==620 else .30 if cid==610 else .9 if cid==616 else 1
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1_5_{1 if cid==624 else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in OUT+ADDED)
(HERE/'burning.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Inferno');fields['k48']=('i',str(len(OUT+ADDED)))
fields['k1']=('i','0');fields['kCEK']=('i','4');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - INFERNO.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'modified_original_objects':changes,'visual_trigger_changes':visual_trigger_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False}
(HERE/'burning-manifest.json').write_text(json.dumps(manifest,indent=2));print({k:manifest[k] for k in ['added_objects','total_objects','groups']});print(out)
