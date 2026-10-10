"""v8: rebuilt mixed-mode gameplay and moving, clean-aperture singularities.
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
from balanced_layout import build as layout_build
layout_objects,plan=layout_build()
ROUTE=plan
ROUTE['wave_sections']=[s for s in plan['sections'] if s['mode']=='wave']
base=[(','.join(f'{k},{v}' for k,v in o.items()),o) for o in layout_objects]
(ROOT/'work/balanced-plan.json').write_text(json.dumps(plan,indent=2))
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

def cy_at(x):return 165

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

def label(x,y,text,scale=.4,ch=STAR):
    o=add(580,x,y,ch,sx=scale,z=1,order=12,layer=18)
    o['31']=base64.urlsafe_b64encode(text.encode()).decode()

def halton(i,base):
    f=1;r=0
    while i:
        f/=base;r+=f*(i%base);i//=base
    return r

# Broad, quiet nebula behind the entire route. The curve is continuous across
# mode changes, so each gameplay section belongs to the same place.
for x in range(-200,math.ceil(END+500),95):
    y=165+64*math.sin(x/980)+22*math.sin(x/310)
    for dy,ch,v,r in [(-34,PURPLE,.105,138),(0,PINK,.075,110),(30,ORANGE,.055,90)]:
        glow(x,y+dy,r,ch,v,z=-5,order=-110,layer=11)
for i in range(1,3201):
    x=-200+halton(i,2)*(END+700);y=12+halton(i,3)*306
    # Small stars remain subordinate to the navigable edge and the landmarks.
    add(3625,x,y,STAR,sx=.025+.035*halton(i,5),value=.18+.36*halton(i,7),
        z=-5,order=-90,high=i%3==0,layer=11)

def moving_hole(t,r,tilt,ch):
    x=xt(t);y=165+12*math.sin(t*.4);g=group();start=len(decos)
    # A smooth native 30u circle replaces the former 8u pixelated small ball.
    # Every part shares one translation group; nothing rotates independently.
    for k in range(48):
        a=tau*k/48;cc=ORANGE if math.cos(a)>.35 else PINK if math.sin(a)>.05 else PURPLE
        glow(x+r*1.01*math.cos(a),y+r*1.01*math.sin(a),r*.25,cc,.28,
             group=g,z=-5,order=-60,layer=14)
        if k%2==0:
            glow(x+r*1.04*math.cos(a),y+r*1.04*math.sin(a),r*.52,cc,.12,
                 group=g,z=-5,order=-70,layer=14,high=True)
    # One broad accretion disc, behind the aperture. No bright bands cross it.
    add(3621,x,y,PURPLE,sx=r*1.90/15,sy=r*.24/15,angle=tilt,value=.24,
        group=g,z=-5,order=-58,layer=14)
    add(3621,x,y,PINK,sx=r*1.80/15,sy=r*.115/15,angle=tilt,value=.42,
        group=g,z=-5,order=-57,layer=14)
    add(3621,x,y,ORANGE,sx=r*1.75/15,sy=r*.044/15,angle=tilt,value=.8,
        group=g,z=-5,order=-56,layer=14)
    add(3621,x,y,LIGHT,sx=(r+1.0)/15,value=.72,group=g,z=-5,order=-45,layer=14)
    add(3621,x,y,INK,sx=r/15,group=g,z=-3,order=-30,layer=14)
    # The full feature drifts right and bobs. Motion begins before it enters the
    # viewport and continues until it leaves, without a loop/spawn dependency.
    onset=max(0,t-1.90);moves=[(4*BEAT,64,23),(4*BEAT,-20,-46),(4*BEAT,64,23)]
    offset=0
    for duration,dx,dy in moves:
        trigger(901,xt(onset+offset),**{'51':g,'28':dx,'29':dy,'10':duration,'30':13})
        offset+=duration
    features.append({'kind':'moving singularity','time':t,'x':x,'y':y,'radius':r,
        'group':g,'objects':len(decos)-start,'onset':onset,'moves':moves})

for t,r,tilt,ch in [(3.8,70,-12,PURPLE),(9.1,77,10,PINK),
    (15.0,83,-9,ORANGE),(20.0,69,16,PINK),(25.7,82,-13,PURPLE),
    (31.2,76,7,ORANGE),(35.8,90,-10,ORANGE),(41.5,83,14,PINK),
    (47.8,79,-16,PURPLE),(53.4,86,9,PINK),(57.5,61,-7,ORANGE)]:
    moving_hole(t,r,tilt,ch)

# Decorations exactly follow the collision union; exposed lips carry the
# brightest contrast. Opaque material stays behind the player and portals.
for a,b,lo,hi in fills:
    if b-a>.001:rect((a+b)/2,(lo+hi)/2,b-a,hi-lo,WALL,z=-1,order=-90,layer=15)
for x0,y0,x1,y1,nx,ny in edges:
    if max(y0,y1)<0 or min(y0,y1)>330:continue
    line((x0,y0),(x1,y1),EDGE,1.55,z=1,order=8,layer=16)
    length=math.hypot(x1-x0,y1-y0)
    if length>15:
        n=max(1,math.ceil(length/32))
        for i in range(n):
            q=(i+.5)/n
            glow(x0+(x1-x0)*q-nx*3,y0+(y1-y0)*q-ny*3,7,HALO,.25,
                 z=1,order=1,high=True,layer=16)

# Recessed rock facets are confined to real solid material. They cannot be
# mistaken for floating hazards or landing platforms.
for x in range(0,math.ceil(END),54):
    for y in range(12,334,36):
        pts=[(x-17+34*i/17,y-8+16*i/17) for i in range(18)]
        if all(occupied(xx,yy,6) for xx,yy in pts):
            line(pts[0],pts[-1],SEAM,.75,z=1,order=2,value=.60,high=True,layer=17)
            if (x//54+y//36)%4==0:
                line((x-5,y-2),(x+8,y+4),GOLD,.7,z=1,order=3,value=.30,high=True,layer=17)

# Floor/ceiling flip cues are derived from the authored input points. Small
# chevrons point toward the safe opposite rail and are strictly non-colliding.
for s in plan['sections']:
    for flip in s.get('flips',[]):
        x=flip['x'];up=flip['from_floor'];y=64 if up else 206;sign=1 if up else -1
        line((x-6,y-sign*4),(x,y+sign*2),GOLD,1.25,z=1,value=.60,layer=18)
        line((x,y+sign*2),(x+6,y-sign*4),GOLD,1.25,z=1,value=.60,layer=18)

label(360,288,'OBSIDIAN CHOIR',.58)
label(360,264,'XTRULLOR / SUPERNOVA',.26)
for s,title in zip(plan['sections'],['I / FIRST LIGHT','II / ORBIT','III / COLLAPSE',
    'IV / SUPERNOVA','V / DRIFT','VI / AFTERGLOW']):
    if s['t0']>0:label(s['x0']+200,308,title,.30)
label(END-160,174,'GG',.65)

states=[(0,(255,216,197),(160,54,130)),(11.428,(255,209,182),(205,61,104)),
    (22.722,(239,211,255),(136,58,212)),(34.016,(255,225,177),(247,81,55)),
    (39.663,(255,205,238),(211,50,155)),(45.310,(228,208,255),(137,63,221)),
    (50.957,(255,212,194),(215,54,133)),(56.605,(202,163,227),(114,44,157))]
for t,edge,halo in states:
    color(xt(t),EDGE,edge,.65);color(xt(t),HALO,halo,.8)
for i in range(168):
    t=PHASE+i*BEAT
    if t>plan['end_time']:break
    if i%4==0:pulse(t,EDGE,(255,234,216),fade=.28)
    if i%8==0:pulse(t,HALO,(228,86,150),fade=.42)

H=parse_header(head)
H['kA2']='4';H['kA4']='0'  # full-size wave, normal speed from the start
H['kA3']='0';H['kA8']='0';H['kA10']='0';H['kA11']='0'
channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
for ch,(rgb,bl) in COLORS.items():
    channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':str(int(bl)),
        '6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
level=';'.join([serialize(H)]+[raw for raw,o in base]+[serialize(o) for o in decos+triggers])+';'
(ROOT/'work/v8.level').write_text(level)
fields['k2']=('s','v8')
fields['k3']=('s',base64.urlsafe_b64encode(b'Obsidian Choir v8. Moving singularities. Wave, ball, spider and ship. Balanced normal-speed route. Xtrullor - Supernova.').decode())
fields['k4']=('s',compress(level));fields['k48']=('i',str(len(base)+len(decos)+len(triggers)))
fields['k14']=('f',False)
write_gmd(ROOT/'outputs/v8.gmd',fields)
metrics.update({'name':'v8','original_source_objects':len(source),'new_gameplay_objects':len(base),
    'new_decorations':len(decos),'new_triggers':len(triggers),
    'total_objects':len(base)+len(decos)+len(triggers),'features':features,
    'modes':[s['mode'] for s in plan['sections']],
    'high_detail_objects':sum(o.get('103')=='1' for o in decos)})
(ROOT/'work/build-metrics.json').write_text(json.dumps(metrics,indent=2))
print(json.dumps({k:v for k,v in metrics.items() if k!='features'},indent=2))
