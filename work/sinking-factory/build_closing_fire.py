"""Add a camera-attached closing fire border without modifying existing objects."""
from pathlib import Path
import sys,json,math,random,hashlib,copy
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent/'vendor'))
import numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import triangulate
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gdparse,gmd,render
BASE=ROOT/'outputs/The Sinking Factory - CUSTOM-ORBS.gmd'
fields=gmd.read_gmd(BASE);rawbase=gmd.decompress(fields['k4'][1])
H,SRC=gdparse.load(HERE/'custom-orbs.level')
assert rawbase==(HERE/'custom-orbs.level').read_text()
plan=json.loads((HERE/'custom-orbs-manifest.json').read_text())
schedule=plan['speed_schedule']
def xt(t):return sum(max(0,min(t,schedule[i+1][0] if i+1<len(schedule) else t)-st)*v for i,(st,v) in enumerate(schedule))
def tx(x):
 for i,(t,v) in enumerate(schedule):
  if i+1==len(schedule) or x<xt(schedule[i+1][0]):return t+(x-xt(t))/v
START,END=16785.,24925.
T0=tx(START);TCLOSE=tx(24600);FADE=tx(24795);OFF=tx(END)
CX,CY=17400.,3800.
ROOTGROUP=1200;TARGET=1205
ADDED=[];COLORS={760:(12,4,5),761:(44,8,7),762:(101,17,8),763:(176,37,9),764:(243,104,24),765:(255,174,70),766:(125,32,13),767:(191,66,19)}
BLEND={766:.16,767:.36};records=[];cohorts=[]
def fmt(v):return str(round(v,5)) if isinstance(v,float) else str(v)
def add(oid,x,y,c=760,z=11,order=0,sx=1,sy=None,rot=0,gg=(),layer=160):
 o={'1':str(oid),'2':fmt(x),'3':fmt(y),'21':str(c),'22':str(c),'24':str(z),'25':str(order),
 '128':fmt(sx),'129':fmt(sx if sy is None else sy),'6':fmt(rot),'121':'1','134':'1','64':'1','67':'1','96':'1',
 '20':str(layer),'61':'96','57':'.'.join(map(str,dict.fromkeys([ROOTGROUP,*gg])))}
 ADDED.append(o);return o
def rect(x,y,w,h,c,order,gg,layer=160):return add(211,x,y,c,order=order,sx=w/30,sy=h/30,gg=gg,layer=layer)
def tri(a,b,c,col,order,gg):
 pts=[a,b,c];i=max(range(3),key=lambda i:math.dist(pts[i],pts[(i+1)%3]))
 a,b,c=pts[i],pts[(i+1)%3],pts[(i+2)%3]
 ux,uy=b[0]-a[0],b[1]-a[1];length=math.hypot(ux,uy)
 if length<.001:return
 q=((c[0]-a[0])*ux+(c[1]-a[1])*uy)/(length*length);r=(a[0]+q*ux,a[1]+q*uy)
 for end in [a,b]:
  u=(end[0]-r[0],end[1]-r[1]);v=(c[0]-r[0],c[1]-r[1]);w=math.hypot(*u);h=math.hypot(*v)
  if min(w,h)<.05:continue
  theta=math.atan2(-u[1],-u[0]);dy=(-math.sin(theta),math.cos(theta))
  o=add(693,r[0]+(u[0]+v[0])/2,r[1]+(u[1]+v[1])/2,col,order=order,sx=(w+.5)/30,sy=(h+.5)/30,rot=-math.degrees(theta),gg=gg)
  if v[0]*dy[0]+v[1]*dy[1]<0:o['5']='1'
def fill(shape,c,order,gg):
 if shape.is_empty:return
 if shape.geom_type=='Polygon':
  if shape.area<.15:return
  if len(shape.exterior.coords)==4 and not shape.interiors:tri(*list(shape.exterior.coords)[:3],c,order,gg);return
  for tr in triangulate(shape):
   cut=tr.intersection(shape)
   if cut.area>.15:fill(cut,c,order,gg)
 elif hasattr(shape,'geoms'):
  for part in shape.geoms:fill(part,c,order,gg)
def trigger(oid,x,**kw):
 o={'1':str(oid),'2':fmt(x),'3':str(1440+30*(len(ADDED)%6)),'36':'1','20':'169','61':'96'}
 o.update({k:fmt(v) for k,v in kw.items()});ADDED.append(o);return o

# Native UI coordinates use a 480x320 reference, independently of gameplay zoom.
# Target is not itself a UI object. Explicit edge anchors avoid aspect-ratio gaps.
ref=add(2016,CX,CY,620,z=-5,gg=(TARGET,),layer=169)
ref['57']=str(TARGET);ref['135']='1'
render.SHEETS+=['FireSheet_01'];render.load_atlas()
names=render.load_names(ROOT/'work/handoff/research/objectids.yml')
art_rng=random.Random(9152026)
specs=[('left',1201,3,6,32.,16.,90),('right',1202,4,6,32.,16.,-90),
       ('bottom',1203,2,7,24.,12.,0),('top',1204,2,8,24.,12.,180)]
