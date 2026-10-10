from pathlib import Path
import sys,math,json
from PIL import Image,ImageDraw
import numpy as np
sys.path.insert(0,str(Path(__file__).parent))
from preview_v8 import shot,xt,tx,ROOT,route
out=ROOT/'work/full-review';out.mkdir(exist_ok=True)
times=list(range(60));times[-1]=tx(route['end_x'])-.025
stats=[];tiles=[]
for i,t in enumerate(times):
    x=round(xt(t),3)
    p=out/f'{i:02d}.png'
    cy=shot(x,p,1.5)
    im=Image.open(p)
    rgb=np.asarray(im,dtype=float)
    lum=.2126*rgb[:,:,0]+.7152*rgb[:,:,1]+.0722*rgb[:,:,2]
    stats.append({'time':t,'x':x,'camera_y':cy,'mean_luma_255':round(float(lum.mean()),3),
                  'p99_luma_255':round(float(np.percentile(lum,99)),3),
                  'clipped_white_fraction':round(float((rgb.min(2)>250).mean()),6)})
    tile=Image.new('RGB',(600,350),(13,20,26));tile.paste(im.resize((600,330),Image.Resampling.LANCZOS),(0,20))
    ImageDraw.Draw(tile).text((8,4),f'{t:05.2f}s | x {x:.0f} | camera {cy:.1f}',fill=(192,209,215))
    tiles.append(tile)
    if len(tiles)==10:
        page=Image.new('RGB',(1200,1750),(13,20,26))
        for j,tile in enumerate(tiles):page.paste(tile,(j%2*600,j//2*350))
        page.save(out/f'page-{i//10+1}.png');tiles=[]
    print('checked',i,flush=True)
ldm=Image.new('RGB',(1200,1050),(13,20,26))
for i,x in enumerate([2200,9550,17500]):
    for j,low in enumerate([False,True]):
        p=out/f'ldm-{x}-{low}.png';shot(x,p,1.5,ldm=low)
        im=Image.open(p).resize((600,330),Image.Resampling.LANCZOS)
        ldm.paste(im,(j*600,i*350+20))
        ImageDraw.Draw(ldm).text((j*600+8,i*350+4),f'x {x} | '+('LOW DETAIL' if low else 'FULL DETAIL'),fill=(192,209,215))
ldm.save(out/'ldm-comparison.png')
(ROOT/'work/frame-metrics.json').write_text(json.dumps(stats,indent=2))
print('FULL REVIEW COMPLETE',flush=True)
