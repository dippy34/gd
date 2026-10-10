"""Native-object foundry environment. Executed by build_meltdown.py.

Art geometry is authored in world coordinates. Only the source-derived metal
skin follows colliders; environmental machinery has a separate, rear draw plane.
"""
import random
rng=random.Random(148876671)
colors.update({
 600:(13,4,7),601:(26,9,13),602:(15,12,16),603:(47,24,25),
 604:(199,78,39),605:(244,130,58),606:(126,23,11),607:(250,106,24),
 608:(87,10,10),609:(161,82,51),610:(24,8,12),611:(5,5,8),
 612:(75,22,17),613:(93,45,31),614:(170,36,15),615:(255,216,129),
 616:(216,53,15),617:(80,42,30),618:(116,20,13),619:(26,15,20),
 620:(0,0,0),621:(255,160,48),622:(59,11,11),623:(255,232,172),624:(156,24,10),
 630:(218,46,13),631:(255,102,26),632:(255,193,81),633:(134,31,19),
 634:(5,3,6),635:(104,28,22),636:(64,39,36),637:(33,25,29),
 638:(255,154,68),639:(211,57,17),640:(251,204,146),641:(255,47,17)
})
BLEND={630:.55,631:.50,632:.42,633:.30,638:.32,639:.17,640:.22,641:.32}
ALPHA={634:.48,635:.75}
fixtures=[];emitters=[];art_sections=[];surface_bodies=[]

def glow(x,y,r,c=630,z=1,gg=(),sx=1,sy=1):
 # Four native quarter-radial gradients. No synthetic glow object IDs.
 for i in range(4):
  a=math.radians(i*90);dx=(-math.cos(a)+math.sin(a))*r/2;dy=(math.sin(a)+math.cos(a))*r/2
  add(504,x+dx*sx,y+dy*sy,c,z,-25,r/20*sx,r/20*sy,i*90,gg,ldm=True)

def arc(x,y,r,start,end,w,c,z=-3,order=5,gg=()):
 n=max(3,int(abs(end-start)*r/900))
 pts=[(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a))) for a in np.linspace(start,end,n+1)]
 for a,b in zip(pts,pts[1:]):line(*a,*b,w,c,z,order,gg)

def label(text,x,y,size=0.25,c=609,z=-1,gg=()):
 o=add(580,x,y,c,z,20,sx=size,gg=gg);o['31']=base64.urlsafe_b64encode(text.encode()).decode()

def conduit(pts,width=10,z=-3,gg=(),hot=False):
 for k,c in [(width+6,611),(width,636),(width*.46,619)]:
  for a,b in zip(pts,pts[1:]):line(*a,*b,k,c,z,4,gg)
 for a,b in zip(pts,pts[1:]):
  length=math.dist(a,b)
  for f in np.arange(22,length-12,54):
   q=f/length;x=a[0]+(b[0]-a[0])*q;y=a[1]+(b[1]-a[1])*q
   ang=-math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]))
   rect(x,y,5,width+8,613,z,6,gg,ang)
  line(a[0],a[1]+width*.22,b[0],b[1]+width*.22,1.3,604 if hot else 613,z,7,gg)
 for x,y in pts[1:-1]:disc(x,y,width*.6,636,z,7,gg)

def truss(a,b,width=22,z=-3,c=603,gg=()):
 dx=b[0]-a[0];dy=b[1]-a[1];l=math.hypot(dx,dy);nx=-dy/l;ny=dx/l
 line(*a,*b,width+5,611,z,3,gg)
 for sign in [-1,1]:line(a[0]+nx*width*.5*sign,a[1]+ny*width*.5*sign,b[0]+nx*width*.5*sign,b[1]+ny*width*.5*sign,3,c,z,4,gg)
 n=max(1,int(l/32))
 for i in range(n):
  f=i/n;f1=(i+1)/n;sign=1 if i%2 else -1
  p=(a[0]+dx*f+nx*width*.4*sign,a[1]+dy*f+ny*width*.4*sign)
  q=(a[0]+dx*f1-nx*width*.4*sign,a[1]+dy*f1-ny*width*.4*sign)
  line(*p,*q,2,c,z,5,gg)

