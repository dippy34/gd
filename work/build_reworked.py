"""v8 / eclipse observatory. Fresh decoration on the supplied bare layout.

Geometry is computed from the exact source rectangles, not the handoff's 5u
occupancy approximation. Source object strings remain byte-for-byte intact.
"""
from pathlib import Path
import sys, math, random, json, base64, hashlib
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / 'work/handoff/tools'
sys.path.insert(0, str(TOOLS))
from gdparse import parse_header, parse_ks38
from gmd import read_gmd, decompress, compress, write_gmd

SOURCE = ROOT / 'work/handoff/OBSIDIAN-CHOIR.gmd'
ROUTE = json.loads((ROOT / 'work/handoff/level/route-and-beats.json').read_text())
fields = read_gmd(SOURCE)
original = decompress(fields['k4'][1])
head, *chunks = original.split(';')
source = []
for raw in chunks:
    if not raw: continue
    tokens = raw.split(',')
    source.append((raw, dict(zip(tokens[::2], tokens[1::2]))))
base = []
removed=[]
for raw,o in source:
    x=float(o['2'])
    old_deco=o.get('121')=='1' and o.get('134')=='1'
    visual=o['1'] in ('899','1006','901','1346','580')
    cube=(x<5680 or 7570<x<8830) and o['1'] in ('1','8','39','36','141')
    if old_deco or visual or cube:removed.append((raw,o))
    else:base.append((raw,o))
from cube_rework import build_cube
cube_objects,cube_plan=build_cube()
base.extend((','.join(f'{k},{v}' for k,v in o.items()),o) for o in cube_objects)
(ROOT/'work/cube-plan.json').write_text(json.dumps(cube_plan,indent=2))
rng = random.Random(83072)
tau = math.tau
decos, triggers, features = [], [], []
metrics = {}
BEAT, PHASE = ROUTE['beat'], ROUTE['phase']
SPEEDS = ROUTE['speed_schedule']
END = ROUTE['end_x']

def xt(t):
    return sum(max(0, min(t, SPEEDS[i+1][0] if i+1<len(SPEEDS) else t)-start)*v
               for i,(start,v) in enumerate(SPEEDS))

def tx(x):
    for i,(t,v) in enumerate(SPEEDS):
        x0 = xt(t)
        if i+1 == len(SPEEDS) or x < xt(SPEEDS[i+1][0]):
            return t + (x-x0)/v

def wave(x):
    return any(s['x0'] <= x <= s['x1'] for s in ROUTE['wave_sections'])

def fmt(x):
    if isinstance(x,float): return f'{x:.6f}'.rstrip('0').rstrip('.') or '0'
    return str(x)

def add(oid, x, y, color, z=-5, order=0, sx=1, sy=None, angle=0,
        value=1, group=None, high=False, layer=10):
    o={'1':oid,'2':x,'3':y,'21':color,'22':color,'24':z,'25':order,
       '20':layer,'64':1,'67':1,'96':1,'121':1,'134':1,
       '128':sx,'129':sx if sy is None else sy}
    if angle: o['6']=angle
    if value != 1:
        o.update({'41':1,'42':1,'43':f'0a1a{fmt(value)}a0a0','44':f'0a1a{fmt(value)}a0a0'})
    if group: o['57']='.'.join(map(str,group)) if isinstance(group,tuple) else group
    if high: o['103']=1
    decos.append({k:fmt(v) for k,v in o.items()})
    return decos[-1]

# All new opaque material uses -5/-3/-1; the sole positive layer is additive
# highlights. These channel roles are isolated from the old control tracks.
INK, WALL, PANEL, GHOST, STAR, EDGE, LIGHT, HALO, GOLD, LATTICE = range(60,70)
ORANGE,PINK,PURPLE,PLUM,STONE,SEAM=range(70,76)
COLORS = {
  1:((16,8,24),False), 2:((10,5,16),False), 3:((255,235,211),False),
  4:((238,209,237),True),
  INK:((0,0,0),False), WALL:((8,3,14),False), PANEL:((19,9,29),False),
  GHOST:((68,29,105),True), STAR:((214,180,234),True),
  EDGE:((255,181,104),True), LIGHT:((255,237,212),True),
  HALO:((197,62,89),True), GOLD:((255,139,61),True),
  LATTICE:((103,53,135),True),
  ORANGE:((255,102,32),True),PINK:((255,57,158),True),
  PURPLE:((130,66,255),True),PLUM:((33,9,54),False),
  STONE:((48,17,57),True),SEAM:((100,34,102),True),
  1000:((4,1,9),False),1001:((4,1,9),False),1002:((130,57,170),True),
  1004:((255,255,255),False),
}

