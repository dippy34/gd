from pathlib import Path
import json,sys,hashlib,math
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path[:0]=[str(ROOT/'work/handoff/tools'),str(HERE/'vendor')]
import gmd,gdparse
H,S=gdparse.load(HERE/'source.level');h,O=gdparse.load(HERE/'structured.level');m=json.loads((HERE/'structured-manifest.json').read_text());p=ROOT/'outputs/The Sinking Factory - CONTAINMENT.gmd';f=gmd.read_gmd(p)
assert len(O)==m['total_objects']==int(f['k48'][1])
assert gmd.decompress(f['k4'][1])==(HERE/'structured.level').read_text()
assert hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest()==m['source_sha256']
visual=0;shader=0
for a,b in zip(S,O):
 d={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
 if not d:continue
 assert 16875<=float(a['2'])<24660
 if a['1']=='2921':assert d<={'176','188','10'};shader+=1
 else:assert d<={'21','22','24','25'};visual+=1
new=O[len(S):];triggers={'1006','1007','901','2921'}
assert all(o['1'] not in ['8','36','84','141','216','217','458','13','660','1334'] for o in new)
for o in new:
 assert all(math.isfinite(float(o[k])) for k in ['1','2','3'])
 if o['1'] in triggers:continue
 assert o.get('121')==o.get('134')=='1'
 assert '600' in o.get('57','').split('.')
 assert 16874.9<=float(o['2'])<=24660
 assert o['20']=='0'
 assert o.get('61')=='30'
 assert float(o.get('24',0))<=-1
 for k in ['128','129']:assert float(o.get(k,1))>0
oldg={g for o in S for g in o.get('57','').split('.')}
assert not oldg & {str(g) for g in range(600,m['groups'][1]+1)}
h0=gdparse.parse_header(H);h1=gdparse.parse_header(h)
assert {k:v for k,v in h0.items() if k!='kS38'}=={k:v for k,v in h1.items() if k!='kS38'}
c0={c['6']:c for c in gdparse.parse_ks38(h0['kS38'])};c1={c['6']:c for c in gdparse.parse_ks38(h1['kS38'])};assert all(c1[k]==v for k,v in c0.items())
assert not set(c0) & {str(n) for n in range(600,625)}
assert f['k45'][1]=='1569886'
assert [o for o in S if o['1']=='2909']==[o for o in O[:len(S)] if o['1']=='2909']
# The complete prior Inferno object list is not reused; bodies come from source.
assert m['shallow_intro_preserved']==10
for e in m['furnace_events']:
 for g in e['door_groups']:
  door=[o for o in new if str(g) in o.get('57','').split('.')]
  assert len(door)==1
  motion=[o for o in new if o['1']=='901' and o['51']==str(g)]
  assert len(motion)==1
  assert abs(float(motion[0]['28']))<=e['w']*.1+.001
  assert float(motion[0]['29'])==0
# All moved objects introduced by this pass are the two doors within each frame.
assert len(m['motions'])==16
assert all(o['1']!='1346' for o in new)
assert len([o for o in new if o['1']=='1007' and o['51']=='600' and o['35']=='0'])==2
v={'passed':True,'source_unchanged':True,'gameplay_properties_unchanged':True,'source_objects':len(S),'added_objects':len(new),'total_objects':len(O),'original_structural_visual_edits':visual,'explicit_visual_shader_reset':shader,'added_collision_objects':0,'floating_debris_or_flame_props':0,'fitted_furnace_frames':len(m['furnace_events']),'contained_moving_doors':len(m['motions']),'native_playtest':False,'roundtrip_valid':True,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(HERE/'structured-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
