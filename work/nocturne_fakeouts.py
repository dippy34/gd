"""Restore layered false shelves and cut deliberate false gaps in real banks."""
from pathlib import Path
from collections import Counter, defaultdict
import base64
import hashlib
import json
import math
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'work/handoff/tools'))
from gdparse import load
from gmd import read_gmd, write_gmd, compress

P = json.loads((ROOT / 'work/nocturne-plan.json').read_text())
H, O = load(str(ROOT / 'work/v8-nocturne-skinned.level'))
R = [r for r in P['rectangles'] if not r.get('group')]
bins = defaultdict(list)
for r in R:
    for b in range(math.floor(r['a'] / 100), math.floor(r['b'] / 100) + 1):
        bins[b].append(r)
decoys = []
art = []
switch_art = []


def nearby(a, b):
    return list({id(r): r for i in range(math.floor(a / 100), math.floor(b / 100) + 1) for r in bins[i]}.values())


def box(a, b, lo, hi, ch=2, z=5, group=None):
    if b - a < .1 or hi - lo < .1:
        return
    obj = {'1': '211', '2': str((a + b) / 2), '3': str((lo + hi) / 2),
           '128': str((b - a) / 30), '129': str((hi - lo) / 30),
           '21': str(ch), '22': str(ch), '24': str(z), '25': '2', '20': '11',
           '64': '1', '67': '1', '96': '1', '121': '1', '134': '1'}
    if group is not None:
        obj['57'] = str(group)
    O.append(obj)
    art.append(obj)
    return obj


def frame(a, b, lo, hi, group=None, ch=2, fill=1, z=5, seams=False):
    box(a, b, lo, hi, fill, z, group)
    for low, high in ((lo, lo + .8), (hi - .8, hi)):
        box(a, b, low, high, ch, z + 1, group)
    for left, right in ((a, a + .65), (b - .65, b)):
        box(left, right, lo, hi, ch, z + 1, group)
    if seams:
        for x in range(math.ceil((a + 6) / 30) * 30, math.floor(b - 6), 30):
            box(x, x + .55, lo, hi, 6, z + 1, group)


def overlaps(q, r, pad=0):
    a, b, lo, hi = q
    return a < r['b'] + pad and b > r['a'] - pad and lo < r['hi'] + pad and hi > r['lo'] - pad


def avoid_orbs(q):
    a, b, lo, hi = q
    return not any(a - 25 < o['x'] < b + 25 and lo - 25 < o['y'] < hi + 25 for o in P['orbs'])


def free_spans(a, b, lo, hi):
    spans = [(a, b)]
    # False ledges terminate at actual pillars rather than outlining their
    # interiors. They can look attached while remaining non-colliding.
    for r in nearby(a, b):
        if not lo < r['hi'] or not hi > r['lo']:
            continue
        next_spans = []
        for aa, bb in spans:
            if r['b'] <= aa or r['a'] >= bb:
                next_spans.append((aa, bb))
            else:
                if r['a'] > aa:
                    next_spans.append((aa, r['a']))
                if r['b'] < bb:
                    next_spans.append((r['b'], bb))
        spans = next_spans
    return [(aa, bb) for aa, bb in spans if bb - aa >= 25]


