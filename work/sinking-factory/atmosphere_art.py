"""Atmosphere revision of Meltdown, retaining its factory scenes and gameplay."""
base=(HERE/'meltdown_art.py').read_text()
# Remove the previous faint rising particle layer, then build the established art.
a=base.index('# Foreground atmosphere:');b=base.index('# Oversized overhead foreground',a)
base=base[:a]+base[b:]
base=base[:base.index("head=gdparse.parse_header(H);cs=")]
exec(compile(base,str(HERE/'meltdown_art.py'),'exec'))

atmo_start=len(ADDED)
colors.update({
 600:(8,4,7),601:(17,7,10),603:(34,23,26),604:(159,65,34),
 605:(219,113,52),609:(125,79,51),612:(52,19,19),613:(64,38,33),
 617:(58,34,29),619:(18,13,19),636:(51,36,36),637:(22,19,25),
 650:(2,2,5),651:(22,11,15),652:(87,55,39),653:(242,119,49),
 654:(170,96,59),655:(155,90,60),656:(249,167,83),657:(151,58,25),
 658:(55,45,45),659:(26,24,29),660:(201,120,46),661:(180,47,19),
 662:(253,191,115),663:(4,4,7),664:(197,63,24),665:(225,87,30),
 666:(21,15,20),667:(92,59,43)
})
BLEND.update({653:.68,654:.34,656:.8,657:.19,662:.28,664:.23,665:.32})
ALPHA.update({650:.69,651:.48,652:.19,655:.67,663:.28})
# Less even neon on the edge; keep the strong pulses on the fires themselves.
for o in ADDED:
 if o['1']=='1006' and o.get('51')=='604':
  for k in ['7','8','9']:o[k]=fmt(float(o[k])*.74)

ash_groups=[];fog_groups=[];industrial_additions=[]

def linear_move(g,x,dy,duration,dx=0):
 move(g,x,dy,duration,dx)
 ADDED[-1]['30']='0'

def gauge(x,y,r,z=-1,gg=()):
 disc(x,y,r+3,611,z,20,gg);disc(x,y,r+1,658,z,21,gg)
 disc(x,y,r-2,619,z,22,gg)
 arc(x,y,r-5,20,160,1,660,z,23,gg)
 for a in [20,55,90,125,160]:
  rad=math.radians(a)
  line(x+(r-7)*math.cos(rad),y+(r-7)*math.sin(rad),x+(r-4)*math.cos(rad),y+(r-4)*math.sin(rad),1,609,z,24,gg)
 g=group();cg=center(x,y)
 line(x,y,x+(r-6)*.82,y+(r-6)*.57,1.3,660,z,25,(*gg,g))
 disc(x,y,2,658,z,26,gg)
 st=max(START,xt(tx(x)-.7))
 rotate(g,cg,st,-22,.35);rotate(g,cg,xt(tx(st)+.38),13,.6)

def hazard_band(x,y,w,h,z=-1,gg=()):
 shape=box(x-w/2,y-h/2,x+w/2,y+h/2)
 fill(shape,611,z,28,gg)
 for xx in np.arange(x-w/2-h,x+w/2,h*1.6):
  q=Polygon([(xx,y-h/2),(xx+h*.65,y-h/2),(xx+h*1.65,y+h/2),(xx+h,y+h/2)]).intersection(shape)
  fill(q,660,z,29,gg)

def control_box(x,y,w=112,h=62,caption='PRESSURE',gg=()):
 # Bolted electrical box with conduit, gauge, status lights and a hazard sill.
 rect(x,y,w+6,h+6,611,-1,18,gg);rect(x,y,w,h,658,-1,19,gg)
 rect(x,y,w-6,h-6,659,-1,20,gg)
 gauge(x-w*.27,y+5,13,-1,gg)
 rect(x+w*.16,y+7,w*.36,20,611,-1,21,gg)
 for j in range(5):rect(x+w*.03+j*6,y+7,3,9+(j%3)*2,661 if j>2 else 660,-1,22,gg)
 label(caption,x+5,y-h*.31,.14,609,-1,gg)
 hazard_band(x,y-h/2+3,w-6,5,-1,gg)
 for dx in [-w/2+4,w/2-4]:
  for dy in [-h/2+4,h/2-4]:add(1765,x+dx,y+dy,609,-1,30,.33,gg=gg,ldm=True)
 industrial_additions.append({'type':'control_box','x':x,'y':y,'w':w,'h':h,'groups':list(gg)})