def line(a,b,ch,width=.7,**kw):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    if length<.08: return
    # Small solid quads, capped at 120u: no empty gridLine sprites or huge culls.
    n=max(1,math.ceil(length/120))
    for i in range(n):
        t=(i+.5)/n
        add(211,a[0]+dx*t,a[1]+dy*t,ch,sx=(length/n+.03)/30,sy=width/30,
            angle=-math.degrees(math.atan2(dy,dx)),**kw)

def arc(cx,cy,r,ch,*,a0=0,span=tau,squash=1,width=.65,n=None,**kw):
    n=n or max(12,math.ceil(abs(span)*r/6))
    for i in range(n):
        a=a0+span*i/n;b=a0+span*(i+1)/n
        line((cx+r*math.cos(a),cy+r*math.sin(a)*squash),
             (cx+r*math.cos(b),cy+r*math.sin(b)*squash),ch,width,**kw)

def rect(x,y,w,h,ch,**kw):
    add(211,x,y,ch,sx=w/30,sy=h/30,**kw)

def glow(x,y,r,ch,value=.35,**kw):
    add(1888,x,y,ch,sx=r/20,value=value,**kw)

gid=1200
def group():
    global gid
    gid+=1
    return gid

def trigger(oid,x,**kw):
    o={'1':str(oid),'2':fmt(x),'3':'-450','20':'5'}
    o.update({k:fmt(v) for k,v in kw.items()})
    triggers.append(o)

def color(x,ch,rgb,duration=.45):
    trigger(899,x,**{'23':ch,'7':rgb[0],'8':rgb[1],'9':rgb[2],
                     '10':duration,'17':int(COLORS[ch][1]),'35':1})

def pulse(t,ch,rgb,hold=.035,fade=.24):
    trigger(1006,xt(t),**{'51':ch,'7':rgb[0],'8':rgb[1],'9':rgb[2],
                         '45':0,'46':hold,'47':fade,'48':0,'52':0})

def rotate(x,g,c,deg,duration):
    trigger(1346,x,**{'51':g,'71':c,'68':deg,'69':0,'10':duration,'30':0})

# Exact union sweep of the 7.5u, 15u and 30u source collision rectangles.
events=defaultdict(list)
rectangles=[]
for raw,o in base:
    if o['1'] not in ('1','1910'):continue
    unit=30 if o['1']=='1' else 15
    scale=float(o.get('32',1))
    sx=float(o.get('128',scale));sy=float(o.get('129',scale))
    x,y=float(o['2']),float(o['3'])
    b=tuple(round(q,6) for q in (x-unit*sx/2,x+unit*sx/2,y-unit*sy/2,y+unit*sy/2))
    rectangles.append(b)
    events[b[0]].append((1,b[2:]))
    events[b[1]].append((-1,b[2:]))

def merge(ints):
    out=[]
    for a,b in sorted(ints):
        if out and a <= out[-1][1]+1e-5:out[-1]=(out[-1][0],max(b,out[-1][1]))
        else:out.append((a,b))
    return out

def difference(left,right):
    out=[]
    for lo,hi in left:
        cursor=lo
        for a,b in right:
            if b<=cursor or a>=hi:continue
            if a>cursor:out.append((cursor,min(a,hi)))
            cursor=max(cursor,b)
            if cursor>=hi:break
        if cursor<hi:out.append((cursor,hi))
    return out

active=Counter();slabs=[];vertical=[];prev=[]
xs=sorted(events)
for j,x in enumerate(xs):
    for sign,iv in events[x]:
        active[iv]+=sign
        if active[iv]==0:del active[iv]
    current=merge(active)
    for a,b in difference(prev,current):vertical.append((x,a,x,b,1,0))
    for a,b in difference(current,prev):vertical.append((x,a,x,b,-1,0))
    if j+1<len(xs):slabs.append((x,xs[j+1],current))
    prev=current

horizontal=defaultdict(list)
for a,b,intervals in slabs:
    for lo,hi in intervals:
        horizontal[(lo,-1)].append((a,b));horizontal[(hi,1)].append((a,b))
