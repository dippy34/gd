"""A restrained v8 revision: two blind routes and physical portal passages."""
import base64
import bisect
import copy
import json
import math
import numpy as np
import branching_layout as B
from gdparse import load
from gmd import read_gmd, write_gmd, compress

ROOT = B.ROOT


class SimpleLevel(B.BranchLevel):
    def remember(self, *args, **kwargs):
        # Remove the randomized wall minigame, including its extra inputs.
        pass

    def envelope(self, s, a, b, pad=0):
        return super().envelope(s, a, b, pad + (5.5 if s['mode'] == 'wave' else 0))

    def timing_door(self, s, t, width, pad, kind, decoy=False, side=1):
        # A small change to existing timing gates only, preserving wave relief.
        reduction = .65 if s['mode'] not in ('wave', 'ship') else 0
        super().timing_door(s, t, width, max(0, pad-reduction), kind, False, side)


def cut_rect(r, q):
    if not (r['a'] < q[1] and r['b'] > q[0] and r['lo'] < q[3] and r['hi'] > q[2]):
        return [r]
    a, b = max(r['a'], q[0]), min(r['b'], q[1])
    lo, hi = max(r['lo'], q[2]), min(r['hi'], q[3])
    pieces = [(r['a'], a, r['lo'], r['hi']), (b, r['b'], r['lo'], r['hi']),
              (a, b, r['lo'], lo), (a, b, hi, r['hi'])]
    return [dict(r, a=aa, b=bb, lo=ll, hi=hh) for aa, bb, ll, hh in pieces
            if bb-aa > .3 and hh-ll > .3]


def main():
    B.BranchLevel = SimpleLevel
    L = B.build()
    sections = {s['name']: s for s in L.sections}
    old = json.loads((ROOT/'work/deception-plan.json').read_text())
    branches = [copy.deepcopy(b) for b in old['branches'] if b['section'] in ('BLINDFOLD', 'UNDERTOW')]
    assert len(branches) == 2
    cuts = [q for b in branches for q in b['cuts']]
    for q in cuts:
        L.rects = [rr for r in L.rects for rr in cut_rect(r, q)]
    # Rebuild colliders from the cut rectangles. Artwork is built from their
    # exposed union afterward, so there are no stacked false shelf skins.
    L.objects = [o for o in L.objects if o['1'] != '1']
    rects = L.rects
    L.rects = []
    for r in rects:
        L.rect(r['a'], r['b'], r['lo'], r['hi'], r['kind'], r.get('group'))
    removed = []
    for o in list(L.objects):
        if o['1'] != '8':
            continue
        x, y = float(o['2']), float(o['3'])
        r = 15*float(o.get('32', 1))
        if any(x-r < q[1] and x+r > q[0] and y-r < q[3] and y+r > q[2] for q in cuts):
            L.objects.remove(o)
            removed.append((x, y))
    L.spikes = [s for s in L.spikes if not any(abs(s['x']-x) < .001 and abs(s['y']-y) < .001 for x, y in removed)]

    # Every required portal is physically inside a floor-to-roof divider.
    # The opening contains the swept reference body, including both adjacent
    # modes at transitions. Its entire open interval lies inside a conservative
    # 30-unit core of the native portal, with only vertical scale when needed.
    # A normal-size, non-touching native sprite displays the portal. The
    # larger activation object is hidden, so the opening stays enforced without
    # stretching a bright arc across the screen. Both share the same center.
    # This does not depend on the editor's Preview checkbox activating gameplay.
    portal_ids = {10, 11, 12, 13, 47, 99, 101, 111, 200, 201, 660, 745, 1331}
    paths = sorted(L.paths, key=lambda p: p[1])
    xs = [p[1] for p in paths]
    passages = []
    for o in list(L.objects):
        oid = int(o['1'])
        if oid not in portal_ids:
            continue
        x = float(o['2'])
        near = paths[max(0, bisect.bisect_left(xs, x-24)-1):bisect.bisect_right(xs, x+24)+1]
        near = [p for p in near if abs(p[1]-x) <= 6+p[4]+1]
        assert near, (oid, x)
        lo = max(0, min(p[2]-p[4] for p in near)-6)
        hi = min(300, max(p[2]+p[4] for p in near)+6)
        cy = (lo+hi)/2
        sy = max(1, math.ceil((hi-lo+4)/30*100)/100)
        o.update({'3':str(round(cy, 5)), '128':'1', '129':str(sy), '507':'1', '372':'1'})
        visual = dict(o, **{'129':'1', '121':'1', '134':'1', '13':'0', '20':'12'})
        L.objects.append(visual)
        o['135'] = '1'
        L.rect(x-6, x+6, -30, lo, 'portal passage lower')
        L.rect(x-6, x+6, hi, 330, 'portal passage upper')
        passages.append(dict(id=oid, x=x, y=cy, a=x-6, b=x+6, lo=lo, hi=hi,
                             scale_y=sy, conservative_core_height=30*sy))

    for o in L.objects:
        if o['1'] in ('36', '84', '141'):
            o.update({'57':'8500', '507':'1', '372':'1'})
    L.obj(1007, 0, -600, **{'51':8500, '35':.13, '10':0, '20':5})
    H, _ = load(str(ROOT/'work/v8-nocturne-base.level'))
    ser = lambda o: ','.join(f'{k},{v}' for k, v in o.items())
    raw = ';'.join([H]+[ser(o) for o in L.objects])+';'
    f = read_gmd(ROOT/'outputs/v8-1573528-deception.gmd')
    desc = 'Song 1573528. Original spider fakeouts retained. Two other blind routes, slightly tighter timings, and solid passages enforcing required portals.'
    f.update({'k4':('s',compress(raw)), 'k48':('i',str(len(L.objects))),
              'k3':('s',base64.urlsafe_b64encode(desc.encode()).decode()), 'k14':('f',False)})
    write_gmd(ROOT/'work/simple-base.gmd', f)
    (ROOT/'work/v8-simple-base.level').write_text(raw)
    P = dict(sections=L.sections, controls=sorted(L.controls,key=lambda e:e['time']),
             paths=L.paths, rectangles=L.rects, spikes=L.spikes, orbs=L.orbs,
             memories=[], random_locks=[], fakeouts=copy.deepcopy(old['fakeouts']), gates=L.gates, moves=L.moves,
             timing_features=L.timing_features, phrases=L.phrases, branches=branches,
             portal_passages=passages, speed_schedule=[[s['t0'],s['speed']] for s in L.sections],
             end_time=B.M.END, end_x=B.M.xt(B.M.END), bpm=131, song=1573528, phase=B.M.PHASE,
             objects=len(L.objects), slow_percent=old['slow_percent'],
             timing_clearance_reduction=.65, wave_extra_clearance_each_side=5.5,
             validation_limit='Approximate route/replay checks; full native completion remains unverified.')
    assert P['paths'] == old['paths']
    assert P['controls'] == [e for e in old['controls'] if e['kind'] != 'memory']
    (ROOT/'work/simple-plan.json').write_text(json.dumps(P,separators=(',',':')))
    print(json.dumps(dict(objects=len(L.objects), inputs=len(L.controls), branches=len(branches),
                          portal_passages=len(passages), max_portal_scale_y=max(p['scale_y'] for p in passages))))


if __name__ == '__main__':
    main()
