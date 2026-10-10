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
  o=add(693,r[0]+(u[0]+v[0])/2,r[1]+(u[1]+v[1])/2,color,z,order,(w+.3)/30,(h+.3)/30,-math.degrees(theta),gg,ldm=ldm)
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

# Back wall spans the room; openings, beams and fixtures all share the same bays.
# The deepest plane stays subdued so the foreground corridor reads as one form.
for a in np.arange(START,END,360):
 w=min(360,END-a);rect(a+w/2,230,w,1050,600,-5,-30)
 add(1011,a+w/2,130,608,-5,-25,w/30,15)
for x in np.arange(16905,24600,510):
 rect(x,250,30,680,611,-3,-10)
 rect(x+3,250,9,680,601,-3,-9)
 rect(x,370,120,14,601,-3,-8)
 # Horizontal rear pipe fits the column bay, never crosses the front corridor.
 line(x+15,355,min(x+495,24640),355,8,601,-3,-8)
 line(x+15,357,min(x+495,24640),357,1.5,613,-3,-7)

furnace_events=[]
def recess(x,y,w,h,opening_x):
 # Frame and doors have a shared rectangular envelope; fire stays behind them.
 rect(x,y,w+24,h+24,611,-3,0)
 rect(x,y,w+14,h+14,603,-3,1)
 rect(x,y,w,h,606,-3,2)
 add(1011,x,y,616,-3,3,w/30,h/30)
 # Three narrow hot cores are recessed, with no pointed flame props in the route.
 for dx in [-w*.26,0,w*.26]:
  add(1011,x+dx,y-h*.18,607,-3,4,w*.13/30,h*.7/30)
  add(1011,x+dx,y-h*.34,615,-3,5,w*.07/30,h*.25/30)
 # Fixed steel grate divides the aperture and contains the fire.
 for dx in np.arange(-w/2+7,w/2,22):rect(x+dx,y,5,h,611,-3,6)
 for dy in [-h/2,h/2]:rect(x,y+dy,w+30,8,602,-3,10)
 for dx in [-w/2,w/2]:rect(x+dx,y,8,h+15,602,-3,10)
 for dx in [-w/2-7,w/2+7]:
  for dy in [-h/2+8,h/2-8]:disc(x+dx,y+dy,1.8,609,-3,11,ldm=True)
 # Shutters travel inside this same frame: no detached doors flying into space.
 g1=group();g2=group()
 rect(x-w*.30,y,w*.40,h-4,602,-3,8,(g1,));rect(x+w*.30,y,w*.40,h-4,602,-3,8,(g2,))
 move(g1,opening_x,0,.32,dx=-w*.10);move(g2,opening_x,0,.32,dx=w*.10)
 # Extra slab caps cover the travel, so the shutter never protrudes past its frame.
 for dx in [-w*.55,w*.55]:rect(x+dx,y,w*.12,h+24,611,-3,12)
 furnace_events.append({'x':x,'y':y,'w':w,'h':h,'trigger_x':opening_x,'door_groups':[g1,g2]})

# Sparse rear apertures. Their placement is on the structural bay grid.
for args in [(17160,100,150,220,16875),(17670,255,150,240,17250),(19110,200,170,200,18700),(20130,210,170,210,19720),(21150,240,160,250,20750),(22170,205,160,240,21750),(23190,190,150,230,22750),(24210,180,150,220,23780)]:recess(*args)

# Build continuous outward wall shapes from the source slope hypotenuses.
segments=json.loads((HERE/'audit/slope-boundaries.json').read_text())['segments']
solid_parts=[];terrain_edges=[];shallow=[]
for s in segments:
 x,y=s['center']
 if not 16875<=x<20685:continue
 a,b=s['edge'];a=tuple(a);b=tuple(b)
 if 18195<=x<18855:
  shallow.append(s);continue
 outer=-180 if s['side']=='lower' else 650
 shape=Polygon([a,b,(b[0],outer),(a[0],outer)]).intersection(box(16875,-180,20685,650))
 if not shape.is_valid:shape=shape.buffer(0)
 solid_parts.append(shape);terrain_edges.append(LineString([a,b]))
