"""Independent containment, import, and gameplay-preservation checks."""
from pathlib import Path
from collections import Counter,defaultdict
import sys,json,math,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd,decompress

P=json.loads((ROOT/'work/memory-plan.json').read_text())
A=json.loads((ROOT/'work/visual-cleanup-audit.json').read_text())
H,old=load(str(ROOT/'work/revision-before-visual-cleanup/v8-memory.level'))
new_h,new=load(str(ROOT/'work/v8-clean.level'))
_,native=load(str(ROOT/'work/clean-native-import.level'))
assert H==new_h
signature=lambda oo:Counter(tuple(sorted(o.items())) for o in oo)
norm=lambda o:{k:v for k,v in o.items() if not(o['1']=='8' and k=='135')}
assert signature(norm(o) for o in old if o['1']!='211')==signature(norm(o) for o in new if o['1'] not in ('211','693'))
assert signature(o for o in old if o['1']=='211' and o.get('57'))==signature(o for o in new if o['1']=='211' and o.get('57'))
assert all(o.get('121')==o.get('134')=='1' for o in new if o['1']=='693')
assert all(o.get('121')==o.get('134')=='1' for o in native if o['1']=='693')
assert all(o.get('135')=='1' for o in native if o['1']=='8')
assert len(new)==len(native)==A['objects']
assert Counter(o['1'] for o in new)==Counter(o['1'] for o in native)

# Native serialization rounds dimensions to .001 and world coordinates to six
# significant digits. Compare with those measured serialization tolerances.
native_checks=0
for oid in ('1','8','693','99','101','1913','1914','2925','1594','1049','901'):
    aa=[o for o in new if o['1']==oid];bb=[o for o in native if o['1']==oid]
    for a,b in zip(aa,bb):
        assert abs(float(a['2'])-float(b['2']))<.056
        assert abs(float(a['3'])-float(b['3']))<.013
        for key in ('128','129'):
            sa=float(a.get(key,a.get('32',1)));sb=float(b.get(key,b.get('32',1)))
            assert abs(sa-sb)<=.00051,(oid,key,sa,sb)
        keys={'1913':['371'],'1914':['71','101','36'],'2925':['111'],
              '1594':['51','56'],'1049':['51','56'],'901':['51','28','29','10']}.get(oid,[])
        for key in keys:assert abs(float(a.get(key,0))-float(b.get(key,0)))<.0006
        native_checks+=1

# Check the actual static art boxes against a union of authored solid bounds.
# Clips are integrated strip by strip; concavities are not approximated by a
# large bounding box or just checking each face's center point.
bins=defaultdict(list)
for r in P['rectangles']:
    if r.get('group'):continue
    for i in range(math.floor(r['a']/100),math.floor(r['b']/100)+1):bins[i].append(r)
def covered_area(q):
    cand={id(r):r for i in range(math.floor(q['a']/100),math.floor(q['b']/100)+1) for r in bins[i]}
    clips=[]
    for r in cand.values():
        a=max(q['a'],r['a']);b=min(q['b'],r['b']);lo=max(q['lo'],r['lo']);hi=min(q['hi'],r['hi'])
        if a<b and lo<hi:clips.append((a,b,lo,hi))
    xs=sorted({x for r in clips for x in r[:2]});area=0
    for a,b in zip(xs,xs[1:]):
        mid=(a+b)/2;ys=sorted((lo,hi) for aa,bb,lo,hi in clips if aa<=mid<=bb)
        length=0;end=-1e9
        for lo,hi in ys:
            length+=max(0,hi-max(lo,end));end=max(end,hi)
        area+=(b-a)*length
    return area
tested=0;max_missing=0
for q in A['surfaces']:
    if q['tag']=='service-recess':continue
    area=(q['b']-q['a'])*(q['hi']-q['lo']);missing=max(0,area-covered_area(q))
    max_missing=max(max_missing,missing)
    assert missing<.0002,(q,missing)
    tested+=1
for q in A['details']:
    r=q['host'];assert q['a']>=r['a']+4.9 and q['b']<=r['b']-4.9
    assert q['lo']>=r['lo']+2.9 and q['hi']<=r['hi']-2.9

V=json.loads((ROOT/'outputs/v8-1573528-clean-validation.json').read_text())
assert V['rooms_with_nominal_overlaps']==0
assert V['sha256']==A['sha256']
V.update(visual_cleanup={k:v for k,v in A.items() if k not in ('surfaces','details')},
    static_art_containment=dict(tested_rectangles=tested,max_area_outside_solid=max_missing,
                               method='Analytic clipped-rectangle union area; service recesses excluded.'),
    native_validation=dict(imported=True,objects=len(native),object_id_counts_match=True,
        checked_gameplay_camera_and_spike_art_objects=native_checks,
        new_spike_art_passable_and_no_touch=True,spike_colliders_hidden_only=True,
        opening_visually_inspected=True,editor_rooms_inspected=['CUTWIRE','BLIND ELEVATOR','FAULTLINE'],
        full_completion_verified=False,difficulty_verified=False,
        note='Native opening viewed with existing Ignore Damage enabled; later rooms inspected in editor.'),
    scripted_visual_review=dict(frames=30,rooms=15,renderer='Native sprite atlas, serialized camera, colors and trigger states.'))
(ROOT/'outputs/v8-1573528-clean-validation.json').write_text(json.dumps(V,indent=2))
print(json.dumps(dict(objects=len(new),native_checks=native_checks,contained_art_boxes=tested,
    max_uncontained_area=max_missing,nominal_route_collisions=0,gameplay_preserved=True),indent=2))
