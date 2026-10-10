"""Try each real bait input, then keep only traps that cause a collision."""
from pathlib import Path
import json
import replay_deception as R

ROOT=Path(__file__).resolve().parent.parent
original=list(R.P['controls'])
checks=[]
for bait in R.P['bait_candidates']:
    section=next(s for s in R.P['sections'] if s['name']==bait['section'])
    injected=dict(time=bait['t'],x=bait['x'],kind='orb',mode=section['mode'],orb_id=bait['id'])
    R.P['controls']=sorted(original+[injected],key=lambda e:e['time'])
    result,_=R.replay(section,stop_at=min(section['t1']-.95,bait['t']+1.25))
    collisions={k:v for k,v in result['errors'].items() if k in ('solid collision','spike collision')}
    first={k:v for k,v in result['first'].items() if k in collisions}
    check=dict(bait,wrong_hit_collides=bool(collisions),collision_counts=collisions,first_collision=first)
    checks.append(check)
    print(bait['section'],round(bait['t'],3),bait['id'],'trap' if collisions else 'REMOVE',flush=True)
R.P['controls']=original
(ROOT/'work/deception-bait-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(dict(tested=len(checks),verified_traps=sum(q['wrong_hit_collides'] for q in checks))))