def link_chain(x,y,length,z=-3,gg=(),swing=0):
 if swing:
  g=group();cg=center(x,y);gg=(*gg,g);st=max(START,x-650)
  rotate(g,cg,st,swing,1.4);rotate(g,cg,min(END-100,st+700),-swing*1.7,1.6)
 for j in range(math.ceil(length/14)):
  yy=y-j*14
  add(3050 if j%2==0 else 3052,x,yy,613,z,10,.66,.66,gg=gg)
  if j%2==0:add(3050,x-1,yy+1,602,z,11,.49,.55,gg=gg)
 return gg

def turbine(x,y,r,z=-3,drive=True,body=None,gg=()):
 # Bolted casing, pressure ports, inset rotor, hub and a real drive shaft.
 idx=len(ADDED)
 for rr,c in [(r+9,611),(r+5,636),(r,613),(r-5,602),(r-12,612),(r-19,611)]:disc(x,y,rr,c,z,7,gg)
 # Bevel segments catch light across the curved casing, including darker sides.
 for i in range(40):
  aa=i*9;bb=aa+9.15;rr=r+1
  a=(x+rr*math.cos(math.radians(aa)),y+rr*math.sin(math.radians(aa)))
  b=(x+rr*math.cos(math.radians(bb)),y+rr*math.sin(math.radians(bb)))
  o=line(*a,*b,6,636,z,8,gg)
  o['41']='1';o['43']=f'0a1a{.4+.85*max(0,math.cos(math.radians(aa-60)))}a0a0'
 for i in range(16):
  a=i*math.pi/8;xx=x+(r-12)*math.cos(a);yy=y+(r-12)*math.sin(a)
  rect(xx,yy,r*.075,5,607 if i%4==0 else 613,z,12,gg,-i*22.5)
 # Shadowed inner wall ribs give the chamber a second depth plane.
 for rr in [.36,.57,.78]:ring(x,y,r*rr,1,601,z,8,gg)
 for i in range(20):
  a=i*math.pi/10
  line(x+r*.22*math.cos(a),y+r*.22*math.sin(a),x+r*.83*math.cos(a+.10),y+r*.83*math.sin(a+.10),1,603,z,8,gg)
 for i in range(12):
  a=i*math.pi/6
  disc(x+(r-2)*math.cos(a),y+(r-2)*math.sin(a),2.3,609,z,12,gg,True)
 arc(x,y,r-10,15,145,2,604,z,11,gg);arc(x,y,r-10,198,325,1.5,616,z,11,gg)
 rotor=group();cg=center(x,y);rotgg=(*gg,rotor)
 for i in range(7):
  a=i*2*math.pi/7
  pts=[]
  for rr,aa in [(r*.2,a),(r*.62,a+.13),(r*.81,a+.32),(r*.83,a+.48),(r*.54,a+.52),(r*.3,a+.68)]:pts.append((x+rr*math.cos(aa),y+rr*math.sin(aa)))
  fill(Polygon(pts),637,z,9,rotgg)
  fill(Polygon([pts[0],pts[1],pts[2],pts[4]]),636,z,10,rotgg)
  line(*pts[2],*pts[3],2,609,z,11,rotgg)
  line(*pts[0],*pts[1],1,613,z,11,rotgg)
  for f in [.35,.52,.70]:
   ang=a+.22;rr=r*f
   line(x+rr*math.cos(ang),y+rr*math.sin(ang),x+(rr+7)*math.cos(ang+.19),y+(rr+7)*math.sin(ang+.19),1,603,z,11,rotgg)
 disc(x,y,r*.23,613,z,12,gg);disc(x,y,r*.16,602,z,13,gg);disc(x,y,r*.07,607,z,14,gg)
 ring(x,y,r*.19,2,636,z,14,gg)
 for i in range(6):
  a=i*math.pi/3;disc(x+r*.20*math.cos(a),y+r*.20*math.sin(a),2,609,z,15,gg,True)
 disc(x,y,r*.035,615,z,15,gg)
 if body is None:glow(x,y,r*.70,630,1,gg)
 if drive:
  rotate(rotor,cg,max(START,x-700),-520 if x<22665 else 740,4.5)
 fixtures.append({'type':'turbine','x':x,'y':y,'r':r,'group':rotor,'objects':len(ADDED)-idx})

