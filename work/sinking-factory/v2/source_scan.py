import sys, json
from pathlib import Path
from collections import Counter, defaultdict
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / 'handoff/tools'))
import gdparse, render as R
names = R.load_names(str(HERE.parents[1] / 'handoff/research/objectids.yml'))
H, S = gdparse.load(HERE.parent / 'source.level')
h = gdparse.parse_header(H)
print({k: v for k, v in h.items() if k != 'kS38'})
print('source objects', len(S))
xs = [float(o.get('2', 0)) for o in S]
print('x extent', min(xs), max(xs))
# object ids in window vs outside
win = [o for o in S if 16500 <= float(o.get('2', 0)) <= 25000]
print('in 16500..25000:', len(win))
print(Counter(o['1'] for o in win).most_common(40))
special = {'10','11','12','13','47','111','660','745','1331','1933','200','201','202','203','1334','99','101','286','287','45','46','747','1913','1914','1915','1916','1917','2925','2904','2905','2907','2909','2910','2911','2912','2913','2914','2915','2916','2917','2919','2920','2921','2922','2923','2924','1520','899','1006','1007','1049','901','1346','1616','1268','2067','3606','3612','1932','2999','3600','2899','2066','33','32','22','24','23','25','26','27','28','55','56','57','58','59','1812','1818','1819','3602','3603','1934','1935','2903','2901'}
for o in sorted(S, key=lambda o: float(o.get('2', 0))):
    x = float(o.get('2', 0))
    if 15500 <= x <= 26000 and o['1'] in special:
        keep = {k: v for k, v in o.items() if k not in ('155', '156', '36')}
        print(round(x), o['1'], names.get(int(o['1']), ''), {k: keep[k] for k in list(keep)[:26]})
