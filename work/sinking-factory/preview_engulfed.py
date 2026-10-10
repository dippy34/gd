from pathlib import Path
import os,sys,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
os.environ['GD_PREVIEW_PLAN']=str(HERE/'engulfed-manifest.json');os.environ['GD_PREVIEW_LEVEL']=str(HERE/'engulfed.level')
sys.path.insert(0,str(ROOT/'work'))
import preview_memory as P
R=P.R
R.SHEETS += ['FireSheet_01','GJ_ParticleSheet'];R.load_atlas()
# Native fire fill sprites are stored at half resolution and scaled 2x by
# GameObject::setupCustomSprites; center them using their own source size.
# Also sample different real atlas frames to show the randomized preset loop.
for family in ['01','02','03','04']:
 for frame in range(1,12):
  native=f'Fire_{family}_2_looped_{frame:03d}.png'
  alias=f'Fire_{family}_looped_{frame:03d}_2_001.png'
  if native in R._frames:
   sp=R.sprite(native)
   R._cache[alias]=sp.resize((sp.width*2,sp.height*2),Image.Resampling.BILINEAR)
   R._frames[alias]=R._frames[native]
# The legacy renderer appends _2_001 after replacing only a _001 suffix.
# Give each frame a custom normal-looking alias with a matching detail layer.
for family in ['01','02','03','04']:
 for frame in range(1,12):
  native=f'Fire_{family}_looped_{frame:03d}.png'
  if native not in R._frames:continue
  alias=f'previewFire_{family}_{frame:03d}_001.png'
  R._cache[alias]=R.sprite(native);R._frames[alias]=R._frames[native]
  dn=f'Fire_{family}_2_looped_{frame:03d}.png'
  if dn in R._frames:
   sp=R.sprite(dn);da=alias.replace('_001.png','_2_001.png')
   R._cache[da]=sp.resize((sp.width*2,sp.height*2),Image.Resampling.BILINEAR);R._frames[da]=R._frames[dn]
# Apply the same 2x correction to old fire objects in the preserved factory.
for oid in [920,921,923,924,1936,1937,1938,1939]:
 nm=P.names[oid]
 dn=nm.replace('_looped_','_2_looped_') if '_looped_' in nm else nm.replace('_001.png','_2_001.png')
 da=nm.replace('_001.png','_2_001.png')
 if dn in R._frames:
  sp=R.sprite(dn);R._cache[da]=sp.resize((sp.width*2,sp.height*2),Image.Resampling.BILINEAR);R._frames[da]=R._frames[dn]
# Pit-slope textures are horizontal in the atlas; their native default tilt is
# separate from serialized rotation. These diagnostic tilts follow the source
# slope dimensions and the diagonal teeth visible in native-play-ship.png.
# The .gmd keeps the original native objects and all their physical properties.
for oid,tilt in [(1717,45),(1718,math.degrees(math.atan(.5)))]:
 spr=R.sprite(P.names[oid]);nm=f'__pit_default_{oid}'
 R._cache[nm]=spr.rotate(tilt,expand=True,resample=Image.Resampling.BICUBIC)
 P.names[oid]=nm
for o in P.objs:
 if o["1"]=="899" and "23" not in o:o["23"]="1000"
# Native GD draws these legacy geometric objects procedurally. Diagnostic-only
# masks reproduce their dimensions; they are not objects added to the .gmd.
for oid,w,h,shape in [(94,30,30,'square'),(1338,30,30,'slope'),(1339,60,30,'slope'),(468,30,1.5,'square')]:
 im=Image.new('RGBA',(int(w*4),max(1,int(h*4))),(0,0,0,0));d=ImageDraw.Draw(im)
 if shape=='slope':d.line([(0,h*4-1),(w*4-1,0),(w*4-1,h*4-1),(0,h*4-1)],fill='white',width=3)
 else:d.rectangle((0,0,w*4-1,h*4-1),fill='white')
 im=im.resize((int(w*2),max(1,int(h*2))))
 nm=f'__geo_{oid}';R._cache[nm]=im;P.names[oid]=nm
# Portal colors are intrinsic; default block colors do not tint these sprites.
for o in P.objs:
 if o['1'] in ['10','11','12','13','47','111','660','745','1331','99','101','200','201','202','203','1334','36','84','141','1330','1333','1704','1751']:
  o['21']='1010';o['22']='1010'
# White diagnostic channel solely for native portal sprites.
P.head+=',kSdummy,0'

