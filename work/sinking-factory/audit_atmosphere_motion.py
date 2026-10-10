"""Check serialized ash motion through the existing trigger preview evaluator."""
from pathlib import Path
import os,sys,json,math
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
os.environ['GD_PREVIEW_PLAN']=str(HERE/'atmosphere-manifest.json')
os.environ['GD_PREVIEW_LEVEL']=str(HERE/'atmosphere.level')
sys.path.insert(0,str(ROOT/'work'))
import preview_memory as P
m=json.loads((HERE/'atmosphere-manifest.json').read_text())
for o in P.objs:
 if o['1']=='899' and '23' not in o:o['23']='1000'
ash={str(e['group']):e for e in m['ash_groups']}
def ash_group(o):return next((g for g in o.get('57','').split('.') if g in ash),None)
all_objs=P.objs
# Restrict visual objects to ashes; retain color/alpha controls for evaluation.
P.objs=[o for o in all_objs if ash_group(o) or o['1'] in ['899','1006','1007','1049']]
samples=[]
for x,cy,zoom in [(17400,190,.75),(19155,210,1),(21465,300,1),(23520,200,1)]:
 t=P.tx(x);before,_=P.snapshot(x,t=t);after,_=P.snapshot(x,t=t+.35)
 a=[o for o in before if ash_group(o)];b=[o for o in after if ash_group(o)]
 assert len(a)==len(b)
 measured=0;inside=0;speeds=set()
 for o,q in zip(a,b):
  g=ash_group(o);e=ash[g];assert g==ash_group(q)
  if e['trigger_time']+.05<t<e['trigger_time']+e['duration']-.40:
   assert abs((float(q['3'])-float(o['3']))-.35*e['speed_y'])<.002
   assert abs((float(q['2'])-float(o['2']))-.35*e['speed_x'])<.002
   if abs(float(o['2'])-x)<285/zoom and abs(float(o['3'])-cy)<160/zoom:
    measured+=1;speeds.add(e['speed_y'])
  if abs(float(o['2'])-x)<285/zoom and abs(float(o['3'])-cy)<160/zoom:inside+=1
 assert measured>=20 and len(speeds)==3
 samples.append({'x':x,'song_time_estimate':round(t,4),'ash_objects_within_view_rectangle':inside,'moving_objects_checked':measured,'fall_speeds':sorted(speeds)})
# Every ash group has a single linear downward move, rather than accumulating
# conflicting moves or stopping while its zone is being traversed.
for g,e in ash.items():
 ts=[o for o in all_objs if o['1']=='901' and o.get('51')==g]
 assert len(ts)==1 and ts[0]['30']=='0' and float(ts[0]['29'])<0
 assert e['trigger_time']<=P.tx(e['center_x'])<e['trigger_time']+e['duration']
# All atmospheric visuals, including front ash flakes, share the exit-fade group.
for o in all_objs:
 if ash_group(o):assert '600' in o['57'].split('.') and o['121']==o['134']=='1'
v={'passed':True,'motion_method':'serialized move triggers evaluated in atlas simulator','native_runtime_verified':False,'groups_checked':len(ash),'samples':samples}
(HERE/'atmosphere-motion-validation.json').write_text(json.dumps(v,indent=2))
print(json.dumps(v,indent=2))
