"""Check the restored artwork, interactive trim, and group-24 regression."""
from pathlib import Path
from collections import Counter
import sys,json
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gdparse
_,s=gdparse.load(HERE/'source.level')
_,a=gdparse.load(HERE/'atmosphere.level')
_,c=gdparse.load(HERE/'refinery.level')
_,n=gdparse.load(HERE/'foundry.level')
m=json.loads((HERE/'foundry-manifest.json').read_text())
gs=lambda o:set(o.get('57','').split('.'))-set([''])
encode=lambda o:tuple(sorted(o.items()))
available=Counter(encode(o) for o in n[len(s):])

# Restoration means the former native source appearance and all old ship skin
# are present, not merely an approximate recoloring of Cinder's replacement.
ship=Counter(encode(o) for o in a[len(s):] if o.get('24')=='-1' and 16875<=float(o['2'])<18195)
assert not ship-available
for i,o in enumerate(a[:len(s)]):
 if 16875<=float(o.get('2',0))<18195:assert o==n[i]
# Use the accepted Afterburn wave skin: Cinder also included three ship closure
# triangles centered exactly at the ship/wave boundary, removed by the revert.
wave_robot=Counter(encode(o) for o in a[len(s):] if o.get('24')=='-1' and 18195<=float(o['2'])<22020 and '25' not in gs(o))
assert not wave_robot-available

# Exact regression: previously the following orb and 29 later objects shared
# the move target. Now the follow target contains only the orb and its trim.
blue_i=m['group_fix'][0]['index'];move_i=m['group_fix'][1]['index']
new_g=str(m['isolated_orb_group'])
old_members=[i for i,o in enumerate(s) if '24' in gs(o)]
later=[i for i in old_members if float(s[i]['2'])>24660]
assert len(old_members)>1 and len(later)>0
assert s[move_i]['1']=='901' and s[move_i]['51']=='24'
assert s[blue_i]['1']=='84'
assert {k:v for k,v in s[move_i].items() if k!='51'}=={k:v for k,v in n[move_i].items() if k!='51'}
assert {k:v for k,v in s[blue_i].items() if k!='57'}=={k:v for k,v in n[blue_i].items() if k!='57'}
assert n[move_i]['51']==new_g and new_g in gs(n[blue_i]) and '24' not in gs(n[blue_i])
assert [i for i,o in enumerate(n[:len(s)]) if new_g in gs(o)]==[blue_i]
assert [o for o in n if o['1']=='901' and o.get('51')==new_g]==[n[move_i]]
assert not [o for o in n if o['1']=='901' and o.get('51')=='24']
assert all(s[i]==n[i] for i in later)
assert all(s[i]==n[i] for i in range(len(s)) if float(s[i].get('2',0))>=24660)
assert not [o for o in n[len(s):] if '24' in gs(o)]
assert [o for o in n[:len(s)] if o['1']=='1006' and o.get('51')=='24']==[o for o in s if o['1']=='1006' and o.get('51')=='24']

# The blue trim and the original orb must follow the same group. The source
# Move trigger retains duration, dx/dy and both player-lock flags exactly.
trim=[o for o in n[len(s):] if new_g in gs(o)]
blue_frame=next(f for f in m['interaction_frames'] if f['source_index']==blue_i)
assert len(trim)==blue_frame['objects']
assert blue_frame['groups']==[int(new_g)]
for o in trim:
 assert o['121']==o['134']=='1' and '600' in gs(o)
 assert abs(float(o['2'])-22065)<35 and abs(float(o['3'])-75)<35

# Every visible orb/portal/speed location in the decorated interval has one
# matching frame; coincident mode/size portals share a single housing.
ids={'orb':{'36','84','141','1330','1333','1704','1751'},
 'portal':{'10','11','12','13','47','99','101','111','660','745','1331'},
 'speed':{'200','201','202','203','1334'}}
expected=set()
for i,o in enumerate(s):
 if not 16785<=float(o.get('2',0))<24660 or '6' in gs(o):continue
 for kind,values in ids.items():
  if o['1'] in values:expected.add((kind,float(o['2']),float(o['3'])))
actual={(f['kind'],f['x'],f['y']) for f in m['interaction_frames']}
assert actual==expected
for f in m['interaction_frames']:
 i=f['source_index'];o=s[i]
 assert o==n[i] or i==blue_i
 if '25' in gs(o):assert 25 in f['groups']
 assert f['objects']>0

# Ash geometry/control memberships from Cinder are retained; no atmospheric
# change was used as a substitute for the requested machinery detail.
old_m=json.loads((HERE/'refinery-manifest.json').read_text())
assert m['ash_groups']==old_m['ash_groups'] and m['ash_particles']==old_m['ash_particles']
ash_groups={str(e['group']) for e in old_m['ash_groups']}
ash=Counter(encode(o) for o in c[len(s):] if gs(o)&ash_groups)
assert not ash-available

out={'passed':True,'restored_ship_skin_objects':sum(ship.values()),
 'wave_and_earlier_robot_skin_objects_retained':sum(wave_robot.values()),
 'preserved_ash_geometry_objects':sum(ash.values()),'interaction_housings':len(actual),
 'orb_housings':sum(f['kind']=='orb' for f in m['interaction_frames']),
 'mode_portal_housings':sum(f['kind']=='portal' for f in m['interaction_frames']),
 'speed_portal_housings':sum(f['kind']=='speed' for f in m['interaction_frames']),
 'original_group_24_members':len(old_members),'later_objects_removed_from_orb_follow_target':len(later),
 'later_objects_data_unchanged':True,'isolated_blue_orb_group':int(new_g),
 'blue_orb_trim_objects_following_with_orb':len(trim),'orb_follow_settings_preserved':True,
 'ending_group_24_pulse_preserved':True,'native_playtest':False}
(HERE/'foundry-audit.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
