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
colors={600:(12,7,7),601:(21,14,13),602:(31,29,29),603:(42,38,36),604:(126,91,65),605:(225,172,112),606:(93,27,13),607:(231,107,34),608:(40,14,10),609:(146,122,90),610:(17,12,13),611:(8,7,8),612:(31,13,10),613:(74,56,41),614:(133,42,16),615:(255,208,117),616:(185,54,16),617:(65,34,24),618:(55,19,11),619:(20,16,16),620:(0,0,0),621:(255,158,56),622:(65,14,9),623:(241,190,119),624:(120,25,9)}

def fmt(x):return str(round(x,5)) if isinstance(x,float) else str(x)
def groups(s):return [int(v) for v in s.split('.') if v]
def group():
 global nextgroup
 nextgroup+=1;return nextgroup

def add(oid,x,y,c=603,z=-1,order=0,sx=1,sy=None,rot=0,gg=(),detail=None,ldm=False):
 o={'1':str(oid),'2':fmt(x),'3':fmt(y),'21':str(c),'22':str(c if detail is None else detail),'24':str(z),'25':str(order),'128':fmt(sx),'129':fmt(sx if sy is None else sy),'6':fmt(rot),'121':'1','134':'1','64':'1','67':'1','96':'1','20':'0','61':'30','57':'.'.join(map(str,dict.fromkeys([ROOTGROUP,*gg])))}
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


# Exact attached architecture. No object placements are inherited from Inferno.
sys.path.insert(0,str(HERE/'vendor'))
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union,triangulate
from shapely import affinity
import base64

def triangle(a,b,c,color,z,order=0,gg=(),ldm=False):
 pts=[a,b,c];i=max(range(3),key=lambda i:math.dist(pts[i],pts[(i+1)%3]))
 a,b,c=pts[i],pts[(i+1)%3],pts[(i+2)%3]
 ux,uy=b[0]-a[0],b[1]-a[1];length=math.hypot(ux,uy)
 if length<.001:return
 q=((c[0]-a[0])*ux+(c[1]-a[1])*uy)/(length*length)
 r=(a[0]+q*ux,a[1]+q*uy)
 for end in [a,b]:
  u=(end[0]-r[0],end[1]-r[1]);v=(c[0]-r[0],c[1]-r[1]);w=math.hypot(*u);h=math.hypot(*v)
  if min(w,h)<.05:continue
  theta=math.atan2(-u[1],-u[0]);dy=(-math.sin(theta),math.cos(theta))
  o=add(693,r[0]+(u[0]+v[0])/2,r[1]+(u[1]+v[1])/2,color,z,order,(w+1.2)/30,(h+1.2)/30,-math.degrees(theta),gg,ldm=ldm)
  if v[0]*dy[0]+v[1]*dy[1]<0:o['5']='1'

def fill(shape,c=602,z=-1,order=1,gg=(),ldm=False):
 if shape.is_empty:return
 if shape.geom_type=='Polygon':
  if shape.area<.2:return
  xmin,ymin,xmax,ymax=shape.bounds
  if abs(shape.area-(xmax-xmin)*(ymax-ymin))<.005:
   rect((xmin+xmax)/2,(ymin+ymax)/2,xmax-xmin,ymax-ymin,c,z,order,gg,ldm=ldm);return
  if len(shape.exterior.coords)==4 and not shape.interiors:
   triangle(*list(shape.exterior.coords)[:3],c,z,order,gg,ldm);return
  cuts=[tri.intersection(shape) for tri in triangulate(shape)]
  covered=sum(t.area for t in cuts)
  assert abs(covered-shape.area)<max(.1,shape.area*1e-5), ('unfilled polygon',shape.area,covered)
  for cut in cuts:
   if cut.area<.2:continue
   fill(cut,c,z,order,gg,ldm)
 elif hasattr(shape,'geoms'):
  for part in shape.geoms:fill(part,c,z,order,gg,ldm)

def stroke(shape,c=604,z=-1,order=4,width=1,gg=(),ldm=False):
 if shape.is_empty:return
 if shape.geom_type in ['LineString','LinearRing']:
  pts=list(shape.coords)
  for a,b in zip(pts,pts[1:]):
   if math.dist(a,b)>.2:line(*a,*b,width,c,z,order,gg,ldm)
 elif shape.geom_type=='Polygon':stroke(shape.exterior,c,z,order,width,gg,ldm)
 elif hasattr(shape,'geoms'):
  for part in shape.geoms:stroke(part,c,z,order,width,gg,ldm)

def clipped_line(body,a,b,c=613,width=1.2,gg=(),order=4):
 stroke(LineString([a,b]).intersection(body),c,-1,order,width,gg)


exec(compile((HERE/'atmosphere_art.py').read_text(),str(HERE/'atmosphere_art.py'),'exec'))
