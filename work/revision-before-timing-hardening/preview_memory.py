"""Atlas-based inspection with color/pulse interpolation and rotate evaluation.
This is a diagnostic renderer; it does not simulate player physics or engine FPS.
"""
from pathlib import Path
import sys,json,math,re,base64,os
from collections import defaultdict
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
import render as R
from gdparse import load,parse_header
route=json.loads((ROOT/'work/memory-plan.json').read_text())
speed=route['speed_schedule']
def xt(t):
    return sum(max(0,min(t,speed[i+1][0] if i+1<len(speed) else t)-st)*v for i,(st,v) in enumerate(speed))
def tx(x):
    for i,(t,v) in enumerate(speed):
        if i+1==len(speed) or x<xt(speed[i+1][0]):return t+(x-xt(t))/v

head,objs=load(os.environ.get('GD_PREVIEW_LEVEL',str(ROOT/'work/v8-memory.level')))
for o in objs:
    if o['1'] in ('12','660','200','201','203') and '21' not in o:
        # Native portal art is intrinsically colored; it does not take the
        # default block's dark tint. This changes the preview only.
        o['21']='1004';o['22']='1004'
R.load_atlas();names=R.load_names(str(ROOT/'work/handoff/research/objectids.yml'))
names[1887]='__glow_small';names[1886]='__glow_med';names[1888]='__glow_large'

# Use the game's own font atlas for the unchanged source text labels.
font={}
for ln in (R.RES/'bigFont-hd.fnt').read_text().splitlines():
    if ln.startswith('char id='):
        d={k:int(v) for k,v in re.findall(r'(\w+)=(-?\d+)',ln)};font[d['id']]=d
font_img=Image.open(R.RES/'bigFont-hd.png').convert('RGBA')
for i,o in enumerate(objs):
    if o['1']!='580':continue
    text=base64.urlsafe_b64decode(o['31']+'===').decode()
    width=sum(font.get(ord(c),font[32])['xadvance'] for c in text)+4
    out=Image.new('RGBA',(width,67),(0,0,0,0));px=2
    for c in text:
        f=font.get(ord(c),font[32]);x,y,w,h=[f[k] for k in ['x','y','width','height']]
        cut=font_img.crop((x,y,x+w,y+h))
        out.paste(cut,(px+f['xoffset'],f['yoffset']),cut);px+=f['xadvance']
    oid=100000+i;nm=f'__text_{i}';names[oid]=nm;R._cache[nm]=out
    o['1']=str(oid)

class DynamicPalette(R.Palette):
    def __init__(self,head,objs,t):
        super().__init__(head,objs);self.t=t
        self.events=defaultdict(list);self.pulses=defaultdict(list)
        for o in objs:
            if o['1']=='899':self.events[int(o['23'])].append(o)
            if o['1']=='1006' and o.get('52','0')=='0':self.pulses[int(o['51'])].append(o)
        for es in self.events.values():es.sort(key=lambda o:float(o['2']))
    def set_x(self,x):pass
    def get(self,cid,depth=0):
        if cid in self._c:return self._c[cid]
        rgb,bl,op=super().get(cid,depth)
        start=rgb;target=rgb;tt=0;duration=0
        for e in self.events[cid]:
            now=tx(float(e['2']))
            if now>self.t:break
            q=min(1,max(0,(now-tt)/duration)) if duration else 1
            start=tuple(a+(b-a)*q for a,b in zip(start,target))
            target=tuple(float(e.get(k,255)) for k in ['7','8','9'])
            tt=now;duration=float(e.get('10',0));bl=e.get('17')=='1';op=float(e.get('35',1))
        q=min(1,max(0,(self.t-tt)/duration)) if duration else 1
        rgb=tuple(a+(b-a)*q for a,b in zip(start,target))
        for e in self.pulses[cid]:
            dt=self.t-tx(float(e['2']));fi=float(e.get('45',0));hold=float(e.get('46',0));fo=float(e.get('47',0))
            if not 0<=dt<fi+hold+fo:continue
            q=dt/fi if fi and dt<fi else 1 if dt<fi+hold else max(0,1-(dt-fi-hold)/max(fo,.001))
            target=tuple(float(e.get(k,255)) for k in ['7','8','9'])
            rgb=tuple(a+(b-a)*q for a,b in zip(rgb,target))
        out=(tuple(int(max(0,min(255,c))) for c in rgb),bl,op);self._c[cid]=out;return out

groups=defaultdict(list)
for o in objs:
    for g in o.get('57','').split('.'):
        if g:groups[g].append(o)
rotates=[o for o in objs if o['1']=='1346' and float(o['2'])>=0]
moves=[o for o in objs if o['1']=='901']
alphas=[o for o in objs if o['1']=='1007']
toggles=[o for o in objs if o['1']=='1049']

