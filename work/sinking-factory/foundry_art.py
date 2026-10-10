"""Restore Afterburn ship; build the press/cube hall and turbine mechanisms."""
code=(HERE/'refinery_art.py').read_text()
code=code[:code.index('# Strengthen local heat contrast')]
code=code.replace('def target(x):return 16875<=x<18195 or 22665<=x<END','def target(x):return 22665<=x<END')
a=code.index('shipbody=terrain.intersection(');b=code.index('# UFO housings',a)
code=code[:a]+code[b:]
exec(compile(code,str(HERE/'refinery_art.py'),'exec'))
restored_base_count=len(ADDED)
colors.update({720:(9,8,11),721:(35,27,28),722:(61,45,39),723:(99,66,46),
 724:(152,97,56),725:(193,95,39),726:(76,31,23),727:(18,13,17),728:(45,37,36),
 729:(119,92,62),730:(241,150,65),731:(97,40,26),732:(22,17,21),733:(45,21,19)})
BLEND.update({730:.32,731:.17})
detail_fixtures=[];interaction_frames=[];skin_records=[]

def bevel_panel(shape,z=-3,order=32,gg=(),face=721):
 fill(shape,720,z,order,gg)
 fill(shape.buffer(-2.7,join_style=2),722,z,order+1,gg)
 face_shape=shape.buffer(-5.2,join_style=2)
 fill(face_shape,face,z,order+2,gg)
 stroke(shape.buffer(-4,join_style=2),723,z,order+3,1,gg)
 return face_shape

def fastener(x,y,r=1.5,z=-3,order=42,gg=()):
 disc(x,y,r+1,720,z,order,gg,True);disc(x,y,r,723,z,order+1,gg,True)
 line(x-r*.55,y,x+r*.55,y,.6,720,z,order+2,gg,True)

def flange(x,y,r,z=-3,gg=()):
 disc(x,y,r+3,720,z,35,gg);disc(x,y,r,722,z,36,gg)
 disc(x,y,r-3,727,z,37,gg);ring(x,y,r-1,1,723,z,38,gg)
 for i in range(6):
  a=i*math.pi/3;fastener(x+(r-1)*math.cos(a),y+(r-1)*math.sin(a),1,z,39,gg)

def pipe_bundle(x,y0,y1,n=5,pitch=13,z=-3):
 # Common collector/manifold at both ends; tubes meet their flanged fittings.
 w=(n-1)*pitch+26
 for y in [y0,y1]:
  rect(x,y,w+8,18,720,z,31);rect(x,y,w,12,722,z,32)
  line(x-w/2+2,y+3,x+w/2-2,y+3,1.6,724,z,33)
  for dx in [-w/2+5,w/2-5]:fastener(x+dx,y,1.6,z,34)
 for j in range(n):
  xx=x+(j-(n-1)/2)*pitch
  line(xx,y0+4,xx,y1-4,10,720,z,28)
  line(xx,y0+4,xx,y1-4,6.5,722 if j%2 else 721,z,29)
  line(xx-2,y0+5,xx-2,y1-5,1.3,723,z,30)
  for y in [y0+13,y1-13]:rect(xx,y,11,4,728,z,34)
 for y in np.arange(y0+50,y1-20,60):
  rect(x,y,w,4,720,z,35)
  for dx in [-w/2+5,w/2-5]:fastener(x+dx,y,1,z,36)

def service_cabinet(x,y,w,h,caption):
 p=box(x-w/2,y-h/2,x+w/2,y+h/2)
 bevel_panel(p,-3,30)
 for xx in [x-w*.26,x+w*.26]:
  door=box(xx-w*.19,y-h*.37,xx+w*.19,y+h*.37)
  bevel_panel(door,-3,35,face=727)
  for yy in np.arange(y+h*.02,y+h*.3,8):
   line(xx-w*.13,yy,xx+w*.13,yy,3,720,-3,39)
   line(xx-w*.13,yy-1.6,xx+w*.13,yy-1.6,.8,722,-3,40)
  rect(xx+w*.09,y-h*.1,3,14,723,-3,40)
  for yy in [y-h*.28,y+h*.28]:fastener(xx-w*.13,yy,1.3,-3,40)
 rect(x,y+h*.43,w-14,12,720,-3,41);label(caption,x,y+h*.43,.13,729,-3)
 ADDED[-1]['25']='44'
 hazard_band(x,y-h*.42,w-12,5,-3)
 detail_fixtures.append({'kind':'switchgear','x':x,'y':y,'w':w,'h':h})

