from pathlib import Path
import sys,json,hashlib,collections,math
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'));import gdparse,gmd
original=Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
output=ROOT/'outputs/The Sinking Factory - Flooded Drop.gmd'
manifest=json.loads((HERE/'build-manifest.json').read_text())
sourcefields=gmd.read_gmd(original);fields=gmd.read_gmd(output)
raw=gmd.decompress(fields['k4'][1]);assert raw==(HERE/'decorated.level').read_text()
h0,src=gdparse.load(HERE/'source.level');h1,out=gdparse.load(HERE/'decorated.level')
assert len(out)==int(fields['k48'][1])==manifest['total_objects']
assert hashlib.sha256(original.read_bytes()).hexdigest()==manifest['source_sha256']=='9429ecc3df11cd6d0aab4b573b4bb0da9560240da78ec92223f2f92436b9386a'
assert len(out)>len(src)
changes=[]
for i,(a,b) in enumerate(zip(src,out)):
 different={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
 if different:
  assert 16875<=float(a['2'])<24660,(i,a)
  assert different<={'21','22','24','25'},(i,different)
  changes.append(i)
# All original object IDs, positions, rotations, scales, groups, interaction
# flags, physics properties, and all original triggers are unchanged.
new=out[len(src):];triggers={'1006','1007','901','1346'}
for o in new:
 assert all(math.isfinite(float(o[k])) for k in ['1','2','3'])
 if o['1'] not in triggers:
  assert o.get('121')=='1',o
  assert '600' in o.get('57','').split('.'),o
  assert 16785<=float(o['2'])<=24660,o
 else:
  assert int(o['51'])>=600,o
h0=gdparse.parse_header(h0);h1=gdparse.parse_header(h1)
assert {k:v for k,v in h0.items() if k!='kS38'}=={k:v for k,v in h1.items() if k!='kS38'}
c0={c['6']:c for c in gdparse.parse_ks38(h0['kS38'])};c1={c['6']:c for c in gdparse.parse_ks38(h1['kS38'])}
assert all(c1[k]==v for k,v in c0.items())
used_colors=set(c0)
for o in src:
 for key in ['21','22','23','50']:
  if key in o:used_colors.add(o[key])
 if o['1']=='1006' and o.get('52','0')=='0':used_colors.add(o.get('51','0'))
assert not used_colors & {str(n) for n in range(600,621)}
used_groups=set()
for o in src:
 used_groups.update(o.get('57','').split('.'))
 if o['1'] not in ['1006','899']:
  used_groups.update(o.get(k,'') for k in ['51','71'])
assert not used_groups & {str(n) for n in range(600,650)}
for o in new:
 if o['1']=='1346':
  centers=[c for c in new if o['71'] in c.get('57','').split('.')]
  assert len(centers)==1,(o,len(centers))
  assert o['51'] not in centers[0].get('57','').split('.')
# New master group gates the entire decoration; no new effects reach originals.
gates=sorted([o for o in new if o['1']=='1007' and o['51']=='600'],key=lambda o:float(o['2']))
assert [(float(o['2']),float(o['35'])) for o in gates]==[(0,0),(16785,1),(24510,0),(24660,0)]
# Root visibility guarantee is independent of camera scrolling after the exit.
assert float(gates[-2]['10'])<=150/468+1e-5
assert fields['k45']==sourcefields['k45']
physical_new=sum(o['1'] not in triggers and o.get('121')!='1' for o in new)
summary={'passed':True,'source_untouched':True,'original_objects_preserved':len(src),'original_visual_edits':len(changes),'all_original_gameplay_properties_unchanged':True,'all_original_triggers_unchanged':True,'added_objects':len(new),'new_collidable_objects':physical_new,'new_color_channels':len(c1)-len(c0),'new_motion_triggers':sum(o['1'] in ['901','1346'] for o in new),'measured_music_accents':len(manifest['measured_onsets']),'unique_rotation_centers':True,'new_id_collisions':0,'scope_visibility_gates_valid':True,'gmd_roundtrip_valid':True,'file_bytes':output.stat().st_size,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'native_playtest':'Not performed; native bridge unavailable. Atlas diagnostics do not reproduce native shaders or exact camera tracking.'}
(HERE/'validation.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
