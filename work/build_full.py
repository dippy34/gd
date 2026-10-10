"""v8: recognizable musical chapters, gravity looms and moving scenery.
The source supplies song metadata. All gameplay changes are user-authorized.
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
from full_layout import build as layout_build
layout_objects,plan=layout_build()
ROUTE=plan
ROUTE['wave_sections']=[s for s in plan['sections'] if s['mode']=='wave']
base=[(','.join(f'{k},{v}' for k,v in o.items()),o) for o in layout_objects]
(ROOT/'work/full-plan.json').write_text(json.dumps(plan,indent=2))
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
    # Normalize export rounding at shared seams before computing the union.
    b=tuple(round(q,3) for q in (x-unit*sx/2,x+unit*sx/2,y-unit*sy/2,y+unit*sy/2))
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

def cy_at(x):return 150

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

# Material colors: opaque faces make mass readable; additive highlights define
# only the true collision boundaries and the light sources.
ROCK,FACE,BEVEL,SHADOW,CRYSTAL,AMBER,VIOLET=range(80,87)
COLORS.update({ROCK:((23,12,33),False),FACE:((39,22,49),False),
 BEVEL:((73,43,80),False),SHADOW:((8,5,16),False),CRYSTAL:((209,103,133),False),
 AMBER:((247,166,106),False),VIOLET:((98,53,128),False)})

def label(x,y,text,scale=.35,ch=STAR):
    o=add(580,x,y,ch,sx=scale,z=1,order=25,layer=18)
    o['31']=base64.urlsafe_b64encode(text.encode()).decode()

def halton(i,b):
    f=1;r=0
    while i:f/=b;r+=f*(i%b);i//=b
    return r

# The continuous nebula is retained, with chapter-scale changes in curvature.
for x in range(-240,math.ceil(END+450),110):
    t=tx(max(0,x));y=150+54*math.sin(x/1150)+28*math.sin(x/440)
    for dy,ch,v,r in [(-38,PURPLE,.13,145),(0,PINK,.075,118),(32,ORANGE,.055,95)]:
        glow(x,y+dy,r,ch,v,z=-5,order=-130,layer=11)
for i in range(1,math.ceil(END/5)):
    x=-150+halton(i,2)*(END+500);y=-10+halton(i,3)*330
    add(3625,x,y,STAR,sx=.025+.045*halton(i,5),value=.18+.35*halton(i,7),
        z=-5,order=-100,high=i%3==0,layer=11)

# A shared kinetic architecture gives the musical chapters a recognizable
# silhouette. These groups contain decoration only; collision objects are never
# moved or attached to the scenery. Black holes remain completely absent.
def move(t,g,dx,dy,duration,easing=13):
    trigger(901,xt(max(0,t)),**{'51':g,'28':dx,'29':dy,'10':duration,'30':easing})

def diamond(cx,cy,w,h,ch,**kw):
    points=[(cx,cy+h/2),(cx+w/2,cy),(cx,cy-h/2),(cx-w/2,cy),(cx,cy+h/2)]
    for aa,bb in zip(points,points[1:]):line(aa,bb,ch,**kw)

def charge_fins(t,strength=1):
    x=xt(t)+85;start=len(decos);groups=[]
    for sign in [-1,1]:
        g=group();groups.append(g);y=150+sign*113
        # Three solid, staggered vanes form a recognizable chevron bank.
        for i in range(3):
            xx=x-78+i*64;yy=y+sign*(i-1)*14
            rect(xx,yy,54,18,SHADOW,z=-3,order=-10,angle=-sign*18,group=g,layer=14)
            line((xx-25,yy-sign*8),(xx+26,yy+sign*8),GOLD,1,
                 z=-3,order=-7,value=.65,group=g,layer=14)
            glow(xx,yy,18,ORANGE,.16,z=-5,group=g,layer=14)
        move(t-2*BEAT,g,0,-sign*22*strength,2*BEAT)
        move(t,g,-26,sign*38*strength,3*BEAT)
    features.append(dict(kind='charging fins',time=t,x=x,groups=groups,objects=len(decos)-start))

def split_gate(beat,scale=1):
    t=PHASE+beat*BEAT;x=xt(t)+170;y=150;start=len(decos);members=[]
    diamond(x,y,310*scale,300,BEVEL,width=3,z=-5,order=-30,value=.55,layer=14)
    diamond(x,y,325*scale,310,GOLD,width=.8,z=-5,order=-29,value=.33,layer=14)
    for sign in [-1,1]:
        g=group();pivot=group();members.append(g);yy=y+sign*82
        add(1764,x,yy,INK,sx=.01,group=pivot,z=-5,layer=14)
        rect(x,yy,230*scale,34,SHADOW,z=-3,order=-14,group=g,layer=14)
        rect(x,yy+sign*7,210*scale,18,BEVEL,z=-3,order=-13,value=.45,group=g,layer=14)
        for side in [-1,1]:
            line((x+side*115*scale,yy),(x+side*25,yy-sign*38),GOLD,2,
                 z=-3,order=-10,value=.7,group=g,layer=14)
            glow(x+side*100*scale,yy,24,ORANGE,.20,z=-5,group=g,layer=14)
        move(t-4*BEAT,g,0,-sign*24,4*BEAT)
        move(t,g,0,sign*136,.40)
        move(t+.40,g,-28,sign*18,8*BEAT)
        # The pivot is fixed so the opening has a small hinged flourish.
        rotate(xt(t),g,pivot,sign*12,.40)
    pulse(t,GOLD,(255,218,163),fade=.55)
    features.append(dict(kind='split drop gate',beat=beat,time=t,x=x,groups=members,objects=len(decos)-start))

def lantern(t,long=False):
    x=xt(t)+90;anchor=308;y=177 if long else 211;g=group();pivot=group();start=len(decos)
    add(1764,x,anchor,INK,sx=.01,group=pivot,z=-5,layer=14)
    line((x,anchor),(x,y+23),BEVEL,1.2,z=-3,group=g,layer=14)
    diamond(x,y,30,48,GOLD,width=1.3,z=-3,value=.65,group=g,layer=14)
    add(3628,x,y+5,VIOLET,sx=.7,sy=.9,z=-3,order=-5,value=.55,group=g,layer=14)
    glow(x,y,30,PINK,.22,z=-5,group=g,layer=14)
    for dt,angle in [(0,-14),(3*BEAT,28),(6*BEAT,-14)]:
        rotate(xt(max(0,t-3*BEAT+dt)),g,pivot,angle,3*BEAT)
    features.append(dict(kind='pendulum lantern',time=t,x=x,groups=[g],pivot=pivot,objects=len(decos)-start))

for s in plan['sections']:
    length=s['t1']-s['t0']
    if s['chapter'] in ['THE LOOM','SUSPENSION'] or s['name']=='afterglow':
        lantern(s['t0']+length*.32,True)
        if length>8:lantern(s['t0']+length*.72)
    else:
        charge_fins(s['t0']+length*.28,.8 if s['speed_index']==1 else 1.3)
        if length>8:charge_fins(s['t0']+length*.72,1.3 if s['speed_index']>1 else 1)
for beat,scale in [(96,1),(288,1),(352,1.15),(608,1.05),(672,1.25)]:split_gate(beat,scale)

# Gravity looms share a pair of lit overhead rails. Their small chevrons pull
# in the same direction as the upcoming transfer, anticipating the mechanic.
for e in plan['gravity_events']:
    if e['source']!='blue orb':continue
    g=group();x=e['x'];sign=e['gravity'];yy=190 if sign>0 else 110;start=len(decos)
    for j in range(3):
        y=yy+sign*j*16
        line((x-17,y-sign*9),(x,y),PINK,1.4,z=-3,value=.55,group=g,layer=14)
        line((x,y),(x+17,y-sign*9),PINK,1.4,z=-3,value=.55,group=g,layer=14)
    move(e['time']-.5,g,0,sign*32,1.2)
    features.append(dict(kind='gravity cue',time=e['time'],x=x,groups=[g],objects=len(decos)-start))

# Carved block bodies. The hidden native collision blocks are dressed by this
# exact union, eliminating their stock grid texture and double internal edges.
for a,b,lo,hi in fills:
    lo=max(-48,lo);hi=min(355,hi)
    if b-a>.1 and hi>lo:rect((a+b)/2,(lo+hi)/2,b-a,hi-lo,ROCK,z=-1,order=-80,layer=15)
for a,b,lo0,hi0,kind in plan['rectangles']:
    lo=max(-43,lo0);hi=min(350,hi0)
    if hi-lo<10:continue
    # Panels follow the size and orientation of each real mass. Stepped side
    # faces and lit bevels give even the small islands a consistent material.
    n=max(1,math.ceil((b-a)/110));ww=(b-a)/n
    for j in range(n):
        left=a+j*ww+5;right=a+(j+1)*ww-5;bottom=lo+5;top=hi-5
        if right-left<12 or top-bottom<12:continue
        cx=(left+right)/2;cy=(top+bottom)/2;w=right-left;h=top-bottom
        rect(cx,cy,w,h,SHADOW,z=-1,order=-30,layer=15)
        rect(cx-1,cy+1,max(2,w-5),max(2,h-5),FACE,z=-1,order=-25,layer=15)
        bevel=min(8,w/4,h/4)
        line((left+bevel,top-2),(right-2,top-2),BEVEL,2,z=-1,order=-20,layer=15)
        line((right-2,bottom+bevel),(right-2,top-2),BEVEL,1.5,z=-1,order=-20,layer=15)
        # A single broad diagonal plane is an inset material facet, not a
        # repeated field of unconnected strokes.
        facet=add(693,cx,cy,VIOLET,sx=max(2,w-8)/30,sy=max(2,h-8)/30,
            z=-1,order=-22,value=.45,high=True,layer=15)
        if (j+int(a/90))%2:facet['4']='1'
        if w>30 and h>20:
            line((left+6,bottom+7),(min(right-6,left+w*.46),bottom+7),GOLD,.6,
                z=1,order=3,value=.4,high=True,layer=16)

for x0,y0,x1,y1,nx,ny in edges:
    if max(y0,y1)<-45 or min(y0,y1)>350:continue
    line((x0,y0),(x1,y1),EDGE,1.25,z=1,order=10,value=.85,layer=16)
    length=math.hypot(x1-x0,y1-y0)
    if length>24:
        for j in range(max(1,math.ceil(length/45))):
            q=(j+.5)/max(1,math.ceil(length/45))
            glow(x0+(x1-x0)*q-nx*3,y0+(y1-y0)*q-ny*3,9,HALO,.20,
                z=1,order=1,high=True,layer=16)

# Spike art exactly matches each hidden native spike's 30u triangle. The two
# solid facets and thin light edge distinguish it from a safe platform.
for h in plan['hazards']:
    x,y,sc=h['x'],h['y'],h['scale'];up=h['up'];ang=0 if up else 180
    add(3628,x,y,CRYSTAL,sx=sc,angle=ang,z=-1,order=40,layer=17)
    left=add(693,x-7.5*sc,y,VIOLET,sx=.5*sc,sy=sc,z=-1,order=41,layer=17)
    right=add(693,x+7.5*sc,y,AMBER,sx=.5*sc,sy=sc,z=-1,order=41,layer=17);right['4']='1'
    if not up:left['5']='1';right['5']='1'
    sign=1 if up else -1
    tip=(x,y+15*sc*sign)
    line((x-15*sc,y-15*sc*sign),tip,LIGHT,.7,z=1,order=20,value=.85,layer=17)
    line(tip,(x+15*sc,y-15*sc*sign),GOLD,.8,z=1,order=20,value=.8,layer=17)
    glow(*tip,4,LIGHT,.2,z=1,order=18,high=True,layer=17)

label(350,285,'OBSIDIAN CHOIR',.70)
label(350,259,'XTRULLOR / SUPERNOVA',.28)
for beat,_,title,_ in plan['chapters'][1:]:
    label(xt(PHASE+beat*BEAT)+220,306,title,.48)
label(END-230,155,'AFTERGLOW',.46);label(END-110,113,'GG',.65)

# Scene changes occur at musical phrases. Short pulses follow actual measured
# attacks, selecting strong transients rather than firing on an arbitrary loop.
chapters=[(0,(237,188,207),(145,62,120),(23,12,33)),
 (96,(255,216,165),(245,91,48),(32,14,29)),(160,(251,185,229),(215,53,147),(29,12,39)),
 (224,(218,198,249),(121,65,175),(18,13,34)),(288,(247,212,181),(225,80,71),(31,14,33)),
 (352,(255,228,174),(250,111,42),(35,16,27)),(416,(240,203,252),(166,60,197),(24,12,41)),
 (480,(255,195,212),(224,64,122),(31,12,37)),(560,(204,180,233),(117,53,164),(18,11,29)),
 (608,(250,202,232),(210,55,154),(29,11,37)),(672,(255,223,182),(253,110,61),(36,16,29)),
 (728,(208,174,224),(110,44,145),(17,9,27))]
for beat,edge,halo,body in chapters:
    x=xt(0 if beat==0 else PHASE+beat*BEAT)
    color(x,EDGE,edge,.6);color(x,HALO,halo,.6);color(x,ROCK,body,.6)
from full_layout import ONSETS
last=-10
for onset in ONSETS:
    t=onset['time']
    if t>plan['end_time']:break
    if onset['strength']>.10 and t-last>.24:
        pulse(t,EDGE,(255,229,212),fade=.18);pulse(t,HALO,(244,104,149),fade=.24);last=t
    if onset['strength']>.24:pulse(t,GOLD,(255,201,140),fade=.22)

H=parse_header(head);H.update({'kA2':'0','kA4':'0','kA3':'0','kA8':'0','kA10':'0','kA11':'0'})
H['kA14']=''.join(f'{PHASE+i*BEAT:.5f}~{1 if i%4==0 else 0.8}~' for i in range(737))
channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
for ch,(rgb,bl) in COLORS.items():
    channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':str(int(bl)),
        '6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
level=';'.join([serialize(H)]+[raw for raw,o in base]+[serialize(o) for o in decos+triggers])+';'
(ROOT/'work/v8-full.level').write_text(level)
fields['k2']=('s','v8');fields['k3']=('s',base64.urlsafe_b64encode(b'Obsidian Choir / Supernova by Xtrullor. Gravity looms, inverted flight, charging fins and gates that open on the drops. Seven modes. Chapter revision.').decode())
fields['k4']=('s',compress(level));fields['k48']=('i',str(len(base)+len(decos)+len(triggers)));fields['k14']=('f',False)
fields['k23']=('i','4');fields['k72']=('t',True)
write_gmd(ROOT/'outputs/v8-full.gmd',fields)
metrics.update(dict(total_objects=len(base)+len(decos)+len(triggers),gameplay_objects=len(base),
    decorations=len(decos),triggers=len(triggers),features=features,seconds=plan['end_time'],
    high_detail=sum(o.get('103')=='1' for o in decos)))
(ROOT/'work/full-build-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k!='features'},indent=2))