# Horizontal collider lips form the straight wave channels; extend only outward.
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0))
 if o['1']=='468' and 18195<=x<20685 and '6' not in o.get('57','').split('.'):
  if y<=210:solid_parts.append(box(x-15,-180,x+15,y-.8))
  elif y>240:solid_parts.append(box(x-15,y+.8,x+15,650))
terrain=unary_union(solid_parts).buffer(0)
# Keep native gaps open; no artificial edge is drawn across their mouths.
fill(terrain,602,-1,1)

# Large contiguous plates are clipped to the wall volume. Seams, rivets, vents
# and scorch marks may only exist within this surface, with a 12u edge setback.
structure_stats=[]
def plate_skin(body,gg=(),region='terrain'):
 inner=body.buffer(-11,join_style=2)
 if inner.is_empty:return
 minx,miny,maxx,maxy=body.bounds
 plate_count=0
 for x in np.arange(math.floor(minx/180)*180,maxx,180):
  for y in np.arange(math.floor(miny/120)*120,maxy,120):
   cell=box(x+5,y+5,x+175,y+115).intersection(inner)
   if cell.area<300:continue
   fill(cell,603,-1,2,gg)
   # One outline per coherent plate, not outlines around the original triangles.
   stroke(cell,613,-1,3,1,gg)
   for xx,yy in [(x+14,y+14),(x+166,y+106)]:
    if inner.covers(Point(xx,yy).buffer(3)):
     add(1765,xx,yy,609,-1,5,sx=.28,gg=gg,ldm=True)
   # Recessed cooling slit: all five bars are inside the plate, or none appear.
   vent=box(x+56,y+44,x+124,y+68)
   if cell.covers(vent):
    fill(vent,611,-1,4,gg)
    for yy in [y+49,y+55,y+61]:line(x+61,yy,x+119,yy,2,613,-1,5,gg)
   # A restrained scorch patch originates at a seam, wholly within the metal.
   if int(x/180+y/120)%4==0:
    patch=Polygon([(x+5,y+37),(x+37,y+43),(x+43,y+65),(x+13,y+80),(x+5,y+80)]).intersection(cell)
    fill(patch,619,-1,4,gg,True)
   plate_count+=1
 structure_stats.append({'region':region,'area':body.area,'plates':plate_count,'groups':list(gg)})
plate_skin(terrain)
# Continuous safety lip follows only actual gameplay-facing slope edges.
for edge in terrain_edges:
 stroke(edge,604,-1,6,2.6)
 # A second dark line offset into the body creates the metal's bevel.
 inside=edge.parallel_offset(5,'left').intersection(terrain.buffer(-.3))
 stroke(inside,611,-1,5,2)

# The intro's intersecting chevrons are intentionally shallow teeth on a rail.
# Their exact triangles are retained, and connected at their existing flat base.
for s in shallow:
 shape=Polygon([*s['edge'],s['solid_vertex']]);fill(shape,602,-1,1)
 stroke(LineString(s['edge']),604,-1,6,2)
# Existing straight lips above/below already supply the mounting rail.

# Robot/cube armor uses the true union of occupied cells, separated by move group.
bygroup=defaultdict(list)
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));gg=tuple(groups(o.get('57','')))
 if 20685<=x<22665 and o['1'] in ['211','208','209'] and 6 not in gg:
  bygroup[gg].append(box(x-15,y-15,x+15,y+15))
for gg,parts in bygroup.items():
 body=unary_union(parts).buffer(0);fill(body,602,-1,1,gg);plate_skin(body,gg,'robot')
 stroke(body,604,-1,6,2,gg)
# This existing moving platform carries all of its new plate detail with it.

# UFO machinery is attached to rails behind the route, not new diagonal props.
rect((22680+24640)/2,350,24640-22680,20,602,-3,0)
rect((22680+24640)/2,-50,24640-22680,24,602,-3,0)
line(22680,361,24640,361,2,613,-3,1)
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));gg=groups(o.get('57',''))
 if o['1']=='94' and 22665<=x<END and 6 not in gg:
  # Cables are narrow and muted. They meet the existing hazard assembly center.
  rail=340 if y>140 else -38
  line(x-5,y,x-5,rail,1,601,-3,-1);line(x+5,y,x+5,rail,1,601,-3,-1)
  rect(x,rail,22,7,603,-3,2)
  rect(x,y,29,29,602,-1,1,gg);rect(x,y,21,21,603,-1,2,gg)
  line(x-9,y-9,x+9,y-9,1,613,-1,3,gg)
  for dx in [-7,7]:disc(x+dx,y+6,1.1,609,-1,4,gg,True)

