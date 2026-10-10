"""Targeted ship/UFO cladding revision; preserve the approved wave and robot."""
base=(HERE/'atmosphere_art.py').read_text()
a=base.index('# Three ash planes.');b=base.index('# Local shadows',a)
base=base[:a]+base[b:]
base=base[:base.rindex("\nhead=gdparse.parse_header(H);cs=")]
exec(compile(base,str(HERE/'atmosphere_art.py'),'exec'))
colors.update({700:(12,13,17),701:(50,49,50),702:(89,80,71),703:(160,114,74),
 704:(29,29,34),705:(69,65,62),706:(20,18,23),707:(113,99,85),
 708:(203,110,53),709:(101,31,20),710:(81,60,48),711:(150,57,28),
 712:(245,140,59),713:(87,73,59),714:(26,20,22),715:(116,59,38),716:(229,168,103)})
ALPHA.update({650:.77,651:.53,652:.16,713:.77,714:.88,710:.64})
colors[652]=(50,31,28)
BLEND.update({711:.48,712:.82,715:.32,716:.63})

def target(x):return 16875<=x<18195 or 22665<=x<END

# Retire the earlier front-facing skins only. Source colliders are in OUT and
# are never removed. The wave/robot objects at x18195..22665 are retained.
removed=[];retained=[]
for o in ADDED:
 x=float(o.get('2',0));z=o.get('24')
 if z=='-1' and target(x):removed.append(o)
 else:retained.append(o)
ADDED[:]=retained
new_skin_start=len(ADDED)

def native_shape(o,shape):
 sx=float(o.get('128',o.get('32',1)));sy=float(o.get('129',sx))
 shape=affinity.scale(shape,(-1 if o.get('4')=='1' else 1)*sx,(-1 if o.get('5')=='1' else 1)*sy,origin=(0,0))
 shape=affinity.rotate(shape,-float(o.get('6',0)),origin=(0,0))
 return affinity.translate(shape,xoff=float(o['2']),yoff=float(o['3']))

def surface_line(body,a,b,w,c,order,gg=()):
 stroke(LineString([a,b]).intersection(body),c,-1,order,w,gg)

shipbody=terrain.intersection(box(16875,-180,18195,650))
fill(shipbody,700,-1,0)
inner=shipbody.buffer(-12,join_style=2)
fill(inner,704,-1,1)

# Large joined steel plates, each recessed behind a heavy rolled edge. Plate
# seams and rib ends are clipped against the real ship wall, not a grid of vents.
for col,xx in enumerate(np.arange(16860,18200,180)):
 for row,yy in enumerate(np.arange(-180,650,110)):
  shape=Polygon([(xx+7,yy+10),(xx+151,yy+10),(xx+173,yy+31),(xx+173,yy+89),(xx+151,yy+105),(xx+7,yy+105)])
  panel=shape.intersection(inner)
  if panel.area<350:continue
  fill(panel,706,-1,2)
  face=panel.buffer(-4,join_style=2)
  fill(face,701 if (row+col)%3 else 704,-1,3)
  # One muted top highlight and a substantial lower shadow establish thickness.
  surface_line(face,(xx+12,yy+98),(xx+159,yy+98),1.5,702,4)
  surface_line(face,(xx+12,yy+17),(xx+159,yy+17),3,700,4)
  for px,py in [(xx+17,yy+24),(xx+155,yy+87)]:
   if face.covers(Point(px,py).buffer(3.2)):
    disc(px,py,3.1,700,-1,7);disc(px,py,1.65,702,-1,8)
    line(px-1,py,px+1,py,.7,700,-1,9)
  # Corrugated reinforcement and a cast identification rib occupy alternate bays.
  if (row+col)%2:
   for rx in np.arange(xx+44,xx+133,18):
    surface_line(face,(rx,yy+30),(rx,yy+77),4,700,5)
    surface_line(face,(rx+2,yy+31),(rx+2,yy+76),1.2,705,6)
  else:
   channel=box(xx+32,yy+44,xx+146,yy+70)
   if face.covers(channel):
    fill(channel,700,-1,5);fill(channel.buffer(-3),706,-1,6)
    for rx in np.arange(xx+40,xx+142,13):rect(rx,yy+56,6,12,705,-1,7)
    line(xx+37,yy+47,xx+141,yy+47,1,709,-1,8)