manifest=json.loads((HERE/'engulfed-manifest.json').read_text())
fx=manifest['engulfed'];cx,cy=fx['camera_reference']
base_time=P.tx(17450)
base_cache={}
all_source_objects=P.objs
ui_source_objects=[o for o in P.objs if '1200' in o.get('57','').split('.') or o['1'] in ['899','1006']]
# UI mapping is based on the native 480x320 reference and explicit edge enums.
def render_frame(name,x,y,zoom,t,aspect=16/9):
 width=320*aspect;height=320
 P.objs=ui_source_objects
 try:oo,pal=P.snapshot(x,t=t)
 finally:P.objs=all_source_objects
 pal._c[1010]=((255,255,255),False,1)
 if x not in base_cache:base_cache[x]=P.snapshot(x)
 base,basepal=base_cache[x];basepal._c[1010]=((255,255,255),False,1)
 # Preserve scene time while comparing border growth at the same location.
 allobjs=[o for o in base if not (set(o.get('57','').split('.'))&{'1200','1205'})]
 for o in oo:
  gg=set(o.get('57','').split('.'));edge=next((e for e in fx['edges'] if str(e['group']) in gg),None)
  if str(fx['takeover_group']) in gg:edge={'xref':2,'yref':6}
  if edge is None:continue
  q=dict(o);xx=float(o['2'])-cx;yy=float(o['3'])-cy
  if int(q['1']) in [920,923,924]:
   fam={920:'03',923:'01',924:'02'}[int(q['1'])]
   seed=int(abs(float(o['2'])*13+float(o['3'])*7))
   frame=1+(seed+int((t-fx['start_time'])*12))%9
   fake=400000+int(fam)*100+frame
   P.names[fake]=f'previewFire_{fam}_{frame:03d}_001.png';q['1']=str(fake)
  ux=xx+240 if edge['xref']==3 else width+xx-240 if edge['xref']==4 else width/2+xx
  uy=yy+160 if edge['yref']==7 else height+yy-160 if edge['yref']==8 else height/2+yy
  q['2']=str(x+(ux-width/2)/zoom);q['3']=str(y+(uy-height/2)/zoom)
  for k in ['128','129']:q[k]=str(float(q.get(k,1))/zoom)
  # Generated opacity channels are per palette, copy their actual RGBA values.
  for key in ['21','22']:
   cid=int(q.get(key,0))
   if cid>=80000:
    dest=500000+len(basepal._c);basepal._c[dest]=pal.get(cid);q[key]=str(dest)
  allobjs.append(q)
 allobjs=[o for o in allobjs if int(o['1']) not in [1755,2909,2921,1520,1934,2016,3613] and not P.names.get(int(o['1']),'').startswith('edit_')]
 out=HERE/('engulfed-'+name+'.png')
 R.render(allobjs,basepal,P.names,x-width/2/zoom,x+width/2/zoom,y-height/2/zoom,y+height/2/zoom,ppu=1.8*zoom,bg=(12,7,7),out=str(out))
 print('rendered',name,flush=True);return out
d=fx['fully_engulfed_time']-fx['start_time']
shots=[('start',17450,200,.8,fx['start_time']+1,16/9),
 ('middle',17450,200,.8,fx['start_time']+d*.55,16/9),
 ('closing',17450,200,.8,fx['start_time']+d*.9,16/9),
 ('engulfed',17450,200,.8,fx['fully_engulfed_time']+.04,16/9),
 ('wide',17450,200,.8,fx['fully_engulfed_time']+.04,21/9),
 ('exit',24925,230,1,fx['off_time']+.01,16/9)]
selected=os.environ.get('GD_FIRE_SHOTS','')
if selected:shots=[s for s in shots if s[0] in selected.split(',')]
files=[render_frame(*args) for args in shots]
out=Image.new('RGB',(1440,math.ceil(len(shots)/2)*432),(12,12,14));d=ImageDraw.Draw(out)
for i,(f,args) in enumerate(zip(files,shots)):
 im=Image.open(f);im.thumbnail((720,400));xx=(i%2)*720;yy=(i//2)*432
 out.paste(im,(xx+(720-im.width)//2,yy+30));d.text((xx+12,yy+8),args[0]+' / atlas diagnostic - not native play',fill=(210,190,170))
out.save(HERE/('engulfed-comparison.png' if selected else 'engulfed-sheet.png'))
