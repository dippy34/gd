"""Slow memory/precision layout, authored musical sections, no timewarp."""
from pathlib import Path
import sys,json,math,base64,bisect,hashlib
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/handoff/tools'))
from gmd import read_gmd,decompress,compress,write_gmd
from gdparse import parse_header,parse_ks38
from demon_layout import build,xt,bt,B,PHASE,ONSETS
objects,plan=build()
# Native collision geometry stays visible. Spare color creates the dark layout.
for o in objects:
 if o['1'] in ['1','8']:
  o.pop('135',None);o['21']='1' if o['1']=='1' else '3';o['22']='2' if o['1']=='1' else '3'
  o['24']='-1';o['25']='1'

def add(oid,x,y,**kw):
 d={'1':oid,'2':round(x,5),'3':round(y,5),'64':1,'67':1,'96':1,'20':0};d.update(kw)
 o={k:str(v) for k,v in d.items()};objects.append(o);return o

def solid(l,r,lo,hi,kind):
 if r-l<1 or hi-lo<1:return
 plan['rectangles'].append([l,r,lo,hi,kind])
 n=math.ceil((r-l)/90);m=math.ceil((hi-lo)/90)
 for i in range(n):
  for j in range(m):add(1,l+(i+.5)*(r-l)/n,lo+(j+.5)*(hi-lo)/m,**{'128':(r-l)/n/30,'129':(hi-lo)/m/30,'21':1,'22':2,'24':-1})

precision=[]
for sec in plan['sections']:
 pts=[p for p in plan['paths'] if sec['t0']<=p[0]<sec['t1']]
 times=[p[0] for p in pts]
 def yt(t):
  i=max(0,min(len(pts)-2,bisect.bisect_right(times,t)-1));a,b=pts[i],pts[i+1]
  return a[2]+(b[2]-a[2])*(t-a[0])/max(1e-8,b[0]-a[0])
 mode=sec['mode']
 if mode in ['cube','robot']:
  for j,e in enumerate(sec['actions']):
   tt=e['time']+(.24 if mode=='cube' else e.get('hold',.2)+.08)
   xx=xt(tt);w=18+[0,9,4,15,6,12,3,10,7,14,5][j%11];pad=21+(j%3)
   ys=[yt(tt+(k-10)*(w/2+17)/sec['speed']/10) for k in range(21)]
   low,high=min(ys)-pad,max(ys)+pad
   # Two floating faces require an accurately held arc. Open sides allow entry.
   if low>38:solid(xx-w/2,xx+w/2,low-14-j%4,low,'precision lower island')
   if high<310:solid(xx-w/2,xx+w/2,high,high+15+j%5,'precision suspended cap')
   precision.append(dict(section=sec['name'],time=tt,x=xx,low=low,high=high,width=w))
 elif mode in ['ship','ufo','wave']:
  strong=[o for o in ONSETS if sec['t0']+1<o['time']<sec['t1']-.8 and o['strength']>.13]
  last=sec['t0']
  for j,e in enumerate(strong):
   tt=e['time']
   if tt-last<(.65 if mode=='wave' else .85):continue
   last=tt;xx=xt(tt);w=20+(j*7+sec['index']*3)%29;pad=24 if mode=='wave' else 30
   ys=[yt(tt+(k-12)*(w/2+17)/sec['speed']/12) for k in range(25)]
   low,high=min(ys)-pad,max(ys)+pad
   if low>42:solid(xx-w/2,xx+w/2,18+(j%3)*2,low,'airborne lower tooth')
   if high<285:solid(xx-w/2,xx+w/2,high,312-(j%3)*2,'airborne upper tooth')
   precision.append(dict(section=sec['name'],time=tt,x=xx,low=low,high=high,width=w))