edges=list(vertical)
for (y,normal),spans in horizontal.items():
    for a,b in merge(spans):edges.append((a,y,b,y,0,normal))
metrics['source_rectangles']=len(rectangles)
metrics['exact_exposed_segments']=len(edges)

def occupied(x,y,margin=0):
    # Exact slab test; used for wall insets, free-path avoidance and camera.
    import bisect
    i=max(0,min(len(slabs)-1,bisect.bisect_right(xs,x)-1))
    a,b,ivs=slabs[i]
    return a<=x<=b and any(lo+margin<=y<=hi-margin for lo,hi in ivs)

def cy_at(x):
    if not wave(x):return 95
    import bisect
    centers=[]
    for dx in [-90,-60,-30,0,30,60,90]:
        i=max(0,min(len(slabs)-1,bisect.bisect_right(xs,x+dx)-1))
        ivs=slabs[i][2]
        gaps=[(a[1],b[0]) for a,b in zip(ivs,ivs[1:]) if b[0]-a[1]>=35]
        if gaps:
            lo,hi=max(gaps,key=lambda g:g[1]-g[0]);centers.append((lo+hi)/2)
    return sum(centers)/len(centers) if centers else 170

# Merge exact wall spans horizontally, preserving every source boundary.
pending={};fills=[]
for a,b,ivs in slabs:
    new={}
    for iv in ivs:
        start=pending.pop(iv,a)
        if b-start>120:
            fills.append((start,a,*iv));start=a
        new[iv]=start
    for iv,start in pending.items():fills.append((start,a,*iv))
    pending=new
for iv,start in pending.items():fills.append((start,xs[-1],*iv))

def poly(points,ch,width=.7,**kw):
    for a,b in zip(points,points[1:]):line(a,b,ch,width,**kw)

def label(x,y,text,scale=.42,ch=LIGHT):
    o=add(580,x,y,ch,z=-1,sx=scale,layer=19)
    o['31']=base64.urlsafe_b64encode(text.encode()).decode()

# A continuous nebula follows the background's horizon, with a separate warm
# core and violet dust envelope. Every sample belongs to the same flowing form.
for k,x in enumerate(range(-240,int(END)+450,28)):
    cy=cy_at(x)
    if wave(x):
        yy=cy+75*math.sin(x/610)+38*math.sin(x/257)
        glow(x,yy,106,PURPLE,.15,z=-5,order=-150,layer=11,high=k%2==1)
        glow(x,yy+26,58,PINK,.17,z=-5,order=-145,layer=11,high=k%3==1)
        glow(x,yy-19,38,ORANGE,.19,z=-5,order=-140,layer=11,high=k%3==2)
    else:
        yy=12+28*math.sin(x/380)
        glow(x,yy,126,PURPLE,.11,z=-5,order=-150,layer=11,high=k%2==1)
        glow(x,yy-24,82,PINK,.08,z=-5,order=-145,layer=11)

# Small stars, restricted to the open sky. A deterministic low-discrepancy
# distribution prevents visible grids, without scattering unrelated motifs.
def halton(i,b):
    f=1;r=0
    while i:
        f/=b;r+=f*(i%b);i//=b
    return r
for i in range(1,2201):
    x=-180+halton(i,2)*(END+480)
    y=cy_at(x)+(halton(i,3)-.5)*330
    if occupied(x,y,0):continue
    size=.043+.035*halton(i,5)
    add(3625,x,y,STAR,sx=size,value=.35+.65*halton(i,7),z=-5,order=-90,high=i%3==0,layer=11)

# Ground remains a readable continuous surface in cube mode. These decorative
# strips coincide with y=0; raised platforms keep their separately lit tops.
for a,b in [(-180,5680),(7570,8830),(19555,END+240)]:
    for x in range(int(a),int(b),90):
        w=min(90,b-x)
        rect(x+w/2,-40,w,80,WALL,z=-1,order=-100,layer=15)
        line((x,0),(x+w,0),LATTICE,1.1,z=1,order=1,layer=16)
        line((x,-8),(x+w,-8),SEAM,.6,z=1,value=.42,high=True,layer=17)
        line((x,-8),(x,-52),SEAM,.6,z=1,value=.3,high=True,layer=17)

