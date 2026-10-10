"""Check the exported file, exact baseline preservation and UI trigger wiring."""
from pathlib import Path
from collections import Counter
import sys, json, hashlib, math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'work/handoff/tools'))
import gmd, gdparse

manifest = json.loads((HERE / 'closing-fire-manifest.json').read_text())
fx = manifest['closing_fire']
out = ROOT / 'outputs/The Sinking Factory - CLOSING-FIRE.gmd'
base = ROOT / 'outputs/The Sinking Factory - CUSTOM-ORBS.gmd'
source = Path(str(Path(__file__).resolve().parents[2]/'inputs/The Sinking Factory.gmd'))
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert digest(base) == manifest['base_sha256'] == '802bc6c3ed846833bac104d893f3002918e3d170db00f80bb2e0ff161643380c'
assert digest(source) == manifest['source_sha256'] == '9429ecc3df11cd6d0aab4b573b4bb0da9560240da78ec92223f2f92436b9386a'
assert digest(out) == manifest['output_sha256']
f, bf = gmd.read_gmd(out), gmd.read_gmd(base)
raw = gmd.decompress(f['k4'][1])
assert raw == (HERE / 'closing-fire.level').read_text()
assert gmd.decompress(gmd.compress(raw)) == raw
h, objs = gdparse.load(HERE / 'closing-fire.level')
bh, original = gdparse.load(HERE / 'custom-orbs.level')
assert gmd.decompress(bf['k4'][1]) == (HERE / 'custom-orbs.level').read_text()
assert len(original) == manifest['base_object_count'] == 57465
assert len(objs) == manifest['total_objects'] == int(f['k48'][1])
assert objs[:len(original)] == original
added = objs[len(original):]
assert len(added) == manifest['closing_fire_added_objects']
assert manifest['source_objects'] + manifest['added_objects'] == len(objs)
assert f['k2'][1] == 'Factory Encroached' and f['k45'][1] == '1569886'
assert {k:v for k,v in f.items() if k not in {'k2','k4','k48'}} == {k:v for k,v in bf.items() if k not in {'k2','k4','k48'}}

head, oldhead = gdparse.parse_header(h), gdparse.parse_header(bh)
assert {k:v for k,v in head.items() if k != 'kS38'} == {k:v for k,v in oldhead.items() if k != 'kS38'}
colors = {c['6']:c for c in gdparse.parse_ks38(head['kS38'])}
oldcolors = {c['6']:c for c in gdparse.parse_ks38(oldhead['kS38'])}
assert all(colors[k] == v for k,v in oldcolors.items())
newcolors = set(map(str, range(760, 768)))
assert set(colors)-set(oldcolors) == newcolors
assert not any(o.get(k) in newcolors for o in original for k in ['21','22','23','50'])

def gs(o): return set(o.get('57', '').split('.')) - {''}
oldgroups = {g for o in original for g in gs(o)}
# Conservative: include every group-like target reference, even when an
# object's property can instead represent a color channel.
oldgroups |= {o[k] for o in original for k in ['51','71','395','396'] if k in o}
newgroups = {g for o in added for g in gs(o)}
assert not oldgroups & newgroups
assert not any(o.get('61') == '96' for o in original)
assert not any(160 <= int(o.get('20', 0)) <= 169 for o in original)

controls = [o for o in added if o['1'] in {'3613','901','1007'}]
reference = [o for o in added if o['1'] == '2016']
art = [o for o in added if o not in controls and o not in reference]
assert len(reference) == 1
assert gs(reference[0]) == {'1205'} and reference[0]['135'] == '1'
assert [float(reference[0][k]) for k in ['2','3']] == fx['camera_reference']
assert set(o['1'] for o in added) <= {'211','693','923','924','1937','920','504','2016','3613','901','1007'}
for o in added:
    assert o['61'] == '96'
    assert o['20'] in fx['editor_layers']
    assert all(math.isfinite(float(o[k])) for k in ['1','2','3'])
    assert all(float(o.get(k, 1)) > 0 for k in ['128','129'])
    assert len(gs(o)) <= 10
for o in art:
    assert o.get('121') == o.get('134') == o.get('96') == '1'
    assert '1200' in gs(o) and '1205' not in gs(o)
    assert o['24'] == '11'
    assert len(gs(o) & {'1201','1202','1203','1204'}) == 1
for o in controls:
    assert o['51'] in newgroups
    assert not gs(o)
    if '71' in o: assert o['71'] == '1205'

schedule = manifest['speed_schedule']
def xt(t):
    return sum(max(0, min(t, schedule[i+1][0] if i+1 < len(schedule) else t)-start)*v for i,(start,v) in enumerate(schedule))
def tx(x):
    for i,(t,v) in enumerate(schedule):
        if i+1 == len(schedule) or x < xt(schedule[i+1][0]): return t+(x-xt(t))/v
def near(a,b): return abs(float(a)-float(b)) < .00002

