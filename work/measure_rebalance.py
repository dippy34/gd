"""Same-score sensitivity comparisons for the ship and robot balance pass.

Uses actual serialized geometry in separate replays. Results describe these
models only; they cannot certify native difficulty or completion.
"""
from pathlib import Path
import json, statistics
import replay_phrases as OLD
import replay_rebalance as NEW
ROOT=Path(__file__).resolve().parent.parent
def sec(R,name):return next(s for s in R.P['sections'] if s['name']==name)
def events(R,name,kind):
    s=sec(R,name)
    return [e for e in R.P['controls'] if s['t0']+.4<e['time']<s['t1']-1.2 and e['kind']==kind]
def probe(R,name,e,release=False):
    out=[]
    for ticks in range(-12,13):
        shift=ticks/240
        kw=dict(release_shift=shift) if release else dict(input_shift=shift)
        res,_=R.replay(sec(R,name),perturb_time=e['time'],stop_at=e['time']+1.05,stop_first=True,**kw)
        out.append(dict(shift=shift,passes=not bool(res['errors'])))
    assert out[12]['passes'],(name,e)
    return out
comparisons=[]
for name,kind,release in [('UNDERTOW','thrust',False),('NEEDLEWORK','hold',False),('NEEDLEWORK','hold',True)]:
    es=events(NEW,name,kind);selected=[es[1],es[len(es)//2],es[-2]]
    for e in selected:
        previous=next(q for q in events(OLD,name,kind) if abs(q['time']-e['time'])<1e-7)
        a=probe(OLD,name,previous,release);b=probe(NEW,name,e,release)
        comparisons.append(dict(section=name,time=e['time'],probe='hold duration' if release else 'input time',
                                old_passes=sum(q['passes'] for q in a),new_passes=sum(q['passes'] for q in b),old=a,new=b))
summary={}
for name,probe_name in [('UNDERTOW','input time'),('NEEDLEWORK','input time'),('NEEDLEWORK','hold duration')]:
    q=[p for p in comparisons if p['section']==name and p['probe']==probe_name]
    before=sum(p['old_passes'] for p in q);after=sum(p['new_passes'] for p in q)
    if name=='UNDERTOW':assert after>before,(name,before,after)
    else:assert after<before,(name,probe_name,before,after)
    summary[name+' '+probe_name]=dict(previous_passed=before,rebalanced_passed=after,total=75)

finale=[]
for e in [e for e in NEW.P['controls'] if e['kind']=='release']:
    vals=probe(NEW,'LAST WORD',e)
    passing=[q['shift'] for q in vals if q['passes']]
    assert len(passing)<25,'release remains unconstrained'
    finale.append(dict(time=e['time'],tested_pass_range=[min(passing),max(passing)],tests=vals))
momentum=[]
for dv in (-50,0,50):
    result,_=NEW.replay(sec(NEW,'LAST WORD'),dash_release_vy=dv)
    assert not result['errors'],result
    momentum.append(dict(vertical_velocity_after_release=dv,errors=result['errors']))

older=json.loads((ROOT/'work/restored-plan.json').read_text())
selection=[]
def controls(P,s):return [e for e in P['controls'] if s['t0']<=e['time']<s['t1'] and e['kind']!='memory']
for s in NEW.P['sections']:
    current=controls(NEW.P,s);early=controls(older,s);recent=controls(OLD.P,s)
    if s['index']<8 and s['name']!='BLINDFOLD':assert current==early
    if 8<=s['index']<14:assert current==recent and current!=early
    if s['name'] in ('BLINDFOLD','LAST WORD'):assert current!=early and current!=recent
    selection.append(dict(section=s['name'],old_first_half_score=current==early,new_second_half_score=current==recent,inputs=len(current)))
report=dict(balance=summary,comparisons=comparisons,dash_releases=finale,release_momentum_checks=momentum,source_selection=selection,
    limitations='Approximate sensitivity, not native frame windows. No native damage-enabled completion or exact difficulty verification.')
(ROOT/'work/rebalance-measurements.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(balance=summary,dash_release_pass_ranges=[d['tested_pass_range'] for d in finale],momentum_checks=momentum),indent=2))