# Cube visual progression: ruined colonnade, suspended bridges, then the
# observatory's glowing reactor. Architecture lives above/below the jump lane.
for idx,p in enumerate(cube_plan['phrases']):
    x=p['start_x']+240
    if x>8800:continue
    style=idx%3
    if style==0:
        # Recessed arch, its base tied to the physical ground plane.
        for xx in [x-205,x+205]:
            rect(xx,115,16,230,PLUM,z=-3,order=-70,layer=12)
            rect(xx-4,115,2,230,PANEL,z=-3,order=-65,layer=12)
            line((xx-8,0),(xx-8,220),LATTICE,.7,z=-1,value=.32,layer=12)
        arc(x,218,205,LATTICE,a0=0,span=math.pi,squash=.3,width=.85,z=-5,value=.35,layer=12)
        arc(x,218,190,SEAM,a0=0,span=math.pi,squash=.3,width=.65,z=-5,value=.45,high=True,layer=12)
    elif style==1:
        # Suspended bridge cables follow one catenary-like sag above the lane.
        pts=[(x-210+i*15,249-23*math.sin(math.pi*i/28)) for i in range(29)]
        poly(pts,LATTICE,.6,z=-5,value=.5,layer=12)
        for dx in [-180,-120,-60,0,60,120,180]:
            y=249-23*math.sin(math.pi*(dx+210)/420)
            line((x+dx,y),(x+dx,270),SEAM,.6,z=-5,value=.5,layer=12)
    else:
        # Three receding arches create depth; no floating target reticles.
        for rad,val in [(205,.25),(168,.36),(131,.48)]:
            arc(x,202,rad,LATTICE,a0=0,span=math.pi,squash=.35,width=.7,z=-5,value=val,layer=12)

def blackhole(x,y,r,tilt,phase,kind):
    start=len(decos)
    pivot=group();dust=group()
    add(1764,x,y,INK,sx=.03,z=-5,group=pivot,layer=14)
    # Outer lens glow: a narrow luminous rim and a broad diffuse corona.
    for i in range(96):
        a=tau*i/96
        ch=ORANGE if math.cos(a-phase)>.35 else PINK if math.sin(a-phase)>.1 else PURPLE
        rr=r*(1.025+.012*math.sin(a*3))
        glow(x+rr*math.cos(a),y+rr*math.sin(a),r*.24,ch,.53,z=-5,order=-45,layer=14,high=i%3==1)
        glow(x+r*1.08*math.cos(a),y+r*1.08*math.sin(a),r*.43,ch,.17,z=-5,order=-50,layer=14,high=i%2==1)
    # The aperture is truly black and lies behind the real collision geometry.
    add(1764,x,y,INK,sx=r/4,z=-3,order=-20,layer=14)
    arc(x,y,r*1.002,LIGHT,width=.58,z=-1,order=-48,layer=14,value=.78)
    arc(x,y,r*1.02,ORANGE,a0=phase,span=1.7,width=1.2,z=-1,order=-46,layer=14)
    arc(x,y,r*1.024,PINK,a0=phase+1.7,span=2.1,width=1.0,z=-1,order=-46,layer=14)
    arc(x,y,r*1.03,PURPLE,a0=phase+3.8,span=2.45,width=1.05,z=-1,order=-46,layer=14)
    # A flattened accretion disc crosses the core in the background plane.
    # Twist is spatially constant, while the radial wisps rotate very slowly.
    theta=math.radians(tilt)
    def disc(a,rr,sy):
        dx=rr*math.cos(a);dy=rr*sy*math.sin(a)
        return x+dx*math.cos(theta)-dy*math.sin(theta),y+dx*math.sin(theta)+dy*math.cos(theta)
    for band in range(7):
        rr=r*(1.48+band*.048);sy=.17+band*.009
        if kind=='pink collapse':sy=.48+band*.014
        if kind=='purple singularity':sy=.075+band*.006
        ch=[ORANGE,ORANGE,LIGHT,PINK,PINK,PURPLE,PURPLE][band]
        pts=[disc(tau*i/128,rr,sy) for i in range(129)]
        for i,(a,b) in enumerate(zip(pts,pts[1:])):
            front=i>=64
            line(a,b,ch,.6 if band!=2 else 1.0,z=-1 if front else -5,
                 order=-30 if front else -35,layer=14,value=.68 if band==2 else .55,
                 high=band in [1,3,5])
        if band in [0,3,6]:
            for i in range(0,128,3):
                xx,yy=pts[i]
                glow(xx,yy,7,ch,.48,z=-1 if i>=64 else -5,order=-35,
                     layer=14,high=i%2==0)
    # Spiral infall: broken arcs follow the same gravitational centre.
    for k in range(4):
        for j in range(36):
            a=phase+k*math.pi/2+j*.033
            rr=r*(1.45+j*.012)
            aa=a+.025;rr2=rr+r*.009
            line((x+rr*math.cos(a),y+rr*math.sin(a)),
                 (x+rr2*math.cos(aa),y+rr2*math.sin(aa)),
                 PINK if k%2 else PURPLE,.5,z=-5,order=-60,value=.24,
                 group=dust,high=j%2==1,layer=14)
    if kind=='purple singularity':
        # Twin polar jets make the last landmark a quasar, rather than another
        # identical ring. The jets start outside the black aperture.
        for side in [-1,1]:
            for j in range(12):
                yy=y+side*r*(1.15+j*.07)
                glow(x,yy,18-j*.8,PURPLE,.22,z=-5,order=-70,layer=14,high=j%2==1)
                glow(x,yy,7-j*.25,PINK,.2,z=-5,order=-65,layer=14,high=j%2==1)
    if kind=='coronal bloom':
        for k in range(3):
            arc(x,y,r*(1.28+k*.13),PINK if k%2 else ORANGE,
                a0=.4+k*.12,span=2.3,width=.6,z=-5,value=.2,high=k>0,layer=14)
    rotate(max(0,x-650),dust,pivot,16 if phase<2 else -16,5)
    features.append({'kind':kind,'x':x,'y':y,'radius':r,'objects':len(decos)-start,'time':tx(x)})

