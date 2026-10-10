"""Check body clearance along each carved branch up to its real solid cap."""
from pathlib import Path
import json
import replay_deception as R

out=[]
for b in R.P['branches']:
    s=next(s for s in R.P['sections'] if s['name']==b['section'])
    radius=3 if b['section']=='FAULTLINE' else 5 if s['mode']=='wave' else 15
    hits=[]
    for dx in range(int(b['length'])+9):
        if b['section']=='PARALLAX':y=b['y']-.6*(dx*dx/120 if dx<60 else dx-30)
        else:y=b['y']+(b['end_y']-b['y'])*dx/b['length']
        x=b['x']+dx
        kinds=[kind for kind,bins in [('solid',R.bybin),('spike',R.spbin)]
               if any(R.overlap(q,x,y,radius) for q in R.nearby(bins,x,radius))]
        if kinds:hits.append((dx,kinds))
    assert hits and hits[0][0]>=b['length']-radius-2
    out.append(dict(section=b['section'],length=b['length'],body_radius=radius,first_collision=hits[0]))
(Path(__file__).resolve().parent/'deception-branch-checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