# A connected hydraulic press occupies the empty transition shown in the user's
# screenshot. The sliding collars inherit the source ram's group 25.
for x in [22002,22428]:
 rect(x,290,27,590,720,-3,27);rect(x,290,19,590,721,-3,28)
 for dx,c in [(-7,723),(5,722)]:line(x+dx,-5,x+dx,585,2.2,c,-3,29)
 for yy in np.arange(10,585,14):rect(x+1,yy,8,3,722,-3,30)
 for yy in [22,560]:
  bevel_panel(box(x-22,yy-16,x+22,yy+16),-3,31)
  for dx in [-15,15]:fastener(x+dx,yy,2,-3,36)
 # A slider shoe remains attached to each side of the existing moving press.
 rect(x,422,40,52,720,-3,45,(25,));rect(x,422,32,43,722,-3,46,(25,))
 for dy in [-14,14]:
  rect(x,422+dy,33,5,727,-3,47,(25,));fastener(x-9,422+dy,1.5,-3,48,(25,))
truss((21980,573),(22450,573),42,-3,722)
pipe_bundle(21868,70,366,5,14)
conduit([(21868,366),(21868,552),(22002,552)],15,-3)
conduit([(21868,70),(21868,40),(22002,40)],13,-3)
service_cabinet(21940,271,76,145,'PRESS 04')
conduit([(21940,344),(21940,531),(22002,531)],6,-3)
pipe_bundle(22606,164,371,4,12)
conduit([(22606,371),(22606,447),(22428,447)],13,-3)
for xx,yy in [(21910,369),(22593,401)]:
 flange(xx,yy,14)
 g=group();cg=center(xx,yy)
 for ang in [0,60,120]:
  r=math.radians(ang);line(xx-10*math.cos(r),yy-10*math.sin(r),xx+10*math.cos(r),yy+10*math.sin(r),2.2,724,-3,41,(g,))
 rotate(g,cg,max(START,xx-600),85,3)
 detail_fixtures.append({'kind':'valve','x':xx,'y':yy,'group':g})
detail_fixtures.append({'kind':'press_guide_frame','bounds':[21980,-5,22450,594],'slider_group':25})

# Upgrade the press head and the two-orb cube cabinet while retaining their
# source volume and movement. Other robot and wave skin objects are untouched.
def revising_skin(o):
 x=float(o.get('2',0));gg=groups(o.get('57',''))
 return o.get('24')=='-1' and (25 in gg or 22410<=x<22565)
removed_press=[o for o in ADDED if revising_skin(o)]
ADDED[:]=[o for o in ADDED if not revising_skin(o)]

for body,gg,region in surface_bodies:
 if region!='smelter':continue
 body=body if 25 in gg else body.intersection(box(22410,140,22560,245))
 if body.is_empty:continue
 start=len(ADDED);fill(body,720,-1,0,gg)
 inner=body.buffer(-6,join_style=2);fill(inner,721,-1,1,gg)
 stroke(body.buffer(-2,join_style=2),724,-1,16,1.4,gg)
 stroke(inner.boundary,722,-1,17,3.5,gg)
 xmin,ymin,xmax,ymax=body.bounds
 for xx in np.arange(xmin+8,xmax-10,60):
  for yy in np.arange(ymin+8,ymax-10,60):
   shape=Polygon([(xx,yy+7),(xx+7,yy),(xx+44,yy),(xx+51,yy+7),(xx+51,yy+45),(xx+44,yy+52),(xx+7,yy+52),(xx,yy+45)]).intersection(inner)
   if shape.area<160:continue
   face=bevel_panel(shape,-1,2,gg,face=728)
   # Fine machined ribs, screw recesses and soot accumulate within each panel.
   for dx in [12,21,30,39]:
    stroke(LineString([(xx+dx,yy+11),(xx+dx,yy+40)]).intersection(face),720,-1,8,2,gg)
   for dx,dy in [(8,8),(43,44)]:
    if face.covers(Point(xx+dx,yy+dy).buffer(2)):fastener(xx+dx,yy+dy,1.2,-1,9,gg)
 for yy in np.arange(ymin+13,ymax-5,30):
  line_shape=LineString([(xmin+9,yy),(xmax-9,yy)]).intersection(inner)
  stroke(line_shape,727,-1,12,3,gg)
 # A continuous inset drive channel gives the long moving mass one composition.
 if xmax-xmin>200:
  belt=box(xmin+26,ymin+12,xmax-26,ymin+29).intersection(inner)
  fill(belt,720,-1,18,gg)
  for xx in np.arange(xmin+34,xmax-30,15):
   q=box(xx,ymin+15,xx+7,ymin+25).intersection(belt);fill(q,722,-1,19,gg)
  for xx in [xmin+11,xmax-11]:
   for yy in np.arange(ymin+12,ymax-4,24):
    if inner.covers(Point(xx,yy).buffer(3)):fastener(xx,yy,1.7,-1,20,gg)
 skin_records.append({'kind':'press_head' if 25 in gg else 'cube_cabinet','bounds':list(body.bounds),'groups':list(gg),'objects':len(ADDED)-start})

