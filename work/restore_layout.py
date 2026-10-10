"""Restore spider memory and random wall orbs; add restrained attached detail."""
from pathlib import Path
import base64, copy, hashlib, json, math, sys
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load,parse_header,parse_ks38
from gmd import read_gmd,write_gmd,compress

P=json.loads((ROOT/'work/simple-plan.json').read_text())
OLD=json.loads((ROOT/'work/nocturne-plan.json').read_text())
H,O=load(str(ROOT/'work/v8-simple.level'))
_,source=load(str(ROOT/'work/v8-nocturne-base.level'))
skin=json.loads((ROOT/'work/simple-skin-audit.json').read_text())

def groups(o):return {int(g) for g in o.get('57','').split('.') if g}
def add_group(o,g):o['57']='.'.join(str(x) for x in sorted(groups(o)|{g}))
def box_bounds(o):
    x,y=float(o['2']),float(o['3']);hx=15*float(o.get('128',o.get('32',1)));hy=15*float(o.get('129',o.get('32',1)))
    return x-hx,x+hx,y-hy,y+hy
def obj(oid,x,y,**props):
    o={'1':str(oid),'2':str(round(x,6)),'3':str(round(y,6)),'64':'1','67':'1','96':'1','20':'14'}
    o.update({k:str(round(v,7)) if isinstance(v,float) else str(v) for k,v in props.items()});O.append(o);return o
def line(a,b,lo,hi,ch=14,group=None,z=4):
    o=obj(211,(a+b)/2,(lo+hi)/2,**{'128':(b-a)/30,'129':(hi-lo)/30,'21':ch,'22':ch,'121':1,'134':1,'24':z,'25':2})
    if group is not None:add_group(o,group)
    return o
def xt(t):
    s=max((s for s in P['sections'] if s['t0']<=t+1e-8),key=lambda s:s['t0'])
    return s['x0']+(t-s['t0'])*s['speed']

# Remove the isolated moving rectangular plates and their stationary recesses.
old_moving={int(m['group']) for m in P['moves']}
recesses=[(r['a'],r['b'],r['lo'],r['hi']) for r in skin['surfaces'] if r['tag']=='service-recess']
removed=[]
for o in list(O):
    if ((o['1']=='901' and int(o.get('51',0)) in old_moving) or
        (o['1']=='211' and groups(o)&old_moving) or
        (o['1']=='211' and any(max(abs(a-b) for a,b in zip(box_bounds(o),q))<.001 for q in recesses))):
        O.remove(o);removed.append(o)
P['moves']=[]

# The earlier wall minigame owns five groups per decision. Remap every one;
# the simplified build reused some of the original IDs for moving hardware.
keys=('wall','present','absent','branch_yes','branch_no')
original_groups=sorted({m[k] for m in OLD['random_locks'] for k in keys})
remap={g:6000+i for i,g in enumerate(original_groups)}
walls={m['wall'] for m in OLD['random_locks']}
assert not any(groups(o)&set(remap.values()) for o in O)
def mapped(o):
    o=copy.deepcopy(o)
    if '57' in o:o['57']='.'.join(str(remap.get(g,g)) for g in sorted(groups(o)))
    if '51' in o:o['51']=str(remap.get(int(o['51']),int(o['51'])))
    if '152' in o:
        p=o['152'].split('.')
        for i in range(0,len(p),2):p[i]=str(remap[int(p[i])])
        o['152']='.'.join(p)
    return o
restored=[];orb_skins=[]
for o in source:
    oid=o['1'];target=int(o.get('51',0))
    if ((oid in ('1','211') and groups(o)&walls) or
        (oid in ('1594','1049') and (target in remap or groups(o)&set(remap))) or
        (oid=='2068' and int(o['152'].split('.')[0]) in remap)):
        q=mapped(o)
        if oid=='1594':
            q.update({'135':'1','21':'1004','22':'1004','507':'1','372':'1','96':'1'})
            add_group(q,8520)
            x,y=float(q['2']),float(q['3'])
            for oid2,scale in ((3636,.4),(1764,.45)):
                art=obj(oid2,x,y,**{'32':scale,'21':1004,'22':1004,'121':1,'134':1,
                                 '57':q['57'],'24':7,'20':15})
                orb_skins.append(art)
        restored.append(q)
