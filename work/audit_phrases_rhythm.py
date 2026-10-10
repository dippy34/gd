"""Compare actual input scores, and perturb selected inputs in the replay.

These are model sensitivity results, not measured native timing windows.
"""
from pathlib import Path
from collections import Counter
import hashlib,json,statistics
import replay_phrases as R
ROOT=Path(__file__).resolve().parent.parent
P=R.P;OLD=json.loads((ROOT/'work/restored-plan.json').read_text())
audio=json.loads((ROOT/'work/music-1573528-analysis.json').read_text())
onsets=[x['time'] for x in audio['onsets']]
out=[];probes=[]
def events(plan,s):
    return [e for e in plan['controls'] if s['t0']<=e['time']<s['t1'] and e['kind']!='memory']
for s in P['sections']:
    old=next(q for q in OLD['sections'] if q['name']==s['name'])
    current=events(P,s);before=events(OLD,old)
    gaps=[b['time']-a['time'] for a,b in zip(current,current[1:])]
    kinds=Counter(e['kind'] for e in current)
    out.append(dict(section=s['name'],start=s['t0'],end=s['t1'],mode=s['mode'],
        previous_inputs=len(before),current_inputs=len(current),unchanged_input_score=current==before,
        input_types=dict(kinds),minimum_gap=min(gaps),maximum_gap=max(gaps),
        median_onset_distance=statistics.median(min(abs(e['time']-t) for t in onsets) for e in current),
        robot_holds=[e['hold'] for e in current if e['kind']=='hold'],
        dash_holds=[w['end']-w['start'] for w in s.get('dash_windows',[])],
        intervals=[round(g,6) for g in gaps]))
    if current==before:continue
    choices=([e for e in current if e['kind']=='release'] if s['name']=='LAST WORD' else
             [e for e in current if e['kind'] in ('turn','thrust','flip','hold','hop') and e['time']>s['t0']+1])
    if len(choices)>3:choices=[choices[0],choices[len(choices)//2],choices[-2]]
    for e in choices:
        checks=[]
        for shift in (-.05,-.033333,-.016667,0,.016667,.033333,.05):
            res,_=R.replay(s,perturb_time=e['time'],input_shift=shift,stop_at=min(e['time']+1.1,s['t1']-1),stop_first=True)
            checks.append(dict(shift_seconds=shift,passes_model=not bool(res['errors'])))
        assert next(c for c in checks if c['shift_seconds']==0)['passes_model'],(s['name'],e)
        probes.append(dict(section=s['name'],input_time=e['time'],kind=e['kind'],checks=checks))

# The original opening and first spider are deliberately preserved. Every
# later matching mode has a different score and a different structural rule.
preserved={r['section'] for r in out if r['unchanged_input_score']}
assert {'CIPHER','CUTWIRE','SWITCHYARD','BLINDFOLD','OFFBEAT','BLIND ELEVATOR','CROSSCODE'}==preserved
assert all(not r['unchanged_input_score'] for r in out if r['start']>=106.26)
for a,b in [('CIPHER','LAST WORD'),('CUTWIRE','NEEDLEWORK'),('SWITCHYARD','FALSE FLOOR'),('BLINDFOLD','FAULTLINE'),('OFFBEAT','COUNTERFEIT'),('PARALLAX','UNDERTOW'),('BLIND ELEVATOR','RECALL')]:
    aa=next(r for r in out if r['section']==a);bb=next(r for r in out if r['section']==b)
    assert aa['intervals']!=bb['intervals']
report=dict(sections=out,sensitivity_probes=probes,
    changed_sections=[r['section'] for r in out if not r['unchanged_input_score']],
    preserved_sections=sorted(preserved),
    note='No identical first/second counterpart scores. Shared game modes and familiar mechanics remain intentional. Model sensitivity cannot certify native difficulty or beatability.')
(ROOT/'work/phrases-rhythm-checks.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(changed=report['changed_sections'],preserved=report['preserved_sections'],probes=len(probes),probes_rejecting_any_offset=sum(any(not c['passes_model'] for c in p['checks']) for p in probes)),indent=2))