def snapshot(x,t=None,ldm=False):
    t=tx(x) if t is None else t
    result=[]
    active={};opacity={};pal=DynamicPalette(head,objs,t)
    te=[(tx(float(o['2'])),o['51'],o.get('56')=='1') for o in toggles]
    te += [(e['time'],str(e['target']),False) for e in route['controls'] if e['kind']=='memory']
    for tt,g,on in sorted(te):
        if tt<=t:active[g]=on
    for o in sorted(alphas,key=lambda o:float(o['2'])):
        tt=tx(float(o['2']))
        if tt>t:continue
        g=o['51'];q=min(1,(t-tt)/max(.001,float(o.get('10',0))))
        opacity[g]=opacity.get(g,1)*(1-q)+float(o['35'])*q
    for o0 in objs:
        if o0.get('135')=='1':continue
        if ldm and o0.get('103')=='1':continue
        if o0['1'] in ['899','1006','901','1346','3600','2925','1914','1913','1007','1049']:continue
        gg=o0.get('57','').split('.')
        if any(not active.get(g,True) for g in gg):continue
        op=min(opacity.get(g,1) for g in gg)
        if op<.01:continue
        o=dict(o0)
        if op<.999:
            for key in ('21','22'):
                cid=int(o.get(key,1));rgb,bl,alpha=pal.get(cid)
                new=80000+len(pal._c);pal._c[new]=(rgb,bl,alpha*op);o[key]=str(new)
        for tr in rotates:
            if tr['51'] not in o.get('57','').split('.'):continue
            centers=groups.get(tr.get('71',''),[])
            if len(centers)!=1:continue
            dt=t-tx(float(tr['2']))
            if dt<=0:continue
            q=min(1,dt/max(.001,float(tr.get('10',0))))
            a=(float(tr.get('68',0))+360*float(tr.get('69',0)))*q
            cx,cy=float(centers[0]['2']),float(centers[0]['3'])
            dx,dy=float(o['2'])-cx,float(o['3'])-cy;rad=-math.radians(a)
            o['2']=str(cx+dx*math.cos(rad)-dy*math.sin(rad))
            o['3']=str(cy+dx*math.sin(rad)+dy*math.cos(rad))
            o['6']=str(float(o.get('6',0))+a)
        for tr in moves:
            if tr['51'] not in o.get('57','').split('.'):continue
            dt=t-tx(float(tr['2']))
            q=min(1,max(0,dt/max(.001,float(tr.get('10',0)))))
            if tr.get('30')=='13':q=(1-math.cos(math.pi*q))/2
            o['2']=str(float(o['2'])+float(tr.get('28',0))*q)
            o['3']=str(float(o['3'])+float(tr.get('29',0))*q)
        result.append(o)
    return result,pal

# Read the actual static-camera target instead of inventing y=150.
# This remains a diagnostic render; native portal behaviour needs a game check.
def cam(x):
    cs=[o for o in objs if o['1']=='1914' and float(o['2'])<=max(1,x) and o.get('101')=='2']
    if not cs:raise ValueError('No serialized Y camera lock')
    tr=max(cs,key=lambda o:float(o['2']))
    targets=groups[tr['71']]
    assert len(targets)==1
    return float(targets[0]['3'])
def zoom_at(x):
    cs=[o for o in objs if o['1']=='1913' and float(o['2'])<=x]
    return float(max(cs,key=lambda o:float(o['2']))['371']) if cs else 1


def shot(x,path,ppu=1,ldm=False,phase=0):
    cy=cam(x);oo,pal=snapshot(x,tx(x)+phase,ldm)
    half_h=160/zoom_at(x)
    R.render(oo,pal,names,x-211,x+456,cy-half_h,cy+half_h,ppu=ppu,out=str(path))
    return cy

if __name__=='__main__':
    points=json.loads(sys.argv[1]) if len(sys.argv)>1 else [260,1080,2200,3500,4700,5820,6570,7390,8190,8950,9550,10200,11000,12280,13600,14900,16100,17500,18800,19700]
    label=sys.argv[2] if len(sys.argv)>2 else 'review'
    target=ROOT/'work/previews';target.mkdir(exist_ok=True)
    sheet=Image.new('RGB',(1200,350*math.ceil(len(points)/2)),(11,17,23));draw=ImageDraw.Draw(sheet)
    for i,x in enumerate(points):
        path=target/f'{label}-{x}.png';cy=shot(x,path,1.5)
        tile=Image.open(path).resize((600,330),Image.Resampling.LANCZOS)
        left=i%2*600;top=i//2*350
        sheet.paste(tile,(left,top+20));draw.text((left+10,top+4),f'{tx(x):05.2f}s / x {x} / camera {cy:.1f}',fill=(190,205,216))
        print('rendered',x,flush=True)
    sheet.save(target/f'{label}-sheet.png')
