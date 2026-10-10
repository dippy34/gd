"""Replace overlapping static skins with the exposed boundary of solid unions.

Native collision objects, interactive objects, and all triggers are copied
verbatim. Coordinate compression operates on the authored rectangle endpoints;
there is no pixel-grid approximation of the gameplay geometry.
"""
from pathlib import Path
from collections import Counter
import sys, json, math, hashlib, base64, os
import numpy as np

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gmd import read_gmd, decompress, compress, write_gmd
from gdparse import load

SOURCE=ROOT/os.environ.get('GD_SKIN_SOURCE','outputs/v8-1573528-timing.gmd')
TARGET=ROOT/os.environ.get('GD_SKIN_TARGET','outputs/v8-1573528-clean.gmd')
P=json.loads((ROOT/os.environ.get('GD_SKIN_PLAN','work/revision-before-visual-cleanup/memory-plan.json')).read_text())
H,old=load(str(ROOT/os.environ.get('GD_SKIN_RAW','work/revision-before-visual-cleanup/v8-memory.level')))
kept=[dict(o) for o in old if o['1']!='211' or o.get('57')]
art=[]; surfaces=[]; detail=[]; stats=[]

def box(a,b,lo,hi,ch=1,z=-3,tag='fill'):
    if b-a<1e-5 or hi-lo<1e-5:return
    # Keep the editor's separate scale values modest; long flat spans are split.
    n=math.ceil((b-a)/600)
    for i in range(n):
        aa=a+(b-a)*i/n;bb=a+(b-a)*(i+1)/n
        if tag=='fill':
            aa=max(a,aa-.1);bb=min(b,bb+.1)
        d={'1':211,'2':(aa+bb)/2,'3':(lo+hi)/2,'64':1,'67':1,'96':1,
           '20':10,'128':(bb-aa)/30,'129':(hi-lo)/30,'21':ch,'22':ch,
           '121':1,'134':1,'24':z,'25':-2}
        art.append({k:str(round(v,7)) if isinstance(v,float) else str(v) for k,v in d.items()})
        surfaces.append(dict(a=aa,b=bb,lo=lo,hi=hi,tag=tag))

def runs(mask):
    inds=np.flatnonzero(np.diff(np.r_[False,mask,False].astype(np.int8)))
    return list(zip(inds[::2],inds[1::2]))

for s in P['sections']:
    rr=[r for r in P['rectangles'] if not r.get('group') and
        r['a']<s['x1']-1e-6 and r['b']>s['x0']+1e-6]
    rr=[dict(r,a=max(s['x0'],r['a']),b=min(s['x1'],r['b'])) for r in rr]
    xs=np.unique([v for r in rr for v in (r['a'],r['b'])])
    ys=np.unique([v for r in rr for v in (r['lo'],r['hi'])])
    filled=np.zeros((len(xs)-1,len(ys)-1),dtype=bool)
    for r in rr:
        i,j=np.searchsorted(xs,[r['a'],r['b']]);k,l=np.searchsorted(ys,[r['lo'],r['hi']])
        filled[i:j,k:l]=True
    start=len(art);pending={};fills=[]
    for i,col in enumerate(filled):
        spans=set(runs(col))
        for span,a in list(pending.items()):
            if span not in spans:
                fills.append((a,xs[i],ys[span[0]],ys[span[1]]));del pending[span]
        for span in spans:pending.setdefault(span,xs[i])
    for span,a in pending.items():fills.append((a,xs[-1],ys[span[0]],ys[span[1]]))
    # Native sprites have antialiased edges. Original rectangle fills overlap
    # only within solid space, closing raster cracks at the union partition.
    # Their individual outlines are discarded: outlines below use the union.
    for r in rr:box(r['a'],r['b'],r['lo'],r['hi'],1,1)
    fill_count=len(art)-start
    # Horizontal silhouettes: only transitions between solid and empty space.
    for j,y in enumerate(ys):
        below=filled[:,j-1] if j else np.zeros(len(xs)-1,dtype=bool)
        above=filled[:,j] if j<len(ys)-1 else np.zeros(len(xs)-1,dtype=bool)
        for left,right in runs(below & ~above):
            edge=min(.95,(y-ys[j-1])/2);box(xs[left],xs[right],y-edge,y,2,3,'exposed-top')
        for left,right in runs(above & ~below):
            edge=min(.95,(ys[j+1]-y)/2);box(xs[left],xs[right],y,y+edge,2,3,'exposed-bottom')
    # Vertical sides are dimmer than contact edges. No tall support cages.
    for i,x in enumerate(xs):
        left=filled[i-1] if i else np.zeros(len(ys)-1,dtype=bool)
        right=filled[i] if i<len(xs)-1 else np.zeros(len(ys)-1,dtype=bool)
        for lo,hi in runs(left & ~right):
            edge=min(.65,(x-xs[i-1])/2);box(x-edge,x,ys[lo],ys[hi],6,3,'exposed-side')
        for lo,hi in runs(right & ~left):
            edge=min(.65,(xs[i+1]-x)/2);box(x,x+edge,ys[lo],ys[hi],6,3,'exposed-side')
    # A small number of inset faces fit INSIDE existing platform bodies. The
    # old 100 door boxes were 44–50 units wide on 8–14 unit banks: remove them.
    # Each new marking uses its host's dimensions, with a measured clear inset.
    candidates=[r for r in rr if r['kind'] in ('suspended landing','island rail',
                 'upper rail','teleport shelf','suspended ufo chamber lower',
                 'suspended ufo chamber upper') and r['b']-r['a']>=54 and r['hi']-r['lo']>=10]
    last=-1e9
    for r in sorted(candidates,key=lambda r:r['a']):
        if r['a']-last<210:continue
        a,b=r['a']+5,r['b']-5;lo,hi=r['lo']+3,r['hi']-3
        # Do not draw a face across another attached timing bank or spike base.
        blockers=[q for q in rr if q is not r and q!=r and q['a']<b and q['b']>a
                  and q['lo']<hi and q['hi']>lo]
        free=[(a,b)]
        for q in blockers:
            nxt=[]
            for aa,bb in free:
                if q['b']<=aa or q['a']>=bb:nxt.append((aa,bb));continue
                if q['a']-2>aa:nxt.append((aa,min(bb,q['a']-2)))
                if q['b']+2<bb:nxt.append((max(aa,q['b']+2),bb))
            free=nxt
        if not free:continue
        a,b=max(free,key=lambda z:z[1]-z[0])
        if b-a<32:continue
        box(a,b,lo,hi,5,3,'inset-face')
        box(a+2,a+3,lo+.6,hi-.6,6,3,'face-seam')
        detail.append(dict(section=s['name'],a=a,b=b,lo=lo,hi=hi,host=r,kind='contained face'))
        last=r['a']
    stats.append(dict(section=s['name'],old_static_art=sum(o['1']=='211' and not o.get('57') and s['x0']<=float(o['2'])<s['x1'] for o in old),
                      new_static_art=len(art)-start,union_fill_tiles=fill_count,
                      solid_area=float(np.sum(filled*np.diff(xs)[:,None]*np.diff(ys)[None,:]))))

