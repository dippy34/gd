"""Simplified factory composition, complete exit, organized editor layers."""
code=(HERE/'foundry_art.py').read_text()
code=code[:code.rindex('\nchanges=[]')]
# Remove the two additive machinery passes that crowded the route with parallel
# rods, free-standing cupboards, tracks, bearings and repeated mounting plates.
for begin,end in [('# A connected hydraulic press','# Upgrade the press head'),
                  ('# The UFO carriages now connect','# Native portals/orbs')]:
 a=code.index(begin);b=code.index(end,a);code=code[:a]+code[b:]
# Keep group 1156 stable across revisions; the removed valves had consumed four
# group IDs. Never reintroduce the source group-24 following-orb conflict.
code=code.replace('isolated_orb_group=group();group_fix=[]',
 'assert nextgroup<1156\nnextgroup=1155\nisolated_orb_group=group();group_fix=[]')
# Preserve explicit frame membership for editor-layer classification.
code=code.replace("interaction_frames.append({'source_index':idx",
 "for framed_object in ADDED[begin:]:\n  framed_object['_editor_kind']='interaction'\n  framed_object['_editor_section']=str(max(i for i,v in enumerate([START,18195,20685,21800,22665,24600]) if x>=v))\n interaction_frames.append({'source_index':idx")
exec(compile(code,str(HERE/'foundry_art.py'),'exec'))
colors.update({740:(10,10,13),741:(13,16,17),742:(43,38,34),743:(106,79,51),
 744:(153,110,65),745:(8,7,10),746:(213,181,135)})

# Remove the earlier hairline hangers too. These crossed the playable space
# without a clear attachment and visually competed with the actual spikes.
hanger_centers=[(float(o['2']),float(o['3'])) for o in SRC if o['1']=='94' and 22665<=float(o['2'])<END and 6 not in groups(o.get('57',''))]
def old_hanger(o):
 if o['1']!='211' or o.get('24')!='-3':return False
 x=float(o['2']);y=float(o['3']);w=float(o.get('128',1))*30;h=float(o.get('129',1))*30
 for xx,yy in hanger_centers:
  rail=365 if yy>150 else -35
  if abs(x-xx)<.001:
   if o.get('25')=='22' and o.get('21')=='603' and abs(y-(yy+rail)/2)<.001 and abs(h-2)<.001 and abs(w-abs(rail-yy))<.001:return True
   if o.get('25')=='23' and o.get('21')=='636' and abs(y-rail)<.001 and abs(w-24)<.001 and abs(h-8)<.001:return True
 return False
removed_hangers=[o for o in ADDED if old_hanger(o)]
ADDED[:]=[o for o in ADDED if not old_hanger(o)]

# One restrained receiver assembly supports the press head already present in
# the layout. All additions stay on the head rather than filling empty air.
# The early robot, its ladle, and the ship/wave design remain the accepted art.
for x in [22038,22392]:
 for y in [385,462]:
  rect(x,y,12,17,720,-1,21,(25,))
  rect(x,y,7,11,722,-1,22,(25,))
  fastener(x,y,1.6,-1,23,(25,))

# Complete the exit through x24925, where the supplied next section begins.
# The base generator now skins both previously missed UFO housings and all
# eight blades, and the masonry backdrop extends behind them to this boundary.
exit_start=len(ADDED)
for x0,x1,c in [(24660,24750,600),(24750,24840,740),(24840,24925,741)]:
 rect((x0+x1)/2,235,x1-x0,1050,c,-5,-38)
 for row,y in enumerate(range(-80,680,50)):
  for xx in np.arange(x0-35*(row%2),x1,70):
   left=max(x0,xx+2);right=min(x1,xx+67)
   if right>left:rect((left+right)/2,y,right-left,46,601 if c==600 else 740,-5,-37,ldm=True)
# Door lintel and sill terminate the factory room, leaving its opening clear.
for y,w,h in [(408,238,25),(-15,238,18)]:
 rect(24796,y,w,h,611,-3,10);rect(24796,y,w-8,h-7,742,-3,11)
 line(24686,y+h/2-4,24906,y+h/2-4,1.1,743,-3,12)
 for xx in [24700,24892]:fastener(xx,y,1.6,-3,13)