# Cast, inset teeth replace empty outlines in the press/cube transition.
transition_teeth=[]
for i,o in enumerate(SRC):
 x=float(o.get('2',0));gg=groups(o.get('57',''))
 if o['1']!='216' or not 22020<=x<22665 or 6 in gg:continue
 tri=Polygon([(-14,-14),(14,-14),(0,14)])
 fill(native_shape(o,tri),720,-1,35,gg)
 fill(native_shape(o,Polygon([(-11,-11),(0,12),(0,-10)])),722,-1,36,gg)
 fill(native_shape(o,Polygon([(0,-10),(0,12),(11,-11)])),726,-1,37,gg)
 stroke(native_shape(o,LineString([(-10,-10),(0,11)])),724,-1,38,1.2,gg)
 stroke(native_shape(o,LineString([(-9,-12),(9,-12)])),723,-1,39,2,gg)
 stroke(native_shape(o,LineString([(0,11),(8,-8)])),725,-1,40,.8,gg)
 OUT[i]['21']=OUT[i]['22']='620';transition_teeth.append(i)

# The UFO carriages now connect to actual guide tracks instead of thin hanging
# lines. Foreground teeth remain at their original positions and silhouettes.
for a,b in [(22690,23430),(23460,24105),(24135,24630)]:
 for yy in [360,34]:
  bevel_panel(box(a,yy-12,b,yy+12),-3,30,face=727)
  for xx in np.arange(a+14,b-6,22):rect(xx,yy,9,6,722,-3,35)
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));gg=groups(o.get('57',''))
 if o['1']!='94' or not 22665<=x<END or 6 in gg:continue
 rail=360 if y>150 else 34
 line(x,y,x,rail,11,720,-3,27)
 line(x-2,y,x-2,rail,3,722,-3,28)
 line(x+3,y,x+3,rail,1,723,-3,29)
 bevel_panel(box(x-13,rail-10,x+13,rail+10),-3,36)
 for dx in [-8,8]:fastener(x+dx,rail,1.6,-3,40)
 # Detailed bearing face and three hub teeth sit within the 30-unit collider.
 for r,w,c in [(10,2,720),(8,1,723)]:ring(x,y,r,w,c,-1,20,gg)
 disc(x,y,5.5,727,-1,22,gg)
 for ang in [0,120,240]:
  a=math.radians(ang);line(x+2*math.cos(a),y+2*math.sin(a),x+5*math.cos(a),y+5*math.sin(a),1.4,724,-1,23,gg)
 for dx,dy in [(-10,10),(10,-10)]:fastener(x+dx,y+dy,1.2,-1,24,gg)
 detail_fixtures.append({'kind':'guided_ufo_carriage','x':x,'y':y,'rail_y':rail})

# Distinct equipment fills the spaces between the three large turbine chambers.
for x,y,w,h,title in [(23210,235,115,236,'GENERATOR A'),(23878,237,142,265,'COOLANT'),(24505,215,108,226,'EXHAUST')]:
 service_cabinet(x,y,w,h,title)
 pipe_bundle(x-w*.67,y-h*.34,y+h*.37,3,11)
 conduit([(x-w*.67,y+h*.37),(x-w*.67,430),(x+w*.2,430)],13,-3)
 conduit([(x+w*.36,y-h/2),(x+w*.36,52),(x-w*.45,52)],12,-3,hot=True)
 flange(x+w*.33,y-h*.12,15)
 # Hooded inspection slit, scorching and a riveted heat shield.
 slot=box(x-w*.25,y-h*.17,x+w*.06,y-h*.06)
 fill(slot,720,-3,44);fill(slot.buffer(-3),726,-3,45)
 for xx in np.arange(x-w*.23,x+w*.04,7):rect(xx,y-h*.115,2,h*.045,725,-3,46)
 for yy in [y-h*.30,y+h*.29]:
  for dx in [-w*.4,w*.4]:fastener(x+dx,yy,2,-3,47)

