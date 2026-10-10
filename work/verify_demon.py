"""Export-based audits, analytic wave checks and approximate flight integration."""
import json,math,hashlib,bisect,csv
from pathlib import Path
from collections import Counter
import check_demon_paths as C
R=C.ROOT;p=C.plan
f,h,raw,level=C.read(R/'outputs/v8-demon-layout.gmd');objs=[o for _,o in raw]
a=h.split(',');H=dict(zip(a[::2],a[1::2]));ids=Counter(o['1'] for o in objs)
assert f['k2']=='v8' and int(f['k45'])==1573528 and not f['k14']
assert H['kA4']=='1' and H['kA2']=='0' and H['kA32']=='1'
assert not ids['1933'] and not ids['1935'] and not ids['3621']
assert len(objs)==int(f['k48']) and level==(R/'work/v8-demon-layout.level').read_text()
assert set(s['mode'] for s in p['sections'])=={'cube','robot','ball','spider','wave','ufo','ship'}
assert len(p['sections'])==25 and p['slow_time']/p['end_time']>.85
assert p['end_time']<json.loads((R/'work/music-1573528-analysis.json').read_text())['duration']
assert not any(c['errors'] for c in C.checks)
# Native speed portals, independently integrated from their serialized X.
ports=sorted([(float(o['2']),{'200':251.16,'201':311.58}[o['1']]) for o in objs if o['1'] in ['200','201']])
assert not ids['202'] and not ids['203'] and not ids['1334']
x=0;t=0;v=251.16;speed_audit=[]
for px,nv in ports:
 t+=(px-x)/v;x=px;v=nv
 assert abs(t/ p['beat']-round(t/p['beat']))<.01
 speed_audit.append(dict(x=px,time=t,units_per_second=v))
endx=float(next(o['2'] for o in objs if o['1']=='3600'))
assert abs(t+(endx-x)/v-p['end_time'])<.001
# Structure and relative input sequences must differ at each same-mode section.
signatures=[]
for s in p['sections']:
 ev=[e for e in p['controls'] if s['t0']<=e['time']<s['t1']]
 sig=(s['mode'],tuple((round(e['time']-s['t0'],3),e['kind'],e.get('orb_id'),e.get('down')) for e in ev))
 assert sig not in signatures;signatures.append(sig)
for a,b in zip(p['sections'],C.checks):
 if a['index']+1<len(C.checks):assert abs(b['exit_y']-p['sections'][a['index']+1]['incoming_y'])<.01
wave=[];flight=[]
for sec in p['sections']:
 mode=sec['mode']
 if mode not in ['wave','ship','ufo']:continue
 ev=[e for e in p['controls'] if e['mode']==mode and sec['t0']-1e-6<=e['time']<sec['t1']]
 variants=[(None,0)]
 if mode=='wave':variants += [(i,off) for i in range(1,len(ev)) for off in [-.008,.008]]
 minimum=999;bad=[]
 for index,offset in variants:
  events=[dict(e,time=e['time']+(offset if i==index else 0),type='input') for i,e in enumerate(ev)]
  events.extend(dict(e,type='gravity') for e in p['gravity_events'] if e['source']=='portal' and e['section']==sec['name'])
  events.sort(key=lambda e:e['time']);ei=0;t=sec['t0'];y=max(20,min(280,sec['incoming_y']));vy=0;grav=-1;down=False
  while t<sec['t1']-1e-7:
   if ei<len(events) and events[ei]['time']<=t+1e-6:
    e=events[ei];ei+=1
    if e['type']=='gravity':grav=e['gravity']
    elif mode=='ufo':vy=-grav*420
    else:down=e['down']
    continue
   to=min(t+1/240,sec['t1'],events[ei]['time'] if ei<len(events) else math.inf);dt=to-t
   if mode=='wave':y+=dt*sec['speed']*(1 if down else -1)*(-grav)
   else:
    acc=grav*1244.16 if mode=='ufo' else -grav*(1000 if down else -1000)
    y+=vy*dt+.5*acc*dt*dt;vy+=acc*dt
    if mode=='ship':vy=max(-300,min(300,vy))
    else:
     if y<15:y=15;vy=0
     if y>315:y=315;vy=0
   t=to;x=C.xat(sec,t);r=12 if mode=='wave' else 15
   if C.solids(x,y,r) or C.hazard(x,y,r):
    bad.append(dict(index=index,offset=offset,t=t,y=y));break
   minimum=min(minimum,C.clearance(x,y,r))
  if index is None and not bad:assert abs(y-sec['flight_points'][-1][1])<5,(sec['name'],y,sec['flight_points'][-1][1])
 result=dict(section=sec['name'],mode=mode,variants=len(variants),minimum_vertical_clearance=round(minimum,3),failures=bad)
 (wave if mode=='wave' else flight).append(result)
assert not any(v['failures'] for v in wave+flight),[v for v in wave+flight if v['failures']]
reports=[]
for suffix in ['','--0.008-1.0','-0.008-1.0','-0.0-1.03','-0.0-0.97']:
 path=R/f'work/demon-path-checks{suffix}.json'
 if path.exists():
  checks=json.loads(path.read_text());assert len(checks)==25 and not any(c['errors'] for c in checks);reports.append(path.name)
report=dict(file='v8-1573528-layout.gmd',internal_name=f['k2'],song_id=int(f['k45']),seconds=p['end_time'],bpm=131,
 objects=len(objs),sections=25,modes=sorted(set(s['mode'] for s in p['sections'])),slow_percent=100*p['slow_time']/p['end_time'],
 speed_portals=speed_audit,timewarp_objects=0,precision_gates=len(p['precision_gates']),black_holes=0,
 unique_section_input_sequences=True,ground_reports=reports,wave_checks=wave,approximate_flight_checks=flight,
 native_import_verified=False,native_full_playthrough=False,difficulty='Hard Insane Demon to entry Extreme target; not calibrated by human play',
 limitations='Ground, ship and UFO physics remain approximations. Position-trigger activation and mode-transition momentum need native playtesting. Export checks do not prove in-game completion.',
 sha256=hashlib.sha256((R/'outputs/v8-demon-layout.gmd').read_bytes()).hexdigest())
(R/'outputs/v8-1573528-validation.json').write_text(json.dumps(report,indent=2))
with (R/'outputs/v8-1573528-inputs.csv').open('w') as out:
 writer=csv.writer(out);writer.writerow(['time_seconds','tick_240','mode','action','hold_seconds','button_down','orb_id'])
 for e in p['controls']:writer.writerow([e['time'],round(e['time']*240),e['mode'],e['kind'],e.get('hold',''),e.get('down',''),e.get('orb_id','')])
print(json.dumps(report,indent=2))