# Celestial landmarks are composed for phrases, with different size, disc
# inclination and luminosity. They replace the previous instrument glyphs.
blackhole(1970,164,57,-16,.5,'distant sunrise')
blackhole(4650,173,71,12,2.1,'first contact')
blackhole(6590,cy_at(6590),89,-10,1.5,'teaser singularity')
blackhole(8170,165,91,0,.4,'ignition')
for x,r,tilt,phase,name in [
    (9572,102,-8,.3,'orange accretion'),
    (11280,79,18,1.6,'tilted pink lens'),
    (12600,111,-13,2.4,'violet event horizon'),
    (14520,119,6,.8,'coronal bloom'),
    (16280,87,-22,2.6,'pink collapse'),
    (17880,122,14,3.3,'purple singularity'),
    (19090,67,-8,1.2,'fading ember')]:
    blackhole(x,cy_at(x),r,tilt,phase,name)
blackhole(11490,cy_at(11490)+15,36,-16,2.3,'binary companion')

# Exact wall masses and the measured collision silhouette. The tiled layout is
# subdued; the continuous outer edge provides the primary navigation cue.
for a,b,lo,hi in fills:
    if b-a>.001:rect((a+b)/2,(lo+hi)/2,b-a,hi-lo,WALL,z=-1,order=-90,layer=15)
for x0,y0,x1,y1,nx,ny in edges:
    if max(y0,y1)<.01:continue
    line((x0,y0),(x1,y1),EDGE,1.65,z=1,order=8,layer=16)
    length=math.hypot(x1-x0,y1-y0)
    if length>12:
        n=max(1,math.ceil(length/24))
        for i in range(n):
            t=(i+.5)/n
            glow(x0+(x1-x0)*t-nx*3,y0+(y1-y0)*t-ny*3,8,HALO,.3,z=1,order=1,high=True,layer=16)

