"""Regression checks for factory simplification, exit coverage and editor layers."""
from pathlib import Path
from collections import Counter
import sys,json,hashlib,math
HERE=Path(__file__).parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import gmd,gdparse
H,S=gdparse.load(HERE/'source.level')
h,O=gdparse.load(HERE/'custom-orbs.level')
_,A=gdparse.load(HERE/'atmosphere.level')
_,C=gdparse.load(HERE/'refinery.level')
_,F=gdparse.load(HERE/'foundry.level')
m=json.loads((HERE/'custom-orbs-manifest.json').read_text())
p=ROOT/'outputs/The Sinking Factory - CUSTOM-ORBS.gmd';f=gmd.read_gmd(p)
start,end=m['scope'];new=O[len(S):]
gs=lambda o:set(o.get('57','').split('.'))-{''}
def without(o,keys=('20','61')):return {k:v for k,v in o.items() if k not in keys}
def encode(o):return tuple(sorted(without(o).items()))
assert len(O)==m['total_objects']==int(f['k48'][1])
assert gmd.decompress(f['k4'][1])==(HERE/'custom-orbs.level').read_text()
source_digest=hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest()
assert source_digest==m['source_sha256']=='9429ecc3df11cd6d0aab4b573b4bb0da9560240da78ec92223f2f92436b9386a'
assert f['k2'][1]=='Factory Orbs' and f['k45'][1]=='1569886'