# Restore stationary service-plate recesses only. Their moving grouped parts
# and both Move triggers were retained above. Outside the playfield, they do
# not cross structures, hazards, portals, or the moving recall-code tokens.
for o in kept:
    if o['1']=='211' and o.get('57') and (float(o['3'])<0 or float(o['3'])>300):
        x=float(o['2']);y=float(o['3']);box(x-17.5,x+50.5,y-3,y+4,6,-4,'service-recess')

# Cover the unchanged spike colliders with flat silhouettes, assembled from
# two native right-triangle art objects. Filled halves have no crossing inner
# outlines. Solid skins are above them, so embedded spike bases do not cut
# decorative holes through platform faces. Property 135 affects appearance.
spike_art=[]
for o in kept:
    if o['1']!='8':continue
    o['135']='1'
    scale=float(o.get('32',1));r=15*scale;x=float(o['2']);y=float(o['3'])
    upside=float(o.get('6',0))==180
    for side in (-1,1):
        q={'1':'693','2':str(x+side*r/2),'3':str(y),'128':str(scale/2),
           '129':str(scale),'4':str(int(side==1)),'5':str(int(upside)),
           '21':'3','22':'3','121':'1','134':'1','64':'1','67':'1','96':'1',
           '20':'10','24':'-1','25':'-2'}
        if o.get('57'):q['57']=o['57']
        spike_art.append(q)
out=kept+spike_art+art
sig=lambda seq:Counter(tuple(sorted(o.items())) for o in seq)
normal=lambda o:{k:v for k,v in o.items() if not (o['1']=='8' and k=='135')}
assert sig(normal(o) for o in old if o['1']!='211')==sig(normal(o) for o in kept if o['1']!='211')
assert sig(o for o in old if o['1']=='211' and o.get('57'))==sig(o for o in out if o['1']=='211' and o.get('57'))
ser=lambda d:','.join(f'{k},{v}' for k,v in d.items())
raw=';'.join([H]+[ser(o) for o in out])+';'
f=read_gmd(SOURCE);f['k4']=('s',compress(raw));f['k48']=('i',str(len(out)))
f['k3']=('s',base64.urlsafe_b64encode(b'Song 1573528. Joined structural surfaces; memory switches, seven modes and hard timings retained. Native 0.5x for most of the song.').decode())
write_gmd(TARGET,f)
(ROOT/os.environ.get('GD_SKIN_OUTPUT_RAW','work/v8-clean.level')).write_text(raw)
audit=dict(file=TARGET.name,objects=len(out),old_objects=len(old),removed_static_art=len(old)-len(kept),
           new_static_art=len(art),removed_oversized_fake_doors=len(P['fakeouts']),contained_faces=len(detail),
           all_gameplay_properties_identical=True,spike_display_only_hidden=True,spike_art_objects=len(spike_art),
           all_original_grouped_art_identical=True,header_identical=True,
           sha256=hashlib.sha256(TARGET.read_bytes()).hexdigest(),sections=stats,
           surfaces=surfaces,details=detail)
(ROOT/os.environ.get('GD_SKIN_AUDIT','work/visual-cleanup-audit.json')).write_text(json.dumps(audit,separators=(',',':'),default=lambda v:v.item()))
print(json.dumps({k:v for k,v in audit.items() if k not in ('surfaces','details','sections')},indent=2))