def firebank(x,y,w,h,z=-3,gg=(),intensity=1):
 # Native looping fire sprites emerge from a continuous fuel bed.
 def fire_shape(xx,yy,ww,hh,c,order):
  # Curved silhouettes share one anchored fuel bed; tapered lobes are authored.
  curves=[((-0.50,0),(-.64,.20),(-.42,.35),(-.27,.50)),
          ((-.27,.50),(-.26,.29),(.02,.37),(-.02,.69)),
          ((-.02,.69),(.26,.54),(.18,.32),(.27,.23)),
          ((.27,.23),(.57,.39),(.53,.67),(.20,1)),
          ((.20,1),(.68,.79),(.48,.56),(.51,.38)),
          ((.51,.38),(.72,.21),(.65,.10),(.50,0))]
  pts=[]
  for a,b,c1,d in curves:
   for u in np.linspace(0,1,7):
    px=(1-u)**3*a[0]+3*(1-u)**2*u*b[0]+3*(1-u)*u*u*c1[0]+u**3*d[0]
    py=(1-u)**3*a[1]+3*(1-u)**2*u*b[1]+3*(1-u)*u*u*c1[1]+u**3*d[1]
    pts.append((xx+px*ww,yy+py*hh))
  fill(Polygon(pts),c,z,order,gg,True)
 for i,xx in enumerate(np.arange(x-w/2+25,x+w/2-15,43)):
  fh=h*(.65+.35*math.sin(i*2.17)**2)
  fire_shape(xx,y,43,fh,616,14)
  fire_shape(xx-3,y,30,fh*.69,607,15)
  fire_shape(xx-4,y,15,fh*.38,615,16)
  oid=920 if i%3==0 else 923 if i%3==1 else 924
  ow,oh=(63,68.5) if oid==920 else (29,55) if oid==923 else (28.5,50.5)
  add(oid,xx,y+fh*.42,607,z,17,43/ow,fh*.9/oh,gg=gg,ldm=True)
 rect(x,y,w,5,615,z,18,gg)
 for xx in np.arange(x-w/2+20,x+w/2,70):glow(xx,y+20,75*intensity,631,1,gg)
 glow(x,y+h*.45,max(100,w*.62),639,1,gg,sx=1.15,sy=1.55)
 emitters.append({'type':'fire','x':x,'y':y,'width':w,'height':h})

def spark_jet(x,y,trigger_x,dx=35,dy=100,n=12,z=1):
 g=group()
 # A coherent spray cone from one physical nozzle, with no big floating props.
 for i in range(n):
  u=(i+.5)/n;px=x+dx*u+math.sin(i*3.1)*8;py=y+dy*u
  line(px,py,px+dx*.03,py+dy*.035,.9 if i%3 else 1.7,621,z,20,(g,),True)
  if i%4==0:glow(px,py,11,632,z,(g,))
 st=max(START,trigger_x)
 move(g,st,dy*.65,.5,dx=dx*.5)
 trigger(1007,st,**{'51':g,'10':0,'35':1})
 trigger(1007,min(END-5,xt(tx(st)+.25)),**{'51':g,'10':.35,'35':0})
 emitters.append({'type':'sparks','x':x,'y':y,'group':g,'trigger_x':st})

def flame_column(x,top,bottom,width,z=-3):
 # A molten stream exits a nozzle and lands in a receiver: both ends explicit.
 rect(x,(top+bottom)/2,width,top-bottom,616,z,10)
 rect(x-2,(top+bottom)/2,width*.44,top-bottom,621,z,11)
 rect(x-3,(top+bottom)/2,width*.14,top-bottom,615,z,12)
 for yy in np.arange(bottom,top,46):
  add(923,x+width*.35,yy,607,z,13,.55,1.0,180,ldm=True)
  glow(x,yy,70,630,1)
 rect(x,top+10,width+24,20,636,z,16);rect(x,top,width+12,7,611,z,17)
 rect(x,bottom-10,width+85,16,602,z,16);firebank(x,bottom,width+75,35,z)
 spark_jet(x,bottom,max(START,x-450),40,95,16)

