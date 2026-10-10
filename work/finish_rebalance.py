"""Spider-only obscuring rails and dim circular reaction switches; no new trim."""
from pathlib import Path
import base64, copy, hashlib, json, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,write_gmd,compress

# Rebuild the second spider's familiar segmented fake shelves against its new
# burst score. The first spider's original artwork is preserved verbatim.
source=(ROOT/'work/nocturne_fakeouts.py').read_text()
source=source[:source.index('# Replace every hidden white toggle orb')]
source=source.replace('nocturne-plan.json','rebalance-plan.json').replace('v8-nocturne-skinned.level','v8-rebalance-skinned.level')
source=source.replace("for s in P['sections']:\n    spider", "for s in P['sections']:\n    if s['name']!='RECALL':continue\n    spider")
ns={'__file__':str(ROOT/'work/finish_rebalance.py')};exec(source,ns)
P,H,O,decoys,art=[ns[k] for k in ('P','H','O','decoys','art')]
_,old=load(str(ROOT/'work/v8-nocturne.level'))
first=next(s for s in P['sections'] if s['name']=='BLIND ELEVATOR')
original=[o for o in old if o.get('20')=='11' and not o.get('57') and first['x0']<=float(o['2'])<first['x1']]
O+=copy.deepcopy(original)
OLD=json.loads((ROOT/'work/nocturne-plan.json').read_text())
P['fakeouts']=[d for d in OLD['fakeouts'] if d['section']=='BLIND ELEVATOR']+decoys
def groups(o):return {int(g) for g in o.get('57','').split('.') if g}
def add_group(o,g):o['57']='.'.join(str(q) for q in sorted(groups(o)|{g}))
def obj(oid,x,y,**props):
    o={'1':str(oid),'2':str(round(x,5)),'3':str(round(y,5)),'64':'1','67':'1','96':'1'}
    o.update({k:str(v) for k,v in props.items()});O.append(o);return o
skins=[]
for o in list(O):
    if o['1']=='1594':
        o.update({'135':'1','507':'1','372':'1'});add_group(o,8520)
        for oid,scale in ((3636,.4),(1764,.45)):
            skins.append(obj(oid,float(o['2']),float(o['3']),**{'32':scale,'21':1004,'22':1004,'121':1,'134':1,'57':o['57'],'24':7,'20':15}))
hidden=[]
for o in O:
    if o.get('135')=='1' and o['1'] not in ('1049','1007','901'):
        add_group(o,8480);hidden.append(o)
obj(1007,0,-630,**{'51':8480,'35':0,'10':0,'20':5})
obj(1007,0,-660,**{'51':8520,'35':.24,'10':0,'20':5})
assert not any(o.get('20')=='14' for o in O)
assert not any(o['1']=='901' for o in O)
ser=lambda o:','.join(f'{k},{v}' for k,v in o.items());raw=';'.join([H]+[ser(o) for o in O])+';'
f=read_gmd(ROOT/'work/rebalance-skinned.gmd')
desc='Rebalanced dark v8 / song 1573528. Earlier first-half gameplay and redesigned skip/glide wave. New second half retained: wider ship, tighter robot, four dash-release-catch sequences. Spider fakes and random wall switches. No coloured trim.'
f.update({'k4':('s',compress(raw)),'k48':('i',str(len(O))),'k3':('s',base64.urlsafe_b64encode(desc.encode()).decode()),'k14':('f',False)})
write_gmd(ROOT/'outputs/v8-1573528-rebalance.gmd',f)
(ROOT/'work/v8-rebalance.level').write_text(raw)
P.update(objects=len(O),decor_inlays=[],decor_fixtures=[],finish_summary=dict(coloured_trim_objects=0,first_spider_art_preserved=len(original),new_second_spider_art=len(art),spider_fakeouts=len(P['fakeouts']),random_decisions=len(P['random_locks']),circular_orb_skins=len(skins),hidden_helpers=len(hidden),normal_size_portals=len(P['portal_passages'])))
(ROOT/'work/rebalance-plan.json').write_text(json.dumps(P,separators=(',',':')))
print(json.dumps(P['finish_summary'],indent=2));print(hashlib.sha256((ROOT/'outputs/v8-1573528-rebalance.gmd').read_bytes()).hexdigest())