rect(24912,487,25,138,611,-3,10)
rect(24912,487,15,128,742,-3,11)
rect(24800,377,110,20,611,-3,15)
label('FACTORY EXIT',24800,377,.16,744,-3);ADDED[-1]['25']='16'
glow(24735,22,94,657,1,sx=1.35,sy=.55)
exit_art=list(ADDED[exit_start:])
for o in exit_art:o['_editor_section']='5'

# Fade only after the final UFO hazards and the exit have been traversed. The
# former fade ended at x24660 and revealed white before the last two hazards.
for o in ADDED:
 if o['1']=='1007' and o.get('51')=='600' and o.get('35')=='0':
  if abs(float(o['2'])-(END-90))<.01:o['2']=fmt(END+60);o['10']='0.25'
  elif abs(float(o['2'])-END)<.01:o['2']=fmt(END+180)

# Editor L is a precise section/type layer. Editor L2 selects an entire section.
# Render layers, z order, timing and trigger groups do not depend on this map.
section_names=['Ship','Wave','Robot','Press and cube','UFO','Factory exit']
section_starts=[START,18195,20685,21800,22665,24600]
type_names=['Gameplay collision','Portals orbs and frames','Block bodies',
 'Block surface details','Spike and hazard skins','Room background',
 'Machinery and supports','Fire glow and light','Ash smoke and soot','Triggers and pivots']
def section_of(o):
 if '_editor_section' in o:return int(o['_editor_section'])
 x=float(o.get('2',0))
 if '25' in o.get('57','').split('.') or str(isolated_orb_group) in o.get('57','').split('.'):return 3
 # Associate move/rotate/alpha controls with the objects they target. Some ash
 # controls sit early in the level, well before their actual visual section.
 if o['1'] in ['901','1346','1007'] and o.get('51') in target_sections:return target_sections[o['51']]
 for gid in o.get('57','').split('.'):
  if gid in ash_ids|fog_ids:return target_sections[gid]
 for gid in reversed(o.get('57','').split('.')):
  if gid in target_sections:return target_sections[gid]
 return max(i for i,v in enumerate(section_starts) if x>=v) if x>=START else 0

ash_ids={str(e['group']) for e in ash_groups}
fog_ids={str(e['group']) for e in fog_groups}
target_sections={}
for e in ash_groups:
 target_sections[str(e['group'])]=max(i for i,v in enumerate(section_starts) if e['center_x']>=v)
for e in fog_groups:
 if 'x' in e:target_sections[str(e['group'])]=max(i for i,v in enumerate(section_starts) if e['x']>=v)
for e in motions:
 if str(e['group']) not in target_sections:
  owners=[o for o in ADDED if str(e['group']) in o.get('57','').split('.')]
  if owners:
   x=sum(float(o['2']) for o in owners)/len(owners)
   target_sections[str(e['group'])]=max(i for i,v in enumerate(section_starts) if x>=v) if x>=START else 0
   parents={gid for o in owners for gid in o.get('57','').split('.') if gid in ash_ids|fog_ids}
   if len(parents)==1:target_sections[str(e['group'])]=target_sections[parents.pop()]
 if 'center' in e:target_sections[str(e['center'])]=target_sections[str(e['group'])]
target_sections['25']=3;target_sections[str(isolated_orb_group)]=3

names=atlas_names
TRIGGERS={'899','901','1006','1007','1049','1346','1520','1616','1811','1812','1814','1815','1816','1817','1912','1913','1914','1934','2067','2068','2909','2911','2921'}
def is_trigger(o):return o['1'] in TRIGGERS or names.get(int(o['1']),'').startswith('edit_') or o['1']=='31'
def classify(o,original=False):
 oid=o['1'];gg=set(o.get('57','').split('.'));cid=int(o.get('21',0));z=int(o.get('24',0));order=float(o.get('25',0))
 if is_trigger(o) or (oid=='1764' and cid==620):return 9
 if oid in ORB_IDS|PORTAL_IDS|SPEED_IDS or o.get('_editor_kind')=='interaction':return 1
 if original:return 0
 if gg&ash_ids or gg&fog_ids or cid in [634,650,651,652]:return 8
 if oid in ['920','923','924','1937','504','1011'] or (z!=-1 and cid in [607,615,616,621,630,631,632,633,638,639,640,641,657,664,665]):return 7
 if z==-1:
  if 35<=order<=45:return 4
  if order<=1:return 2
  return 3
 if z<=-5:return 5
 return 6

