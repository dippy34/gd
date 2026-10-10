"""Compare one input at a time in the old and new approximate replay models.

These are model sensitivity intervals, NOT native click windows or ratings.
All other inputs stay fixed. We stop 0.70 s after the perturbed input.
"""
from pathlib import Path
from collections import defaultdict
import json, math, statistics

ROOT=Path(__file__).resolve().parent.parent
backup=ROOT/'work/revision-before-timing-hardening'
setup=(ROOT/'work/check_memory.py').read_text().split('events=[]')[0]
source=(ROOT/'work/replay_memory.py').read_text().split("if __name__=='__main__':")[0]
source=source.replace("exec((__import__('pathlib').Path(__file__).parent/'check_memory.py').read_text().split('events=[]')[0])", 'exec(SETUP)')
engines={}
for version in ('previous','current'):
    code=setup
    if version=='previous':
        code=code.replace('outputs/v8-1573528-timing.gmd','work/revision-before-timing-hardening/v8-1573528-refined.gmd')
        code=code.replace('work/memory-plan.json','work/revision-before-timing-hardening/memory-plan.json')
    ns={'SETUP':code,'__file__':str(ROOT/'work/replay_memory.py'),'__name__':'window_engine'}
    exec(source,ns)
    engines[version]=ns

P=engines['current']['P']
rows=[]
for s in P['sections']:
    if s['mode'] in ('ship','wave'):continue
    es=[e for e in P['controls'] if s['t0']<e['time']<s['t1']-1.1 and e['kind'] in ('jump','hold','orb','hop','flip')]
    # Deterministic coverage: early, middle and late inputs, plus distinct orb
    # and robot-release tests. No selection by whether a test improves.
    indices=sorted(set([1,len(es)//2,max(0,len(es)-2)]))
    cases=[(es[i],'press') for i in indices]
    if s['mode']=='cube':
        orbs=[e for e in es if e['kind']=='orb']
        if orbs:cases.append((orbs[len(orbs)//2],'press'))
    if s['mode']=='robot':cases.extend((es[i],'release') for i in indices)
    cases=list({(e['time'],kind):(e,kind) for e,kind in cases}.values())
    for event,kind in cases:
        results={}
        for version,ns in engines.items():
            room=next(z for z in ns['P']['sections'] if z['name']==s['name'])
            tested={}
            def passes(ticks):
                if ticks in tested:return tested[ticks]
                delta=ticks/240
                kw={'input_shift':delta} if kind=='press' else {'release_shift':delta}
                res,_=ns['replay'](room,perturb_time=event['time'],stop_at=event['time']+.70,stop_first=True,**kw)
                tested[ticks]=not bool(res['errors'])
                return tested[ticks]
            assert passes(0),(version,s['name'],event)
            # Measure the contiguous successful interval around the reference,
            # capped at ±20 ticks. We do not interpret other disjoint paths.
            ends=[]
            for direction in (-1,1):
                last=0
                for ticks in range(1,21):
                    if not passes(direction*ticks):break
                    last=ticks
                ends.append(last)
            results[version]=dict(early_ticks=ends[0],late_ticks=ends[1],
                tested_success_span_ms=sum(ends)*1000/240,
                sampled_success_count=1+sum(ends),
                capped=20 in ends)
        rows.append(dict(section=s['name'],mode=s['mode'],input_time=event['time'],
                         input_kind=event['kind'],perturbation=kind,results=results))
    recent=[z for z in rows if z['section']==s['name']]
    old=statistics.median(z['results']['previous']['tested_success_span_ms'] for z in recent)
    new=statistics.median(z['results']['current']['tested_success_span_ms'] for z in recent)
    print(f"{s['name']}: {len(recent)} input tests, median model span {old:.2f} → {new:.2f} ms",flush=True)

groups=defaultdict(list)
for z in rows:groups[z['mode']].append(z)
summary={m:dict(tests=len(zs),previous_median_ms=statistics.median(z['results']['previous']['tested_success_span_ms'] for z in zs),
               current_median_ms=statistics.median(z['results']['current']['tested_success_span_ms'] for z in zs),
               tightened=sum(z['results']['current']['sampled_success_count']<z['results']['previous']['sampled_success_count'] for z in zs)) for m,zs in groups.items()}
out=dict(method='Single-input perturbation, 240 Hz approximate replay, 0.70 s horizon, contiguous success interval, ±20 ticks cap.',
         limitations='Model sensitivity only. Native physics, triangle hitboxes, buffering and portal contact offsets are not fully reproduced. These are not verified native click windows.',
         summary=summary,tests=rows)
(ROOT/'work/timing-window-comparison.json').write_text(json.dumps(out,indent=2))
print(json.dumps(summary,indent=2),flush=True)
