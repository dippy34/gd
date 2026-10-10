"""Replace the rejected border with large preset flames and complete engulfment."""
from pathlib import Path
from collections import Counter
import sys, json, math, random, hashlib

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gdparse,gmd,render
BASE=ROOT/'outputs/The Sinking Factory - CUSTOM-ORBS.gmd'
fields=gmd.read_gmd(BASE)
H,SRC=gdparse.load(HERE/'custom-orbs.level')
assert gmd.decompress(fields['k4'][1])==(HERE/'custom-orbs.level').read_text()
plan=json.loads((HERE/'custom-orbs-manifest.json').read_text())
schedule=plan['speed_schedule']
def xt(t):return sum(max(0,min(t,schedule[i+1][0] if i+1<len(schedule) else t)-st)*v for i,(st,v) in enumerate(schedule))
def tx(x):
 for i,(t,v) in enumerate(schedule):
  if i+1==len(schedule) or x<xt(schedule[i+1][0]):return t+(x-xt(t))/v
START,END=16785.,24925.
T0,TEND=tx(START),tx(END)
FULL=TEND-.14
CX,CY=17400.,3800.
MASTER,REFERENCE,TAKEOVER=1200,1205,1210
ADDED=[];fire_records=[];edge_records=[]
rng=random.Random(15092026)
COLORS={
 760:(106,18,5),761:(158,28,5),762:(229,54,5),
 763:(235,66,7),764:(255,129,22),765:(255,206,88),
 766:(250,91,10),767:(144,27,5),768:(255,123,18),
 769:(218,47,5),770:(255,190,54),771:(251,93,10),
}
BLEND={766:.18,768:.12}
render.SHEETS+=['FireSheet_01'];render.load_atlas()
names=render.load_names(ROOT/'work/handoff/research/objectids.yml')
def fmt(x):return str(round(x,6)) if isinstance(x,float) else str(x)
def add(oid,x,y,c=760,c2=None,scale=1,sy=None,rot=0,order=0,group=None,layer=161):
 o={'1':str(oid),'2':fmt(x),'3':fmt(y),'21':str(c),'22':str(c if c2 is None else c2),
    '128':fmt(scale),'129':fmt(scale if sy is None else sy),'6':fmt(rot),
    '24':'11','25':str(order),'121':'1','134':'1','64':'1','67':'1','96':'1',
    '20':str(layer),'61':'96','57':'.'.join(map(str,[MASTER,*([group] if group else [])]))}
 ADDED.append(o);return o
def trigger(oid,x,**kw):
 o={'1':str(oid),'2':fmt(x),'3':str(1440+30*(len(ADDED)%6)),'36':'1','20':'169','61':'96'}
 o.update({k:fmt(v) for k,v in kw.items()});ADDED.append(o);return o
def flame(oid,x,y,scale,edge,fill,rot,order,group,layer=161):
 o=add(oid,x,y,edge,fill,scale,rot=rot,order=order,group=group,layer=layer)
 o.update({'106':'1','107':'1','122':'1','123':'0','126':'1','127':'1','214':'0'})
 if rng.random()<.5:o['4']='1'
 fire_records.append({'added_index':len(ADDED)-1,'id':oid,'group':group,'scale':scale})
 return o

ref=add(2016,CX,CY,620,group=REFERENCE,layer=169)
ref['57']=str(REFERENCE);ref['135']='1';ref['24']='-5'

# Four native UI anchors keep the fire at the screen boundary across zooms.
# Motion increases toward the end; the opening actually disappears this time.
knots=[(0.,0.),(.55,40.),(.84,85.),(.93,150.),(1.,330.)]
specs=[('left',1201,3,6,90,560,1.08),('right',1202,4,6,-90,560,1.04),
       ('bottom',1203,2,7,0,1200,1.),('top',1204,2,8,180,1200,1.)]
