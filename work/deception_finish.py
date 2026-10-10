"""Restore only the accepted spider artwork and the dim switch skins."""
from pathlib import Path
from collections import Counter
import base64,hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,write_gmd,compress
P=json.loads((ROOT/'work/deception-plan.json').read_text())
H,O=load(str(ROOT/'work/v8-deception-skinned.level'))
_,old=load(str(ROOT/'work/v8-nocturne.level'))
spiders=[s for s in P['sections'] if s['mode']=='spider']
switch_groups={str(m[key]) for m in P['random_locks'] for key in ('present','absent')}
preserved=[o for o in old if o.get('20')=='11' and
           (any(s['x0']<=float(o['2'])<s['x1'] for s in spiders) or o.get('57') in switch_groups)]
O+=preserved
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
raw=';'.join([H]+[serialize(o) for o in O])+';'
fields=read_gmd(ROOT/'work/deception-skinned.gmd');fields['k4']=('s',compress(raw));fields['k48']=('i',str(len(O)))
fields['k3']=('s',base64.urlsafe_b64encode(b'Song 1573528. Spider linework retained; other rooms use live bait orbs and real blind branches. Dark switches: wall present, hit; no wall, skip.').decode())
out=ROOT/'outputs/v8-1573528-deception.gmd'
write_gmd(out,fields);(ROOT/'work/v8-deception.level').write_text(raw)
P['objects']=len(O);P['preserved_spider_and_switch_art']=len(preserved)
(ROOT/'work/deception-plan.json').write_text(json.dumps(P,separators=(',',':')))
print(json.dumps(dict(objects=len(O),preserved_spider_and_switch_art=len(preserved),sha256=hashlib.sha256(out.read_bytes()).hexdigest()),indent=2))
