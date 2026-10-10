"""Independent standard-library read, strict layout audit, decoration safety."""
from pathlib import Path
import xml.etree.ElementTree as ET
import plistlib,base64,gzip,json,math,hashlib
from collections import Counter,defaultdict
ROOT=Path(__file__).resolve().parent.parent
ORIGINAL=Path(str(next(p for p in Path(__file__).resolve().parents if (p/'inputs/OBSIDIAN-CHOIR.gmd').exists())/'inputs/OBSIDIAN-CHOIR.gmd'))
FINAL=ROOT/'outputs/v8.gmd'

def read(path):
    root=ET.parse(path).getroot()
    # Convert GD's compact plist tags to Apple's standard plist dialect, then
    # parse through plistlib independently of the supplied handoff reader.
    tags={'k':'key','s':'string','i':'integer','r':'real','t':'true','f':'false'}
    for el in root.iter():el.tag=tags.get(el.tag,el.tag)
    fields=plistlib.loads(ET.tostring(root,encoding='utf-8'))
    s=fields['k4'];decoded=gzip.decompress(base64.urlsafe_b64decode(s+'===')).decode()
    chunks=decoded.split(';');head=chunks[0];objects=[]
    for c in chunks[1:]:
        if not c:continue
        ts=c.split(',');assert len(ts)%2==0,('odd object field list',ts)
        d=dict(zip(ts[::2],ts[1::2]));assert len(d)==len(ts)//2,('duplicate object keys',d)
        assert all(k in d for k in ['1','2','3'])
        for k in ['1','2','3','128','129','32','6']:
            if k in d:assert math.isfinite(float(d[k])),('nonfinite property',k)
        objects.append((c,d))
    return fields,head,objects,decoded

f0,h0,o0,s0=read(ORIGINAL);f,h,raw,s=read(FINAL)
objs=[d for c,d in raw]
plan=json.loads((ROOT/'work/balanced-plan.json').read_text())
metrics=json.loads((ROOT/'work/build-metrics.json').read_text())
def header(h):
    t=h.split(',');return dict(zip(t[::2],t[1::2]))
H,H0=header(h),header(h0)
assert f['k2']=='v8' and f['k45']==f0['k45']==593661
assert f['k48']==len(objs) and not f.get('k14',False)
assert H['kA2']=='4' and H['kA4']=='0'
assert H.get('kA13')==H0.get('kA13')
assert all(H.get(k,'0')=='0' for k in ['kA3','kA8','kA10','kA11','kA22'])
assert s==(ROOT/'work/v8.level').read_text()
assert ORIGINAL.read_bytes()==(ROOT/'work/handoff/OBSIDIAN-CHOIR.gmd').read_bytes()
deco=lambda d:d.get('121')=='1' and d.get('134')=='1'
dec=[d for d in objs if deco(d)]
assert all(d['1'] in {'211','1764','3621','3625','1888','580'} for d in dec)
assert all(d.get('121')=='1' and d.get('134')=='1' for d in objs if d['1'] in {'211','1764','3621','3625','1888','580'})
channels={}
for item in H['kS38'].split('|'):
    if not item:continue
    t=item.split('_');assert len(t)%2==0
    d=dict(zip(t[::2],t[1::2]));assert d['6'] not in channels;channels[d['6']]=d
assert all(d.get('21','1') in channels for d in objs if deco(d))
assert all(channels[d['21']]['5']=='1' for d in dec if int(d.get('24',0))>=1)
groups=defaultdict(list)
for o in objs:
    for g in o.get('57','').split('.'):
        if g:groups[g].append(o)
moves=[o for o in objs if o['1']=='901']
assert len(moves)==33 and not any(o['1']=='1346' for o in objs)
for tr in moves:
    assert tr['51'] in groups and all(deco(o) for o in groups[tr['51']])
    assert tr['30']=='13' and float(tr['10'])>0
for feature in metrics['features']:
    members=groups[str(feature['group'])]
    assert len(members)==feature['objects']
    assert sum(o['1']=='3621' and o['21']=='60' for o in members)==1
    assert any(o['1']=='3621' and o.get('103')!='1' and o['21']=='60' for o in members)