visual=0;shader=0;source_layers=0;outside=0
for i,(a,b) in enumerate(zip(S,O)):
 d={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
 if not start<=float(a.get('2',0))<end:
  assert not d,(i,d);outside+=1;continue
 assert 100<=int(b['20'])<=159 and 90<=int(b['61'])<=95
 source_layers+=1;d-={'20','61'}
 if not d:continue
 if i in m['native_visuals_hidden']:
  assert d<=({'57'} if i!=2462 else {'57'})
 elif a['1']=='2921':assert d<={'176','188','10'};shader+=1
 elif a['1']=='84' and float(a['2'])==22065:assert d=={'57'}
 elif a['1']=='901' and float(a['2'])==22065:assert d=={'51'}
 else:assert d<={'21','22','24','25'},(i,d);visual+=1
legend=[o for o in new if o.get('20')=='99']
assert len(legend)==m['legend_objects']==16
assert all(o.get('61')=='0' and not gs(o) and float(o['3'])>1800 for o in legend)
for o in new:
 assert all(math.isfinite(float(o[k])) for k in ['1','2','3'])
 assert not any(k.startswith('_') for k in o)
 assert o['1'] not in {'1','8','36','84','141','216','217','458','13','660','1334','94','1338','1339'}
 assert all(float(o.get(k,1))>0 for k in ['128','129'])
 assert len(gs(o))<=10
 if o not in legend:
  assert 100<=int(o['20'])<=159 and 90<=int(o['61'])<=95
  assert (int(o['20'])-100)//10==int(o['61'])-90
 if o['1'] in {'1006','1007','901','1346','2921'}:continue
 assert o.get('121')==o.get('134')=='1'
 if o not in legend:assert '600' in gs(o)
assert not {int(o.get('20',0)) for o in S if not start<=float(o.get('2',0))<end}&set(range(90,160))
assert Counter(int(o['20']) for o in O if o.get('20') and 100<=int(o['20'])<=159)==Counter({int(k):v for k,v in m['layer_counts'].items()})

# Editor fields must not change the accepted ship/wave/early robot design.
available=Counter(encode(o) for o in new)
ship=Counter(encode(o) for o in A[len(S):] if o.get('24')=='-1' and 16875<=float(o['2'])<18195)
wave_robot=Counter(encode(o) for o in A[len(S):] if o.get('24')=='-1' and 18195<=float(o['2'])<22020 and '25' not in gs(o))
assert not ship-available
assert not wave_robot-available
# Original source changes are checked against Refined below, including the
# newly authorized spike retints and native-interaction visibility groups.

# The blue orb's follow group cannot contain the ending objects.
blue_i=m['group_fix'][0]['index'];move_i=m['group_fix'][1]['index'];new_g=str(m['isolated_orb_group'])
assert new_g=='1156'
assert without(S[blue_i],('20','61','57'))==without(O[blue_i],('20','61','57'))
assert without(S[move_i],('20','61','51'))==without(O[move_i],('20','61','51'))
assert O[move_i]['51']==new_g and new_g in gs(O[blue_i]) and '24' not in gs(O[blue_i])
assert [i for i,o in enumerate(O[:len(S)]) if new_g in gs(o)]==[blue_i]
assert [o for o in O if o['1']=='901' and o.get('51')==new_g]==[O[move_i]]
assert not [o for o in O if o['1']=='901' and o.get('51')=='24']
later=[i for i,o in enumerate(S) if '24' in gs(o) and float(o['2'])>24660]
assert len(later)==29 and all(S[i]==O[i] for i in later)
assert not [o for o in new if '24' in gs(o)]
assert [without(o) for o in O[:len(S)] if o['1']=='1006' and o.get('51')=='24']==[without(o) for o in S if o['1']=='1006' and o.get('51')=='24']
trim=[o for o in new if new_g in gs(o)]
assert len(trim)==next(e['objects'] for e in m['interaction_frames'] if e['source_index']==blue_i) and all(o['20']=='131' and o['61']=='93' for o in trim)
for o in trim:assert abs(float(o['2'])-22065)<35 and abs(float(o['3'])-75)<35

# Native portal and orb art, hitboxes, and settings remain intact. Every visible
# interaction location has one set of frames, including source moving groups.
ids={'orb':{'36','84','141','1330','1333','1704','1751'},'portal':{'10','11','12','13','47','99','101','111','660','745','1331'},'speed':{'200','201','202','203','1334'}}
expected=set()
for i,o in enumerate(S):
 if not start<=float(o.get('2',0))<end or '6' in gs(o):continue
 for kind,values in ids.items():
  if o['1'] in values:expected.add((kind,float(o['2']),float(o['3'])))
actual={(e['kind'],e['x'],e['y']) for e in m['interaction_frames']}
assert actual==expected
for e in m['interaction_frames']:
 i=e['source_index'];assert without(S[i],('20','61','57'))==without(O[i],('20','61','57'))
 assert e['objects']>0
 if '25' in gs(S[i]):assert 25 in e['groups']

# Exact ash geometry retained; entire clouds stay on their assigned section.
cm=json.loads((HERE/'refinery-manifest.json').read_text())
assert m['ash_groups']==cm['ash_groups'] and m['ash_particles']==cm['ash_particles']
ash_ids={str(e['group']) for e in cm['ash_groups']}
ash=Counter(encode(o) for o in C[len(S):] if gs(o)&ash_ids)
assert not ash-available
for gid in ash_ids:
 members=[o for o in new if gid in gs(o)]
 assert len({o['61'] for o in members})==1,gid

# The missed exit contains two housings and eight blades, all still collidable
# at the original positions/scales. The first left blade was in the old scope.
tail=list(range(2720,2730))
assert Counter(S[i]['1'] for i in tail)=={'94':2,'216':8}
for i in tail:
 assert without(S[i],('20','61','21','22','24','25'))==without(O[i],('20','61','21','22','24','25'))
 assert O[i].get('21')!=S[i].get('21')
 assert O[i]['20']=='150'
tail_skins=[o for o in new if 24660<=float(o['2'])<24820 and o.get('24')=='-1']
assert len(tail_skins)>100
fade=[o for o in new if o['1']=='1007' and o.get('51')=='600' and o.get('35')=='0']
assert sorted(float(o['2']) for o in fade)==[24985,25105]
assert m['removed_hanger_objects']==84 and m['exit_art_objects']==125

# Complete custom replacements: retain active native gameplay, hide only their
# visual appearance, and keep custom skins out of the hidden group.
alpha=str(m['native_alpha_group']);assert alpha=='1157'
assert {i for i,o in enumerate(O[:len(S)]) if alpha in gs(o)}==set(m['native_visuals_hidden'])
assert not [o for o in new if alpha in gs(o)]
assert len([o for o in new if o['1']=='1007' and o.get('51')==alpha and o.get('35')=='0'])==1
assert not [o for o in O if o['1']=='1049' and o.get('51')==alpha]
for i in m['native_visuals_hidden']:
 assert without(F[i],('20','61','57'))==without(O[i],('20','61','57'))
 assert gs(O[i])==gs(F[i])|{alpha}
# F is Foundry; editor organization can differ, so compare gameplay fields
# separately below against Refined for every original object.
_,R=gdparse.load(HERE/'refined.level')
for i,o in enumerate(S):
 allowed={'21','22'} if i in {e['source_index'] for e in m['custom_spikes']} else set()
 if i in m['native_visuals_hidden']:allowed.add('57')
 assert without(R[i],allowed)==without(O[i],allowed),(i,allowed)
expected_spikes={i for i,o in enumerate(S) if start<=float(o['2'])<22665 and o['1'] in {'216','217'} and '6' not in gs(o)}
assert expected_spikes=={e['source_index'] for e in m['custom_spikes']}
assert all(O[i]['21']==O[i]['22']=='620' for i in expected_spikes)
assert all(e['objects']>10 for e in m['custom_spikes'])

# Original channels/settings remain and new channels/groups are isolated.
oldg={g for o in S for g in gs(o)}
assert not oldg&{str(g) for g in range(600,m['groups'][1]+1)}
h0=gdparse.parse_header(H);h1=gdparse.parse_header(h)
assert without(h0,('kS38',))==without(h1,('kS38',))
c0={c['6']:c for c in gdparse.parse_ks38(h0['kS38'])};c1={c['6']:c for c in gdparse.parse_ks38(h1['kS38'])}
assert all(c1[k]==v for k,v in c0.items()) and not set(c0)&set(m['colors'])
assert [without(o) for o in S if o['1']=='2909']==[without(o) for o in O[:len(S)] if o['1']=='2909']
assert m['shallow_intro_preserved']==10
assert sum(o['1']=='31' for o in S)==sum(o['1']=='31' for o in O)

# Exact requested rollback: all portal/speed art and source data match Refined;
# all custom orb artwork matches Custom. Everything else is unchanged.
_,C=gdparse.load(HERE/'custom.level')
cm=json.loads((HERE/'custom-manifest.json').read_text())
rm=json.loads((HERE/'refined-manifest.json').read_text())
def frame_parts(objs,meta):
 art=[o for o in objs[len(S):] if int(o.get('20',0))%10==1 and 100<=int(o.get('20',0))<160]
 assert len(art)==sum(e['objects'] for e in meta['interaction_frames'])
 result={};pos=0
 for e in meta['interaction_frames']:
  result[e['source_index']]=art[pos:pos+e['objects']];pos+=e['objects']
 return result
cf=frame_parts(C,cm);rf=frame_parts(R,rm);nf=frame_parts(O,m)
for frame in m['interaction_frames']:
 idx=frame['source_index']
 assert nf[idx]==(cf[idx] if frame['kind']=='orb' else rf[idx]),idx
portal_ids=ids['portal']|ids['speed']
restored=[i for i,o in enumerate(S) if start<=float(o['2'])<end and o['1'] in portal_ids]
assert all(O[i]==R[i] for i in restored)
assert len(m['native_visuals_hidden'])==8
assert all(S[i]['1'] in ids['orb'] for i in m['native_visuals_hidden'])
remove=Counter(tuple(sorted(o.items())) for e in cm['interaction_frames'] if e['kind']!='orb' for o in cf[e['source_index']])
addback=Counter(tuple(sorted(o.items())) for e in rm['interaction_frames'] if e['kind']!='orb' for o in rf[e['source_index']])
def nonlegend(objs):return Counter(tuple(sorted(o.items())) for o in objs[len(S):] if o.get('20')!='99')
assert nonlegend(C)-remove+addback==nonlegend(O)

v={'passed':True,'source_unchanged':True,'roundtrip_valid':True,'scope':m['scope'],
 'total_objects':len(O),'object_reduction_from_foundry':len(F)-len(O),
 'source_objects_outside_scope_untouched':outside,'source_objects_given_editor_layers':source_layers,
 'factory_objects_organized':m['layer_assignment_count'],'editor_legend_objects':len(legend),
 'source_visual_edits':visual,'visual_shader_resets':shader,'added_collision_objects':0,
 'ship_skin_objects_retained':sum(ship.values()),'wave_early_robot_skin_objects_retained':sum(wave_robot.values()),
 'ash_geometry_objects_retained':sum(ash.values()),'falling_ash_particles':len(m['ash_particles']),
 'interaction_housings':len(actual),'isolated_blue_orb_group':int(new_g),'blue_orb_trim_objects':len(trim),
 'ending_group_24_objects_unchanged':len(later),'ending_group_24_pulse_preserved':True,
 'missed_exit_hazards_finished':len(tail),'root_fade_positions':sorted(float(o['2']) for o in fade),
 'custom_spikes':len(m['custom_spikes']),'native_interactions_visually_hidden':len(m['native_visuals_hidden']),'native_visual_alpha_group':m['native_alpha_group'],'portal_rollback_exact':True,'custom_orbs_retained_exactly':True,'all_other_added_art_unchanged':True,'native_playtest':False,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(HERE/'custom-orbs-validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
