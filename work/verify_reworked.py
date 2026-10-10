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

f0,h0,o0,s0=read(ORIGINAL);f,h,o,s=read(FINAL)
is_deco=lambda d:d.get('121')=='1' and d.get('134')=='1'
full=Counter(c for c,d in o)
base0=Counter(c for c,d in o0)
missing=base0-full;new=full-base0
visual={'899','1006','901','1346','580'}
cube_ids={'1','8','39','36','141'}
def cube_scope(d):
    x=float(d['2']);return x<5680 or 7570<x<8830
for c,d in o0:
    if not missing[c]:continue
    assert is_deco(d) or d['1'] in visual or (cube_scope(d) and d['1'] in cube_ids),('unapproved source removal',d)
# Every wave wall and every mode/speed/camera object is identical, including
# transition geometry. This is independent of source object order or counts.
protected=[(c,d) for c,d in o0 if not is_deco(d) and
           (d['1'] in {'1910','660','12','200','201','203','3600'} or
            (d['1'] in cube_ids and not cube_scope(d)))]
assert not Counter(c for c,d in protected)-full
added=[d for c,d in o if new[c]]
deco=[d for d in added if is_deco(d)]
gameplay=[d for d in added if not is_deco(d) and d['1'] in cube_ids]
triggers=[d for d in added if not is_deco(d) and d['1'] not in cube_ids]
assert all(cube_scope(d) for d in gameplay)
assert all(d['1'] in {'899','1006','1346'} for d in triggers)
assert all(d['1'] in {'211','1764','1888','3625','580'} for d in deco)
assert all(float(d.get('128',1))>0 and float(d.get('129',1))>0 for d in deco)

def header(s):
    t=s.split(',');assert len(t)%2==0;return dict(zip(t[::2],t[1::2]))
H0,H=header(h0),header(h)
assert {k:v for k,v in H0.items() if k!='kS38'}=={k:v for k,v in H.items() if k!='kS38'}
channels={}
for entry in H['kS38'].split('|'):
    if not entry:continue
    t=entry.split('_');assert len(t)%2==0;d=dict(zip(t[::2],t[1::2]))
    assert d['6'] not in channels;channels[d['6']]=d
assert all(d['21'] in channels and d['22'] in channels for d in deco)
front=[d for d in deco if int(d['24'])>=1]
assert all(channels[d['21']]['5']=='1' for d in front)
frontch={d['21'] for d in front}
assert all(d.get('17')=='1' for c,d in o if d['1']=='899' and d.get('23') in frontch)
groups=defaultdict(list)
for c,d in o:
    for g in d.get('57','').split('.'):
        if g:groups[g].append(d)
for d in triggers:
    if d['1']!='1346':continue
    assert d['51'] in groups and len(groups[d['71']])==1
    assert all(is_deco(a) for g in [d['51'],d['71']] for a in groups[g])
    assert any(a.get('103')!='1' for a in groups[d['51']])
assert f['k2']=='v8' and f['k45']==f0['k45']==593661
assert f['k48']==len(o) and not f.get('k14',False)
assert s==(ROOT/'work/v8.level').read_text()
assert hashlib.sha256(ORIGINAL.read_bytes()).digest()==hashlib.sha256((ROOT/'work/handoff/OBSIDIAN-CHOIR.gmd').read_bytes()).digest()
clearance=json.loads((ROOT/'work/cube-clearance.json').read_text())
assert all(a['ok'] for a in clearance['nominal'])
assert all(all(b['valid_offsets'] for b in a['variants']) for a in clearance['sensitivity'])
plan=json.loads((ROOT/'work/cube-plan.json').read_text())
report={
 'file':'v8.gmd','level_name':f['k2'],'song_id':f['k45'],'file_bytes':FINAL.stat().st_size,
 'total_objects':len(o),'protected_wave_and_transition_objects':len(protected),
 'changed_protected_objects':0,'new_cube_gameplay_objects':len(gameplay),
 'cube_phrases':len(plan['phrases']),'planned_cube_inputs':len(plan['inputs']),
 'new_decoration_objects':len(deco),'new_visual_triggers':len(triggers),
 'unsafe_decoration_ids':0,'missing_no_touch_or_passable':0,
 'opaque_new_decoration_on_positive_layers':0,'gameplay_in_motion_groups':0,
 'undefined_decoration_channels':0,'nonvisual_header_settings_unchanged':True,
 'source_file_unchanged':True,'ldm_objects':sum(d.get('103')!='1' for c,d in o),
 'standard_plist_gzip_roundtrip':'PASS','cube_approximate_clearance_model':'PASS',
 'cube_model_limits':'Ballistic estimates at 240 Hz; not a native engine test. Timing and parameter sensitivity checked.',
 'native_import_and_playtest':'NOT VERIFIED','rating_or_feature_guaranteed':False,
 'final_sha256':hashlib.sha256(FINAL.read_bytes()).hexdigest(),
}
(ROOT/'outputs/v8-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