# Secondary turbine casing details: cable looms, paired saddles and restrained
# insulation plates give the large chambers a human-sized construction scale.
for x,y,r in [(22935,255,140),(23535,220,165),(24210,240,152)]:
 for sign in [-1,1]:
  yy=y+sign*(r+15)
  bevel_panel(box(x-r*.52,yy-13,x+r*.52,yy+13),-3,25)
  for xx in np.arange(x-r*.43,x+r*.5,28):fastener(xx,yy,2,-3,32)
 for ang in [35,145,215,325]:
  a=math.radians(ang);xx=x+(r+6)*math.cos(a);yy=y+(r+6)*math.sin(a)
  rect(xx,yy,24,15,720,-3,30,rot=-ang)
  rect(xx,yy,17,9,722,-3,31,rot=-ang);fastener(xx,yy,2,-3,32)
 conduit([(x-r*.6,y+r*.65),(x-r*.6,y+r+34),(x+r*.3,y+r+34)],5,-3)

# Native portals/orbs keep their actual art, dimensions and gameplay data.
# Their frames use measured sprite dimensions; co-located portals share one
# housing, avoiding several nested cages around a single transition.
import render as atlas_render
atlas_render.load_atlas();atlas_names=atlas_render.load_names(ROOT/'work/handoff/research/objectids.yml')
ORB_IDS={'36','84','141','1330','1333','1704','1751'}
PORTAL_IDS={'10','11','12','13','47','99','101','111','660','745','1331'}
SPEED_IDS={'200','201','202','203','1334'}
seen=set()
for idx,o in enumerate(SRC):
 oid=o['1'];x=float(o.get('2',0));y=float(o.get('3',0));gg=groups(o.get('57',''))
 if oid not in ORB_IDS|PORTAL_IDS|SPEED_IDS or not START<=x<END or 6 in gg:continue
 category='orb' if oid in ORB_IDS else 'portal' if oid in PORTAL_IDS else 'speed'
 key=(category,x,y,tuple(gg))
 if key in seen:continue
 seen.add(key);begin=len(ADDED)
 spr=atlas_render.sprite(atlas_names.get(int(oid),''))
 w,h=(spr.width/2,spr.height/2) if spr is not None else ((30,30) if category=='orb' else (40,90))
 sx=float(o.get('128',o.get('32',1)));sy=float(o.get('129',sx))
 def local_shape(shape):return native_shape(o,shape)
 def local_line(a,b,width,c,order):stroke(local_shape(LineString([a,b])),c,-1,order,width,gg)
 if category=='orb':
  r=max(20,min(24,w/2+5))
  # Open bearing ring; the clickable glowing center remains unobstructed.
  for start in [12,132,252]:
   pts=[(r*math.cos(math.radians(a)),r*math.sin(math.radians(a))) for a in np.linspace(start,start+96,13)]
   stroke(local_shape(LineString(pts)),720,-1,25,5,gg)
   stroke(local_shape(LineString(pts)),723,-1,26,1.5,gg)
  for a in [0,120,240]:
   ar=math.radians(a);px=(r+1)*math.cos(ar);py=(r+1)*math.sin(ar)
   p=local_shape(Point(px,py));fastener(p.x,p.y,1.6,-1,28,gg)
   local_line(((r-3)*math.cos(ar),(r-3)*math.sin(ar)),((r+4)*math.cos(ar),(r+4)*math.sin(ar)),3,722,27)
  # Single paired contacts beneath the ring connect the orb to its mounting.
  for dx in [-5,5]:
   local_line((dx,-r-2),(dx,-r-8),2,722,27)
 else:
  rx=w/2+7;ry=h/2+7
  if category=='portal':
   for side in [-1,1]:
    angles=np.linspace(-62,62,17)
    pts=[(side*rx*math.cos(math.radians(a)),ry*math.sin(math.radians(a))) for a in angles]
    stroke(local_shape(LineString(pts)),720,-1,25,7,gg)
    stroke(local_shape(LineString(pts)),722,-1,26,3.8,gg)
    stroke(local_shape(LineString(pts)),724,-1,27,.8,gg)
   for dy in [-ry,ry]:
    shape=local_shape(box(-11,dy-5,11,dy+5));bevel_panel(shape,-1,25,gg)
    p=local_shape(Point(0,dy));fastener(p.x,p.y,1.5,-1,30,gg)
   for side in [-1,1]:
    for dy in [-ry*.46,ry*.46]:
     p=local_shape(Point(side*rx*.89,dy));fastener(p.x,p.y,1.6,-1,29,gg)
  else:
   # Compact roller brackets keep speed arrows distinct from mode portals.
   for dy in [-ry,ry]:
    local_line((-rx*.7,dy),(rx*.7,dy),4,720,25)
    local_line((-rx*.7,dy),(rx*.7,dy),1.3,723,26)
    for dx in [-rx*.7,rx*.7]:
     p=local_shape(Point(dx,dy));fastener(p.x,p.y,1.4,-1,28,gg)
  # Small segmented hot contacts belong to the frame, outside the opening.
  for dy in [-ry,ry]:local_line((-4,dy),(4,dy),1.1,725,32)
 interaction_frames.append({'source_index':idx,'object_id':oid,'kind':category,'x':x,'y':y,'groups':gg,'sprite_size':[w,h],'objects':len(ADDED)-begin})