# Raised perimeter extrusions: nested outlines remain inside the source hull.
for dist,w,c,order in [(3,5,700,10),(7,3.5,702,11),(11,2,706,12),(17,3,705,13),(23,1.1,700,14)]:
 skin=shipbody.buffer(-dist,join_style=2)
 stroke(skin.boundary,c,-1,order,w)

segments_ship=[s for s in segments if 16875<=s['center'][0]<18195]
rail_segments=0
for s in segments_ship:
 a,b=s['edge'];edge=LineString([a,b]);solid=Point(s['solid_vertex'])
 # Signed inward normal is derived from the original triangle's solid vertex.
 dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
 nx,ny=-dy/length,dx/length
 mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
 if (solid.x-mid[0])*nx+(solid.y-mid[1])*ny<0:nx,ny=-nx,-ny
 for dist,width,c,order in [(2,3,701,20),(5,1,707,21),(31,7,700,14),(34,2,702,15)]:
  surface_line(shipbody,(a[0]+nx*dist,a[1]+ny*dist),(b[0]+nx*dist,b[1]+ny*dist),width,c,order)
 for f in [0.25,0.75]:
  px=a[0]+dx*f;py=a[1]+dy*f
  # Rib feet meet the rolled edge and stop within the wall surface.
  surface_line(inner,(px+nx*21,py+ny*21),(px+nx*58,py+ny*58),6,700,16)
  surface_line(inner,(px+nx*23,py+ny*23),(px+nx*55,py+ny*55),2,705,17)
 rail_segments+=1

# A few fitted inspection covers interrupt the metal skin at useful scales.
inspection_covers=[]
for x,y in [(17025,280),(17340,345),(17620,-25),(17895,430),(18040,55)]:
 r=31
 if not inner.covers(Point(x,y).buffer(r+9)):continue
 disc(x,y,r+8,700,-1,25);disc(x,y,r+4,702,-1,26);disc(x,y,r,704,-1,27)
 ring(x,y,r-5,1.5,705,-1,28)
 for j in range(8):
  a=j*math.pi/4;disc(x+(r+3)*math.cos(a),y+(r+3)*math.sin(a),1.7,707,-1,29)
 for dx in [-10,10]:rect(x+dx,y,4,18,700,-1,30)
 rect(x,y,30,5,701,-1,31);line(x-13,y+2,x+13,y+2,1,707,-1,32)
 inspection_covers.append([x,y])

# The existing sloped pit sprites remain native and retain their physical data.
# Their bright yellow fill is replaced with a steel tone and a restrained rim.
for o in OUT:
 x=float(o.get('2',0))
 if 16875<=x<18195 and o['1'] in ['1717','1718']:
  o['21']='702';o['22']='701';o['25']='45'

