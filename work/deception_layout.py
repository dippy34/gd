"""Mechanical wrong choices outside the preserved spider rooms.

Start from the eased, dark collision build. Cut real blind branches, then
place live optional orbs in measured gaps between the required inputs.
"""
from pathlib import Path
from collections import Counter
import base64, bisect, copy, json, math, sys
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd, write_gmd, compress

OLD=json.loads((ROOT/'work/nocturne-plan.json').read_text())
P=copy.deepcopy(OLD)
H,O=load(str(ROOT/'work/v8-nocturne-base.level'))
SECTIONS={s['name']:s for s in P['sections']}
B=60/131

# Required and optional orbs share the same native size and subdued display.
# A bright-versus-dim distinction would give away every bait immediately.
for existing in O:
    if existing['1'] in ('36','84','141'):
        existing['57']='8500'
        existing['507']='1'
        existing['372']='1'


def xat(s,t):return s['x0']+(t-s['t0'])*s['speed']
def point(s,t):return min(s['points'],key=lambda p:abs(p[0]-t))
def obj(oid,x,y,**props):
    q={'1':str(oid),'2':str(round(x,5)),'3':str(round(y,5)),
       '64':'1','67':'1','96':'1','20':'0'}
    q.update({str(k):str(v) for k,v in props.items()});O.append(q);return q
def intersects(r,q):
    return r['a']<q[1] and r['b']>q[0] and r['lo']<q[3] and r['hi']>q[2]
def cut_rect(r,q):
    if not intersects(r,q):return [r]
    a,b=max(r['a'],q[0]),min(r['b'],q[1]);lo,hi=max(r['lo'],q[2]),min(r['hi'],q[3])
    candidates=[(r['a'],a,r['lo'],r['hi']),(b,r['b'],r['lo'],r['hi']),
                (a,b,r['lo'],lo),(a,b,hi,r['hi'])]
    return [dict(r,a=aa,b=bb,lo=ll,hi=hh) for aa,bb,ll,hh in candidates if bb-aa>.3 and hh-ll>.3]


# Each branch is authored at a particular bend, not distributed periodically.
# Wave branches continue through a required turn. Ship branches invite the
# wrong descent or the wrong decision to maintain altitude.
BRANCH_SCORE=[
    ('BLINDFOLD',3.07,'continue through the lower turn',75,-1,20),
    ('FAULTLINE',22.06,'continue the mini-wave climb',60,2,20),
    ('PARALLAX',3.2,'dive into the lower service duct',164,-.6,30),
    ('UNDERTOW',16.0,'hold altitude past the descent',180,0,30),
]
branches=[];cutouts=[]
for name,beat,rule,length,slope,half in BRANCH_SCORE:
    s=SECTIONS[name];t=s['t0']+beat*B
    if s['mode']=='wave':
        turn=min((e for e in P['controls'] if e['mode']=='wave' and s['t0']<e['time']<s['t1']),key=lambda e:abs(e['time']-t))
        t=turn['time']
    x=xat(s,t);y=point(s,t)[1]
    def center(dx):
        if s['mode']=='ship' and slope:
            return y+slope*(dx*dx/120 if dx<60 else dx-30)
        return y+slope*dx
    assert 8<center(length)-half<center(length)+half<292,(name,center(length))
    cuts=[]
    for a in np.arange(0,length,6):
        b=min(length,a+6)
        cuts.append((x+float(a),x+float(b),min(center(a),center(b))-half,max(center(a),center(b))+half))
    before=sum((r['b']-r['a'])*(r['hi']-r['lo']) for r in P['rectangles'])
    for q in cuts:
        P['rectangles']=[rr for r in P['rectangles'] for rr in (cut_rect(r,q) if not r.get('group') else [r])]
    after=sum((r['b']-r['a'])*(r['hi']-r['lo']) for r in P['rectangles'])
    assert before-after>150,(name,'not a real branch')
    # The cut ends against existing solid collision geometry. Verify a body
    # following the blind branch meets a real cap while the intended route
    # has a separate opening at the same x coordinate.
    end_x=x+length+4;end_y=center(length);r=3 if s['mode']=='wave' else 15
    cap=[q for q in P['rectangles'] if q['a']<end_x+r and q['b']>end_x-r and q['lo']<end_y+r and q['hi']>end_y-r]
    assert cap,(name,'branch needs a solid dead end',end_x,end_y)
    correct_y=point(s,t+(length+4)/s['speed'])[1]
    assert abs(correct_y-end_y)>r+half+5,(name,'cap too close to intended route',correct_y,end_y)
    branches.append(dict(section=name,rule=rule,t=t,x=x,y=y,length=length,half_width=half,
                         end_x=end_x,end_y=end_y,correct_y_at_end=correct_y,removed_solid_area=before-after,
                         cuts=cuts))
    cutouts.extend(cuts)

# Rebuild only the affected flight rooms' block colliders from the difference
# geometry. All other collision objects and both spider rooms are retained.
affected={q['section'] for q in branches}
def in_affected(o):
    x=float(o['2'])
    return any(SECTIONS[n]['x0']<=x<SECTIONS[n]['x1'] for n in affected)
O=[o for o in O if not(o['1']=='1' and in_affected(o))]
for r in P['rectangles']:
    if not any(SECTIONS[n]['x0']<=r['a']<SECTIONS[n]['x1'] for n in affected):continue
    n=math.ceil((r['b']-r['a'])/75);m=math.ceil((r['hi']-r['lo'])/75)
    for i in range(n):
        for j in range(m):
            props={'128':(r['b']-r['a'])/n/30,'129':(r['hi']-r['lo'])/m/30,
                   '21':1,'22':2,'24':-1,'135':1}
            if r.get('group'):props['57']=r['group']
            obj(1,r['a']+(i+.5)*(r['b']-r['a'])/n,r['lo']+(j+.5)*(r['hi']-r['lo'])/m,**props)

