import sys
from pathlib import Path
from collections import Counter
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / 'handoff/tools'))
import gdparse
head, objs = gdparse.load(sys.argv[1])
for tid in sys.argv[2].split(','):
    tr = [o for o in objs if o['1'] == tid]
    keys = Counter(k for o in tr for k in o)
    print(tid, len(tr), sorted(keys.items(), key=lambda kv: -kv[1])[:40])
    for o in tr[:3]: print('   ', o)
    if tid in ('899', '1006'):
        print('   spawn-triggered (62=1):', sum(o.get('62') == '1' for o in tr), ' touch (11=1):', sum(o.get('11') == '1' for o in tr), ' copy (50):', sum('50' in o for o in tr), ' groups-target 52=1:', sum(o.get('52') == '1' for o in tr))
# which objects have enter-effects / hsv / opacity
print('objects with HSV main enabled (41=1):', sum(o.get('41') == '1' for o in objs), ' detail (42=1):', sum(o.get('42') == '1' for o in objs))
print('dont-fade 64:', sum(o.get('64') == '1' for o in objs), ' dont-enter 67:', sum(o.get('67') == '1' for o in objs), ' no-glow 96:', sum(o.get('96') == '1' for o in objs))
print('hidden 135:', sum(o.get('135') == '1' for o in objs), ' high detail 103:', sum(o.get('103') == '1' for o in objs))
print('z-order 25 present:', sum('25' in o for o in objs))