# UFO housings are compact, chamfered crusher heads; each source block keeps its
# original position, size, groups and suspension cable in the rear plane.
ufo_housings=0;ufo_blades=0
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));gg=groups(o.get('57',''))
 if not 22665<=x<END or 6 in gg:continue
 if o['1']=='94':
  shell=Polygon([(-15,-10),(-10,-15),(10,-15),(15,-10),(15,10),(10,15),(-10,15),(-15,10)])
  fill(native_shape(o,shell),700,-1,10,gg)
  fill(native_shape(o,shell.buffer(-2,join_style=2)),702,-1,11,gg)
  fill(native_shape(o,shell.buffer(-4,join_style=2)),704,-1,12,gg)
  # Bearing block, lower split and paired fasteners replace the glowing square.
  fill(native_shape(o,box(-6,-5,6,6)),700,-1,13,gg)
  fill(native_shape(o,Polygon([(-4,-2),(0,-4),(4,-2),(4,3),(0,5),(-4,3)])),705,-1,14,gg)
  stroke(native_shape(o,LineString([(-9,9),(9,9)])),707,-1,15,1,gg)
  for dx,dy in [(-9,-8),(9,8)]:
   pt=native_shape(o,Point(dx,dy));disc(pt.x,pt.y,1.5,707,-1,16,gg)
  pt=native_shape(o,Point(0,-9));rect(pt.x,pt.y,5,1.3,708,-1,17,gg,rot=float(o.get('6',0)))
  ufo_housings+=1
 if o['1']=='216':
  # Solid chisel: dark back face, bevel, mounting root and worn hot leading edge.
  tri=Polygon([(-14,-14),(14,-14),(0,14)])
  fill(native_shape(o,tri),700,-1,35,gg)
  fill(native_shape(o,Polygon([(-11,-11),(0,12),(0,-10)])),705,-1,36,gg)
  fill(native_shape(o,Polygon([(0,12),(11,-11),(0,-10)])),701,-1,36,gg)
  stroke(native_shape(o,LineString([(-10,-10),(0,11)])),707,-1,37,1.1,gg)
  stroke(native_shape(o,LineString([(0,11),(9,-9)])),702,-1,37,.8,gg)
  fill(native_shape(o,Polygon([(-9,-12),(9,-12),(6,-7),(-6,-7)])),706,-1,38,gg)
  stroke(native_shape(o,LineString([(-7,-10),(7,-10)])),702,-1,39,1.2,gg)
  # Narrow heat residue stays at the mounting joint, not around the whole tooth.
  stroke(native_shape(o,LineString([(-4,-12),(4,-12)])),711,-1,40,1,gg)
  ufo_blades+=1
for o in OUT:
 if 22665<=float(o.get('2',0))<END and o['1'] in ['94','216'] and '6' not in o.get('57','').split('.'):
  o['21']=o['22']='620' # visuals replaced; original collision object retained

# Remove the old halo at each UFO block; it made every housing equally luminous.
old_centers=[(float(o['2']),float(o['3'])) for o in SRC if o['1']=='94' and 22665<=float(o['2'])<END and '6' not in o.get('57','').split('.')]
ADDED[:]=[o for o in ADDED if not (o['1']=='504' and o.get('21')=='630' and o.get('24')=='1' and any(abs(float(o['2'])-x)<=12 and abs(float(o['3'])-y)<=12 for x,y in old_centers))]

# Ash is mostly cooled, irregular carbon flakes. A minority has a hot edge.
# Wind cohorts vary in speed and direction; larger flakes tumble individually.
ash_groups=[];ash_particles=[];rr=random.Random(6132026)
def flake_fill(shape,c,z,order,gg):
 # Triangulate at a larger working scale so the structural filler does not
 # discard sub-unit ash fragments as negligible geometry.
 cx,cy=shape.centroid.coords[0];start=len(ADDED)
 fill(affinity.scale(shape,8,8,origin=(cx,cy)),c,z,order,gg,True)
 for q in ADDED[start:]:
  q['2']=fmt(cx+(float(q['2'])-cx)/8);q['3']=fmt(cy+(float(q['3'])-cy)/8)
  for key in ['128','129']:
   if q['1']=='693':q[key]=fmt(max(.002,(float(q[key])*30-1.2)/8/30+.15/30))
   else:q[key]=fmt(float(q[key])/8)

