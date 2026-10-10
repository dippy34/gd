import sys, math, statistics as st
from collections import Counter, defaultdict
sys.path.insert(0,'.')
from gdparse import load
from names import name
head, objs = load('../research/109381612.level')
def F(o,k,d=0.0):
    try: return float(o.get(k,d))
    except: return d
TRIGGER_IDS={899,901,1006,1007,1049,1268,1346,1347,1520,1585,1595,1611,1616,1811,1812,1814,1815,
 1816,1817,1818,1819,1912,1913,1914,1916,1917,1931,1932,1934,1935,2015,2016,2062,2063,2066,2067,
 2068,2069,2899,2900,2901,2903,2925,2999,3016,3022,3029,3030,3031,3032,3033,3600,3602,3603,3604,
 3605,3606,3607,3608,3609,3612,3613,3614,3615,3617,3618,3619,3620,3640,3641,3642,3643,3645,3655,
 3660,3661,3662,2904,2905,2907,2909,2910,2911,2912,2913,2914,2915,2916,2917,2919,2920,2921,2922,
 2923,2924,3006,3007,3008,3009,3010,3011,3012,3013,3014,3015,3017,3018,3019,3020,3021,3023,3024,31}
vis=[o for o in objs if int(o['1']) not in TRIGGER_IDS]
print(f"visible objects: {len(vis)}  (triggers: {len(objs)-len(vis)})")

print("\n--- 1. REPETITION TEST: exact stamp duplication ---")
# signature of an object: id + rounded scale + rotation + colour + flip
def sig(o):
    return (o['1'], round(F(o,'128',F(o,'32',1)),3), round(F(o,'129',F(o,'32',1)),3),
            round(F(o,'6'),1), o.get('21','-'), o.get('4','0')+o.get('5','0'), o.get('43','-'))
sg=Counter(sig(o) for o in vis)
uniq=sum(1 for v in sg.values() if v==1)
print(f"  distinct (id,scale,rot,colour,flip,hsv) signatures: {len(sg)}  = {100*len(sg)/len(vis):.1f}% of objects")
print(f"  signatures used exactly once: {uniq} ({100*uniq/len(sg):.0f}% of signatures)")
print(f"  top repeated signature used {sg.most_common(1)[0][1]} times")
# neighbourhood stamps: for each object, the multiset of (dx,dy,id) of others within 45u
grid=defaultdict(list)
for o in vis: grid[(int(F(o,'2')//60), int(F(o,'3')//60))].append(o)
def near(o, R=45):
    gx, gy = int(F(o,'2')//60), int(F(o,'3')//60); out=[]
    for a in (-1,0,1):
        for b in (-1,0,1):
            for p in grid.get((gx+a,gy+b),()):
                if p is o: continue
                dx=F(p,'2')-F(o,'2'); dy=F(p,'3')-F(o,'3')
                if abs(dx)<=R and abs(dy)<=R: out.append((round(dx,1),round(dy,1),p['1']))
    return tuple(sorted(out))
import random
random.seed(7)
samp=random.sample(vis, 6000)
nb=Counter(near(o) for o in samp)
solo=sum(v for k,v in nb.items() if k==())
print(f"  sampled 6000: distinct 45u-neighbourhood patterns {len(nb)} "
      f"({100*len(nb)/len(samp):.0f}% unique); isolated objects {solo}")
print(f"  most-repeated neighbourhood appears {nb.most_common(1)[0][1]}x out of 6000")

print("\n--- 2. LOCAL DENSITY / CLUSTERING ---")
d1=[]
for o in random.sample(vis, 4000):
    gx, gy = int(F(o,'2')//60), int(F(o,'3')//60); best=1e9
    for a in (-1,0,1):
        for b in (-1,0,1):
            for p in grid.get((gx+a,gy+b),()):
                if p is o: continue
                d=math.hypot(F(p,'2')-F(o,'2'), F(p,'3')-F(o,'3'))
                if d<best: best=d
    if best<1e8: d1.append(best)
q=st.quantiles(d1,n=10)
print(f"  nearest-neighbour distance (units): p10={q[0]:.2f} p25={st.quantiles(d1,n=4)[0]:.2f} "
      f"median={st.median(d1):.2f} p75={st.quantiles(d1,n=4)[2]:.2f} p90={q[8]:.2f}")
print(f"  fraction with a neighbour within 5u: {100*sum(1 for d in d1 if d<5)/len(d1):.0f}%   within 15u: {100*sum(1 for d in d1 if d<15)/len(d1):.0f}%")

print("\n--- 3. STYLE DRIFT: top-ID overlap between adjacent 800u slices ---")
sl=defaultdict(Counter)
for o in vis: sl[int(F(o,'2')//800)][o['1']]+=1
ks=sorted(sl)
ov=[]
for a,b in zip(ks,ks[1:]):
    A={k for k,_ in sl[a].most_common(15)}; B={k for k,_ in sl[b].most_common(15)}
    if len(sl[a])>5 and len(sl[b])>5: ov.append(len(A&B)/15)
print(f"  adjacent-slice top-15 ID overlap: median {st.median(ov)*100:.0f}%  min {min(ov)*100:.0f}%  max {max(ov)*100:.0f}%")
print(f"  slices: {len(ks)}; distinct IDs per 800u slice: median {st.median([len(sl[k]) for k in ks]):.0f}")

print("\n--- 4. DEPTH BUDGET: objects per z-layer, and their character ---")
zl=defaultdict(list)
for o in vis: zl[o.get('24','unset')].append(o)
order={'-5':0,'-3':1,'-1':2,'unset':3,'1':4,'3':5,'5':6,'7':7,'9':8,'11':9}
for k in sorted(zl, key=lambda k: order.get(k,99)):
    g=zl[k]; c=Counter(o['1'] for o in g).most_common(5)
    s=[F(o,'128',F(o,'32',1)) for o in g]
    print(f"  z={k:>5} n={len(g):>6} ({100*len(g)/len(vis):4.1f}%) medscale={st.median(s):.2f}  "
          + ', '.join(f"{i}({name(int(i))[:16]}):{v}" for i,v in c[:4]))

print("\n--- 5. SCALE BANDS ---")
bands=[(0,.12,'dust'),(.12,.4,'tiny'),(.4,.9,'small'),(.9,1.6,'normal'),(1.6,4,'big'),(4,12,'huge'),(12,1e9,'backdrop')]
s=[F(o,'128',F(o,'32',1)) for o in vis]
for lo,hi,nm2 in bands:
    n=sum(1 for v in s if lo<=v<hi)
    print(f"  {nm2:<9} {lo:>5}-{hi if hi<1e8 else '..':<5} {n:>7} ({100*n/len(s):4.1f}%)")

print("\n--- 6. WHAT SITS IN FRONT OF GAMEPLAY (z>=5) ---")
front=[o for o in vis if F(o,'24',0)>=5]
print("  ", ', '.join(f"{i}:{v}" for i,v in Counter(o['1'] for o in front).most_common(12)))
print(f"  of those, on blending-ish channels? colours: "+', '.join(f"{i}:{v}" for i,v in Counter(o.get('21','-') for o in front).most_common(10)))

print("\n--- 7. TRIGGER CENSUS ---")
tc=Counter(o['1'] for o in objs if int(o['1']) in TRIGGER_IDS)
for i,v in tc.most_common(22): print(f"  {i:>5} {name(int(i)):<22} {v}")