ui = [o for o in controls if o['1'] == '3613']
assert len(ui) == 4
mainmoves = []
vectors = {'left':(16,0), 'right':(-16,0), 'bottom':(0,12), 'top':(0,-12)}
anchors = {'left':('3','6'), 'right':('4','6'), 'bottom':('2','7'), 'top':('2','8')}
for e in fx['edges']:
    g = str(e['group'])
    trigger = [o for o in ui if o['51'] == g]
    assert len(trigger) == 1
    t = trigger[0]
    assert t['71'] == '1205' and (t['385'],t['386']) == anchors[e['edge']]
    assert t['387'] == t['388'] == '0'
    moves = [o for o in controls if o['1'] == '901' and o['51'] == g]
    assert len(moves) == 1
    move = moves[0];mainmoves.append(move)
    assert (float(move['28']),float(move['29'])) == vectors[e['edge']]
    assert near(tx(float(move['2'])), fx['start_time'])
    assert near(move['10'], fx['fully_closed_time']-fx['start_time'])
    assert move['30'] == '0'
    assert e['final_nominal_thickness']/e['initial_nominal_thickness'] == 1.5
    assert e['final_nominal_thickness']-e['initial_nominal_thickness'] == e['advance']
    assert e['advance'] < 65  # Outer edge remains outside the viewport.
    assert sum(o['1'] in {'923','924','1937','920'} and g in gs(o) for o in art) == e['native_flames']

embers = [o for o in art if o['20'] == '163']
assert len(embers) == 144
for cohort in fx['ember_cohorts']:
    g = str(cohort['group'])
    members = [o for o in embers if g in gs(o)]
    assert len(members) == cohort['particles']
    moves = sorted([o for o in controls if o['1']=='901' and o['51']==g], key=lambda o:float(o['2']))
    assert moves
    for i,o in enumerate(moves):
        t = tx(float(o['2']))
        assert o['30'] == '13'
        assert fx['start_time']-.00002 <= t < fx['fully_closed_time']
        assert near(t + float(o['10']), min(t+2.4,fx['fully_closed_time']))
        if i:
            previous = moves[i-1]
            assert near(t, tx(float(previous['2']))+float(previous['10']))
            assert near(float(o['28']), -float(previous['28']))
            assert near(float(o['29']), -float(previous['29']))

alpha = sorted([o for o in controls if o['1']=='1007'], key=lambda o:float(o['2']))
assert len(alpha) == 4 and all(o['51']=='1200' for o in alpha)
assert [float(o['35']) for o in alpha] == [0,.94,0,0]
assert float(alpha[0]['2']) == 0 and float(alpha[0]['10']) == 0
assert near(tx(float(alpha[1]['2'])), fx['start_time']) and float(alpha[1]['10']) == .7
assert near(tx(float(alpha[2]['2'])), fx['fade_start_time'])
assert near(tx(float(alpha[2]['2']))+float(alpha[2]['10']), fx['off_time'])
assert near(tx(float(alpha[3]['2'])), fx['off_time']) and float(alpha[3]['10']) == 0
assert fx['start_time'] < fx['fully_closed_time'] < fx['fade_start_time'] < fx['off_time']

# Direct edge anchoring leaves no aspect-ratio gap. Bounds are conservative
# nominal body thicknesses; flame tips and embers have irregular silhouettes.
aspect_checks = {}
for name,aspect in [('4:3',4/3),('16:9',16/9),('21:9',21/9)]:
    w,h = 320*aspect,320
    assert all(e['span'] >= (w if e['edge'] in {'top','bottom'} else h)+60 for e in fx['edges'])
    clear_w,clear_h = w-2*48,h-2*36
    assert clear_w > 0 and clear_h > 0
    aspect_checks[name] = {'ui_size':[w,h], 'nominal_final_clear_center':[clear_w,clear_h]}

result = {
    'passed':True, 'roundtrip_valid':True, 'source_unchanged':True,
    'baseline_objects_preserved_exactly':len(original),
    'baseline_header_and_color_channels_preserved':True,
    'custom_orbs_and_restored_portals_preserved':True,
    'blue_orb_group_fix_preserved':True,
    'new_group_and_color_collisions':0, 'added_collision_objects':0,
    'total_objects':len(objs), 'added_objects':len(added),
    'native_looping_flame_objects':sum(e['native_flames'] for e in fx['edges']),
    'ember_particles':len(embers), 'camera_edge_anchors':4,
    'closing_moves':len(mainmoves), 'nominal_thickness_multiplier':1.5,
    'timing_seconds':{k:fx[k] for k in ['start_time','fully_closed_time','fade_start_time','off_time']},
    'aspect_ratio_bounds':aspect_checks,
    'editor_layers':dict(Counter(o['20'] for o in added)),
    'effect_editor_section_layer':96,
    'native_playtest':False,
    'limitation':'Atlas renders model UI anchoring and trigger transforms; they do not verify native runtime behavior or gameplay visibility.',
    'sha256':digest(out),
}
(HERE / 'closing-fire-validation.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