def furnace(x,y,w,h,num):
 # Chamfered rectangular blast-furnace shell, refractory brick throat, grating.
 shape=Polygon([(x-w/2,y-h/2+20),(x-w/2+20,y-h/2),(x+w/2-20,y-h/2),(x+w/2,y-h/2+20),(x+w/2,y+h/2-30),(x+w/2-30,y+h/2),(x-w/2+30,y+h/2),(x-w/2,y+h/2-30)])
 fill(shape,611,-3,0);fill(shape.buffer(-6,join_style=2),636,-3,1);fill(shape.buffer(-15,join_style=2),612,-3,2)
 inner=shape.buffer(-26,join_style=2);fill(inner,608,-3,3)
 for yy in np.arange(y-h/2+28,y+h/2-20,28):
  for xx in np.arange(x-w/2+28,x+w/2-20,48):
   tile=box(xx+2,yy+2,xx+44,yy+24).intersection(inner)
   fill(tile,614 if int(yy/28)%3==0 else 606,-3,4)
 firebank(x,y-h/2+34,w-62,h*.65,-3)
 for xx in np.arange(x-w/2+34,x+w/2-25,36):
  rect(xx,y,7,h-54,611,-3,20);line(xx-1,y-h/2+27,xx-1,y+h/2-27,1,613,-3,21)
 for yy in [y-h/2+17,y+h/2-17]:
  rect(x,yy,w-32,8,602,-3,22)
  for xx in np.arange(x-w/2+28,x+w/2-20,35):disc(xx,yy,2,609,-3,23,ldm=True)
 label('FURNACE '+str(num),x,y+h/2-5,.19,609,-3)
 for s in [-1,1]:conduit([(x+s*w/2,y+h*.15),(x+s*(w/2+28),y+h*.15),(x+s*(w/2+28),y+h/2+40)],9,-3)
 fixtures.append({'type':'furnace','x':x,'y':y,'w':w,'h':h})

# Scene-wide rear architecture. Every bay has continuous rail/pipe connections.
for a in np.arange(START,END,300):
 w=min(300,END-a);rect(a+w/2,235,w,1050,600,-5,-40)
 add(1011,a+w/2,40,608,-5,-35,w/30,16)
 # Refractory masonry deep behind the steelwork.
 for j,yy in enumerate(range(-90,610,45)):
  for xx in np.arange(a-35*(j%2),a+w,70):
   xmin=max(a,xx+2);xmax=min(a+w,xx+67)
   if xmax>xmin:rect((xmin+xmax)/2,yy,xmax-xmin,41,601 if j%3 else 610,-5,-34,ldm=True)
for x in np.arange(16900,24620,395):
 truss((x,-130),(x,620),22,-5,612)
 for yy in [10,405]:rect(x,yy,42,12,617,-5,-3)
for a,b,y in [(16810,18170,390),(18220,20650,425),(20710,22625,520),(22700,24630,385)]:
 truss((a,y),(b,y),35,-3,613)
 conduit([(a+20,y+65),(b-30,y+65),(b-30,y+10)],16,-3,hot=True)
 for x in np.arange(a+75,b-20,170):
  rect(x,y-30,32,13,611,-3,7);rect(x,y-32,24,4,607,-3,8);glow(x,y-38,76,630,1)

# 1. Furnace intake: large, individually proportioned furnace chambers.
for p in [(17115,205,235,430,1),(17640,265,315,510,2),(18000,250,220,430,3)]:furnace(*p)
conduit([(16830,470),(17280,470),(17280,390),(18090,390)],20,-3,hot=True)
for x,y,l in [(17005,480,160),(17475,570,185),(17910,490,105)]:
 link_chain(x,y,l,-3,swing=3);rect(x,y-l,24,16,636,-3,15)

# 2. Pressure duct: cylindrical heat exchangers, warning lights and pipe rupture.
for x,y,r in [(18465,175,116),(19035,175,145),(19710,215,130),(20460,235,108)]:
 conduit([(x-r-75,y),(x-r,y)],20,-3,hot=True)
 conduit([(x+r,y),(x+r+55,y),(x+r+55,410)],17,-3,hot=True)
 turbine(x,y,r,-3)
 for d in [-1,1]:truss((x+d*r*.75,y+r*.7),(x+d*(r+30),425),15,-3,603)
for x,y in [(18765,330),(19485,370),(20025,320)]:
 rect(x,y,36,14,602,-3,18);firebank(x,y+4,32,105,-3)
 spark_jet(x,y+14,x-290,45,105,14)