# Fit control stations to actual wall interiors. Candidate modules are accepted
# only if the complete casing and its feeder cable fit inside the source hull.
for body,gg,region in surface_bodies:
 inner=body.buffer(-9,join_style=2)
 if inner.is_empty:continue
 ax,ay,bx,by=inner.bounds
 station_index=0
 for xx in np.arange(max(17040,math.ceil(ax/360)*360),min(END-120,bx),540):
  ys=[300,390,40,120,480] if region=='duct' else [70,175,420,490]
  for yy in ys:
   station=box(xx-66,yy-39,xx+66,yy+39)
   if not inner.covers(station):continue
   caption=('DRAFT 01' if xx<18195 else 'PRESSURE' if xx<20685 else 'CRANE CTRL')
   control_box(xx,yy,112,62,caption,gg)
   # The feeder terminates at a mounted junction inside the same solid wall.
   route=LineString([(xx+59,yy),(xx+83,yy),(xx+83,yy+60)])
   if inner.covers(route.buffer(7)):
    conduit(list(route.coords),5,-1,gg)
    rect(xx+83,yy+62,17,17,611,-1,22,gg);rect(xx+83,yy+62,11,11,658,-1,23,gg)
   station_index+=1;break

 # Worn caution paint is fitted to actual horizontal ledges, inside the metal.
 pieces=list(body.geoms) if hasattr(body,'geoms') else [body]
 painted=0
 for piece in pieces:
  coords=list(piece.exterior.coords)
  for a,b in zip(coords,coords[1:]):
   if abs(a[1]-b[1])>.1 or abs(a[0]-b[0])<85 or not -15<a[1]<480:continue
   xx=(a[0]+b[0])/2
   for sign in [-1,1]:
    yy=a[1]+sign*9;w=min(80,abs(a[0]-b[0])-20)
    band=box(xx-w/2,yy-3,xx+w/2,yy+3)
    if body.covers(band.buffer(2)):
     hazard_band(xx,yy,w,6,-1,gg);painted+=1;break
 industrial_additions.append({'type':'fitted_caution_paint','count':painted,'groups':list(gg)})

def duct_hood(x,y,w,h,roof):
 # Suspended extraction hood, throat and a duct that meets the collector rail.
 points=[(x-w*.5,y-h*.5),(x+w*.5,y-h*.5),(x+w*.35,y+h*.25),(x+w*.18,y+h*.5),(x-w*.18,y+h*.5),(x-w*.35,y+h*.25)]
 shell=Polygon(points)
 fill(shell,611,-3,30);fill(shell.buffer(-4,join_style=2),658,-3,31)
 fill(shell.buffer(-10,join_style=2),659,-3,32)
 line(x-w*.39,y-h*.30,x+w*.39,y-h*.30,3,636,-3,33)
 for dx in np.arange(-w*.32,w*.35,16):line(x+dx,y-h*.39,x+dx,y-h*.15,2,611,-3,34)
 conduit([(x,y+h*.5),(x,roof)],w*.16,-3)
 for dx in [-w*.4,w*.4]:line(x+dx,y-h*.3,x+dx,roof,1.5,636,-3,28)
 hazard_band(x,y-h*.44,w*.9,7,-3)
 label('EXTRACTION',x,y+h*.02,.18,609,-3)
 industrial_additions.append({'type':'extraction_hood','x':x,'y':y,'w':w,'h':h,'roof':roof})
 # Exhaust haze is broad and translucent, emitted from the throat.
 g=group();st=max(START,xt(tx(x)-1))
 for dx,dy,r in [(-18,0,56),(22,39,67),(-8,82,73)]:
  glow(x+dx,y+h*.28+dy,r,651,1,(g,),sx=1.5,sy=.75)
 linear_move(g,st,42,3.5,dx=-18)
 fog_groups.append({'group':g,'kind':'exhaust','x':x,'dx':-18,'dy':42})

for args in [(17255,285,174,88,455),(17910,350,155,80,455),(18900,365,168,82,490),(19925,348,176,75,490),(21230,390,180,82,575),(21910,425,177,84,575),(22985,345,165,76,450),(23770,352,182,83,450),(24340,345,154,74,450)]:duct_hood(*args)

def cable_tray(a,b,y):
 # Cable bundle contained in a supported channel, with visible upright brackets.
 rect((a+b)/2,y,b-a,18,611,-3,24)
 for dy,c in [(-5,603),(0,636),(5,613)]:line(a,y+dy,b,y+dy,1.5,c,-3,25)
 for xx in np.arange(a+12,b,28):line(xx,y-10,xx,y+10,2,658,-3,26)
 for xx in np.arange(a+25,b,145):
  line(xx,y+10,xx,y+43,3,659,-3,24);rect(xx,y+44,20,6,636,-3,25)
 industrial_additions.append({'type':'cable_tray','a':a,'b':b,'y':y})
for args in [(16880,18165,365),(18320,20620,396),(20725,22600,490),(22730,24610,364)]:cable_tray(*args)

# Warning lamps at functional entry points, mounted to collector supports.
for x,y,caption in [(17010,342,'BURNER 01'),(18330,325,'HIGH PRESSURE'),(20750,430,'HOT METAL'),(22800,325,'EXHAUST 04'),(24100,335,'EVACUATE')]:
 rect(x,y,104,24,611,-3,31);rect(x,y,98,18,659,-3,32)
 label(caption,x,y,.17,660,-3)
 rect(x,y+25,19,12,658,-3,32);disc(x,y+29,6,661,-3,33)
 line(x,y+35,x,y+70,3,636,-3,31)
 glow(x,y+28,38,665,1)
 for k in range(3):
  t=max(tx(START),tx(x)-.65)+k*.37
  trigger(1006,xt(t),**{'51':661,'45':.01,'46':.05,'47':.14,'7':245,'8':84,'9':29,'52':0})

