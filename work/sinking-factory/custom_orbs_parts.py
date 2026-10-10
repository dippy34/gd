"""Fitted steel teeth and fully custom interactive artwork."""
colors.update({750:(22,23,27),751:(68,65,64),752:(112,102,89),753:(173,135,91),
 754:(230,159,68),755:(161,87,139),756:(84,159,172),757:(205,83,43),758:(106,158,108)})
def tightfill(shape,c,z,order,gg=()):
 begin=len(ADDED);fill(shape,c,z,order,gg)
 # A narrow overlap closes sprite sampling seams without the broad padding
 # used on large structural wall surfaces.
 for q in ADDED[begin:]:
  if q['1']=='693':
   for k in ['128','129']:q[k]=fmt(max(.001,float(q[k])-.8/30))

custom_spikes=[]
for idx,o in enumerate(SRC):
 x=float(o.get('2',0));gg=groups(o.get('57',''))
 # Preserve the approved UFO crusher blades; finish all other full and short
 # teeth, including both screenshot rows and the early short spike type.
 if o['1'] not in ['216','217'] or not START<=x<22665 or 6 in gg:continue
 begin=len(ADDED);half=14.4 if o['1']=='216' else 6.15
 def tf(points,c,order):tightfill(native_shape(o,Polygon(points)),c,-1,order,gg)
 def sl(points,c,width,order):stroke(native_shape(o,LineString(points)),c,-1,order,width,gg)
 tf([(-14.4,-half),(14.4,-half),(0,half)],750,41)
 tf([(-12,-half+1.8),(0,half-1),(0,-half+3)],752,42)
 tf([(0,half-1),(12,-half+1.8),(0,-half+3)],751,42)
 tf([(-9,-half+2),(9,-half+2),(6,-half+5),(-6,-half+5)],720,43)
 sl([(-10,-half+2),(0,half-2)],753,.9,44)
 sl([(0,half-2),(0,-half+5)],750,.7,44)
 sl([(-7,-half+3),(7,-half+3)],752,1,45)
 for dx in [-5,5]:
  pt=native_shape(o,Point(dx,-half+3));disc(pt.x,pt.y,.8,753,-1,46,gg)
 OUT[idx]['21']=OUT[idx]['22']='620'
 sec=max(i for i,v in enumerate([START,18195,20685,21800,22665,24600]) if x>=v)
 if 25 in gg:sec=3
 for q in ADDED[begin:]:q['_editor_kind']='hazard';q['_editor_section']=str(sec)
 custom_spikes.append({'source_index':idx,'id':o['1'],'objects':len(ADDED)-begin,'section':sec})

# Retire the previous decorative frames; a complete replacement is built once
# per native interaction location, including co-located mode/size portals.
old_frames=list(interaction_frames)
frame_objects=[o for o in ADDED if o.get('_editor_kind')=='interaction']
cursor=0
for frame in old_frames:
 for q in frame_objects[cursor:cursor+frame['objects']]:q['_editor_category']=frame['kind']
 cursor+=frame['objects']
