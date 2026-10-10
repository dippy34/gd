"""Where is the gameplay in a reference level? Print per-1000u bins: portals, orbs/pads, hazard y-range, object density."""
import sys
from pathlib import Path
from collections import Counter, defaultdict
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / 'handoff/tools'))
import gdparse
head, objs = gdparse.load(sys.argv[1]); step = float(sys.argv[2]) if len(sys.argv) > 2 else 1000
portals = {'12': 'cube', '13': 'ship', '47': 'ball', '111': 'ufo', '660': 'wave', '745': 'robot', '1331': 'spider', '1933': 'swing', '200': '.5x', '201': '1x', '202': '2x', '203': '3x', '1334': '4x', '10': 'gravN', '11': 'gravF', '99': 'big', '101': 'mini', '286': 'dual', '287': 'solo', '45': 'mirror', '46': 'unmirror', '3600': 'END', '31': 'startpos'}
haz = {'8', '39', '103', '392', '216', '217', '218', '458', '459', '1715', '1716', '1717', '1718', '1719', '1720', '1721', '1722', '9', '61', '243', '244', '366', '367', '368', '446', '447', '667', '720', '1582', '1619', '1620', '1701', '1702', '1703', '88', '89', '98', '397', '398', '399', '740', '741', '742', '1705', '1706', '1707', '1708', '1709', '1710', '1734', '1735', '1736', '1889', '1890', '1891', '186', '187', '188', '678', '679', '680'}
orbs = {'36': 'Y', '84': 'B', '141': 'P', '1022': 'G', '1330': 'K', '1333': 'R', '1704': 'Gd', '1751': 'Dash', '35': 'yp', '67': 'bp', '140': 'pp', '1332': 'rp', '3004': 'sp'}
bins = defaultdict(list)
for o in objs:
    bins[int(float(o.get('2', 0)) // step)].append(o)
for b in sorted(bins):
    oo = bins[b]
    ps = sorted((round(float(o['2'])), portals[o['1']], round(float(o.get('3', 0)))) for o in oo if o['1'] in portals)
    hz = [float(o['3']) for o in oo if o['1'] in haz and o.get('121') != '1']
    ob = Counter(orbs[o['1']] for o in oo if o['1'] in orbs)
    ys = sorted(float(o.get('3', 0)) for o in oo)
    print(f"x{int(b*step):>7} n={len(oo):>6} y10-90={ys[len(ys)//10]:.0f}..{ys[len(ys)*9//10]:.0f} haz={len(hz)} {('hy %.0f..%.0f' % (min(hz), max(hz))) if hz else ''} orbs={dict(ob)} portals={ps[:8]}")
