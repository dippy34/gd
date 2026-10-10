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
base = [(raw,o) for raw,o in source if not (o.get('121') == '1' and o.get('134') == '1')]
rng = random.Random(83071)
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
INK, WALL, PANEL, GHOST, STAR, EDGE, LIGHT, HALO, GOLD, LATTICE = range(30,40)
COLORS = {
  1:((9,17,23),False), 2:((6,11,17),False), 3:((255,245,219),False),
  4:((110,146,157),False),
  INK:((1,3,6),False), WALL:((4,8,13),False), PANEL:((12,22,29),False),
  GHOST:((34,64,83),True), STAR:((220,230,238),True),
  EDGE:((142,223,229),True), LIGHT:((233,245,237),True),
  HALO:((43,115,136),True), GOLD:((221,155,76),True),
  LATTICE:((46,81,92),True),
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

# Continuous star backdrop, limited to the camera band. 12 compact stars per
# clump, same 0.051 baseline as the measured reference, plus sparse bright stars.
for k,x0 in enumerate(range(-180,int(END)+1,150)):
    cy=cy_at(x0+75)
    for j in range(2):
        cx=x0+rng.uniform(10,135);yy=cy+rng.uniform(-130,142)
        for n in range(12):
            theta=rng.random()*tau;rad=math.sqrt(rng.random())*rng.uniform(11,24)
            x=cx+rad*math.cos(theta);y=yy+rad*math.sin(theta)*.65
            add(3625,x,y,STAR,sx=.051 if n%4 else .079,z=-5,order=-100,
                value=rng.uniform(.65,1),angle=rng.uniform(-35,35),high=n>5,layer=11)
    for n in range(4):
        x=x0+rng.uniform(0,150);y=cy+rng.uniform(-154,154)
        add(3625,x,y,STAR,sx=.062,z=-5,order=-100,value=.8,high=n>1,layer=11)
    if k%3==1:
        x=x0+62;y=cy+110*math.sin(k*2.1)
        add(3625,x,y,LIGHT,sx=.083,z=-5,order=-70,layer=11)
        glow(x,y,9,STAR,.34,z=-5,order=-75,high=True,layer=11)
    # Low-contrast atmospheric shelf, anchored to the measured camera. Compact
    # overlapping radial sprites avoid a visible rectangle or overscale cutoff.
    glow(x0+75,cy-65,116,GHOST,.28,z=-5,order=-120,high=True,layer=11)
    glow(x0+75,cy+95,78,GHOST,.12,z=-5,order=-120,high=True,layer=11)

# Three-depth floor/ceiling architecture, deliberately quiet and inset from the
# cube's jump lane. Rhythm is based on an 8-beat phrase, never random placement.
for t in [PHASE+i*8*BEAT for i in range(21)]:
    x=xt(t)
    if x>END-150:continue
    cy=cy_at(x)
    if not wave(x):
        for side in (-1,1):
            yy=-42 if side<0 else 254
            line((x-76,yy),(x+76,yy),LATTICE,.55,z=-5,order=-50,layer=12)
            line((x-76,yy),(x-90,yy+side*15),LATTICE,.55,z=-5,order=-50,layer=12)
            for dx in (-62,-31,0,31,62):
                line((x+dx,yy),(x+dx,yy+side*5),LATTICE,.6,z=-5,order=-50,layer=12)

def eclipse(x,cy,r,variant,label):
    start=len(decos)
    center=group();spin=group();outer=group()
    # A single invisible/no-touch pivot in its own group, as in the reference.
    add(1764,x,cy,INK,sx=.05,z=-5,group=center,layer=14)
    # Broad corona: subdued, spatially continuous; grouped dust has differential
    # angular speeds like the measured 109/113/114 reference groups.
    for i in range(36):
        a=tau*i/36
        rr=r*(1.17+.07*math.sin(a*3+variant))
        glow(x+rr*math.cos(a),cy+rr*math.sin(a),r*.21,HALO,.26,
             z=-5,order=-40,group=outer,high=i%2==1,layer=14)
    # Measured reference group 114 is a narrow annulus, separate from its broad
    # 109/113 corona. Put the luminous inner annulus behind the dark aperture.
    for i in range(72):
        a=tau*i/72
        glow(x+r*1.035*math.cos(a),cy+r*1.035*math.sin(a),r*.17,
             EDGE,.42+.2*math.sin(a+.7),z=-5,order=-25,group=outer,
             high=i%3==1,layer=14)
    # Exact dark aperture masks the starfield; keep the core in LDM.
    add(1764,x,cy,INK,sx=r/4,z=-3,order=0,layer=14)
    # Crisp main rim stays behind the corridor's opaque wall mass.
    arc(x,cy,r*1.012,EDGE,width=.64,z=-1,order=-30,layer=14)
    arc(x,cy,r*1.06,LIGHT,width=.85,a0=.15+variant*.3,span=1.0,z=-1,order=-28,layer=14)
    arc(x,cy,r*1.045,GOLD,width=.55,a0=3.0,span=.75,z=-1,order=-28,layer=14)
    # Two asymmetric annuli and only a handful of satellite marks.
    for i in range(18):
        a=tau*i/18+.2
        arc(x,cy,r*1.28,LATTICE,width=.5,a0=a,span=.17,z=-1,order=-35,
            group=spin,high=True,layer=14)
        if i%3==0:
            line((x+math.cos(a)*r*1.32,cy+math.sin(a)*r*1.32),
                 (x+math.cos(a)*r*1.4,cy+math.sin(a)*r*1.4),GOLD,.6,
                 z=-1,order=-34,group=spin,layer=14)
    if variant in (1,3):
        # Thin lens-disc, split at the core: three curves instead of a solid
        # glowing bar crossing the entire playable corridor.
        for dy in (-2,0,2):
            arc(x,cy+dy,r*1.72,HALO,a0=0,span=math.pi,squash=.23,width=.8,
                z=-5,order=-20,value=.6,high=dy!=0,layer=14)
        arc(x,cy,r*1.72,EDGE,a0=math.pi,span=math.pi,squash=.23,width=.7,
            z=-1,order=-15,value=.65,layer=14)
        for i in range(48):
            a=tau*i/48
            xx=x+r*1.72*math.cos(a);yy=cy+r*.23*math.sin(a)
            front=a>=math.pi
            glow(xx,yy,8,HALO,.5,z=-1 if front else -5,order=-18,
                 high=i%2==1,layer=14)
    elif variant==2:
        # An instrument's orbital tracks; the empty core remains the focal point.
        arc(x,cy,r*1.65,LATTICE,squash=.53,width=.6,a0=-.25,span=2.4,
            z=-1,order=-35,high=True,layer=14)
    for a in [1.1+variant,.15+variant*1.7]:
        px=x+math.cos(a)*r*1.45;py=cy+math.sin(a)*r*1.45
        add(1764,px,py,LIGHT,sx=.36,z=-1,order=-10,group=spin,layer=14)
        glow(px,py,6,HALO,.4,z=-1,order=-15,group=spin,high=True,layer=14)
    activation=max(0,x-520)
    rotate(activation,spin,center,28 if variant%2 else -22,4)
    rotate(activation,outer,center,-12,4)
    features.append({'kind':label,'x':x,'y':cy,'radius':r,'camera_y':cy_at(x),
                     'objects':len(decos)-start,'time':tx(x),'groups':[center,spin,outer]})

def instrument(x,y,r,variant):
    start=len(decos)
    arc(x,y,r,LATTICE,width=.6,z=-5,order=-40,layer=13)
    for j in range(4):
        a=j*math.pi/2+.4
        arc(x,y,r*1.13,EDGE,a0=a,span=.35,width=.6,value=.5,z=-5,order=-35,layer=13)
    arc(x,y,r*.66,LATTICE,width=.5,a0=.1,span=4.6,z=-5,order=-35,layer=13,high=True)
    for j in range(4):
        a=j*math.pi/2
        p=(x+math.cos(a)*r*.22,y+math.sin(a)*r*.22)
        q=(x+math.cos(a)*r*.4,y+math.sin(a)*r*.4)
        line(p,q,GOLD,.6,z=-5,order=-30,layer=13)
    add(3625,x,y,LIGHT,sx=.13,z=-5,order=-20,layer=13)
    glow(x,y,10,HALO,.6,z=-5,order=-25,layer=13)
    # A sparse constellation and scale ticks give the instrument a purpose.
    pts=[(-.52,.20),(-.18,.49),(.30,.26),(.54,-.15),(.06,-.40)]
    for j,(a,b) in enumerate(zip(pts,pts[1:])):
        p=(x+a[0]*r,y+a[1]*r);q=(x+b[0]*r,y+b[1]*r)
        line(p,q,LATTICE,.5,z=-5,order=-20,layer=13)
    for u,v in pts:
        add(3625,x+u*r,y+v*r,LIGHT,sx=.065,z=-5,order=-15,layer=13)
    for j in range(24):
        a=tau*j/24
        rr=r*(.96 if j%3 else .93)
        line((x+rr*math.cos(a),y+rr*math.sin(a)),
             (x+r*math.cos(a),y+r*math.sin(a)),LATTICE,.5,z=-5,order=-25,high=True,layer=13)
    features.append({'kind':'observatory reticle','x':x,'y':y,'radius':r,
                     'camera_y':cy_at(x),'objects':len(decos)-start,'time':tx(x)})

# Authored landmark sequence: establish, reveal, eclipse, compress, then alternate
# dark apertures and open star charts during the fast wave passage.
instrument(1080,154,60,0)
eclipse(2220,158,61,0,'first eclipse')
instrument(3490,138,83,1)
eclipse(4780,151,78,2,'observatory aperture')
eclipse(6590,cy_at(6590)+4,68,0,'wave teaser eclipse')
eclipse(8180,160,84,1,'pre-drop lens')
drop=ROUTE['wave_sections'][1]
for i in range(8):
    t=drop['t0']+(i+.52)*8*BEAT
    x=xt(t);cy=cy_at(x)
    if i in (0,2,4,6):
        eclipse(x,cy,83 if i<6 else 99,[3,0,1,3][i//2],
                'drop eclipse '+str(i//2+1))
    else:
        instrument(x,cy,94 if i==7 else 72,i)
instrument(19810,127,58,0)

# Distant observatory bays. The gap between stations is intentionally larger than
# the viewport, so a bay is a composed place, not a repeated screen overlay.
for x in [1360,3690,5380,7870]:
    cy=95
    # Dark support pylons and narrow lit edges, behind the original obstacles.
    for side in [-1,1]:
        px=x+side*135
        rect(px,116,18,232,PANEL,z=-3,order=-60,layer=12)
        line((px-side*7,10),(px-side*7,220),LATTICE,.65,z=-1,order=-60,layer=12,value=.5)
        line((px,220),(x+side*92,244),LATTICE,.65,z=-1,order=-60,layer=12,value=.5)
        for yy in [40,100,160,215]:
            line((px-4,yy),(px+4,yy),GOLD,.65,z=-1,order=-55,value=.3,layer=12)
    line((x-92,244),(x+92,244),LATTICE,.65,z=-1,order=-60,value=.5,layer=12)
    # Indented lintel plates offer a different silhouette from the circular sky.
    rect(x,237,82,8,PANEL,z=-3,order=-55,layer=12)
    line((x-41,233),(x+41,233),GOLD,.65,z=-1,order=-50,value=.45,layer=12)

# Exact wall material. All fills are behind the original gameplay objects.
for a,b,lo,hi in fills:
    if b-a<.001:continue
    rect((a+b)/2,(lo+hi)/2,b-a,hi-lo,WALL,z=-1,order=-90,layer=15)

# The rim is the collision silhouette, including every 7.5-unit step. No
# simplification that might falsely imply a wider safe corridor.
for x0,y0,x1,y1,nx,ny in edges:
    if max(y0,y1)<1:continue
    a,b=(x0,y0),(x1,y1)
    line(a,b,EDGE,.65,z=1,order=5,layer=16)
    length=math.hypot(x1-x0,y1-y0)
    if length>9:
        # Place halo on the solid side of the exposed edge.
        n=max(1,math.ceil(length/22))
        for i in range(n):
            t=(i+.5)/n
            glow(x0+(x1-x0)*t-nx*2.5,y0+(y1-y0)*t-ny*2.5,7,HALO,.24,
                 z=1,order=0,high=True,layer=16)

# Large, quiet machinery panels inside the measured solid walls. Subordinate
# luminance and one detail per 120u prevents the source tile grid taking over.
for x in range(5860,int(END),75):
    if not wave(x):continue
    for y in range(22,352,25):
        if not all(occupied(x+dx,y+dy,2) for dx in [-10,0,10] for dy in [-5,5]):continue
        line((x-9,y-4),(x+9,y-4),LATTICE,.65,z=1,order=1,value=.85,high=True,layer=17)
        line((x-9,y-4),(x-9,y+4),LATTICE,.65,z=1,order=1,value=.85,high=True,layer=17)
        line((x+9,y-4),(x+9,y+4),LATTICE,.65,z=1,order=1,value=.85,high=True,layer=17)
        if (x//75)%2==0:
            line((x-6,y+4),(x,y+4),GOLD,.8,z=1,order=2,value=.55,layer=17)

# Cube structures: discrete support brackets derived from actual overhead block
# clusters, all decorative and behind the jump/orb lane.
for raw,o in base:
    if o['1']!='1':continue
    x,y=float(o['2']),float(o['3'])
    if wave(x):continue
    line((x-10,y+10),(x+10,y+10),LIGHT,.65,z=1,order=6,value=.9,layer=16)
    line((x-10,y-9),(x+10,y-9),LATTICE,.65,z=1,order=6,layer=16)
    line((x-10,y-9),(x-10,y+6),LATTICE,.65,z=1,order=6,layer=16)
    line((x+10,y-9),(x+10,y+6),LATTICE,.65,z=1,order=6,layer=16)
    for dx in [-11,11]:
        add(1764,x+dx,y+11,GOLD,sx=.16,z=1,order=8,layer=16)
    if y>112:
        line((x,y+15),(x,y+40),LATTICE,.8,z=-1,order=-40,layer=12)
        line((x-5,y+40),(x+5,y+40),GOLD,.65,z=-1,order=-35,layer=12)

# Preserve original controls, but supersede their obsolete wall-color track a
# fraction of a unit later. Only channel appearance changes; source controls do
# not acquire new motion targets and no gameplay object gains a group.
for raw,o in base:
    if o['1']=='899' and o.get('23') in ('1','2'):
        ch=int(o['23']);color(float(o['2'])+.01,ch,COLORS[ch][0],0)

# Four coherent palette states. No whiteout shader, shake or visibility tricks.
states=[
 (ROUTE['wave_sections'][0]['t0'],(156,218,229),(51,111,134),(225,160,78)),
 (SPEEDS[2][0],(120,151,183),(36,66,103),(155,114,69)),
 (drop['t0'],(215,239,242),(74,137,162),(248,189,98)),
 (drop['t0']+16*BEAT,(161,211,233),(42,96,144),(225,160,78)),
 (drop['t0']+32*BEAT,(166,182,225),(57,73,139),(232,165,90)),
 (drop['t0']+48*BEAT,(239,218,172),(130,91,45),(250,209,133)),
 (SPEEDS[-1][0],(203,223,209),(64,112,111),(209,163,97)),
]
for t,edge,halo,gold in states:
    for ch,rgb in [(EDGE,edge),(HALO,halo),(GOLD,gold)]:color(xt(t),ch,rgb,.7)

for i in range(166):
    t=PHASE+i*BEAT
    if t>tx(END):break
    if i%4==0:
        pulse(t,EDGE,(226,243,235),fade=.23 if t>=drop['t0'] else .32)
    if i%8==0:
        pulse(t,HALO,(95,151,163),fade=.42)
    if i%16==8:
        pulse(t,GOLD,(247,204,135),fade=.34)

H=parse_header(head)
channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
for ch,(rgb,bl) in COLORS.items():
    channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1',
                  '5':str(int(bl)),'6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
newhead=','.join(f'{k},{v}' for k,v in H.items())
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
level=';'.join([newhead]+[raw for raw,o in base]+[serialize(o) for o in decos+triggers])+';'
(ROOT/'work/v8.level').write_text(level)
fields['k2']=('s','v8')
fields['k3']=('s',base64.urlsafe_b64encode(b'Obsidian Choir. Eclipse observatory decoration on the original cube/wave layout. Xtrullor - Supernova.').decode())
fields['k4']=('s',compress(level))
fields['k48']=('i',str(len(base)+len(decos)+len(triggers)))
# Imported local draft: never claim that the player has verified the level.
fields['k14']=('f',False)
write_gmd(ROOT/'outputs/v8.gmd',fields)
metrics.update({'name':'v8','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
 'source_objects':len(source),'preserved_objects':len(base),'removed_old_decorations':len(source)-len(base),
 'new_decorations':len(decos),'new_triggers':len(triggers),'total_objects':len(base)+len(decos)+len(triggers),
 'high_detail_objects':sum(o.get('103')=='1' for o in decos),
 'exact_wall_fill_rectangles':len(fills),'features':features,
 'decoration_ids':dict(Counter(o['1'] for o in decos))})
(ROOT/'work/build-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k!='features'},indent=2))