for s in P['sections']:
    spider = s['mode'] == 'spider'
    local = [r for r in R if s['x0'] <= r['a'] and r['b'] <= s['x1']]
    rails = [r for r in local if r['kind'] in ('teleport shelf', 'island rail', 'upper rail', 'suspended landing')]
    # Restore the old spider's line-and-shelf language. Give real supports
    # and false supports the same dark frames and 30-unit segmentation.
    if spider:
        for r in rails:
            frame(r['a'], r['b'], r['lo'], r['hi'], seams=True)
    for index, r in enumerate(rails):
        offsets = (-108, -54, 54, 108) if spider else ((54, -54) if index % 2 == 0 else (-72, 72))
        for offset in offsets:
            lo = round((r['lo'] + offset) / 6) * 6
            hi = lo + (10 if spider else min(12, r['hi'] - r['lo']))
            if not 18 <= lo < hi <= 282:
                continue
            for a, b in free_spans(r['a'] + 3, r['b'] - 3, lo, hi):
                q = (a, b, lo, hi)
                if not avoid_orbs(q) or any(overlaps(q, d, 3) for d in decoys):
                    continue
                frame(*q, seams=spider)
                decoys.append(dict(section=s['name'], kind='false teleport shelf' if spider else 'false landing rail',
                                   a=a, b=b, lo=lo, hi=hi, host=[r['a'], r['b'], r['lo'], r['hi']]))

    # Multiple apparent openings on the same real bank create an actual
    # visual choice. The false aperture covers a still-solid bank, and its
    # approach rails use the same vocabulary as the real landing shelves.
    gates = [g for g in P['gates'] if g['section'] == s['name']]
    for index, gate in enumerate(gates):
        if s['mode'] in ('wave', 'ship') and index % 2:
            continue
        a, b = gate['a'], gate['b']
        banks = [r for r in local if abs(r['a'] - a) < .01 and abs(r['b'] - b) < .01 and r['hi'] - r['lo'] > 58]
        used = 0
        for bank in sorted(banks, key=lambda r: -(r['hi'] - r['lo'])):
            height = 33 if spider else 30
            centers = [y for y in range(36, 277, 36) if bank['lo'] + 8 < y - height / 2 and y + height / 2 < bank['hi'] - 8]
            true_center = (gate['lo'] + gate['hi']) / 2
            centers.sort(key=lambda y: abs(y - true_center))
            for cy in centers:
                q = (a - .9, b + .9, cy - height / 2, cy + height / 2)
                if not avoid_orbs(q) or any(overlaps(q, d, 3) for d in decoys):
                    continue
                # A bank-wide dark cut, two lip lines, and horizontal ledges.
                # There is no oversized rectangular cage around the pillar.
                box(*q, ch=5, z=7)
                box(a - 1.5, b + 1.5, q[2] - .8, q[2], 2, 8)
                box(a - 1.5, b + 1.5, q[3], q[3] + .8, 2, 8)
                reach = (45, 66, 54, 81)[index % 4]
                for aa, bb in free_spans(a - reach, b + reach, q[2] - 5, q[2]):
                    if avoid_orbs((aa, bb, q[2] - 5, q[2])):
                        box(aa, bb, q[2] - .8, q[2], 2, 6)
                        box(aa, bb, q[2] - 5, q[2] - 4.3, 6, 6)
                decoys.append(dict(section=s['name'], kind='false opening in solid bank',
                                   a=q[0], b=q[1], lo=q[2], hi=q[3],
                                   bank=[bank['a'], bank['b'], bank['lo'], bank['hi']]))
                used += 1
                if used >= (2 if spider else 1):
                    break
            if used >= (2 if spider else 1):
                break

# Replace every hidden white toggle orb with identical dull olive hardware.
# Both mutually exclusive copies inherit exactly their original visible group.
for native in list(O):
    if native['1'] != '1594':
        continue
    assert native.get('135') == '1' and native.get('445') == '1'
    x, y = float(native['2']), float(native['3'])
    group = int(native['57'])
    start = len(art)
    frame(x - 8, x + 8, y - 8, y + 8, group, ch=13, fill=1, z=9)
    box(x - 3.5, x + 3.5, y - 3.5, y + 3.5, 7, 11, group)
    # Two tiny contact marks keep the click target distinguishable at study
    # distance without a white ring, glow, pulse or animated mask.
    box(x - 11, x - 9, y - .6, y + .6, 4, 11, group)
    box(x + 9, x + 11, y - .6, y + .6, 4, 11, group)
    switch_art.append(dict(group=group, target=int(native['51']), x=x, y=y, objects=len(art) - start))

serialize = lambda obj: ','.join(f'{k},{v}' for k, v in obj.items())
raw = ';'.join([H] + [serialize(o) for o in O]) + ';'
fields = read_gmd(ROOT / 'work/nocturne-skinned.gmd')
fields['k4'] = ('s', compress(raw))
fields['k48'] = ('i', str(len(O)))
fields['k3'] = ('s', base64.urlsafe_b64encode(b'Song 1573528. Dark layered false routes. Wider wave clearance; dim reaction switches. Wall present: hit. No wall: skip.').decode())
out = ROOT / 'outputs/v8-1573528-nocturne.gmd'
write_gmd(out, fields)
(ROOT / 'work/v8-nocturne.level').write_text(raw)
P.update(objects=len(O), fakeouts=decoys, switch_art=switch_art)
(ROOT / 'work/nocturne-plan.json').write_text(json.dumps(P, separators=(',', ':')))
audit = dict(objects=len(O), added_art_objects=len(art), fakeouts=len(decoys),
             by_kind=dict(Counter(d['kind'] for d in decoys)),
             by_section=dict(Counter(d['section'] for d in decoys)),
             switch_skins=len(switch_art), sha256=hashlib.sha256(out.read_bytes()).hexdigest())
(ROOT / 'work/nocturne-fakeout-audit.json').write_text(json.dumps(audit, indent=2))
print(json.dumps(audit, indent=2))