O+=restored
P['random_locks']=copy.deepcopy(OLD['random_locks'])
for m in P['random_locks']:
    for k in keys:m[k]=remap[m[k]]
P['memories']=copy.deepcopy(OLD['memories'])
for m in P['memories']:m['group']=remap[m['group']]
for e in OLD['controls']:
    if e['kind']=='memory':
        q=copy.deepcopy(e);q['target']=remap[q['target']];P['controls'].append(q)
P['controls'].sort(key=lambda e:e['time'])
for r in OLD['rectangles']:
    if r.get('group') in walls:
        q=copy.deepcopy(r);q['group']=remap[q['group']];P['rectangles'].append(q)
for o in OLD['orbs']:
    if o['id']==1594:
        q=copy.deepcopy(o)
        for k in ('51','57'):q[k]=remap[int(q[k])]
        P['orbs'].append(q)

# Explicit runtime invisibility protects against editor Hide settings and
# special objects exposing intrinsic-white sprites. This group is never
# toggled: alpha changes appearance only, leaving every collider operational.
hidden=[]
for o in O:
    if o.get('135')=='1' and o['1'] not in ('1049','1007','901'):
        add_group(o,8480);hidden.append(o)
        if o['1']=='1764':o.update({'21':'5','22':'5','96':'1','507':'1'})
obj(1007,0,-630,**{'51':8480,'35':0,'10':0,'20':5})
obj(1007,0,-660,**{'51':8520,'35':.24,'10':0,'20':5})

# Muted metal accents sit inside the existing solid boundaries. Spider
# linework is copied verbatim; none of these highlights identifies its route.
header=parse_header(H);channels={int(c['6']):c for c in parse_ks38(header['kS38'])}
for cid,rgb in {7:(35,30,23),14:(49,27,19),15:(34,23,43),16:(47,26,34),17:(67,43,26)}.items():
    channels[cid]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':'0','6':str(cid),'7':'1','15':'1','18':'0','8':'1'}
