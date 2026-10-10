"""Remove any proposed orb whose wrong-input replay did not prove a trap."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,write_gmd,compress
P=json.loads((ROOT/'work/deception-plan.json').read_text())
checks=json.loads((ROOT/'work/deception-bait-checks.json').read_text())
key=lambda b:(b['section'],b['id'],b['t'])
assert {key(b) for b in checks}=={key(b) for b in P['bait_candidates']}
rejected=[b for b in checks if not b['wrong_hit_collides']]
H,O=load(str(ROOT/'work/v8-deception.level'))
for b in rejected:
    matches=[o for o in O if o['1']==str(b['id']) and o.get('20')=='12' and abs(float(o['2'])-b['x'])<.0001 and abs(float(o['3'])-b['y'])<.0001]
    assert len(matches)==1
    O.remove(matches[0])
P['orbs']=[o for o in P['orbs'] if not(o.get('bait') and any(abs(o['t']-b['t'])<.0001 for b in rejected))]
P['baits']=[b for b in checks if b['wrong_hit_collides']]
P['rejected_baits']=rejected
P['objects']=len(O)
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
raw=';'.join([H]+[serialize(o) for o in O])+';'
out=ROOT/'outputs/v8-1573528-deception.gmd'
fields=read_gmd(out);fields['k4']=('s',compress(raw));fields['k48']=('i',str(len(O)))
write_gmd(out,fields);(ROOT/'work/v8-deception.level').write_text(raw)
(ROOT/'work/deception-plan.json').write_text(json.dumps(P,separators=(',',':')))
print(json.dumps(dict(objects=len(O),retained_baits=len(P['baits']),removed_baits=len(rejected),sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2))