for edge,g,xref,yref,thick,advance,rot in specs:
 begin=len(ADDED);horizontal=edge in ['top','bottom'];span=1100 if horizontal else 450
 def point(t,u):
  if edge=='left':return CX-240+u,CY+t
  if edge=='right':return CX+240-u,CY+t
  if edge=='bottom':return CX+t,CY-160+u
  return CX+t,CY+160-u
 def profile(t):return thick-7+2.4*math.sin(t*.053+g)+1.7*math.sin(t*.117+g*.31)
 positions=np.arange(-span/2,span/2+1,8)
 # Broad curved red fire bed, scorched outer band and layered inner tongues.
 # No uniform rectangle or opaque fill touches the center of the viewport.
 for off,col,order in [(0,763,0),(-3.8,762,1),(-9.0,761,2),(-15,760,6)]:
  pts=[point(-span/2,-65),point(span/2,-65)]
  pts.extend(point(float(t),profile(float(t))+off) for t in reversed(positions))
  fill(Polygon(pts),col,order,(g,))
 # Native looping fire gives the edge an animated, irregular silhouette.
 flame_count=0
 for k,t in enumerate(np.arange(-span/2+10,span/2-7,18)):
  oid=[923,924,920][k%3];sprite=render.sprite(names[oid]);sw,sh=sprite.width/2,sprite.height/2
  w=art_rng.uniform(17,27);h=art_rng.uniform(23,33)
  base=profile(float(t))-h*.52-1.2
  x,y=point(float(t),base+h/2)
  o=add(oid,x,y,765,order=5,sx=w/sw,sy=h/sh,rot=rot,gg=(g,),layer=161)
  o['22']='764'
  # No identical silhouette/reflection pattern along the four edges.
  if k%3==0:o['4']='1'
  flame_count+=1
 # A sparse soft halo stays close to the flame tips rather than tinting gameplay.
 for t in np.arange(-span/2+35,span/2,70):
  x,y=point(float(t),thick-1)
  add(504,x,y,766,order=-2,sx=1.2 if horizontal else .34,sy=.34 if horizontal else 1.2,gg=(g,),layer=162)
 # Four ember cohorts drift along their edge; the root group closes them inward.
 for cohort in range(4):
  eg=1220+(g-1201)*4+cohort
  n=12 if horizontal else 6
  for j in range(n):
   t=art_rng.uniform(-span/2,span/2);u=art_rng.uniform(thick-4,thick+10)
   x,y=point(t,u)
   o=add(211,x,y,765 if j%4==0 else 767,order=8,sx=art_rng.uniform(.017,.035),sy=art_rng.uniform(.022,.055),rot=art_rng.uniform(-30,30),gg=(g,eg),layer=163)
  # Gentle looping drift is realized as alternating, smooth fixed-duration moves.
  # No random triggers or changes to any gameplay state are introduced.
  for step in range(int((TCLOSE-T0)/2.4)+1):
   a=T0+step*2.4
   if a>=TCLOSE:break
   du=(1 if step%2==0 else -1)*(2+cohort*.4)
   dt=(1 if (step+cohort)%2==0 else -1)*(5+cohort)
   p0=point(0,0);p1=point(dt,du)
   trigger(901,xt(a),**{'51':eg,'28':p1[0]-p0[0],'29':p1[1]-p0[1],'10':min(2.4,TCLOSE-a),'30':13})
  cohorts.append({'edge':edge,'group':eg,'particles':n})
 # UI is applied at load, even though this control is placed near the section.
 trigger(3613,START-120,**{'51':g,'71':TARGET,'385':xref,'386':yref,'387':0,'388':0})
 p0=point(0,0);p1=point(0,advance)
 trigger(901,START,**{'51':g,'28':p1[0]-p0[0],'29':p1[1]-p0[1],'10':TCLOSE-T0,'30':0})
 records.append({'edge':edge,'group':g,'xref':xref,'yref':yref,'span':span,'initial_nominal_thickness':thick,
 'final_nominal_thickness':thick+advance,'advance':advance,'objects':len(ADDED)-begin,'native_flames':flame_count})

# The UI exists at load but is invisible until the factory. The entrance fades
# in, thickness increases continuously, then the entire effect clears at exit.
trigger(1007,0,**{'51':ROOTGROUP,'10':0,'35':0})
trigger(1007,START,**{'51':ROOTGROUP,'10':.7,'35':.94})
trigger(1007,xt(FADE),**{'51':ROOTGROUP,'10':OFF-FADE,'35':0})
trigger(1007,END,**{'51':ROOTGROUP,'10':0,'35':0})
head=gdparse.parse_header(H);cs=head['kS38'].rstrip('|')
for cid,rgb in COLORS.items():
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{BLEND.get(cid,1)}_15_1_18_0_8_1_5_{1 if cid in BLEND else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in SRC+ADDED)
(HERE/'closing-fire.level').write_text(raw)
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Encroached');fields['k48']=('i',str(len(SRC+ADDED)))
out=ROOT/'outputs/The Sinking Factory - CLOSING-FIRE.gmd';gmd.write_gmd(out,fields)
manifest={**plan,'base_gmd':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
 'base_object_count':len(SRC),'total_objects':len(SRC+ADDED),'added_objects':len(SRC+ADDED)-plan['source_objects'],'closing_fire_added_objects':len(ADDED),
 'closing_fire':{'root_group':ROOTGROUP,'camera_reference_group':TARGET,'camera_reference':[CX,CY],
 'ui_reference_size':[480,320],'scope':[START,END],'start_time':T0,'fully_closed_time':TCLOSE,'fade_start_time':FADE,'off_time':OFF,
 'edges':records,'ember_cohorts':cohorts,'editor_section_layer':96,'editor_layers':{'160':'Fire bed','161':'Native animated flames','162':'Heat halo','163':'Embers','169':'Controls and UI reference'},
 'native_verified':False,'research':'research/ui-native-properties.md'}}
(HERE/'closing-fire-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:manifest[k] for k in ['base_object_count','total_objects','closing_fire_added_objects','output_sha256']},indent=2))
print(out)