# Clear old boundary teeth only where the new, real passage cuts through them.
removed_spikes=[]
for o in list(O):
    if o['1']!='8':continue
    x,y=float(o['2']),float(o['3']);r=15*float(o.get('32',1))
    if any(x-r<q[1] and x+r>q[0] and y-r<q[3] and y+r>q[2] for q in cutouts):
        O.remove(o);removed_spikes.append((x,y,r))
P['spikes']=[q for q in P['spikes'] if not any(abs(q['x']-x)<.001 and abs(q['y']-y)<.001 for x,y,r in removed_spikes)]

# Native gravity portals tempt a wrong move inside the two ship branches.
# Their reduced activation regions are measured clear of the intended path.
branch_portals=[]
for branch in branches:
    s=SECTIONS[branch['section']]
    if s['mode']!='ship':continue
    dx=branch['length']-28
    yy=branch['y']+(-.6*(dx-30) if branch['section']=='PARALLAX' else 0)
    xx=branch['x']+dx;tt=branch['t']+dx/s['speed']
    pp=point(s,tt)
    # Keep the center well outside the normal route's body + scaled portal.
    if abs(pp[1]-yy)<45:continue
    oid=11 if pp[2]<0 else 10
    obj(oid,xx,yy,**{'32':.3,'13':1,'21':1004,'22':1004,'507':1,'57':8500,'20':12})
    branch_portals.append(dict(section=s['name'],id=oid,x=xx,y=yy,t=tt,scale=.3,route_separation=abs(pp[1]-yy)))

# Live bait orbs live between specific, required inputs. Their native effects
# are real; a later wrong-input replay decides which candidates are retained.
BAIT_SCORE={
    'CIPHER':[(4.9,36),(10.0,84),(18.2,36)],
    'CUTWIRE':[(4.0,84),(7.0,36),(14.0,36),(20.0,84)],
    'SWITCHYARD':[(5.0,84),(12.0,36),(20.0,84)],
    'OFFBEAT':[(4.2,84),(11.3,36),(22.2,84)],
    'CROSSCODE':[(5.4,36),(15.2,84),(25.6,36)],
    'NEEDLEWORK':[(6.0,36),(12.8,84),(19.4,36)],
    'FALSE FLOOR':[(8.1,84),(18.2,36),(26.4,84)],
    'COUNTERFEIT':[(5.4,36),(14.1,84),(25.6,36)],
    'LAST WORD':[(5.1,84),(12.1,36),(24.7,84)],
}
baits=[]
for name,score in BAIT_SCORE.items():
    s=SECTIONS[name]
    inputs=[e for e in P['controls'] if s['t0']<=e['time']<s['t1']]
    for beat,oid in score:
        ideal=s['t0']+beat*B
        candidates=[]
        for t in np.arange(ideal-.55,ideal+.55,1/60):
            if not s['t0']+.9<t<s['t1']-1.3:continue
            if any(abs(t-e['time'])<.28 or (e['kind']=='hold' and e['time']-.26<t<e['time']+e.get('hold',0)+.26) for e in inputs):continue
            p=point(s,t);x=xat(s,t);y=p[1]
            if not 35<y<265:continue
            if any(abs(o['x']-x)<80 for o in P['orbs']):continue
            if any(abs(b['x']-x)<150 for b in baits):continue
            candidates.append((abs(t-ideal),float(t),x,y))
        if not candidates:continue
        _,t,x,y=min(candidates)
        obj(oid,x,y,**{'32':1,'21':1004,'22':1004,'57':8500,'507':1,'372':1,'20':12})
        bait=dict(section=name,id=oid,t=t,x=x,y=y,kind='live gravity bait' if oid==84 else 'live jump bait',group=8500)
        baits.append(bait)
        P['orbs'].append(dict(id=oid,t=t,x=x,y=y,bait=True))

# Constant opacity, applied once at the start. It never flashes or hides a
# collider. Intrinsically colored native portals/orbs otherwise ignore tint.
obj(1007,0,-600,**{'51':8500,'35':.13,'10':0,'20':5})
P['branches']=branches;P['branch_portals']=branch_portals;P['bait_candidates']=baits
P['fakeouts']=[d for d in OLD['fakeouts'] if SECTIONS[d['section']]['mode']=='spider']
P['removed_nonspider_decoys']=len(OLD['fakeouts'])-len(P['fakeouts'])
P['removed_boundary_spikes']=len(removed_spikes)
P['objects']=len(O)
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
raw=';'.join([H]+[serialize(o) for o in O])+';'
fields=read_gmd(ROOT/'work/nocturne-base.gmd');fields['k4']=('s',compress(raw));fields['k48']=('i',str(len(O)))
write_gmd(ROOT/'work/deception-base.gmd',fields)
(ROOT/'work/v8-deception-base.level').write_text(raw)
(ROOT/'work/deception-plan.json').write_text(json.dumps(P,separators=(',',':')))
print(json.dumps(dict(base_objects=len(O),branches=[{k:v for k,v in b.items() if k!='cuts'} for b in branches],
                      bait_candidates=len(baits),branch_portals=branch_portals,removed_nonspider_decoys=P['removed_nonspider_decoys']),indent=2))