# The original group 24 combines the following blue orb with 29 later objects.
# Isolate only the orb, its trim and its follow-move trigger. The later group 24
# pulse remains attached to its original objects and preserves the ending.
isolated_orb_group=group();group_fix=[]
blue_indices=[i for i,o in enumerate(SRC) if o['1']=='84' and float(o['2'])==22065 and '24' in o.get('57','').split('.')]
assert len(blue_indices)==1
for idx in blue_indices:
 OUT[idx]['57']='.'.join(str(isolated_orb_group) if g=='24' else g for g in OUT[idx]['57'].split('.'))
 group_fix.append({'index':idx,'property':'57','from':'24','to':str(isolated_orb_group),'kind':'blue_orb'})
for idx,o in enumerate(OUT):
 if o['1']=='901' and float(o.get('2',0))==22065 and o.get('51')=='24':
  o['51']=str(isolated_orb_group)
  group_fix.append({'index':idx,'property':'51','from':'24','to':str(isolated_orb_group),'kind':'orb_follow_move'})
assert len(group_fix)==2
for o in ADDED:
 if '24' in o.get('57','').split('.'):
  o['57']='.'.join(str(isolated_orb_group) if g=='24' else g for g in o['57'].split('.'))
for f in interaction_frames:
 if f['source_index'] in blue_indices:f['groups']=[isolated_orb_group if g==24 else g for g in f['groups']]

changes=[]
for i,(a,b) in enumerate(zip(SRC,OUT)):
 diff=sorted(k for k in set(a)|set(b) if a.get(k)!=b.get(k))
 if diff and a['1']!='2921':changes.append({'index':i,'keys':diff})
head=gdparse.parse_header(H);cs=head.get('kS38','').rstrip('|')
for cid,rgb in colors.items():
 op=0 if cid==620 else BLEND.get(cid,ALPHA.get(cid,1))
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1_5_{1 if cid in BLEND else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in OUT+ADDED)
(HERE/'foundry.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Foundry');fields['k48']=('i',str(len(OUT+ADDED)));fields['k1']=('i','0');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - FOUNDRY.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'modified_original_objects':changes,'visual_trigger_changes':visual_shader_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'fixtures':fixtures,'emitters':emitters,'shallow_intro_preserved':len(shallow),'ash_groups':ash_groups,'ash_particles':ash_particles,'fog_groups':fog_groups,'industrial_additions':industrial_additions,'detail_fixtures':detail_fixtures,'skin_records':skin_records,'interaction_frames':interaction_frames,'group_fix':group_fix,'isolated_orb_group':isolated_orb_group,'ship_restored_from':'AFTERBURN','removed_press_skin_objects':len(removed_press),'new_transition_teeth':len(transition_teeth),'additional_detail_objects':len(ADDED)-restored_base_count+len(removed_press)}
(HERE/'foundry-manifest.json').write_text(json.dumps(manifest,indent=2))
print({k:manifest[k] for k in ['total_objects','groups','additional_detail_objects','new_transition_teeth','isolated_orb_group']});print(out)
