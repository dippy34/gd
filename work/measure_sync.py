"""Timing perturbations and sync measurements for the final exported file."""
import hashlib,json
from pathlib import Path
import numpy as np
import replay_sync as NEW
import replay_rebalance as OLD
ROOT=Path(__file__).resolve().parent.parent
AT=np.array([q['time'] for q in json.loads((ROOT/'work/music-1573528-analysis.json').read_text())['onsets']])

def section(R,name):return next(s for s in R.P['sections'] if s['name']==name)
def controls(R,name,kind):
    s=section(R,name)
    return [e for e in R.P['controls'] if s['t0']<=e['time']<s['t1'] and e['kind']==kind]
def probe(R,name,e):
    tests=[]
    for tick in range(-12,13):
        result,_=R.replay(section(R,name),perturb_time=e['time'],input_shift=tick/240,stop_at=e['time']+.85,stop_first=True)
        tests.append(dict(shift_ms=round(tick/240*1000,3),passes=not bool(result['errors'])))
    assert tests[12]['passes'],(name,e)
    passed=[q['shift_ms'] for q in tests if q['passes']]
    return dict(time=e['time'],kind=e['kind'],orb=e.get('orb_id'),passes=len(passed),range_ms=[min(passed),max(passed)],tests=tests)

balance=[]
for R,label in [(OLD,'previous'),(NEW,'new')]:
    tested=[]
    for kind,indices in [('release',[0,1,2,3]),('jump',[0,4,-2]),('orb',[-3,-2,-1])]:
        es=controls(R,'LAST WORD',kind)
        tested.extend(probe(R,'LAST WORD',es[i]) for i in indices)
    if label=='new':assert min(q['passes'] for q in tested)>=5,[(q['time'],q['passes']) for q in tested]
    balance.append(dict(version=label,passes=sum(q['passes'] for q in tested),total=25*len(tested),probes=tested))
    print(label,'final cube tolerance',balance[-1]['passes'],'/',balance[-1]['total'],flush=True)
assert balance[1]['passes']<balance[0]['passes'],'new ending is not meaningfully tighter in sampled tests'
spider=[]
for name in ('BLIND ELEVATOR','RECALL'):
    es=controls(NEW,name,'orb')
    for e in (es[0],es[len(es)//2],es[-1]):
        p=probe(NEW,name,e);p['section']=name;spider.append(p)
        assert p['passes']>=5,(name,p['range_ms'])
momentum=[]
for v in (-35,0,35):
    res,_=NEW.replay(section(NEW,'LAST WORD'),dash_release_vy=v)
    assert not res['errors'],res
    momentum.append(dict(release_vertical_velocity=v,errors=res['errors']))

sync=[]
for R,label in [(OLD,'previous'),(NEW,'new')]:
    rooms=[]
    for s in R.P['sections']:
        es=[e for e in R.P['controls'] if s['t0']<=e['time']<s['t1']]
        errors=np.array([min(abs(AT-e['time'])) for e in es])
        rooms.append(dict(section=s['name'],inputs=len(es),within_25ms=int(sum(errors<=.025)),median_ms=float(np.median(errors)*1000),p90_ms=float(np.quantile(errors,.9)*1000)))
    sync.append(dict(version=label,inputs=sum(s['inputs'] for s in rooms),within_25ms=sum(s['within_25ms'] for s in rooms),rooms=rooms))
assert sync[1]['within_25ms']/sync[1]['inputs']>.8

# Scores and structures differ between rooms of the same mode. The music's
# recurring beat is intentionally retained; this does not assert that every
# local motif or interval is absent elsewhere in the level.
uniqueness=[]
for mode in ('wave','ship','ufo','spider'):
    ss=[s for s in NEW.P['sections'] if s['mode']==mode]
    signatures=[]
    for s in ss:
        es=[e for e in NEW.P['controls'] if s['t0']<=e['time']<s['t1']]
        signatures.append([(round((e['time']-s['t0'])*240),e['kind'],e.get('orb_id')) for e in es])
    assert signatures[0]!=signatures[1]
    uniqueness.append(dict(mode=mode,rooms=[s['name'] for s in ss],different_relative_input_scores=True))
report=dict(file_sha256=hashlib.sha256((ROOT/'outputs/v8-1573528-sync.gmd').read_bytes()).hexdigest(),audio_sync=sync,final_cube_timing=balance,spider_orb_timings=spider,momentum_checks=momentum,room_comparisons=uniqueness,
    limitations='Measured onset proximity and independent approximate physics. These are sampled timing sensitivities, not native frame windows, full native completion, or a demon-rating certification.')
(ROOT/'work/sync-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(sync=[dict(version=q['version'],percent=round(100*q['within_25ms']/q['inputs'],1)) for q in sync],new_spider_orbs=len(controls(NEW,'BLIND ELEVATOR','orb'))+len(controls(NEW,'RECALL','orb')),timing_passes=[q['passes'] for q in balance]),indent=2))