# Obsidian strata: diagonal seams live entirely within solid walls, checked at
# every 2 units. Their warmer intersections echo the accretion-disc material.
for x in range(5800,19500,56):
    if not wave(x):continue
    for y in range(25,360,36):
        pts=[(x-18+36*i/18,y-9+18*i/18) for i in range(19)]
        if not all(occupied(xx,yy,5) for xx,yy in pts):continue
        line(pts[0],pts[-1],SEAM,.65,z=1,order=2,value=.7,high=True,layer=17)
        if (x//56+y//36)%3==0:
            line((x-8,y-4),(x+4,y+2),GOLD,.7,z=1,order=3,value=.3,high=True,layer=17)

# Physical cube platforms receive recessed panels, lit top lips, and grounded
# piers. Details are derived from the new platform faces, never arbitrary boxes.
for a,b,bottom,top in cube_plan['platforms']:
    if bottom>=130:continue
    for xx in range(math.ceil(a+16),int(b-12),44):
        if xx+18>b:continue
        yy=top/2
        w=min(30,b-xx-4)
        rect(xx,yy,w,max(6,top-12),PANEL,z=-1,order=-15,layer=15)
        poly([(xx-w/2+4,7),(xx-w/2+4,top-8),(xx+w/2-4,top-8)],LATTICE,.65,z=1,value=.42,layer=17)
    line((a+3,top-3),(b-3,top-3),GOLD,.7,z=1,value=.65,layer=17)
    # Non-colliding foundation lies below the ground.
    rect((a+b)/2,-10,b-a,20,PLUM,z=-1,order=-20,layer=12)
    line((a,-20),(b,-20),LATTICE,.65,z=-1,value=.5,layer=12)

# Minimal titles use the native font, placed beyond the cube's highest arc.
label(365,237,'OBSIDIAN CHOIR',.70)
label(365,207,'XTRULLOR / SUPERNOVA',.31,ch=STAR)
label(1355,246,'I / ASCENT',.35,ch=STAR)
label(5880,326,'II / EVENT HORIZON',.33,ch=STAR)
label(7850,256,'III / IGNITION',.35,ch=STAR)
label(9170,336,'IV / SUPERNOVA',.38,ch=STAR)
label(19720,171,'AFTERGLOW',.58,ch=STAR)
label(20000,113,'GG',.75)

# Music-synced material changes; warm and cool discs remain multicoloured.
# Colour progression is phrase-based. Pulses never reset the whole scene white.
states=[
 (0,(255,223,190),(149,57,103),(25,12,38)),
 (11.428,(255,207,186),(179,47,111),(34,12,48)),
 (22.722,(255,215,249),(151,58,174),(40,15,56)),
 (28.369,(255,218,175),(192,59,83),(38,15,43)),
 (34.016,(255,229,187),(244,77,58),(50,20,31)),
 (39.663,(255,206,239),(205,47,154),(48,15,57)),
 (45.310,(234,213,255),(129,61,216),(32,19,64)),
 (50.957,(255,215,192),(228,54,113),(46,14,46)),
 (54.134,(244,214,255),(128,48,201),(37,15,67)),
 (56.605,(173,136,205),(98,38,137),(10,4,18)),
]
for t,ed,ha,body in states:
    color(xt(t),EDGE,ed,.65);color(xt(t),HALO,ha,.85)
    color(xt(t),1,body,.85)
    color(xt(t),2,tuple(int(v*.65) for v in body),.85)
for i in range(168):
    t=PHASE+i*BEAT
    if t>tx(END):break
    if i%4==0:
        rgb=(255,237,213) if i<112 or 144<=i else (244,219,255)
        pulse(t,EDGE,rgb,fade=.28)
    if i%8==0:
        pulse(t,HALO,(228,86,150),fade=.42)
    if i%8==4 and t>22:
        pulse(t,GOLD,(255,181,95),fade=.34)

H=parse_header(head)
channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
for ch,(rgb,bl) in COLORS.items():
    channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':str(int(bl)),
                  '6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
newhead=','.join(f'{k},{v}' for k,v in H.items())
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
level=';'.join([newhead]+[raw for raw,o in base]+[serialize(o) for o in decos+triggers])+';'
(ROOT/'work/v8.level').write_text(level)
fields['k2']=('s','v8')
fields['k3']=('s',base64.urlsafe_b64encode(b'Obsidian Choir v8. Orange, pink and violet singularities. Rebuilt cube gameplay. Original wave route. Xtrullor - Supernova.').decode())
fields['k4']=('s',compress(level));fields['k48']=('i',str(len(base)+len(decos)+len(triggers)))
fields['k14']=('f',False)
write_gmd(ROOT/'outputs/v8.gmd',fields)
metrics.update({'name':'v8','source_objects':len(source),'removed_source_objects':len(removed),
    'new_cube_objects':len(cube_objects),'new_decorations':len(decos),'new_triggers':len(triggers),
    'total_objects':len(base)+len(decos)+len(triggers),'features':features,
    'cube_phrases':len(cube_plan['phrases']),'cube_inputs':len(cube_plan['inputs']),
    'high_detail_objects':sum(o.get('103')=='1' for o in decos)})
(ROOT/'work/build-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k!='features'},indent=2))
