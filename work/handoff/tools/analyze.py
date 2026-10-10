import sys, json, statistics as st
from collections import Counter, defaultdict
sys.path.insert(0,'.')
from gdparse import load, parse_header, parse_ks38, fnum
from names import name

head, objs = load('../research/109381612.level')
H = parse_header(head)
N = len(objs)
def F(o,k,d=0.0):
    try: return float(o.get(k,d))
    except: return d

print("="*78); print("A. COLOR CHANNELS (kS38) — %d entries" % len(parse_ks38(H['kS38'])))
print("="*78)
ch = {}
for c in parse_ks38(H['kS38']):
    cid = c.get('6')
    if cid is None: continue
    ch[int(cid)] = c
for cid in sorted(ch):
    c = ch[cid]
    rgb = (c.get('1','?'), c.get('2','?'), c.get('3','?'))
    blend = c.get('5','0'); op = c.get('7','1'); copy = c.get('9'); hsv=c.get('10')
    pl = c.get('8'); 
    print(f"  ch{cid:<5} rgb=({rgb[0]:>3},{rgb[1]:>3},{rgb[2]:>3}) blend={blend} opacity={op}"
          + (f" copy_from={copy} hsv={hsv}" if copy else ""))

print(); print("="*78); print("B. USE OF COLOR CHANNELS BY OBJECTS"); print("="*78)
c1 = Counter(o.get('21') for o in objs if '21' in o)
c2 = Counter(o.get('22') for o in objs if '22' in o)
print(" primary (p21) top 25:", ', '.join(f"{k}:{v}" for k,v in c1.most_common(25)))
print(" secondary(p22) top 15:", ', '.join(f"{k}:{v}" for k,v in c2.most_common(15)))

print(); print("="*78); print("C. HSV RECOLOURING"); print("="*78)
hsv1 = Counter(o.get('43') for o in objs if o.get('41')=='1')
print(f" objects with HSV on colour-1: {sum(hsv1.values())} ({100*sum(hsv1.values())/N:.1f}%), distinct HSV strings: {len(hsv1)}")
for k,v in hsv1.most_common(20): print(f"   {k:<28} {v}")
hh=[]
for o in objs:
    if o.get('41')=='1' and '43' in o:
        p=o['43'].split('a')
        try: hh.append((float(p[0]),float(p[1]),float(p[2])))
        except: pass
if hh:
    print(f" hue shift: min {min(x[0] for x in hh):.0f} max {max(x[0] for x in hh):.0f}; "
          f"sat mult median {st.median(x[1] for x in hh):.2f}; val mult median {st.median(x[2] for x in hh):.2f}")

print(); print("="*78); print("D. Z-LAYER / Z-ORDER"); print("="*78)
zl = Counter(o.get('24','(unset)') for o in objs)
print(" z_layer:", ', '.join(f"{k}:{v}" for k,v in sorted(zl.items(), key=lambda kv:-kv[1])[:12]))
zo = [F(o,'25') for o in objs if '25' in o]
if zo: print(f" z_order: n={len(zo)} min={min(zo):.0f} p25={st.quantiles(zo,n=4)[0]:.0f} med={st.median(zo):.0f} p75={st.quantiles(zo,n=4)[2]:.0f} max={max(zo):.0f}")

print(); print("="*78); print("E. GEOMETRY: scale / rotation / skew"); print("="*78)
sx=[F(o,'128',1) for o in objs if '128' in o]; sy=[F(o,'129',1) for o in objs if '129' in o]
rot=[F(o,'6') for o in objs if '6' in o and F(o,'6')!=0]
print(f" scale_x n={len(sx)} min={min(sx):.3f} p10={st.quantiles(sx,n=10)[0]:.2f} med={st.median(sx):.2f} p90={st.quantiles(sx,n=10)[8]:.2f} max={max(sx):.1f}")
print(f" scale_y n={len(sy)} min={min(sy):.3f} med={st.median(sy):.2f} max={max(sy):.1f}")
aniso=sum(1 for o in objs if abs(F(o,'128',1)-F(o,'129',1))>1e-6)
print(f" anisotropic (scale_x != scale_y): {aniso} ({100*aniso/N:.1f}%)")
print(f" rotated (p6 != 0): {len(rot)} ({100*len(rot)/N:.1f}%)")
rr=Counter(round(r) for r in rot)
print("  top rotations:", ', '.join(f"{k}:{v}" for k,v in rr.most_common(12)))
nonmult=sum(1 for r in rot if round(r)%90!=0)
print(f"  non-90-multiple rotations: {nonmult} ({100*nonmult/max(1,len(rot)):.0f}% of rotated)")
skew=sum(1 for o in objs if '131' in o or '132' in o)
print(f" skewed: {skew} ({100*skew/N:.1f}%)")
flip=sum(1 for o in objs if o.get('4')=='1' or o.get('5')=='1')
print(f" flipped: {flip} ({100*flip/N:.1f}%)")

print(); print("="*78); print("F. SPATIAL EXTENT AND DENSITY"); print("="*78)
xs=[F(o,'2') for o in objs]; ys=[F(o,'3') for o in objs]
print(f" x: {min(xs):.0f} .. {max(xs):.0f}   y: {min(ys):.0f} .. {max(ys):.0f}")
cols=Counter(int(F(o,'2')//30) for o in objs)
vals=sorted(cols.values())
print(f" per-30u column: n_cols={len(cols)} min={vals[0]} p25={vals[len(vals)//4]} med={vals[len(vals)//2]} p75={vals[3*len(vals)//4]} max={vals[-1]}")
print(f" mean objects / 30u column over span: {N/((max(xs)-min(xs))/30):.0f}")
ongrid=sum(1 for o in objs if abs((F(o,'2')-15)%30)<0.01)
print(f" x on 30-grid centres: {ongrid} ({100*ongrid/N:.1f}%)")

print(); print("="*78); print("G. TOP-70 ID PROFILES"); print("="*78)
byid=defaultdict(list)
for o in objs: byid[int(o['1'])].append(o)
print(f"{'id':>6} {'count':>6} {'%':>5}  {'scale(p25/med/p75)':<22} {'rot%':>5} {'top colours':<22} {'zL':>4} {'zOrd med':>8}  name")
for i,(oid,grp) in enumerate(sorted(byid.items(), key=lambda kv:-len(kv[1]))[:70]):
    n=len(grp)
    s=[F(o,'128',1) for o in grp]
    q=st.quantiles(s,n=4) if len(s)>3 else [0,0,0]
    r=100*sum(1 for o in grp if F(o,'6')!=0)/n
    cc=Counter(o.get('21','-') for o in grp).most_common(3)
    zls=Counter(o.get('24','-') for o in grp).most_common(1)[0][0]
    zos=[F(o,'25') for o in grp if '25' in o]
    print(f"{oid:>6} {n:>6} {100*n/N:5.2f}  {q[0]:.2f}/{st.median(s):.2f}/{q[2]:.2f}".ljust(46)
          + f"{r:5.0f} " + ','.join(f"{k}:{v}" for k,v in cc).ljust(22)
          + f" {zls:>4} {st.median(zos) if zos else 0:8.0f}  {name(oid)}")
