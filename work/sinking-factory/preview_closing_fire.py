from pathlib import Path
import os,sys,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
os.environ['GD_PREVIEW_PLAN']=str(HERE/'closing-fire-manifest.json');os.environ['GD_PREVIEW_LEVEL']=str(HERE/'closing-fire.level')
sys.path.insert(0,str(ROOT/'work'))
import preview_memory as P
R=P.R
R.SHEETS += ['FireSheet_01','GJ_ParticleSheet'];R.load_atlas()
# Animated flame detail layers use a special native frame name.
# Alias the existing atlas metadata so the renderer draws the real fire fill.
for family in ['01','02','03','04']:
 native=f'Fire_{family}_2_looped_001.png'
 if native in R._frames:R._frames[f'Fire_{family}_looped_2_001.png']=R._frames[native]

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

manifest=json.loads((HERE/'closing-fire-manifest.json').read_text())
fx=manifest['closing_fire'];cx,cy=fx['camera_reference']
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
  if edge is None:continue
  q=dict(o);xx=float(o['2'])-cx;yy=float(o['3'])-cy
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
 out=HERE/('closing-fire-'+name+'.png')
 R.render(allobjs,basepal,P.names,x-width/2/zoom,x+width/2/zoom,y-height/2/zoom,y+height/2/zoom,ppu=1.8*zoom,bg=(12,7,7),out=str(out))
 print('rendered',name,flush=True);return out
shots=[('early',17450,200,.8,fx['start_time']+1,16/9),('late',17450,200,.8,fx['fully_closed_time'],16/9),
 ('cube',22480,220,1,P.tx(22480),16/9),('exit',24925,230,1,fx['off_time']+.1,16/9),
 ('wide',17450,200,.8,fx['fully_closed_time'],21/9),('tablet',17450,200,.8,fx['fully_closed_time'],4/3)]
selected=os.environ.get('GD_FIRE_SHOTS','')
if selected:shots=[s for s in shots if s[0] in selected.split(',')]
files=[render_frame(*args) for args in shots]
out=Image.new('RGB',(1440,math.ceil(len(shots)/2)*432),(12,12,14));d=ImageDraw.Draw(out)
for i,(f,args) in enumerate(zip(files,shots)):
 im=Image.open(f);im.thumbnail((720,400));xx=(i%2)*720;yy=(i//2)*432
 out.paste(im,(xx+(720-im.width)//2,yy+30));d.text((xx+12,yy+8),args[0]+' / atlas diagnostic - not native play',fill=(210,190,170))
out.save(HERE/('closing-fire-comparison.png' if selected else 'closing-fire-sheet.png'))
