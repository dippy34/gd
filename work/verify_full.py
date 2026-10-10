"""Independent export audit and finite-body checks for the structure revision."""
from pathlib import Path
import json,math,hashlib,base64
from collections import Counter,defaultdict
import check_full_paths as C
ROOT=C.ROOT
f,h,raw,level=C.read(ROOT/'outputs/v8-full.gmd')
objs=[o for _,o in raw];ids=Counter(o['1'] for o in objs)
tok=h.split(',');H=dict(zip(tok[::2],tok[1::2]))
p=json.loads((ROOT/'work/full-plan.json').read_text())
assert not any(c['errors'] for c in C.checks)
assert f['k2']=='v8' and int(f['k45'])==593661 and int(f['k48'])==len(objs)
assert not f.get('k14',False)
assert int(f['k23'])==4 and f['k72']
assert H['kA32']=='1'
assert all(H.get(k,'0')=='0' for k in ['kA2','kA3','kA4','kA8','kA10','kA11','kA22'])
assert level==(ROOT/'work/v8-full.level').read_text()
original=Path(str(next(p for p in Path(__file__).resolve().parents if (p/'inputs/OBSIDIAN-CHOIR.gmd').exists())/'inputs/OBSIDIAN-CHOIR.gmd'))
assert original.read_bytes()==(ROOT/'work/handoff/OBSIDIAN-CHOIR.gmd').read_bytes()
assert set(s['mode'] for s in p['sections'])=={'cube','robot','ship','ball','spider','wave','ufo'}
assert not ids['1933'] and len(p['sections'])==27
assert ids['901']>50 and ids['1346']>10 and not ids['3621']
features=json.loads((ROOT/'work/full-build-metrics.json').read_text())['features']
assert len([e for e in features if e['kind']=='split drop gate'])==5
assert ids['84']==6 and ids['11']==6
deco=lambda o:o.get('121')=='1' and o.get('134')=='1'
allowed={'211','693','3628','3625','1888','1764','580'}
decorations=[o for o in objs if deco(o)]
assert all(o['1'] in allowed for o in decorations)
assert all(deco(o) for o in objs if o['1'] in allowed)
groups=defaultdict(list)
for o in objs:
 for g in o.get('57','').split('.'):
  if g:groups[g].append(o)
for tr in objs:
 if tr['1'] in ['901','1346']:
  assert tr['51'] in groups and all(deco(o) for o in groups[tr['51']])
  assert float(tr['10'])>0
  if tr['1']=='1346':assert len(groups[tr['71']])==1 and groups[tr['71']][0]['1']=='1764'
channels={}
for ch in H['kS38'].split('|'):
 if ch:
  t=ch.split('_');d=dict(zip(t[::2],t[1::2]));assert d['6'] not in channels;channels[d['6']]=d
assert all(channels[o['21']]['5']=='1' for o in decorations if int(o.get('24',0))>=1)
assert all(o.get('135')=='1' for o in objs if o['1'] in ['1','8'])
assert sum(o['1']=='3628' and o.get('20')=='17' for o in objs)==ids['8']==len(p['hazards'])
assert sum(float(o['2']) for o in objs if o['1']=='3600')==round(p['end_x'],5)
assert p['end_time']>240 and ids['3600']==1
mode_ids={'cube':'12','ship':'13','ball':'47','ufo':'111','wave':'660','robot':'745','spider':'1331'}
for i,s in enumerate(p['sections']):
 if i:
  assert any(o['1']==mode_ids[s['mode']] and abs(float(o['2'])-(s['x0']+12))<.001 for o in objs)
  if s['speed_index']!=p['sections'][i-1]['speed_index']:
   assert any(o['1']=={1:'201',2:'202',3:'203'}[s['speed_index']] and abs(float(o['2'])-s['x0'])<.001 for o in objs)
assert p['sections'][3]['mode']=='wave' and p['sections'][3]['speed_index']==2
assert len(set(s['structure_style'] for s in p['sections']))==27
old=json.loads((ROOT/'work/revision-before-structure-pass/full-plan.json').read_text())
old_pairs=Counter(tuple(s['mode'] for s in old['sections'][i:i+3]) for i in range(len(old['sections'])-2))
new_pairs=Counter(tuple(s['mode'] for s in p['sections'][i:i+3]) for i in range(len(p['sections'])-2))
assert max(new_pairs.values())==1

wave=[]
for s in p['sections']:
 if s['mode']!='wave':continue
 ev=[e for e in p['controls'] if e['mode']=='wave' and s['t0']-1e-6<=e['time']<s['t1']]
 variants=[('nominal',None,0)]+[(f'turn-{i}',i,off) for i in range(1,len(ev)) for off in [-.025,.025]]
 minmargin=999
 for name,index,off in variants:
  events=[dict(e,time=e['time']+(off if i==index else 0),event_type='input') for i,e in enumerate(ev)]
  events += [dict(e,event_type='gravity') for e in p['gravity_events'] if e['source']=='portal' and e['section']==s['name']]
  events.sort(key=lambda e:e['time']);ei=0;t=s['t0'];y=max(20,min(280,s['incoming_y']));down=events[0]['down']
  gravity=-1
  while t<s['t1']-1e-7:
   if ei<len(events) and events[ei]['time']<=t+1e-6:
    if events[ei]['event_type']=='gravity':gravity=events[ei]['gravity']
    else:down=events[ei]['down']
    ei+=1;continue
   to=min(t+1/240,s['t1'],events[ei]['time'] if ei<len(events) else math.inf)
   y+=(to-t)*s['speed']*(1 if down else -1)*(-gravity);t=to;x=C.xat(s,t)
   assert not C.solids(x,y,12),('wave wall',s['name'],name,off,t,y)
   assert not C.hazard(x,y,12),('wave hazard',s['name'],name,off,t,y)
   minmargin=min(minmargin,C.clearance(x,y,12))
  if index is None:assert abs(y-s['flight_points'][-1][1])<.002
 wave.append(dict(section=s['name'],variants=len(variants),single_turn_offset_ms=25,minimum_clearance=round(minmargin,3)))
ground_variants=[]
for suffix in ['','--0.025-1','-0.025-1','-0.0-1.03','-0.0-0.97']:
 q=ROOT/f'work/full-path-checks{suffix}.json'
 if not q.exists():continue
 results=json.loads(q.read_text());assert len(results)==27 and not any(c['errors'] for c in results)
 ground_variants.append(q.name)
report=dict(file='v8.gmd',internal_name=f['k2'],seconds=p['end_time'],objects=len(objs),
 high_detail_objects=sum(o.get('103')=='1' for o in objs),black_holes=0,
 modes=sorted(set(s['mode'] for s in p['sections'])),mode_changes=26,previous_mode_changes=45,
 repeated_three_mode_sequences=max(new_pairs.values())-1,structure_styles=[s['structure_style'] for s in p['sections']],
 structural_clusters=len(p['gates']),source_unchanged=True,export_round_trip=True,
 chapters=[c[2] for c in p['chapters']],gravity_looms=len(p['landmarks']),blue_orbs=ids['84'],
 inverted_portals=ids['11'],moving_scenery=len(features),move_triggers=ids['901'],rotate_triggers=ids['1346'],
 motion_targets_only_noncolliding_decoration=True,
 nominal_model_sections=27,ground_model_reports=ground_variants,wave_models=wave,
 limits='Ground physics and flight control models are approximations. These checks do not establish native completion or a rating.',
 native_import_verified=False,native_full_playthrough=False,
 sha256=hashlib.sha256((ROOT/'outputs/v8-full.gmd').read_bytes()).hexdigest())
(ROOT/'outputs/v8-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
