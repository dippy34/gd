"""Keep the requested original spider fakeouts, without the old switch skins."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,write_gmd,compress
P=json.loads((ROOT/'work/simple-plan.json').read_text())
H,O=load(str(ROOT/'work/v8-simple-skinned.level'))
_,old=load(str(ROOT/'work/v8-nocturne.level'))
spiders=[s for s in P['sections'] if s['mode']=='spider']
preserved=[o for o in old if o.get('20')=='11' and not o.get('57') and
           any(s['x0']<=float(o['2'])<s['x1'] for s in spiders)]
assert len(preserved)>1000
assert all(o.get('121')=='1' and o.get('134')=='1' for o in preserved)
O+=preserved
raw=';'.join([H]+[','.join(f'{k},{v}' for k,v in o.items()) for o in O])+';'
f=read_gmd(ROOT/'work/simple-skinned.gmd')
f.update({'k4':('s',compress(raw)),'k48':('i',str(len(O)))})
write_gmd(ROOT/'outputs/v8-1573528-simple.gmd',f)
(ROOT/'work/v8-simple.level').write_text(raw)
P['objects']=len(O);P['preserved_spider_art']=len(preserved)
(ROOT/'work/simple-plan.json').write_text(json.dumps(P,separators=(',',':')))
print(json.dumps(dict(objects=len(O),preserved_spider_art=len(preserved),spider_fakeouts=len(P['fakeouts']))))
