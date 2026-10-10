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
preserved=[(c,d) for c,d in o0 if not is_deco(d)]
old=Counter(c for c,d in preserved)
full=Counter(c for c,d in o)
missing=old-full
new=full-old
assert not missing,('changed/missing source objects',sum(missing.values()))
# Preserve both the bytes and original order of all retained source objects.
assert [c for c,d in o[:len(preserved)]]==[c for c,d in preserved]
added=[d for c,d in o[len(preserved):]]
deco=[d for d in added if is_deco(d)]
triggers=[d for d in added if not is_deco(d)]
assert all(d['1'] in {'899','1006','1346'} and d['20']=='5' for d in triggers)
assert all(d['1'] in {'211','1764','1888','3625'} for d in deco)
assert all(float(d.get('128',1))>0 and float(d.get('129',1))>0 for d in deco)
HAZ={'8','9','39','103','152','153','154','155','177','216','217','218','458','1705','1706','1709','920','1582','679','1735','1736','3042','3047','1715'}
INTERACTIVE={'10','11','12','13','45','46','47','99','101','111','286','287','660','745','1331','200','201','202','203','1334','35','36','67','84','140','141','1332','1333','3600','31','1917','2063'}
assert not any(d['1'] in HAZ|INTERACTIVE for d in deco)

def header(s):
    t=s.split(',');assert len(t)%2==0;return dict(zip(t[::2],t[1::2]))
H0,H=header(h0),header(h)
assert {k:v for k,v in H0.items() if k!='kS38'}=={k:v for k,v in H.items() if k!='kS38'}
channels={}
for entry in H['kS38'].split('|'):
    if not entry:continue
    t=entry.split('_');assert len(t)%2==0
    d=dict(zip(t[::2],t[1::2]));ch=d['6'];assert ch not in channels
    channels[ch]=d
assert all(d['21'] in channels and d['22'] in channels for d in deco)
front=[d for d in deco if int(d['24'])>=1]
assert all(channels[d['21']].get('5')=='1' for d in front)
frontch={d['21'] for d in front}
assert all(d.get('17')=='1' for c,d in o if d['1']=='899' and d.get('23') in frontch)
gbase=set(g for c,d in preserved for g in d.get('57','').split('.') if g)
groups=defaultdict(list)
for d in deco:
    for g in d.get('57','').split('.'):
        if g:groups[g].append(d)
targets=set()
for d in triggers:
    if d['1']=='1346':
        assert d['51'] in groups and len(groups[d['71']])==1
        assert any(x.get('103')!='1' for x in groups[d['51']]),'LDM removes entire motion target'
        targets.update([d['51'],d['71']])
assert not targets&gbase
assert f['k2']=='v8' and f['k45']==f0['k45']==593661
assert f['k48']==len(o)
assert not f.get('k14',False),'draft is marked verified'
assert s==(ROOT/'work/v8.level').read_text()
copyhash=hashlib.sha256((ROOT/'work/handoff/OBSIDIAN-CHOIR.gmd').read_bytes()).hexdigest()
sourcehash=hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
assert copyhash==sourcehash,'original source changed'
report={
 'file':'v8.gmd','level_name':f['k2'],'song_id':f['k45'],
 'file_bytes':FINAL.stat().st_size,'total_objects':len(o),
 'source_layout_objects':len(preserved),'missing':0,'changed_or_added_gameplay':0,
 'byte_identical_source_objects':len(preserved),
 'replaced_old_decoration_objects':len(o0)-len(preserved),
 'new_decoration_objects':len(deco),'new_visual_triggers':len(triggers),
 'unsafe_decoration_ids':0,'missing_no_touch_or_passable':0,
 'opaque_new_objects_on_positive_layers':0,'gameplay_in_new_motion_groups':0,
 'undefined_decoration_color_channels':0,'invalid_rotation_centers':0,
 'nonvisual_header_settings_unchanged':True,'source_file_unchanged':True,
 'ldm_objects':sum(d.get('103')!='1' for c,d in o),
 'standard_plist_gzip_roundtrip':'PASS','native_import_and_playtest':'NOT VERIFIED',
 'source_sha256':sourcehash,'final_sha256':hashlib.sha256(FINAL.read_bytes()).hexdigest(),
}
(ROOT/'outputs/v8-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
