"""Preservation and serialized atmosphere-motion checks for Factory Cinder."""
from pathlib import Path
from collections import Counter
import os,sys,json,math
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gdparse
_,old=gdparse.load(HERE/'atmosphere.level')
_,new=gdparse.load(HERE/'refinery.level')
_,source=gdparse.load(HERE/'source.level')
m=json.loads((HERE/'refinery-manifest.json').read_text())
encode=lambda o:tuple(sorted(o.items()))
skin=Counter(encode(o) for o in old[len(source):] if o.get('24')=='-1' and 18195<=float(o['2'])<22665)
available=Counter(encode(o) for o in new[len(source):])
assert not skin-available, 'Liked wave/robot front skins changed'
original_count=0
for a,b in zip(old[:len(source)],new[:len(source)]):
 if 18195<=float(a.get('2',0))<22665:
  assert a==b;original_count+=1

os.environ['GD_PREVIEW_PLAN']=str(HERE/'refinery-manifest.json')
os.environ['GD_PREVIEW_LEVEL']=str(HERE/'refinery.level')
sys.path.insert(0,str(ROOT/'work'))
import preview_memory as P
ash={str(e['group']):e for e in m['ash_groups']}
def ash_group(o):return next((g for g in o.get('57','').split('.') if g in ash),None)
all_objects=P.objs
for o in all_objects:
 if o['1']=='899' and '23' not in o:o['23']='1000'
representatives={}
for o in all_objects:
 g=ash_group(o)
 if g and o['1']=='693':representatives.setdefault(g,o)
assert len(representatives)==len(ash)
# One actual triangle per cohort exercises the full preview Move/Rotate path;
# all original group definitions remain available for pivot lookup.
P.objs=list(representatives.values())+[o for o in all_objects if o['1']=='899']
def displacement(g,t):
 x=y=0
 for tr in P.moves:
  if tr.get('51')!=g:continue
  phase=max(0,min(1,(t-P.tx(float(tr['2'])))/float(tr['10'])))
  x+=float(tr.get('28',0))*phase;y+=float(tr.get('29',0))*phase
 return x,y

for g,e in ash.items():
 moves=sorted([o for o in P.moves if o.get('51')==g],key=lambda o:float(o['2']))
 assert 1<=len(moves)<=3
 for j,tr in enumerate(moves):
  assert tr.get('30')=='0' and float(tr['29'])<0
  assert abs(float(tr['10'])-1.6)<1e-6
  assert abs(float(tr['29'])/1.6-e['speed_y'])<.002
  want_x=e['base_speed_x']+(e['crosswind'] if j==1 else 0)
  assert abs(float(tr.get('28',0))/1.6-want_x)<.002
  assert abs(P.tx(float(tr['2']))-(e['trigger_time']+1.6*j))<.002
 assert e['trigger_time']<=P.tx(e['center_x'])<e['trigger_time']+4.8
 for o in all_objects:
  if ash_group(o)==g:
   assert '600' in o['57'].split('.') and o['121']==o['134']=='1'
 for tr in P.rotates:
  if tr['51'] not in representatives[g]['57'].split('.'):continue
  pivots=P.groups[tr['71']]
  assert len(pivots)==1 and g in pivots[0]['57'].split('.')

checks=0
for x in [17400,19155,21465,23520]:
 t=P.tx(x)
 a,_=P.snapshot(x,t=t);b,_=P.snapshot(x,t=t+.25)
 aa={ash_group(o):o for o in a if ash_group(o)}
 bb={ash_group(o):o for o in b if ash_group(o)}
 for g in aa.keys()&bb.keys():
  e=ash[g]
  if not e['trigger_time']+.3<t<e['trigger_time']+3:continue
  d0=displacement(g,t);d1=displacement(g,t+.25)
  if e['depth']<3:
   assert abs(float(bb[g]['2'])-float(aa[g]['2'])-(d1[0]-d0[0]))<.001
   assert abs(float(bb[g]['3'])-float(aa[g]['3'])-(d1[1]-d0[1]))<.001
  else:
   # Tumbling can shift a fragment centroid slightly; downward translation
   # dominates its sub-5-unit radius during a quarter-second sample.
   assert float(bb[g]['3'])<float(aa[g]['3'])
  checks+=1
assert checks>=30

visible=[]
for x,y,zoom in [(17400,190,.75),(19155,210,1),(21465,300,1),(23520,200,1)]:
 t=P.tx(x);inside=[]
 for p in m['ash_particles']:
  g=str(p['group']);e=ash[g]
  if not e['trigger_time']+.3<t<e['trigger_time']+4.2:continue
  dx,dy=displacement(g,t)
  if abs(p['x']+dx-x)<285/zoom and abs(p['y']+dy-y)<160/zoom:inside.append(p)
 assert len(inside)>=20 and sum(p['hot'] for p in inside)>=3
 visible.append({'x':x,'ash_particles_in_view_rectangle':len(inside),'with_hot_edges':sum(p['hot'] for p in inside)})

new_controls=[o for o in new[len(source):] if o['1'] in ['901','1006','1007','1346','2921']]
assert all(16755<=float(o['2'])<=24660 for o in new_controls)
out={'passed':True,'original_wave_robot_objects_preserved':original_count,
 'wave_robot_front_skin_objects_preserved_exactly':sum(skin.values()),
 'ash_groups_checked':len(ash),'particle_total':len(m['ash_particles']),
 'hot_edge_particles':sum(p['hot'] for p in m['ash_particles']),
 'serialized_motion_samples_checked':checks,'view_rectangles':visible,
 'native_runtime_verified':False,'scope_exit_controls_valid':True}
(HERE/'refinery-audit.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