for cell,x in enumerate(np.arange(16940,24490,300)):
 for layer in range(4):
  count=10 if layer==0 else 14 if layer<3 else 6
  g=group();t0=max(tx(START),tx(x)-1.25);st=xt(t0);duration=4.8
  vy=rr.uniform(27,43) if layer==0 else rr.uniform(40,74) if layer<3 else rr.uniform(65,95)
  vx=rr.uniform(-22,9);elapsed=tx(x)-t0
  z=-3 if layer==0 else 1 if layer<3 else 3
  wind=rr.uniform(-16,20)
  for j in range(count):
   px=min(END-18,max(START+18,x+rr.uniform(-166,166)-vx*elapsed))
   py=rr.uniform(-40,500)+vy*elapsed
   size=rr.uniform(.6,1.3) if layer==0 else rr.uniform(1.2,2.8) if layer<3 else rr.uniform(2.6,4.2)
   hot=rr.random()<.31
   c=710 if layer==0 else 713 if hot else 714 if layer==3 else 710
   # Skewed four/five-sided chip with one chipped corner; no round glow or trail.
   points=[(-.48,-.16),(-.19,-.46),(.40,-.24),(.46,.11),(.02,.40),(-.41,.29)]
   aspect=rr.uniform(.48,1.15)
   shape=Polygon([(px+dx*size*rr.uniform(.8,1.18),py+dy*size*aspect*rr.uniform(.8,1.18)) for dx,dy in points])
   angle=rr.uniform(-180,180);shape=affinity.rotate(shape,angle,origin=(px,py))
   extra=()
   if layer==3:
    spin=group();cg=center(px,py);extra=(spin,)
    # The pivot shares the wind translation, so tumbling doesn't orbit a fixed
    # point after a Move trigger changes the particle's world position.
    ADDED[-1]['57']+='.'+str(g)
    rotate(spin,cg,st,rr.uniform(-190,190),duration)
   # Smaller overlap than structure triangulation keeps chips from ballooning.
   flake_fill(shape,c,z,48,(g,*extra))
   if hot:
    pts=list(shape.exterior.coords);a,b=pts[1],pts[2]
    if size>1.5:
     flake_fill(Polygon([a,b,(px,py)]),711,z,49,(g,*extra))
    line(*a,*b,.65,712 if j%3==0 else 711,z,50,(g,*extra),True)
   ash_particles.append({'group':g,'x':px,'y':py,'hot':hot,'size':size})
  # Three wind stages preserve downward movement while the sideways drift bends.
  for stage in range(3):
   tt=t0+stage*1.6
   if xt(tt)>=END:continue
   linear_move(g,xt(tt),-vy*1.6,1.6,dx=(vx+(wind if stage==1 else 0))*1.6)
  trigger(1007,START-30,**{'51':g,'10':0,'35':0})
  trigger(1007,st,**{'51':g,'10':.3,'35':1})
  if xt(t0+3.0)<END:
   trigger(1007,xt(t0+3.0),**{'51':g,'10':1.4,'35':.18})
  ash_groups.append({'group':g,'center_x':float(x),'trigger_x':st,'trigger_time':t0,'speed_y':-vy,'base_speed_x':vx,'crosswind':wind,'duration':duration,'particle_count':count,'depth':layer})

# Strengthen local heat contrast only in the revised ship/UFO sections.
# The approved wave and robot geometry and material channels remain untouched.
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
(HERE/'refinery.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Cinder');fields['k48']=('i',str(len(OUT+ADDED)));fields['k1']=('i','0');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - CINDER.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'modified_original_objects':changes,'visual_trigger_changes':visual_shader_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'fixtures':fixtures,'emitters':emitters,'shallow_intro_preserved':len(shallow),'ash_groups':ash_groups,'ash_particles':ash_particles,'fog_groups':fog_groups,'industrial_additions':industrial_additions,'removed_old_skin_objects':len(removed),'ufo_housings':ufo_housings,'ufo_blades':ufo_blades,'ship_rail_segments':rail_segments,'inspection_covers':inspection_covers,'preserved_geometry_interval':[18195,22665]}
(HERE/'refinery-manifest.json').write_text(json.dumps(manifest,indent=2))
print({k:manifest[k] for k in ['total_objects','groups','removed_old_skin_objects','ufo_housings','ufo_blades']});print(out)
