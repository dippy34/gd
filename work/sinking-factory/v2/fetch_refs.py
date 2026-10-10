"""Download the two style references from the game's public level API."""
import time, urllib.request, urllib.parse, sys, json
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / 'handoff/tools'))
import gmd
REFS = {'flamewall': 126242564, 'avernus': 89496627}
meta = {}
for name, lid in REFS.items():
    out = HERE / 'refs' / f'{name}-{lid}.level'
    body = urllib.parse.urlencode({'levelID': lid, 'secret': 'Wmfd2893gb7'}).encode()
    req = urllib.request.Request('http://www.boomlings.com/database/downloadGJLevel22.php',
                                 data=body, headers={'User-Agent': ''})
    raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
    if raw.strip() == '-1' or ':4:' not in raw:
        print('REJECTED', name, raw[:80]); time.sleep(4); continue
    head = raw.split('#')[0]
    parts = head.split(':')
    d = {parts[i]: parts[i + 1] for i in range(0, len(parts) - 1, 2)}
    lvl = gmd.decompress(d['4'])
    out.write_text(lvl)
    meta[name] = {k: d.get(k) for k in ['1', '2', '5', '6', '12', '13', '14', '15', '17', '35', '45']}
    meta[name]['objects'] = lvl.count(';') - 1
    print(name, lid, 'name=', d.get('2'), 'objects~', meta[name]['objects'], 'chars', len(lvl))
    time.sleep(4)
(HERE / 'refs' / 'meta.json').write_text(json.dumps(meta, indent=2))