# Match the original outlines to the armor; the edge is now one continuous rim.
OUT=copy.deepcopy(SRC);visual_shader_changes=[]
struct={'1','94','1338','1339','468','211','208','209','693'}
hazards={'8','216','217','458','1717','1718'}
for idx,o in enumerate(OUT):
 x=float(o.get('2',0));oid=o['1']
 if not 16875<=x<END:continue
 if oid in struct|hazards and '6' not in o.get('57','').split('.'):
  before=dict(o);o['21']=str(605 if oid in hazards else 620 if oid in ['1338','1339'] else 602);o['22']=str(620 if oid in ['1338','1339'] else 602);o['24']='-1';o['25']='10' if oid in hazards else '0'
  changes.append({'index':idx,'keys':[k for k in set(o)|set(before) if o.get(k)!=before.get(k)]})
 if oid=='2921' and x==16875:
  visual_shader_changes.append({'index':idx,'original':dict(o)})
  o['176']='0';o['10']='0';o['188']='0'
# Original spike outline, with a fitted solid core; no detached spike glow.
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));oid=o['1'];gg=groups(o.get('57',''))
 if not 16875<=x<END or 6 in gg or oid not in ['216','217','458']:continue
 w,h=(20,20) if oid=='216' else (20,8) if oid=='217' else (8,8)
 tri=Polygon([(-w/2,-h/2-2),(w/2,-h/2-2),(0,h/2-2)])
 tri=affinity.scale(tri,-1 if o.get('4')=='1' else 1,-1 if o.get('5')=='1' else 1,origin=(0,0))
 tri=affinity.rotate(tri,-float(o.get('6',0)),origin=(0,0));tri=affinity.translate(tri,xoff=x,yoff=y)
 fill(tri,603,-1,9,gg)

# Intensity comes from light passing through fixed furnace recesses, with brief
# impacts separated by darker beats. There are no free-floating debris props.
for i,b in enumerate(beats):
 major=i%4==0
 trigger(1006,b['x'],**{'51':606,'45':.008,'46':.035 if major else .01,'47':.22 if major else .13,'7':215 if major else 127,'8':65 if major else 33,'9':14,'52':0})
 trigger(1006,b['x'],**{'51':604,'45':.015,'46':.02,'47':.18,'7':178 if major else 135,'8':111 if major else 96,'9':64,'52':0})
 if major:trigger(1006,b['x'],**{'51':600,'45':.012,'46':.025,'47':.20,'7':33,'8':11,'9':8,'52':0})
for e in visual_shader_changes:
 o=dict(e['original']);o['2']=str(END);o['3']='1410';o['10']='0';o['20']='34';ADDED.append(o)
trigger(1007,START,**{'51':ROOTGROUP,'10':0,'35':1})
trigger(1007,END-90,**{'51':ROOTGROUP,'10':90/468,'35':0})
trigger(1007,END,**{'51':ROOTGROUP,'10':0,'35':0})
head=gdparse.parse_header(H);cs=head.get('kS38','').rstrip('|')
for cid,rgb in colors.items():
 op=0 if cid==620 else 1
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in OUT+ADDED)
(HERE/'structured.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Containment');fields['k48']=('i',str(len(OUT+ADDED)));fields['k1']=('i','0');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - CONTAINMENT.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'modified_original_objects':changes,'visual_trigger_changes':visual_shader_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'structure_stats':structure_stats,'furnace_events':furnace_events,'shallow_intro_preserved':len(shallow)}
(HERE/'structured-manifest.json').write_text(json.dumps(manifest,indent=2))
print({k:manifest[k] for k in ['added_objects','total_objects','groups','shallow_intro_preserved']});print(out)
