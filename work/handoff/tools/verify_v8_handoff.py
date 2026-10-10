import sys, math, json, os; sys.path.insert(0,'.'); sys.path.insert(0,'.')
from collections import Counter
from gdparse import load, parse_header, parse_ks38
from gmd import read_gmd, decompress
OUT='../../../outputs/v8.gmd'
f=read_gmd(OUT); lvl=decompress(f['k4'][1])
TMP='../../v8-handoff-roundtrip.level'
os.makedirs(os.path.dirname(TMP),exist_ok=True); open(TMP,'w').write(lvl)
head,objs=load(TMP)
print(f"1. re-read from .gmd: {f['k2'][1]!r}  objects {len(objs)} (k48 {f['k48'][1]})  song {f['k45'][1]}")
try:
    from gmdkit.models.level import Level
    L=Level.from_file(OUT); k4=L.get('k4')
    print(f"   gmdkit (independent parser) loaded {len(k4.objects)} objects and re-serialised {len(L.to_string())} bytes")
except Exception as e: print('   gmdkit:',type(e).__name__,e)

src_head,src=load('../level/layout.level')
MYTRIG={'899','1006','1007','901','1346'}
def is_layout(o):
    if o.get('121')=='1' and o.get('134')=='1': return False
    if o['1'] in MYTRIG and o.get('20')=='5': return False
    return True
def sig(o): return tuple(sorted(o.items()))
a=Counter(sig(o) for o in src if is_layout(o)); b=Counter(sig(o) for o in objs if is_layout(o))
print(f"\n2. layout: {sum(a.values())} objects in the source, {sum(b.values())} in the build; "
      f"missing {sum((a-b).values())}, changed/added {sum((b-a).values())}")

deco=[o for o in objs if o.get('121')=='1' and o.get('134')=='1']
HAZ={'8','39','103','152','153','154','155','177','216','217','218','458','1705','1706','1709','920','1582','679','1735','1736','3042','3047','1715'}
INT={'10','11','12','13','45','46','47','99','101','111','286','287','660','745','1331','200','201','202','203','1334','35','36','67','84','140','141','1332','1333','3600','31','1917','2063'}
print(f"   decoration {len(deco)}; all passable+no-touch "
      f"{all(o.get('121')=='1' and o.get('134')=='1' for o in deco)}; "
      f"hazard/interactive ids used as decoration {sum(1 for o in deco if o['1'] in HAZ|INT)}")
front=[o for o in deco if int(o.get('24',0))>=1]
H0=parse_header(head)
BLEND={int(c['6']) for c in parse_ks38(H0['kS38']) if c.get('5')=='1'}
opaque=[o for o in front if int(o['21']) not in BLEND and o['1']!='1292']
print(f"   decoration drawn IN FRONT of the gameplay: {len(front)} "
      f"({100*len(front)/len(deco):.1f}%) -- the vignette plus the black hole's glow")
print("   front object ids:", Counter(o['1'] for o in front).most_common())
print(f"   of those, OPAQUE (could hide the corridor): {len(opaque)}")
mv={int(o['51']) for o in objs if o['1']=='901'}|{int(o['51']) for o in objs if o['1']=='1346'}|{int(o.get('71',0)) for o in objs if o['1']=='1346'}
bad=[o for o in objs if '57' in o and int(o['57']) in mv and not (o.get('121')=='1' and o.get('134')=='1')]
print(f"   gameplay objects inside a Move/Rotate group: {len(bad)}")

ids=Counter(o['1'] for o in deco)
print(f"\n3. vocabulary: {len(ids)} distinct decoration ids -> " +
      ', '.join(f"{k}x{v}" for k,v in ids.most_common()))
H=parse_header(head); chans={int(c['6']) for c in parse_ks38(H['kS38']) if '6' in c}
used={int(o['21']) for o in deco}|{int(o.get('21',1)) for o in objs if is_layout(o) and '21' in o}
print(f"   colour channels defined {len(chans)}; used-but-undefined {sorted(used-chans) or 'none'}")
ldm=sum(1 for o in deco if o.get('103')=='1')
cols=Counter(int(float(o['2'])//30) for o in objs); v=sorted(cols.values())
print(f"\n4. {len(objs)} objects total, {os.path.getsize(OUT)/1e6:.2f} MB; LDM hides {ldm} "
      f"({100*ldm/len(deco):.0f}% of deco) leaving {len(objs)-ldm}")
print(f"   objects per 30u column: min {v[0]} med {v[len(v)//2]} p90 {v[int(.9*len(v))]} max {v[-1]}")
