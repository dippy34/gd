"""Resolved-luminance profile of a level: what fraction of objects are actually
bright once channel colour, opacity and the per-object HSV value multiplier are
applied. Run for KOCMOC and for the build to compare."""
import sys, math, statistics as st
sys.path.insert(0,'.')
from gdparse import load, parse_header, parse_ks38
from collections import Counter, defaultdict

def profile(path, label):
    head, objs = load(path)
    H = parse_header(head)
    base = {}
    for c in parse_ks38(H.get('kS38','')):
        if '6' not in c: continue
        base[int(c['6'])] = (int(float(c.get('1',255))), int(float(c.get('2',255))), int(float(c.get('3',255))),
                             c.get('5')=='1', float(c.get('7',1)), int(c['9']) if c.get('9') else None)
    # colour triggers give the channel its running value; take the last one before x
    trig = defaultdict(list)
    for o in objs:
        if o.get('1')=='899' and '23' in o:
            try: trig[int(o['23'])].append((float(o['2']), (int(float(o.get('7',255))),int(float(o.get('8',255))),int(float(o.get('9',255))))))
            except: pass
    for k in trig: trig[k].sort()
    def rgb_of(cid, x, d=0):
        if d > 5: return (255,255,255), False, 1.0
        if cid in trig:
            c = [t for t in trig[cid] if t[0] <= x]
            if c: return c[-1][1], base.get(cid,(0,0,0,False,1,None))[3], base.get(cid,(0,0,0,False,1,None))[4]
        b = base.get(cid)
        if b is None: return (255,255,255), False, 1.0
        if b[5] is not None:
            rgb,_,_ = rgb_of(b[5], x, d+1); return rgb, b[3], b[4]
        return (b[0],b[1],b[2]), b[3], b[4]
    TRIGIDS = {'899','901','1006','1007','1049','1268','1346','1347','1520','1585','1595','2899','3600','1616','1811','1912','2903','2919','2914','2911','2909','1916','1913','2067','2904','3006','3007','3010','2063','1917','1931','1934','1935','2016','2062'}
    lum = []; area = []
    for o in objs:
        if o['1'] in TRIGIDS: continue
        try:
            x = float(o['2']); cid = int(float(o.get('21', 1)))
        except: continue
        rgb, blend, op = rgb_of(cid, x)
        v = 1.0
        if o.get('41')=='1' and '43' in o:
            p = o['43'].split('a')
            try: v = float(p[2])
            except: pass
        L = (0.2126*rgb[0]+0.7152*rgb[1]+0.0722*rgb[2])/255.0 * min(3.5, v) * op
        lum.append(min(1.6, L))
        try: sx=float(o.get('128', o.get('32',1))); sy=float(o.get('129', sx))
        except: sx=sy=1.0
        area.append(abs(sx*sy))
    lum.sort()
    n = len(lum)
    def q(p): return lum[int(p*(n-1))]
    print(f"--- {label}: {n} visible objects")
    print(f"    luminance p10={q(.1):.3f} p25={q(.25):.3f} med={q(.5):.3f} p75={q(.75):.3f} p90={q(.9):.3f} p99={q(.99):.3f}")
    for th in (0.05, 0.15, 0.35, 0.6):
        k = sum(1 for v in lum if v > th)
        print(f"    brighter than {th:.2f}: {k:>7} ({100*k/n:5.1f}%)")
    print(f"    'ink' (L<=0.03): {sum(1 for v in lum if v<=0.03)} ({100*sum(1 for v in lum if v<=0.03)/n:.1f}%)")
    a = sorted(area); print(f"    footprint scale-area p50={a[n//2]:.2f} p90={a[int(.9*n)]:.2f} p99={a[int(.99*n)]:.2f}")

def deco_only(path, label):
    import io
    head, objs = load(path)
    keep = [o for o in objs if (o.get('121') == '1' and o.get('134') == '1') or o.get('1') == '899']
    body = ';'.join(','.join(f"{k},{v}" for k, v in o.items()) for o in keep)
    open('/tmp/_deco.level', 'w').write(head + ';' + body + ';')
    profile('/tmp/_deco.level', label)

profile('../research/109381612.level', 'KOCMOC UNLEASHED hol (all)')
profile('../obsidian_kocmoc.level', 'this build (all)')
deco_only('../obsidian_kocmoc.level', 'this build (decoration only)')