# 3. Smelter hall: a crane carries a pouring ladle over paired catch vats.
for x,w,h in [(20985,145,335),(21765,185,390),(22365,132,300)]:
 y=260;rect(x,y,w,h,619,-3,0);disc(x,y+h/2,w/2,619,-3,0)
 for dx in [-w*.35,w*.35]:line(x+dx,y-h/2,x+dx,y+h/2,4,613,-3,2)
 for yy in [y-h*.27,y+h*.25]:rect(x,yy,w+12,10,636,-3,3)
 for i in range(9):line(x-w*.20,y+i*20-85,x+w*.16,y+i*20-85,1,613,-3,4)
 turbine(x,y+30,w*.27,-3)
 link_chain(x-w*.36,550,550-(y+h/2),-3)
 link_chain(x+w*.36,550,550-(y+h/2),-3)
 label('HOT METAL',x,y-h*.33,.20,609,-3)
for x,top,bottom,w in [(21150,445,85,13),(22005,480,65,21),(22515,390,120,10)]:flame_column(x,top,bottom,w)
for x in [21000,21915]:
 for yy in np.arange(120,470,20):line(x+130,yy,x+149,yy,2,613,-3,12)
 for dx in [130,149]:line(x+dx,110,x+dx,480,3,636,-3,11)

def ladle(x,y,w,h):
 g=group();cg=center(x,y+h/2+28)
 shell=Polygon([(x-w/2,y+h/2),(x-w*.36,y-h/2+16),(x-w*.20,y-h/2),(x+w*.34,y-h/2),(x+w/2,y+h/2)])
 fill(shell,611,-3,5,(g,));fill(shell.buffer(-6,join_style=2),636,-3,6,(g,));fill(shell.buffer(-13,join_style=2),619,-3,7,(g,))
 for xx in np.arange(x-w*.30,x+w*.31,24):
  line(xx,y-h*.30,xx,y+h*.37,3,613,-3,8,(g,))
 # Rear bowl lip shows the molten metal; a hinged spout feeds a fixed trough.
 rect(x,y+h/2-6,w-12,14,614,-3,9,(g,));rect(x,y+h/2,w-20,4,615,-3,10,(g,))
 for dx in [-w*.38,w*.38]:
  disc(x+dx,y+h*.38,8,611,-3,12,(g,));disc(x+dx,y+h*.38,4,609,-3,13,(g,))
  link_chain(x+dx,y+h/2+120,115,-3)
 truss((x-w/2-35,y+h/2+128),(x+w/2+35,y+h/2+128),28,-3,636)
 label('MELT 04',x,y-.12*h,.25,609,-3,(g,))
 rotate(g,cg,max(START,x-450),-11,.7)
 flame_column(x+w*.50,y+h*.5-10,y-h*.5-30,12,-3)
 fixtures.append({'type':'pouring_ladle','x':x,'y':y,'w':w,'h':h,'group':g})
ladle(21425,255,182,182)
ladle(22185,300,143,148)

# 4. Turbine failure: a broken power station, active rotors and floor fire.
for x,y,r in [(22935,255,140),(23535,220,165),(24210,240,152)]:
 turbine(x,y,r,-3)
 conduit([(x-r-50,450),(x-r-50,y),(x-r,y)],18,-3,hot=True)
 conduit([(x+r,y),(x+r+38,y),(x+r+38,-35)],18,-3)
 truss((x-r,390),(x+r,390),28,-3,636)
 link_chain(x-r*.65,410,130,-3,swing=5)
 link_chain(x+r*.65,410,100,-3,swing=-4)
 firebank(x,-20,r*1.5,105,-3)
 spark_jet(x+r*.7,y+80,x-380,-75,-130,20)

# Source-derived wall contours. No art from the earlier revisions is imported.
segments=json.loads((HERE/'audit/slope-boundaries.json').read_text())['segments']
solid_parts=[];terrain_edges=[];shallow=[]
for s in segments:
 x,y=s['center']
 if not 16875<=x<20685:continue
 a,b=[tuple(p) for p in s['edge']]
 if 18195<=x<18855:shallow.append(s);continue
 outer=-180 if s['side']=='lower' else 650
 shape=Polygon([a,b,(b[0],outer),(a[0],outer)]).intersection(box(16875,-180,20685,650))
 if not shape.is_valid:shape=shape.buffer(0)
 solid_parts.append(shape);terrain_edges.append(LineString([a,b]))
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0))
 if o['1']=='468' and 18195<=x<20685 and '6' not in o.get('57','').split('.'):
  if y<=210:solid_parts.append(box(x-15,-180,x+15,y-.8))
  elif y>240:solid_parts.append(box(x-15,y+.8,x+15,650))