assert len(groups['900'])==1 and deco(groups['900'][0])
assert any(o['1']=='2925' and o.get('111')=='1' for o in objs)
assert any(o['1']=='1914' and o.get('71')=='900' and o.get('101')=='2' for o in objs)
assert not any(o['1'] in {'200','201','202','203','1334'} for o in objs)
assert len([o for o in objs if o['1']=='3600'])==1
expected_modes=['wave','ball','spider','wave','ship','ball']
assert [s['mode'] for s in plan['sections']]==expected_modes

# Independent collision data comes from the exported file, not the author's
# wall arrays. Spatial bins allow continuous 240 Hz finite-body evaluation.
bins=defaultdict(list);hazards=[]
for o in objs:
    x,y=float(o['2']),float(o['3'])
    if o['1']=='1':
        w=30*float(o.get('128',o.get('32',1)));ht=30*float(o.get('129',o.get('32',1)))
        box=(x-w/2,x+w/2,y-ht/2,y+ht/2)
        for b in range(math.floor(box[0]/120),math.floor(box[1]/120)+1):bins[b].append(box)
    if o['1']=='8':
        up=float(o.get('6',0))%360==0
        tri=[(x-15,y-15),(x+15,y-15),(x,y+15)] if up else [(x-15,y+15),(x+15,y+15),(x,y-15)]
        hazards.append(tri)

def triangle_box(tri,x,y,r=15):
    box=[(x-r,y-r),(x+r,y-r),(x+r,y+r),(x-r,y+r)]
    axes=[(1,0),(0,1)]
    for a,b in zip(tri,tri[1:]+tri[:1]):axes.append((a[1]-b[1],b[0]-a[0]))
    for ax,ay in axes:
        aa=[xx*ax+yy*ay for xx,yy in tri];bb=[xx*ax+yy*ay for xx,yy in box]
        if max(aa)<=min(bb) or max(bb)<=min(aa):return False
    return True

def gap_clearance(x,y,r):
    margin=10000
    boxes=[]
    for b in range(math.floor((x-r)/120),math.floor((x+r)/120)+1):boxes.extend(bins[b])
    for a,b,lo,hi in boxes:
        if a>=x+r or b<=x-r:continue
        if hi<=y:margin=min(margin,y-r-hi)
        elif lo>=y:margin=min(margin,lo-y-r)
        else:return -1
    return margin

speed=plan['speed_schedule'][0][1];dt=1/240
wave_results=[]
for sec in [s for s in plan['sections'] if s['mode']=='wave']:
    turns=[e for e in plan['controls'] if e['mode']=='wave' and sec['x0']<e['x']<sec['x1']]
    variants=[('nominal',{})]+[(f'turn-{i}-{off}',{i:off}) for i in range(len(turns)) for off in [-.040,.040]]
    margins=[]
    for name,offsets in variants:
        events=[(e['time']+offsets.get(i,0),e['down']) for i,e in enumerate(turns)]
        y=15 if sec['t0']==0 else 45;down=True;t=sec['t0'];ei=0;minimum=1e9
        while t<sec['t1']-1e-8:
            to=min(t+dt,sec['t1'],events[ei][0] if ei<len(events) else 1e9)
            y+=(to-t)*speed*(1 if down else -1);t=to
            c=gap_clearance(t*speed,y,12)
            minimum=min(minimum,c)
            if c < -.01:raise AssertionError(('wave collision',sec['t0'],name,t,y,c))
            if ei<len(events) and abs(t-events[ei][0])<1e-7:down=events[ei][1];ei+=1
        margins.append(minimum)
        if name=='nominal':nominal_exit=y
    wave_results.append({'start':sec['t0'],'gap':sec['gap'],'variants':len(variants),
        'min_clearance_units':round(min(margins),3),'single_turn_perturbation_ms':40,
        'turn_interval_seconds':[round(v*plan['beat'],4) for v in sec['turn_intervals_beats']],
        'nominal_exit_y':round(nominal_exit,4)})