# Three ash planes. Each zone starts before entering view and falls continuously
# while the player traverses it. Initial positions are solved for the local time.
ashrng=random.Random(20260915)
for cell,x in enumerate(np.arange(16950,24500,290)):
 for depth,count,vy,vx,z,c in [('far',18,31,-13,-3,654),('middle',29,61,-27,1,653),('near',12,93,-39,3,655)]:
  g=group();duration=5.0;t=max(tx(START),tx(x)-1.35);st=xt(t)
  elapsed=max(0,tx(x)-t)
  for j in range(count):
   xx=min(END-15,max(START+15,x+ashrng.uniform(-155,155)-vx*elapsed))
   yy=ashrng.uniform(-35,515)+vy*elapsed
   sz=ashrng.uniform(.8,1.7) if depth=='far' else ashrng.uniform(1.6,3.5) if depth=='middle' else ashrng.uniform(2.7,5.2)
   rot=ashrng.uniform(15,75)
   if depth=='near':
    # Irregular charred flake, not a bright game orb or a large square.
    q=add(693,xx,yy,c,z,48,sz/30,sz*.70/30,rot,(g,),ldm=True)
    if j%3==0:line(xx,yy,xx+sz*.42,yy+sz*.2,.6,654,z,49,(g,),True)
   else:
    rect(xx,yy,sz,sz*.50,c,z,45,(g,),rot,True)
    if j%5==0:
     line(xx,yy,xx+2.1,yy+4.7,.55,654,z,44,(g,),True)
    if depth=='middle' and j%4==0:
     rect(xx,yy,sz*.65,sz*.37,656,z,46,(g,),rot,True)
  linear_move(g,st,-vy*duration,duration,dx=vx*duration)
  ash_groups.append({'group':g,'depth':depth,'center_x':float(x),'trigger_x':st,'trigger_time':t,'speed_x':vx,'speed_y':-vy,'duration':duration,'particle_count':count})

# Local shadows and soot collect around the ceiling and below the route. Large
# soft fields replace uniform illumination; no opaque full-screen rectangle.
for i,x in enumerate(np.arange(17050,24450,310)):
 if x<18195:top,bottom=440,-40
 elif x<20685:top,bottom=407,10
 elif x<21800:top,bottom=505,90
 elif x<22665:top,bottom=440,30
 else:top,bottom=405,-10
 g=group();t=max(tx(START),tx(x)-1.3);st=xt(t)
 glow(x,top,145,650,1,(g,),sx=1.8,sy=.83)
 glow(x+60,bottom,124,650,1,(g,),sx=1.75,sy=.60)
 # Irregular drifting soot between the outer band and the lit interior.
 for dx,dy,r in [(-80,-39,67),(10,-5,80),(95,-18,62)]:
  glow(x+dx,top+dy,r,651,1,(g,),sx=1.25,sy=.77)
 linear_move(g,st,9 if i%2 else -8,4.8,dx=-45)
 fog_groups.append({'group':g,'kind':'edge_soot','x':float(x),'top':top,'bottom':bottom})

# Wisps of suspended furnace dust drift through the middle distance, softening
# the exact lattice pattern behind them without drawing a solid fog rectangle.
for i,x in enumerate(np.arange(17125,24400,435)):
 g=group();yy=160+(i%3)*48;st=max(START,xt(tx(x)-1.1))
 for dx,dy,r in [(-55,5,145),(30,-12,126),(90,11,86)]:
  glow(x+dx,yy+dy,r,652,1,(g,),sx=1.7,sy=.30)
 linear_move(g,st,14,4.0,dx=-84)
 fog_groups.append({'group':g,'kind':'suspended_dust','x':float(x),'y':yy})

# Replace dead-even wall lighting with localized warm exhaust reflections.
for x,y in [(17115,115),(17640,215),(19035,175),(19710,215),(21495,270),(22175,255),(23030,95),(23730,95),(24325,115)]:
 glow(x,y,190,657,1,sx=1.25,sy=1.05)

head=gdparse.parse_header(H);cs=head.get('kS38','').rstrip('|')
for cid,rgb in colors.items():
 op=0 if cid==620 else BLEND.get(cid,ALPHA.get(cid,1))
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1_5_{1 if cid in BLEND else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in OUT+ADDED)
(HERE/'atmosphere.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Afterburn');fields['k48']=('i',str(len(OUT+ADDED)));fields['k1']=('i','0');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - AFTERBURN.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'modified_original_objects':changes,'visual_trigger_changes':visual_shader_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'fixtures':fixtures,'emitters':emitters,'shallow_intro_preserved':len(shallow),'ash_groups':ash_groups,'fog_groups':fog_groups,'industrial_additions':industrial_additions,'atmosphere_objects':len(ADDED)-atmo_start}
(HERE/'atmosphere-manifest.json').write_text(json.dumps(manifest,indent=2))
print({k:manifest[k] for k in ['added_objects','total_objects','groups','atmosphere_objects']});print(out)
