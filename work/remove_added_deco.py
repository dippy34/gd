"""Remove only the coloured decoration introduced in the restored revision."""
from pathlib import Path
from collections import Counter
import base64,hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load,parse_header,parse_ks38
from gmd import read_gmd,write_gmd,compress

P=json.loads((ROOT/'work/restored-plan.json').read_text())
H,O=load(str(ROOT/'work/v8-restored.level'))
motion_groups={q['group'] for q in P['decor_fixtures']}
removed=[o for o in O if o.get('20')=='14' or (o['1']=='901' and int(o.get('51',0)) in motion_groups)]
for o in removed:
    assert (o['1'] in ('211','1764') and o.get('121')=='1' and o.get('134')=='1') or (o['1']=='901' and int(o['51']) in motion_groups)
kept=[o for o in O if o not in removed]
sig=lambda seq:Counter(tuple(sorted(o.items())) for o in seq)
physical=lambda o:o.get('121')!='1' and o['1']!='901'
assert sig(o for o in O if physical(o))==sig(o for o in kept if physical(o))
assert sig(o for o in O if o.get('20')=='11')==sig(o for o in kept if o.get('20')=='11')
assert sig(o for o in O if o.get('20')=='15')==sig(o for o in kept if o.get('20')=='15')
header=parse_header(H);channels=parse_ks38(header['kS38'])
channels=[c for c in channels if int(c['6']) not in (14,15,16,17)]
for c in channels:
    if c['6']=='7':c.update({'1':'19','2':'22','3':'14'})
header['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels)+'|'
assert not any(o.get('21') in ('14','15','16','17') for o in kept)
ser=lambda o:','.join(f'{k},{v}' for k,v in o.items())
raw=';'.join([ser(header)]+[ser(o) for o in kept])+';'
f=read_gmd(ROOT/'outputs/v8-1573528-restored.gmd')
f.update({'k4':('s',compress(raw)),'k48':('i',str(len(kept))),
          'k3':('s',base64.urlsafe_b64encode(b'DARK v8: added coloured decoration removed. Spider crossing lines, circular random wall-toggle orbs and normal-size portal display retained. Song 1573528.').decode())})
out=ROOT/'outputs/v8-1573528-dark.gmd';write_gmd(out,f)
(ROOT/'work/v8-dark.level').write_text(raw)
P['objects']=len(kept);P['decor_inlays']=[];P['decor_fixtures']=[];P['moves']=[]
P['removed_added_deco']=len(removed)
P['restore_summary'].update(inlays=0,moving_inlays=0)
(ROOT/'work/dark-plan.json').write_text(json.dumps(P,separators=(',',':')))
V=dict(file=out.name,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),objects=len(kept),
       removed_decor_objects=sum(o['1']!='901' for o in removed),removed_move_triggers=sum(o['1']=='901' for o in removed),
       all_gameplay_objects_unchanged=True,spider_fakeout_art_unchanged=True,wall_orbs_unchanged=True,
       portal_fixes_unchanged=True,new_coloured_channels_removed=True,
       native_import_verified=False,full_native_completion_verified=False)
(ROOT/'outputs/v8-1573528-dark-validation.json').write_text(json.dumps(V,indent=2)+'\n')
print(json.dumps(V,indent=2))
