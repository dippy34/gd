"""Validate replacement export, native preset settings and full-screen closure."""
from pathlib import Path
from collections import Counter
import sys,json,hashlib,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gdparse,gmd
m=json.loads((HERE/'engulfed-manifest.json').read_text());fx=m['engulfed']
out=ROOT/'outputs/The Sinking Factory - ENGULFED.gmd'
base=ROOT/'outputs/The Sinking Factory - CUSTOM-ORBS.gmd'
f,bf=gmd.read_gmd(out),gmd.read_gmd(base)
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert hashfile(base)==m['base_sha256']=='802bc6c3ed846833bac104d893f3002918e3d170db00f80bb2e0ff161643380c'
assert hashfile(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')))==m['source_sha256']=='9429ecc3df11cd6d0aab4b573b4bb0da9560240da78ec92223f2f92436b9386a'
assert hashfile(out)==m['output_sha256']
raw=gmd.decompress(f['k4'][1]);assert raw==(HERE/'engulfed.level').read_text()
assert gmd.decompress(gmd.compress(raw))==raw
h,O=gdparse.load(HERE/'engulfed.level');bh,B=gdparse.load(HERE/'custom-orbs.level')
assert gmd.decompress(bf['k4'][1])==(HERE/'custom-orbs.level').read_text()
assert O[:len(B)]==B and len(B)==m['base_object_count']==57465
A=O[len(B):]
assert len(O)==m['total_objects']==int(f['k48'][1])
assert len(A)==m['engulfed_added_objects']
assert m['source_objects']+m['added_objects']==len(O)
assert f['k2'][1]=='Factory Engulfed' and f['k45']==bf['k45']
assert {k:v for k,v in f.items() if k not in {'k2','k4','k48'}}=={k:v for k,v in bf.items() if k not in {'k2','k4','k48'}}
hh,bb=gdparse.parse_header(h),gdparse.parse_header(bh)
assert {k:v for k,v in hh.items() if k!='kS38'}=={k:v for k,v in bb.items() if k!='kS38'}
c={o['6']:o for o in gdparse.parse_ks38(hh['kS38'])};bc={o['6']:o for o in gdparse.parse_ks38(bb['kS38'])}
assert all(c[k]==v for k,v in bc.items())
newc=set(map(str,range(760,772)))
assert set(c)-set(bc)==newc
assert not any(o.get(k) in newc for o in B for k in ['21','22','23','50'])
gs=lambda o:set(o.get('57','').split('.'))-{''}
bg={g for o in B for g in gs(o)}|{o[k] for o in B for k in ['51','71','395','396'] if k in o}
ag={g for o in A for g in gs(o)}
assert not bg&ag
assert not any(o.get('61')=='96' or 160<=int(o.get('20',0))<=169 for o in B)
controls=[o for o in A if o['1'] in {'901','1007','3613'}]
ref=[o for o in A if o['1']=='2016'];assert len(ref)==1 and gs(ref[0])=={'1205'} and ref[0]['135']=='1'
art=[o for o in A if o not in controls and o not in ref]
for o in A:
 assert o['61']=='96' and o['20'] in fx['editor_layers']
 assert all(math.isfinite(float(o[k])) for k in ['1','2','3'])
 assert all(float(o.get(k,1))>0 for k in ['128','129'])
for o in art:
 assert o['1'] in {'920','923','924','504','211'}  # No procedural triangle fire.
 assert o.get('121')==o.get('134')==o.get('96')=='1'
 assert '1200' in gs(o) and '1205' not in gs(o)
 assert len(gs(o)&{'1201','1202','1203','1204','1210'})==1
for o in controls:
 assert o['51'] in ag and not gs(o)
 if '71' in o:assert o['71']=='1205'
flames=[o for o in art if o['1'] in {'920','923','924'}]
assert len(flames)==len(fx['fire_presets'])
for record in fx['fire_presets']:
 o=A[record['added_index']]
 assert o in flames and str(record['group']) in gs(o)
 assert o['128']==o['129']  # Preset proportions retained.
 assert {'106':o['106'],'107':o['107'],'122':o['122'],'123':o['123'],'126':o['126'],'127':o['127'],'214':o['214']}=={'106':'1','107':'1','122':'1','123':'0','126':'1','127':'1','214':'0'}
 assert '462' not in o  # No fixed-frame animation.
 assert float(o['128'])>1.7

schedule=m['speed_schedule']
def xt(t):return sum(max(0,min(t,schedule[i+1][0] if i+1<len(schedule) else t)-st)*v for i,(st,v) in enumerate(schedule))
def tx(x):
 for i,(t,v) in enumerate(schedule):
  if i+1==len(schedule) or x<xt(schedule[i+1][0]):return t+(x-xt(t))/v
near=lambda a,b:abs(float(a)-float(b))<.00002
ui=[o for o in controls if o['1']=='3613'];assert len(ui)==5
motion_stats={}
for e in fx['edges']:
 g=str(e['group']);ut=[o for o in ui if o['51']==g];assert len(ut)==1
 assert ut[0]['71']=='1205' and int(ut[0]['385'])==e['xref'] and int(ut[0]['386'])==e['yref']
 assert ut[0]['387']==ut[0]['388']=='0'
 mm=sorted([o for o in controls if o['1']=='901' and o['51']==g],key=lambda o:float(o['2']))
 assert len(mm)==4
 total=(0.,0.)
 for i,o in enumerate(mm):
  ta=tx(float(o['2']));tb=ta+float(o['10'])
  assert near(ta,fx['start_time']+e['knots'][i][0]*(fx['fully_engulfed_time']-fx['start_time']))
  assert near(tb,fx['start_time']+e['knots'][i+1][0]*(fx['fully_engulfed_time']-fx['start_time']))
  delta=(e['knots'][i+1][1]-e['knots'][i][1])*e['motion_multiplier']
  expect={'left':(delta,0),'right':(-delta,0),'bottom':(0,delta),'top':(0,-delta)}[e['edge']]
  assert near(o['28'],expect[0]) and near(o['29'],expect[1]) and o['30']=='0'
  total=tuple(a+float(o[k]) for a,k in zip(total,['28','29']))
 assert near(math.hypot(*total),e['final_advance'])
 assert e['start_back_depth']<0 and e['final_back_depth']>160
 motion_stats[e['edge']]={'total_motion':total,'final_opaque_depth':e['final_back_depth']}
take=[o for o in ui if o['51']=='1210'];assert len(take)==1 and take[0]['385']=='2' and take[0]['386']=='6'
alpha=[o for o in controls if o['1']=='1007']
master=sorted([o for o in alpha if o['51']=='1200'],key=lambda o:float(o['2']))
assert len(master)==3 and [float(o['35']) for o in master]==[0,1,0]
assert float(master[0]['2'])==0
assert near(tx(float(master[1]['2'])),fx['start_time']) and float(master[1]['10'])==.5
assert near(tx(float(master[2]['2'])),fx['off_time']) and float(master[2]['10'])==0
ta=sorted([o for o in alpha if o['51']=='1210'],key=lambda o:float(o['2']))
assert len(ta)==2 and [float(o['35']) for o in ta]==[0,1]
assert near(tx(float(ta[1]['2'])),fx['takeover_start_time'])
assert near(tx(float(ta[1]['2']))+float(ta[1]['10']),fx['fully_engulfed_time'])
assert near(fx['off_time']-fx['fully_engulfed_time'],.14)
assert fx['takeover_start_time']<fx['fully_engulfed_time']<fx['off_time']
fullplane=[o for o in art if o['1']=='211' and '1210' in gs(o)]
assert len(fullplane)==1
p=fullplane[0];pw,ph=float(p['128'])*30,float(p['129'])*30
assert [float(p[k]) for k in ['2','3']]==fx['camera_reference']
assert c[p['21']]['7']=='1' and c[p['21']]['5']=='0'
aspects={}
for name,aspect in [('4:3',4/3),('16:9',16/9),('21:9',21/9)]:
 w,h=320*aspect,320
 assert pw>w and ph>h
 assert all(e['span']>w if e['edge'] in ['top','bottom'] else e['span']>h for e in fx['edges'])
 # Top+bottom opaque backs overlap by74 units, independent of aspect ratio.
 depths=sum(e['final_back_depth'] for e in fx['edges'] if e['edge'] in ['top','bottom'])
 assert depths>h
 aspects[name]={'full_coverage':True,'ui_size':[w,h],'vertical_opaque_overlap':depths-h}
result={'passed':True,'roundtrip_valid':True,'base_objects_unchanged':len(B),'source_file_unchanged':True,
 'custom_orbs_original_portals_blue_orb_fix_preserved':True,
 'rejected_closing_fire_effect_removed':True,'new_effect_objects':len(A),'total_objects':len(O),
 'native_preset_flames':len(flames),'uniformly_scaled_presets':True,'randomized_animation_start':True,
 'animation_enabled':True,'added_collision_objects':0,'group_color_collisions':0,
 'motion':motion_stats,'full_coverage':aspects,'full_engulfment_time':fx['fully_engulfed_time'],
 'off_time':fx['off_time'],'effect_layers':dict(Counter(o['20'] for o in A)),
 'native_playtest':False,'sha256':hashfile(out)}
(HERE/'engulfed-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