header['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
decor=[];fixtures=[];B=60/131
for s in P['sections']:
    if s['mode']=='spider':continue
    # Long exposed edges define the chosen hosts, not a grid of loose objects.
    candidates=[q for q in skin['surfaces'] if q['tag'] in ('exposed-top','exposed-bottom') and
                q['b']-q['a']>=64 and s['x0']+120<q['a']<s['x1']-120 and 18<q['lo']<280]
    picked=[]
    for q in sorted(candidates,key=lambda q:-(q['b']-q['a'])):
        cx=(q['a']+q['b'])/2
        if any(abs(cx-(r['a']+r['b'])/2)<260 for r in picked):continue
        picked.append(q)
        if len(picked)==8:break
    for j,q in enumerate(sorted(picked,key=lambda q:q['a'])):
        a,b=q['a']+8,q['b']-8;up=q['tag']=='exposed-top';edge=q['hi'] if up else q['lo']
        lo,hi=(edge-12,edge-4) if up else (edge+4,edge+12)
        # Require the complete inlay to fit an actual collider, including its
        # swept moving light. Reject thin platforms instead of painting over air.
        hosts=[r for r in P['rectangles'] if not r.get('group') and
               r['a']<=a and r['b']>=b and r['lo']<=lo and r['hi']>=hi]
        if not hosts:continue
        if b-a>240:a=(a+b)/2-120;b=a+240
        ch=(14,15,16)[(j+s['index'])%3];mid=(lo+hi)/2
        line(a,b,mid-.45,mid+.45,ch)
        # Short end terminals and three rivet marks belong to this inlay.
        for x in (a,b):line(x-.55,x+.55,lo,hi,ch)
        for x in (a+5,a+10,a+15):line(x,x+.7,mid+1,mid+2.7,17)
        decor.append(dict(section=s['name'],a=a,b=b,lo=lo,hi=hi,host=hosts[0]))
        group=7000+len(fixtures);travel=min(28,(b-a)/3);x=a+22
        line(x,x+3,mid-.7,mid+.7,17,group)
        t=s['t0']+(x-s['x0'])/s['speed']
        beat=max(1,round((t-s['t0'])/B)-1);start=s['t0']+beat*B
        for tt,dx,duration in ((start,travel,B),(start+B,-travel,2*B)):
            obj(901,xt(tt),-690,**{'51':group,'28':dx,'29':0,'10':duration,'30':13,'20':5})
            P['moves'].append(dict(t=tt,group=group,dx=dx,dy=0,duration=duration))
        fixtures.append(dict(group=group,section=s['name'],a=x,b=x+3+travel,lo=mid-.7,hi=mid+.7,host=hosts[0]))

    if s['mode'] in ('wave','ship'):
        banks=[r for r in P['rectangles'] if not r.get('group') and
               s['x0']+120<r['a']<s['x1']-120 and r['b']-r['a']>=8 and
               r['hi']-r['lo']>=80 and r['lo']>=0 and r['hi']<=300 and
               'portal passage' not in r['kind']]
        selected=[]
        for r in sorted(banks,key=lambda r:-(r['hi']-r['lo'])):
            if any(abs(r['a']-q['a'])<360 for q in selected):continue
            selected.append(r)
            if len(selected)==8:break
        for j,r in enumerate(selected):
            cx=(r['a']+r['b'])/2;lo=r['lo']+12;hi=min(r['hi']-12,lo+56)
            if r['lo']==0:hi=r['hi']-12;lo=max(12,hi-56)
            ch=(14,15,16)[(j+s['index'])%3]
            line(cx-.35,cx+.35,lo,hi,ch)
            for y in (lo,hi):line(cx-2,cx+2,y-.4,y+.4,ch)
            group=7000+len(fixtures)
            light=obj(1764,cx,lo+5,**{'32':.2,'21':17,'22':17,'121':1,'134':1,'57':group,'24':4})
            t=s['t0']+(cx-s['x0'])/s['speed'];start=s['t0']+max(1,round((t-s['t0'])/B)-1)*B
            for tt,dy,duration in ((start,20,B),(start+B,-20,2*B)):
                obj(901,xt(tt),-690,**{'51':group,'28':0,'29':dy,'10':duration,'30':13,'20':5})
                P['moves'].append(dict(t=tt,group=group,dx=0,dy=dy,duration=duration))
            decor.append(dict(section=s['name'],a=cx-2,b=cx+2,lo=lo-.4,hi=hi+.4,host=r))
            fixtures.append(dict(group=group,section=s['name'],a=cx-.8,b=cx+.8,lo=lo+4.2,hi=lo+25.8,host=r))

# Small brackets terminate at the existing portal divider, with a normal
# native portal sprite between them. The hidden activation portal never shows.
for p in P['portal_passages']:
    for yy in (p['lo']-4,p['hi']+4):
        if 3<yy<297:line(p['a']+.8,p['b']-.8,yy-.55,yy+.55,15)

P['objects']=len(O);P['restore_summary']=dict(random_decisions=len(P['random_locks']),
    restored_objects=len(restored),removed_floating_rectangles=sum(o['1']=='211' for o in removed),
    explicitly_hidden_objects=len(hidden),preserved_spider_fakeouts=len(P['fakeouts']),
    inlays=len(decor),moving_inlays=len(fixtures),normal_size_visible_portals=67,circular_orb_skin_objects=len(orb_skins))
P['decor_inlays']=decor;P['decor_fixtures']=fixtures
P['validation_limit']='Approximate model checks; full native completion and exact demon difficulty unverified.'
ser=lambda o:','.join(f'{k},{v}' for k,v in o.items())
raw=';'.join([ser(header)]+[ser(o) for o in O])+';'
f=read_gmd(ROOT/'outputs/v8-1573528-simple.gmd')
desc='RESTORED v8: spider crossing lines and random wall-toggle orbs. Normal-size portal artwork, attached metal inlays, no floating pale plates. Song 1573528.'
f.update({'k4':('s',compress(raw)),'k48':('i',str(len(O))),
          'k3':('s',base64.urlsafe_b64encode(desc.encode()).decode()),'k14':('f',False)})
write_gmd(ROOT/'outputs/v8-1573528-restored.gmd',f)
(ROOT/'work/v8-restored.level').write_text(raw)
(ROOT/'work/restored-plan.json').write_text(json.dumps(P,separators=(',',':')))
print(json.dumps(P['restore_summary'],indent=2))