layer_counts=Counter();section_counts=Counter();assignments=[]
for idx,o in enumerate(OUT+ADDED):
 original=idx<len(OUT)
 if original and not START<=float(o.get('2',0))<END:continue
 sec=section_of(o);kind=classify(o,original)
 primary=100+sec*10+kind;secondary=90+sec
 o['20']=str(primary);o['61']=str(secondary)
 layer_counts[primary]+=1;section_counts[secondary]+=1
 assignments.append({'index':idx,'layer':primary,'section_layer':secondary})

# An actual editor-only-position legend sits above the play area on layer 99.
# It has no trigger group and cannot disappear when a section preview fades.
legend_start=len(ADDED)
rect(17300,2200,1010,760,745,-5,-50)
legend_lines=['FACTORY REFINED - EDITOR LAYERS','99 THIS GUIDE   /   ALL TO VIEW EVERYTHING',
 '90 SHIP    91 WAVE    92 ROBOT','93 PRESS-CUBE    94 UFO    95 EXIT',
 '100-109 SHIP       110-119 WAVE','120-129 ROBOT      130-139 PRESS-CUBE',
 '140-149 UFO        150-159 EXIT','LAST DIGIT SELECTS OBJECT TYPE:',
 '0 COLLISION       1 PORTALS - ORBS - FRAMES','2 BLOCK BODIES    3 BLOCK DETAILS',
 '4 SPIKE SKINS     5 ROOM BACKGROUND','6 MACHINERY       7 FIRE - GLOW',
 '8 ASH - SMOKE     9 TRIGGERS - PIVOTS','BLUE FOLLOW ORB = GROUP 1156',
 'GROUP 24 AT THE END IS KEPT SEPARATE']
for i,line_text in enumerate(legend_lines):
 label(line_text,17300,2530-i*45,.3 if i else .43,746,-3)
for o in ADDED[legend_start:]:
 o['20']='99';o['61']='0';o.pop('57',None);o['_editor_kind']='legend'

# Drop authoring tags before serialization. These are not GD object properties.
for o in OUT+ADDED:
 for k in list(o):
  if k.startswith('_editor_'):del o[k]
changes=[]
for i,(a,b) in enumerate(zip(SRC,OUT)):
 diff=sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k))
 if diff:changes.append({'index':i,'keys':diff})
head=gdparse.parse_header(H);cs=head.get('kS38','').rstrip('|')
for cid,rgb in colors.items():
 op=0 if cid==620 else BLEND.get(cid,ALPHA.get(cid,1))
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1_5_{1 if cid in BLEND else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in OUT+ADDED)
(HERE/'refined.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Refined');fields['k48']=('i',str(len(OUT+ADDED)));fields['k1']=('i','0');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - REFINED.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'previous_scope_end':24660,'modified_original_objects':changes,'visual_trigger_changes':visual_shader_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'fixtures':fixtures,'emitters':emitters,'shallow_intro_preserved':len(shallow),'ash_groups':ash_groups,'ash_particles':ash_particles,'fog_groups':fog_groups,'industrial_additions':industrial_additions,'skin_records':skin_records,'interaction_frames':interaction_frames,'group_fix':group_fix,'isolated_orb_group':isolated_orb_group,'removed_hanger_objects':len(removed_hangers),'exit_art_objects':len(exit_art),'legend_objects':len(ADDED)-legend_start,'section_names':section_names,'type_names':type_names,'layer_counts':dict(layer_counts),'section_counts':dict(section_counts),'layer_assignment_count':len(assignments),'source_layer_edits':[i for i in range(len(SRC)) if SRC[i].get('20')!=OUT[i].get('20') or SRC[i].get('61')!=OUT[i].get('61')]}
(HERE/'refined-manifest.json').write_text(json.dumps(manifest,indent=2))
print({k:manifest[k] for k in ['total_objects','scope','removed_hanger_objects','exit_art_objects','layer_assignment_count']});print(out)