terrain=unary_union(solid_parts).buffer(0)

def armor(body,gg=(),region='duct'):
 # The facing is open steel lattice over a hot pressure jacket, with paired
 # safety rims and small fitted service hatches. Everything clips to the hull.
 fill(body,602,-1,0,gg);surface_bodies.append((body,gg,region))
 inner=body.buffer(-10,join_style=2)
 if inner.is_empty:return
 fill(inner,619,-1,1,gg)
 minx,miny,maxx,maxy=body.bounds
 # Layered cross-bracing follows the actual wall volume instead of box stamps.
 for xx in np.arange(math.floor(minx/60)*60-650,maxx+650,60):
  for sign in [-1,1]:
   cut=LineString([(xx,-180),(xx+sign*830,650)]).intersection(inner)
   stroke(cut,611,-1,2,7,gg);stroke(cut,603,-1,3,2,gg)
 # Jacket seams, recessed ports and fasteners on a finer industrial module.
 for xx in np.arange(math.floor(minx/150)*150,maxx,150):
  for yy in np.arange(math.floor(miny/100)*100,maxy,100):
   panel=box(xx+14,yy+16,xx+135,yy+84).intersection(inner)
   if panel.area<650:continue
   # Alternating chamfered armor plates interrupt the lattice with heavy masses.
   tile_mode=(int(xx/150)+int(yy/100))%3
   if tile_mode!=1:
    rawplate=Polygon([(xx+15,yy+20),(xx+113,yy+20),(xx+134,yy+41),(xx+134,yy+80),(xx+35,yy+80),(xx+15,yy+60)])
    fitted=rawplate.intersection(inner)
    fill(fitted,611,-1,4,gg);fill(fitted.buffer(-4,join_style=2),603,-1,5,gg)
    stroke(fitted.buffer(-5,join_style=2),613,-1,6,1,gg)
    # Angled scorched crease is etched into the plate, never protruding.
    scar=LineString([(xx+21,yy+61),(xx+37,yy+47),(xx+55,yy+49),(xx+75,yy+24)]).intersection(fitted.buffer(-5))
    stroke(scar,611,-1,7,3,gg)
    stroke(scar,612,-1,8,.7,gg)
   else:stroke(panel,636,-1,5,1.6,gg)
   # Long glowing vent belongs to this jacket panel, contained on all sides.
   vent=box(xx+46,yy+35,xx+105,yy+61)
   if panel.covers(vent):
    fill(vent,611,-1,6,gg);fill(vent.buffer(-4),608,-1,7,gg)
    for zz in np.arange(xx+54,xx+102,9):
     line(zz,yy+41,zz,yy+55,2,616,-1,8,gg)
    line(xx+49,yy+37,xx+102,yy+37,1,604,-1,9,gg)
   for bx,by in [(xx+20,yy+24),(xx+127,yy+76)]:
    if panel.covers(Point(bx,by).buffer(3)):
     disc(bx,by,2.5,611,-1,8,gg,True);add(1765,bx,by,609,-1,9,.43,gg=gg,ldm=True)
 # Perimeter extrusions stay attached and create a layered, lit silhouette.
 stroke(inner.boundary,613,-1,11,3.0,gg)
 stroke(body.buffer(-3,join_style=2).boundary,604,-1,12,1.6,gg)
 # Narrow linked cable trays run along both sides of each real wall edge.
 for dist,width,c,order in [(17,5,611,12),(20,1.4,613,13),(24,.9,636,13)]:
  skin=body.buffer(-dist,join_style=2)
  if not skin.is_empty:stroke(skin.boundary,c,-1,order,width,gg)
 # Functional heat seams are fitted into the wall at a sparse set of modules.
 for xx in np.arange(minx+70,maxx-20,260):
  yy=40+(int(xx/260)%4)*120
  port=Point(xx,yy).buffer(29)
  if inner.covers(port):
   disc(xx,yy,28,611,-1,13,gg);ring(xx,yy,25,3,636,-1,14,gg)
   for angle in [0,90]:
    a=math.radians(angle);line(xx-18*math.cos(a),yy-18*math.sin(a),xx+18*math.cos(a),yy+18*math.sin(a),4,613,-1,15,gg)
   disc(xx,yy,6,614,-1,16,gg);glow(xx,yy,42,630,1,gg)