# Spike rails prevent ship/UFO floor riding or ceiling bypasses. Keep transitions
# clear, then fit rail spikes outside the whole finite-body reference path.
for sec in plan['sections']:
 if sec['mode'] not in ['ship','ufo','wave']:continue
 pts=sec['flight_points'];ts=[v[0] for v in pts]
 for j in range(int((sec['x1']-sec['x0']-400)/28)):
  xx=sec['x0']+220+j*28;tt=sec['t0']+(xx-sec['x0'])/sec['speed']
  near=[y for t,y in pts[max(0,bisect.bisect_left(ts,tt-.13)):bisect.bisect_right(ts,tt+.13)]]
  if not near:continue
  for up in [True,False]:
   if (min(near)>61 if up else max(near)<269):
    base=0 if up else 330;yy=15 if up else 315
    add(8,xx,yy,**{'6':0 if up else 180,'32':1,'21':3,'22':3,'24':-1})
    plan['hazards'].append(dict(x=xx,y=yy,base=base,up=up,scale=1))

# Tiny distant panels reinforce the palette, without arrows telling the route.
# Native visible blocks are the layout; there is no occluding foreground mask.
for o in list(objects):
 if o['1']=='1':
  add(211,float(o['2']),float(o['3']),**{'128':o.get('128','1'),'129':o.get('129','1'),'21':5,'22':5,'24':-3,'25':-5,'20':10,'121':1,'134':1})
# Sparse phrase color changes; no flashes, timewarp or random triggers.
for sec in plan['sections']:
 rgb=[(72,36,91),(92,40,75),(89,46,39),(65,37,95),(81,37,87),(60,36,77),(91,37,64)][sec['index']%7]
 add(899,sec['x0'],-450,**{'23':1,'7':rgb[0],'8':rgb[1],'9':rgb[2],'10':.6,'20':5})
# Explicit slow speed object at spawn as well as the native start setting.
add(200,0,150,**{'13':1,'21':1004,'22':1004,'128':1,'129':3.2})
fields=read_gmd(ROOT/'work/handoff/OBSIDIAN-CHOIR.gmd');H=parse_header(decompress(fields['k4'][1]).split(';')[0])
H.update({'kA2':'0','kA4':'1','kA3':'0','kA8':'0','kA10':'0','kA11':'0','kA32':'1','kA22':'0'})
H['kA14']=''.join(f'{PHASE+i*B:.5f}~{1 if i%4==0 else .8}~' for i in range(449))
colors={1:(72,36,91),2:(109,54,105),3:(157,91,112),5:(19,9,27),60:(0,0,0),1000:(6,2,11),1001:(6,2,11),1002:(61,27,76),1004:(255,255,255)}
channels={int(c['6']):c for c in parse_ks38(H['kS38'])}
for ch,rgb in colors.items():channels[ch]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':'0','6':str(ch),'7':'1','15':'1','18':'0','8':'1'}
H['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
serialize=lambda o:','.join(f'{k},{v}' for k,v in o.items())
raw=';'.join([serialize(H)]+[serialize(o) for o in objects])+';'
fields.update({'k2':('s','v8'),'k3':('s',base64.urlsafe_b64encode(b'Song 1573528 slow memory layout. 0.5x native speed for most of the song. Seven modes, no swing. Insane/entry Extreme target; unverified.').decode()),'k4':('s',compress(raw)),'k48':('i',str(len(objects))),'k45':('i','1573528'),'k14':('f',False),'k23':('i','4'),'k72':('f',False)})
(ROOT/'work/v8-demon-layout.level').write_text(raw)
plan['precision_gates']=precision
plan['slow_time']=sum(s['t1']-s['t0'] for s in plan['sections'] if s['speed_index']==0)
(ROOT/'work/demon-plan.json').write_text(json.dumps(plan,indent=2))
write_gmd(ROOT/'outputs/v8-demon-layout.gmd',fields)
print(json.dumps(dict(objects=len(objects),seconds=plan['end_time'],slow_percent=100*plan['slow_time']/plan['end_time'],precision_gates=len(precision),sections=len(plan['sections'])),indent=2))
