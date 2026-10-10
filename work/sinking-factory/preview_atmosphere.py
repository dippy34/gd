from pathlib import Path
import os,sys,json,math
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).parent
os.environ['GD_PREVIEW_PLAN']=str(HERE/'atmosphere-manifest.json');os.environ['GD_PREVIEW_LEVEL']=str(HERE/'atmosphere.level')
sys.path.insert(0,str(ROOT/'work'))
import preview_memory as P
R=P.R
R.SHEETS += ['FireSheet_01','GJ_ParticleSheet'];R.load_atlas()
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
shots=[('Ship',17400,190,.75),('Wave',19155,210,1),('Wave exit',20190,230,1),('Robot',21465,300,1),('Moving platform',22190,235,1),('UFO',23520,200,1)]
rows=[]
for name,x,y,zoom in shots:
 oo,pal=P.snapshot(x);pal._c[1010]=((255,255,255),False,1)
 oo=[o for o in oo if int(o['1']) not in [1755,2909,2921,1520,1934] and not P.names.get(int(o['1']),'').startswith('edit_')]
 # Match aspect and serialized zoom, with center bounded to local gameplay.
 hw=285/zoom;hh=160/zoom
 f=HERE/f"atmosphere-{name.replace(' ','-').lower()}.png"
 R.render(oo,pal,P.names,x-hw,x+hw,y-hh,y+hh,ppu=1.7,bg=(12,7,7),out=str(f))
 rows.append((name,Image.open(f)))
 print('rendered',name,flush=True)
out=Image.new('RGB',(1500,3*450),(8,13,16));d=ImageDraw.Draw(out)
for i,(name,im) in enumerate(rows):
 im=im.resize((750,421));xx=i%2*750;yy=i//2*450;out.paste(im,(xx,yy+29));d.text((xx+12,yy+8),name+' / atlas diagnostic; native shaders not simulated',fill=(176,192,185))
out.save(HERE/'atmosphere-sheet.png')