armor(terrain)
for edge in terrain_edges:
 stroke(edge,605,-1,18,1.5)
 # A narrow hot seam, not a broad opaque stripe through the playable gap.
 stroke(edge,639,1,-10,9)
for s in shallow:
 shape=Polygon([*s['edge'],s['solid_vertex']]);fill(shape,602,-1,0)
 stroke(LineString(s['edge']),605,-1,18,1.5)

bygroup=defaultdict(list)
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));gg=tuple(groups(o.get('57','')))
 if 20685<=x<22665 and o['1'] in ['211','208','209'] and 6 not in gg:bygroup[gg].append(box(x-15,y-15,x+15,y+15))
for gg,parts in bygroup.items():armor(unary_union(parts).buffer(0),gg,'smelter')

# Fine fittings are attached to the source's individual UFO hazard housings.
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));gg=groups(o.get('57',''))
 if o['1']!='94' or not 22665<=x<END or 6 in gg:continue
 rail=365 if y>150 else -35
 line(x,y,x,rail,2,603,-3,22)
 rect(x,rail,24,8,636,-3,23)
 rect(x,y,29,29,602,-1,1,gg);rect(x,y,23,23,613,-1,2,gg);rect(x,y,19,19,611,-1,3,gg)
 disc(x,y,7,636,-1,4,gg);disc(x,y,3.5,616,-1,5,gg)
 glow(x,y,23,630,1,gg)

# Attached surface fire/heat panels occupy real wall interiors, never route gaps.
for x,y,r in [(17360,350,65),(17610,-20,60),(19380,40,70),(19590,440,64),(20235,390,46)]:
 hatch=Point(x,y).buffer(r+8)
 if terrain.covers(hatch):
  disc(x,y,r+8,611,-1,13);disc(x,y,r+3,636,-1,14);disc(x,y,r,608,-1,15)
  firebank(x,y-r*.5,r*1.25,r*1.2,-1)
  ring(x,y,r-2,5,613,-1,20)
  for dx in np.arange(-r*.6,r*.7,13):
   hh=math.sqrt(max(0,(r-8)**2-dx**2));line(x+dx,y-hh,x+dx,y+hh,4,611,-1,21)

# Foreground atmosphere: particles and smoke flow from machinery/fuel beds.
# The screen centre remains free of large opaque objects.
for x,y in [(17150,70),(17750,170),(19020,170),(19800,210),(21320,180),(22050,250),(23010,90),(23970,120),(24330,140)]:
 g=group();st=max(START,x-750)
 for i in range(22):
  xx=x+rng.uniform(-150,150);yy=y+rng.uniform(-110,150)
  add(1764,xx,yy,607 if i%3 else 615,1,30,.10 if i%4 else .19,gg=(g,),ldm=True)
 move(g,st,75,3.8,dx=-48)
 for j in range(3):
  xx=x+j*43-40;yy=y+135+j*18
  glow(xx,yy,66+j*12,634,1,(g,),sx=1.5,sy=.75)

# Oversized overhead foreground hardware is limited to scene transitions.
for x,top,length in [(18165,530,150),(20650,570,160),(22635,495,100),(24490,475,120)]:
 gg=link_chain(x,top,length,1,swing=2)
 rect(x,top,40,24,611,1,35)
 arc(x,top-length-10,14,170,465,5,611,1,36,gg)

# Source collision/control data stays identical, with purely visual retints.
OUT=copy.deepcopy(SRC);visual_shader_changes=[]
struct={'1','94','1338','1339','468','211','208','209','693'}
hazards={'8','216','217','458','1717','1718'}
for idx,o in enumerate(OUT):
 x=float(o.get('2',0));oid=o['1']
 if not 16875<=x<END:continue
 if oid in struct|hazards and '6' not in o.get('57','').split('.'):
  before=dict(o);o['21']=str(605 if oid in hazards else 620 if oid in ['1338','1339'] else 602);o['22']=str(620 if oid in ['1338','1339'] else 602);o['24']='-1';o['25']='40' if oid in hazards else '-5'
  changes.append({'index':idx,'keys':[k for k in set(o)|set(before) if o.get(k)!=before.get(k)]})
 if oid=='2921' and x==16875:
  visual_shader_changes.append({'index':idx,'original':dict(o)});o['176']='0';o['10']='0';o['188']='0'