for edge,g,xref,yref,rot,span,mult in specs:
 def point(t,u):
  if edge=='left':return CX-240+u,CY+t
  if edge=='right':return CX+240-u,CY+t
  if edge=='bottom':return CX+t,CY-160+u
  return CX+t,CY+160-u
 # These are only the opaque backs, completely offscreen at the start.
 # The entire visible boundary is the unwarped, animated native fire sprite.
 base=-133.
 x,y=point(0,(base-860)/2)
 o=add(211,x,y,760,scale=(span if edge in ['top','bottom'] else base+860)/30,
       sy=(base+860 if edge in ['top','bottom'] else span)/30,group=g,order=-8,layer=160)
 # Broad dark-red flames form the rear front. Wide native preset 920 avoids
 # the old pattern of tiny, individually squashed flames around a rectangle.
 for row,(pitch,lo,hi,normal,c1,c2,order) in enumerate([
       (73,2.45,2.85,-152,761,760,-3),
       (63,2.35,2.78,-135,764,762,1),
       (67,1.78,2.22,-106,765,763,3)]):
  t=-span/2-60+rng.uniform(0,20)
  while t<span/2+65:
   scale=rng.uniform(lo,hi)
   oid=920
   h=render.sprite(names[oid]).height/2*scale
   # Smooth depth differences create an uneven advancing front. Uniform
   # scale preserves each preset's proportions and animation silhouette.
   u=normal+5*math.sin(t*.019+g)+3*math.sin(t*.041+row)+h/2
   x,y=point(t,u)
   flame(oid,x,y,scale,c1,c2,rot,order,g)
   t+=pitch+rng.uniform(-9,11)
 # A few narrow native tongues emerge within the larger fire masses.
 for i,t in enumerate(range(-int(span/2),int(span/2)+1,121)):
  oid=923 if i%2 else 924;scale=rng.uniform(2.65,3.05)
  h=render.sprite(names[oid]).height/2*scale
  x,y=point(t+rng.uniform(-20,20),-126+h/2)
  flame(oid,x,y,scale,765,764,rot,4,g)
 for t in range(-int(span/2),int(span/2)+1,132):
  x,y=point(t,-24)
  add(504,x,y,766,scale=3.4,order=-10,group=g,layer=162)
 trigger(3613,START-120,**{'51':g,'71':REFERENCE,'385':xref,'386':yref,'387':0,'388':0})
 for (qa,da),(qb,db) in zip(knots,knots[1:]):
  ta=T0+qa*(FULL-T0);tb=T0+qb*(FULL-T0)
  p0=point(0,0);p1=point(0,(db-da)*mult)
  trigger(901,xt(ta),**{'51':g,'28':p1[0]-p0[0],'29':p1[1]-p0[1],'10':tb-ta,'30':0})
 edge_records.append({'edge':edge,'group':g,'xref':xref,'yref':yref,'span':span,
                      'start_back_depth':base,'final_back_depth':base+330*mult,
                      'final_advance':330*mult,'knots':knots,'motion_multiplier':mult})

# Finish in moving fire, not in the previous frame or a disappearing border.
# A late crossfade to larger native flames joins the fronts without seams.
# Its opaque red rear plane guarantees full coverage on all supported ratios.
take_start=FULL-.36
add(211,CX,CY,767,scale=1200/30,sy=800/30,order=10,group=TAKEOVER,layer=163)
for row,(positions,normal,lo,hi,c1,c2,order) in enumerate([
     ([-570,-335,-95,155,395,610],-205,7.1,8.0,762,769,11),
     ([-485,-220,40,295,545],-194,6.35,7.3,764,771,12),
     ([-570,-280,15,310,590],-230,5.8,7.,770,764,13)]):
 for t in positions:
  scale=rng.uniform(lo,hi);h=render.sprite(names[920]).height/2*scale
  flame(920,CX+t+rng.uniform(-25,25),CY+normal+h/2,scale,c1,c2,0,order,TAKEOVER,163)
trigger(3613,START-120,**{'51':TAKEOVER,'71':REFERENCE,'385':2,'386':6,'387':0,'388':0})
trigger(1007,0,**{'51':MASTER,'10':0,'35':0})
trigger(1007,0,**{'51':TAKEOVER,'10':0,'35':0})
trigger(1007,START,**{'51':MASTER,'10':.5,'35':1})
trigger(1007,xt(take_start),**{'51':TAKEOVER,'10':FULL-take_start,'35':1})
# Hold the engulfed view until the factory boundary; then cut to the next part.
trigger(1007,END,**{'51':MASTER,'10':0,'35':0})

head=gdparse.parse_header(H);cs=head['kS38'].rstrip('|')
for cid,rgb in COLORS.items():
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{BLEND.get(cid,1)}_15_1_18_0_8_1_5_{1 if cid in BLEND else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in SRC+ADDED)
(HERE/'engulfed.level').write_text(raw)
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Engulfed');fields['k48']=('i',str(len(SRC+ADDED)))
out=ROOT/'outputs/The Sinking Factory - ENGULFED.gmd';gmd.write_gmd(out,fields)
manifest={**plan,'base_gmd':str(BASE),'base_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),
 'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'base_object_count':len(SRC),
 'total_objects':len(SRC+ADDED),'added_objects':len(SRC+ADDED)-plan['source_objects'],'engulfed_added_objects':len(ADDED),
 'engulfed':{'root_group':MASTER,'camera_reference_group':REFERENCE,'camera_reference':[CX,CY],
 'ui_reference_size':[480,320],'scope':[START,END],'start_time':T0,'fully_engulfed_time':FULL,'off_time':TEND,
 'takeover_group':TAKEOVER,'takeover_start_time':take_start,'edges':edge_records,'fire_presets':fire_records,
 'editor_section_layer':96,'editor_layers':{'160':'Opaque fire backs','161':'Native flame fronts','162':'Heat light','163':'Final native fire takeover','169':'Controls and UI reference'},
 'native_verified':False,'reference':'https://www.youtube.com/watch?v=wZbqwUv5NI8&t=400s'}}
(HERE/'engulfed-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'objects':len(SRC+ADDED),'new_effect_objects':len(ADDED),'native_flames':len(fire_records),'sha256':manifest['output_sha256']},indent=2))