assert cursor==len(frame_objects)
custom_frames_removed=sum(o.get('_editor_category')=='orb' for o in ADDED)
ADDED[:]=[o for o in ADDED if o.get('_editor_category')!='orb']
interaction_frames=[f for f in old_frames if f['kind']!='orb']
native_visuals_hidden=[];seen=set()
native_alpha=group();assert native_alpha==1157
trigger(1007,START-100,**{'51':native_alpha,'10':0,'35':0})['3']='1260' # retain previous editor position
for idx,o in enumerate(SRC):
 oid=o['1'];x=float(o.get('2',0));y=float(o.get('3',0));gg=groups(OUT[idx].get('57',''))
 if oid not in ORB_IDS or not START<=x<END or 6 in gg:continue
 # Alpha affects drawing, not activation. Do not toggle off the gameplay object.
 OUT[idx]['57']='.'.join(map(str,[*gg,native_alpha]))
 native_visuals_hidden.append(idx)
 category='orb' if oid in ORB_IDS else 'portal' if oid in PORTAL_IDS else 'speed'
 key=(category,x,y,tuple(gg))
 if key in seen:continue
 seen.add(key);begin=len(ADDED)
 spr=atlas_render.sprite(atlas_names.get(int(oid),''))
 w,h=(spr.width/2,spr.height/2) if spr is not None else ((30,30) if category=='orb' else (40,90))
 def tf(shape,c,order):tightfill(native_shape(o,shape),c,-1,order,gg)
 def sl(points,c,width,order):stroke(native_shape(o,LineString(points)),c,-1,order,width,gg)
 def poly(points,c,order):tf(Polygon(points),c,order)
 def ellipse(rx,ry):return Polygon([(rx*math.cos(a),ry*math.sin(a)) for a in np.linspace(0,2*math.pi,49)[:-1]])
 accent={'36':754,'84':756,'141':755,'1330':752,'1333':757,'1704':758,'1751':756}.get(oid,754)
 if category=='orb':
  # Octagonal pressure-switch casting: inset glass, button face, two screws
  # and contacts. No default white rings or circular native core remain.
  shell=Polygon([(-18,-10),(-10,-18),(10,-18),(18,-10),(18,10),(10,18),(-10,18),(-18,10)])
  tf(shell,720,25);tf(shell.buffer(-1.7,join_style=2),752,26)
  tf(shell.buffer(-3.2,join_style=2),750,27)
  sx=float(o.get('128',o.get('32',1)));sy=float(o.get('129',sx))
  add(3637,x,y,720,-1,28,11.5/25*sx,11.5/25*sy,float(o.get('6',0)),gg)
  button=Polygon([(-8,-5),(-5,-8),(5,-8),(8,-5),(8,5),(5,8),(-5,8),(-8,5)])
  tf(button,accent,29);tf(button.buffer(-2,join_style=2),751 if oid=='1330' else 750,30)
  # Small functional symbol also distinguishes black/down and blue/reverse.
  if oid=='1330':sl([(-3,2),(0,-3),(3,2)],accent,1.8,31)
  elif oid=='84':sl([(-4,2),(0,5),(4,2),(0,-4),(-4,-1)],accent,1.2,31)
  else:sl([(-3,-2),(0,3),(3,-2)],accent,1.8,31)
  for dx,dy in [(-12,11),(12,-11)]:
   tf(Point(dx,dy).buffer(2,resolution=6),720,31)
   sl([(dx-1,dy),(dx+1,dy)],753,.9,32)
  for dx in [-6,6]:
   tf(box(dx-2,-22,dx+2,-17),751,26);sl([(dx,-21),(dx,-18)],accent,1.1,32)
  for dy in [-12,12]:sl([(-4,dy),(4,dy)],accent,1.1,31)
 elif category=='portal':
  # Eight segmented steel shoes form a gate around a clear opening.
  rx=w/2+3;ry=h/2+3
  for j in range(8):
   aa=np.linspace(j*math.pi/4+.04,(j+1)*math.pi/4-.04,6)
   path=[((rx+1)*math.cos(a),(ry+1)*math.sin(a)) for a in aa]
   sl(path,720,8,25);sl(path,751,5,26)
   sl([((rx+2)*math.cos(a),(ry+2)*math.sin(a)) for a in aa],752,1.1,27)
  # Warm contacts use a small identity accent, rather than a stock neon hoop.
  for sign in [-1,1]:
   for dy in [-ry*.42,0,ry*.42]:
    px=sign*(rx-2)*math.sqrt(max(0,1-(dy/ry)**2))
    sl([(px,dy-3),(px,dy+3)],754,2,29)
  tf(box(-12,ry-4,12,ry+13),720,30)
  tf(box(-10,ry-2,10,ry+11),751,31)
  # Tiny mode glyph on the gate lintel, not an obstruction across its opening.
  yy=ry+4
  if oid=='660':pts=[(-7,yy-2),(-3,yy+3),(1,yy-2),(6,yy+3)]
  elif oid=='13':pts=[(-6,yy-3),(6,yy),(-6,yy+3),(-2,yy),(-6,yy-3)]
  elif oid=='111':pts=[(-7,yy),(-4,yy+3),(4,yy+3),(7,yy),(-7,yy)]
  elif oid=='745':pts=[(-6,yy-3),(-3,yy+3),(2,yy+3),(2,yy-2),(6,yy-2)]
  else:pts=[(-4,yy-3),(-4,yy+3),(4,yy+3),(4,yy-3),(-4,yy-3)]
  sl(pts,753,1.1,32)
 else:
  # Machined speed chevrons retain the recognizable directional language.
  count={'200':1,'201':2,'202':2,'203':3,'1334':4}.get(oid,1)
  pitch=9;width=max(w,count*pitch+4);height=min(h,42)
  for dy in [-height/2-4,height/2+4]:
   tf(box(-width/2,dy-3,width/2,dy+3),720,25)
   sl([(-width/2+2,dy),(width/2-2,dy)],752,1.6,26)
  for j in range(count):
   xx=(j-(count-1)/2)*pitch
   direction=-1 if oid=='200' else 1
   pts=[(xx-direction*3,-height*.36),(xx+direction*4,0),(xx-direction*3,height*.36)]
   sl(pts,720,6,27);sl(pts,752,3,28);sl(pts,754,1,29)
 sec=max(i for i,v in enumerate([START,18195,20685,21800,22665,24600]) if x>=v)
 if 25 in gg or 1156 in gg:sec=3
 for q in ADDED[begin:]:q['_editor_kind']='interaction';q['_editor_section']=str(sec)
 interaction_frames.append({'source_index':idx,'object_id':oid,'kind':category,'x':x,'y':y,'groups':gg,'sprite_size':[w,h],'objects':len(ADDED)-begin,'section':sec})