for o in SRC:
 x=float(o.get('2',0));y=float(o.get('3',0));oid=o['1'];gg=groups(o.get('57',''))
 if not 16875<=x<END or 6 in gg or oid not in ['216','217','458']:continue
 w,h=(24,23) if oid=='216' else (23,9) if oid=='217' else (9,9)
 def tr(shape):
  shape=affinity.scale(shape,-1 if o.get('4')=='1' else 1,-1 if o.get('5')=='1' else 1,origin=(0,0))
  return affinity.translate(affinity.rotate(shape,-float(o.get('6',0)),origin=(0,0)),xoff=x,yoff=y)
 tri=Polygon([(-w/2,-h/2-2),(w/2,-h/2-2),(0,h/2-2)])
 fill(tr(tri),612,-1,37,gg);fill(tr(tri.buffer(-3,join_style=2)),602,-1,38,gg)
 stroke(tr(LineString([(-w/2,-h/2-2),(0,h/2-2)])),604,-1,39,1.1,gg)

# Local music accents: fire, specular edges and amber furnace haze react together.
# The original soundtrack/speed/camera data is untouched.
for i,b in enumerate(beats):
 major=i%4==0
 for cid,rgb in [(607,(255,157 if major else 110,39)),(616,(252 if major else 218,78 if major else 47,15)),(630,(255 if major else 194,68 if major else 38,15)),(604,(234 if major else 183,122 if major else 72,55 if major else 34))]:
  trigger(1006,b['x'],**{'51':cid,'45':.008,'46':.028 if major else .008,'47':.23 if major else .14,'7':rgb[0],'8':rgb[1],'9':rgb[2],'52':0})

# All introduced art fades before the untouched next section.
for e in visual_shader_changes:
 o=dict(e['original']);o['2']=str(END);o['3']='1410';o['10']='0';o['20']='34';ADDED.append(o)
trigger(1007,START,**{'51':ROOTGROUP,'10':0,'35':1})
trigger(1007,END-90,**{'51':ROOTGROUP,'10':90/468,'35':0})
trigger(1007,END,**{'51':ROOTGROUP,'10':0,'35':0})

head=gdparse.parse_header(H);cs=head.get('kS38','').rstrip('|')
for cid,rgb in colors.items():
 op=0 if cid==620 else BLEND.get(cid,ALPHA.get(cid,1))
 cs+='|'+f'1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_6_{cid}_7_{op}_15_1_18_0_8_1_5_{1 if cid in BLEND else 0}'
head['kS38']=cs
raw=','.join(k+','+v for k,v in head.items())+';'+''.join(','.join(k+','+v for k,v in o.items())+';' for o in OUT+ADDED)
(HERE/'meltdown.level').write_text(raw)
fields=gmd.read_gmd(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
fields['k4']=('s',gmd.compress(raw));fields['k2']=('s','Factory Meltdown');fields['k48']=('i',str(len(OUT+ADDED)));fields['k1']=('i','0');fields['k16']=('i','0');fields['k42']=('i','148876671')
out=ROOT/'outputs/The Sinking Factory - MELTDOWN.gmd';gmd.write_gmd(out,fields)
manifest={'source_sha256':hashlib.sha256(Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd')).read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_objects':len(SRC),'added_objects':len(ADDED),'total_objects':len(OUT+ADDED),'scope':[START,END],'modified_original_objects':changes,'visual_trigger_changes':visual_shader_changes,'colors':colors,'groups':[600,nextgroup],'motions':motions,'measured_onsets':beats,'speed_schedule':schedule,'controls':[],'native_verified':False,'fixtures':fixtures,'emitters':emitters,'shallow_intro_preserved':len(shallow)}
(HERE/'meltdown-manifest.json').write_text(json.dumps(manifest,indent=2))
print({k:manifest[k] for k in ['added_objects','total_objects','groups','shallow_intro_preserved']});print(out)