flip_results=[]
for si,sec in enumerate(plan['sections']):
    if sec['mode'] not in ['ball','spider']:continue
    previous=plan['sections'][si-1]
    start_y=previous.get('points',[[0,45]])[-1][1]
    taps=sec['flips'];resets=[float(o['2'])/speed for o in objs if o['1']=='10' and sec['x0']<float(o['2'])<sec['x1']]
    for gravity in [1600,2200,2800,3200]:
        for offset in [-.035,0,.035]:
            events=sorted([(e['time']+offset,'tap') for e in taps]+[(t,'reset') for t in resets])
            t=sec['t0'];y=start_y;v=0;grav=-1;ei=0;landed=0
            localtri=[h for h in hazards if sec['x0']<h[2][0]<sec['x1']]
            while t<sec['t1']-1e-8:
                to=min(t+dt,sec['t1'],events[ei][0] if ei<len(events) else 1e9)
                step=to-t;y+=v*step+.5*grav*gravity*step**2;v+=grav*gravity*step;t=to
                if y<=45:y=45;v=0;landed=-1
                elif y>=225:y=225;v=0;landed=1
                else:landed=0
                if any(abs(h[2][0]-t*speed)<31 and triangle_box(h,t*speed,y) for h in localtri):
                    raise AssertionError(('flip hazard',sec['mode'],sec['t0'],gravity,offset,t,y))
                if ei<len(events) and abs(t-events[ei][0])<1e-7:
                    if events[ei][1]=='reset':grav=-1
                    else:
                        assert landed,('airborne tap',sec['mode'],gravity,offset,t,y)
                        grav*=-1;v=0
                        if sec['mode']=='spider':y=225 if grav==1 else 45
                    ei+=1
            flip_results.append({'start':sec['t0'],'mode':sec['mode'],'gravity':gravity,
                'input_offset_ms':round(offset*1000),'taps':len(taps),'exit_y':round(y,2)})

# Ship viability uses a bounded, responsive controller under several gravity
# estimates. It demonstrates clearance; it is not an exact engine macro.
ship=next(s for s in plan['sections'] if s['mode']=='ship')
ship_results=[]
for acceleration in [800,1100,1400,1700]:
    t=ship['t0'];y=ship['points'][0][1];v=0;minimum=1e9;control=[];down=None;lastswitch=-100
    while t<ship['t1']:
        u=min(1,max(0,(t-ship['t0'])/(ship['t1']-ship['t0'])))
        target=155+40*math.sin(u*math.tau*1.5)
        desired=target-y-v*.18
        choice=desired>0
        if down is None or (choice!=down and t-lastswitch>=.24 and abs(desired)>6):
            down=choice;lastswitch=t;control.append({'time':round(t,5),'down':down})
        step=min(dt,ship['t1']-t);a=acceleration*(1 if down else -1)
        y+=v*step+.5*a*step**2;v=max(-300,min(300,v+a*step));t+=step
        c=gap_clearance(t*speed,y,15);minimum=min(minimum,c)
        assert c>=-.01,('ship collision',acceleration,t,y,c)
    ship_results.append({'acceleration':acceleration,'min_clearance_units':round(minimum,3),
        'inputs':control,'exit_y':round(y,3)})

report={'file':'v8.gmd','level_name':f['k2'],'song_id':f['k45'],
 'file_bytes':FINAL.stat().st_size,'total_objects':len(objs),
 'low_detail_objects':sum(o.get('103')!='1' for o in objs),
 'mode_order':expected_modes,'speed_units_per_second':speed,'drop_time':plan['drop_time'],
 'moving_black_holes':len(metrics['features']),'move_triggers':len(moves),
 'standard_plist_gzip_roundtrip':'PASS','source_file_unchanged':True,
 'decoration_flags_and_ids':'PASS','gameplay_objects_in_motion_groups':0,
 'opaque_decorations_on_positive_layers':0,'undefined_color_channels':0,
 'wave_clearance':wave_results,'flip_clearance_variants':flip_results,
 'ship_clearance_variants':ship_results,
 'physics_model_limits':'240 Hz approximations, finite bodies and full spike triangles. Not the native engine; no completion or exact difficulty claim.',
 'native_import_and_playtest':'NOT VERIFIED','rating_or_feature_guaranteed':False,
 'final_sha256':hashlib.sha256(FINAL.read_bytes()).hexdigest()}
(ROOT/'outputs/v8-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['flip_clearance_variants','ship_clearance_variants']},indent=2))
