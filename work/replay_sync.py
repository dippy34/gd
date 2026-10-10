"""Independent input replay against the actual exported collision objects.
Model assumptions are explicitly reported. No native-completion claim.
"""
exec((__import__('pathlib').Path(__file__).parent/'check_sync_route.py').read_text().split('events=[]')[0])
J=637.2;G=3110.4
def replay(s,offset=0,gravity_scale=1,perturb_time=None,input_shift=0,release_shift=0,stop_at=None,stop_first=False,dash_release_vy=0):
 mode=s['mode'];start=s['t0'];end=s['t1']-(.9 if mode in ('ship','ufo','wave') else 0)
 controls=[dict(e,time=e['time']+offset) for e in P['controls'] if start-1e-7<=e['time']<end-1e-7 and e['mode']==mode]
 if perturb_time is not None:
  selected=[e for e in controls if abs(e['time']-perturb_time)<1e-7]
  assert len(selected)==1,(s['name'],perturb_time,len(selected))
  selected[0]['time']+=input_shift
  if release_shift:selected[0]['hold']=max(0,selected[0].get('hold',0)+release_shift)
 if stop_at is not None:end=min(end,stop_at)
 controls.sort(key=lambda e:e['time']);ei=0;t=start;y=15.;vy=0.;g=-1;on_ground=True;held=False;hold_end=-1;mini=False;dashing=False
 v=s['speed'];jump=637.2 if s['speed_index']==0 else 670.8;active={};count=Counter();first={};trace=[]
 # Carry serialized size state into the room instead of assuming a reset.
 preceding=sorted((float(o['2']),int(o['1'])) for o in objects if o['1'] in ('99','101') and o.get('121')!='1' and float(o['2'])<=s['x0']+.0001)
 mini=preceding[-1][1]==101 if preceding else False
 if mini and mode!='wave':raise AssertionError(('Unexpected inherited mini state',s['name']))
 portals=[]
 for o in objects:
  if int(o['1']) not in (10,11,99,101) or o.get('121')=='1':continue
  x=float(o['2']);tt=start+(x-s['x0'])/v
  if start<tt<end:portals.append((tt,int(o['1']),float(o['3']),float(o.get('129',o.get('32',1)))))
 portals.sort();pi=0
 def err(kind,**kw):
  count[kind]+=1
  if kind not in first:first[kind]=dict(t=t,y=y,x=s['x0']+(t-start)*v,**kw)
 for m in P['memories']:
  if not m['correct']:active[m['group']]=False
 def boxes(x,r=15):return [q for q in nearby(bybin,x,r) if not any(not active.get(g,True) for g in q[4])]
 while t<end-1e-7:
  if stop_first and count:break
  x=s['x0']+(t-start)*v
  while pi<len(portals) and portals[pi][0]<=t+1e-7:
   _,oid,portal_y,portal_scale=portals[pi];pi+=1
   if abs(y-portal_y)>75*portal_scale+(3 if mini and mode=='wave' else 5 if mode=='wave' else 15):continue
   if oid in (10,11):g=-1 if oid==10 else 1;on_ground=False
   else:mini=oid==101
  if ei<len(controls) and controls[ei]['time']<=t+1e-7:
   e=controls[ei];ei+=1;k=e['kind']
   if k in ('jump','hold'):
    if not on_ground:err('airborne input')
    vy=-g*jump*(.5 if mode=='robot' else 1);on_ground=False;hold_end=t+e.get('hold',0)
   elif k=='dash':
    oo=min((o for o in objects if o['1']==str(e['orb_id'])),key=lambda o:abs(float(o['2'])-e['x']))
    if abs(float(oo['3'])-y)>24 or abs(float(oo['2'])-x)>30:err('unreachable dash orb',orb_y=float(oo['3']))
    dashing=True;vy=0;on_ground=False
   elif k=='release':
    dashing=False;vy=-g*dash_release_vy
    if e['orb_id']==1751:g*=-1
   elif k=='orb':
    oo=min((o for o in objects if o['1']==str(e['orb_id'])),key=lambda o:abs(float(o['2'])-e['x']))
    if abs(float(oo['3'])-y)>24 or abs(float(oo['2'])-x)>30:err('unreachable orb',orb_y=float(oo['3']))
    if e['orb_id']==84:g*=-1;vy=g*jump*.4
    else:vy=-g*jump*(.72 if e['orb_id']==141 else 1)
    on_ground=False
   elif k=='memory':
    oo=next(o for o in objects if o['1']=='1594' and int(o.get('51',0))==e['target'])
    if abs(float(oo['3'])-y)>22:err('unreachable memory orb',orb_y=float(oo['3']))
    active[e['target']]=oo.get('56')=='1'
   elif k in ('turn','thrust'):held=e['down']
   elif k=='hop':vy=-g*420;on_ground=False
   elif k=='flip':
    if not on_ground:err('airborne flip')
    g*=-1;on_ground=False;vy=g*jump*.3
    if mode=='spider':
     faces=[q for q in boxes(x,0) if q[0]<=x<=q[1] and (q[2]>=y+14 if g>0 else q[3]<=y-14)]
     if not faces:err('missing teleport face')
     else:y=min(q[2] for q in faces)-15 if g>0 else max(q[3] for q in faces)+15;vy=0;on_ground=True
   continue
  ne=controls[ei]['time'] if ei<len(controls) else end
  np_=portals[pi][0] if pi<len(portals) else end
  nt=min(end,t+1/240,ne,np_)
  if mode=='robot' and t<hold_end:nt=min(nt,hold_end)
  dt=nt-t
  if dt<1e-9:t+=1e-8;continue
  x=s['x0']+(nt-start)*v;old=y;r=(3 if mini else 5) if mode=='wave' else 15
  if dashing:pass
  elif mode=='wave':
   y+=(-g)*(1 if held else -1)*v*(2 if mini else 1)*dt
   if g==-1:y=max(15,y)
  else:
   acc=g*(2200 if mode=='ball' else 1244.16 if mode=='ufo' else 1000 if mode=='ship' else G)*gravity_scale
   if mode=='ship':acc=(-g if held else g)*1000*gravity_scale
   if mode=='robot' and t<hold_end:acc=0;vy=-g*jump*.5
   if mode in ('cube','robot','ball','spider'):
    bb=boxes(x,r)
    support=[q for q in bb if q[0]<x+r and q[1]>x-r and abs((q[2]-15 if g>0 else q[3]+15)-y)<.15]
    if on_ground and not support:on_ground=False
   else:on_ground=False
   if not on_ground:
    y+=vy*dt+.5*acc*dt*dt;vy+=acc*dt
    if mode=='ship':vy=max(-300,min(300,vy))
   bb=boxes(x,r)
   lower=[q for q in bb if q[0]<x+r-.075 and q[1]>x-r+.075 and vy<=0 and old-r>=q[3]-.15 and y-r<=q[3]]
   upper=[q for q in bb if q[0]<x+r-.075 and q[1]>x-r+.075 and vy>=0 and old+r<=q[2]+.15 and y+r>=q[2]]
   if lower and (g<0 or mode=='ship'):y=max(q[3] for q in lower)+r;vy=0;on_ground=True
   if upper and (g>0 or mode=='ship'):y=min(q[2] for q in upper)-r;vy=0;on_ground=True
  t=nt
  for q in boxes(x,r):
   if overlap(q,x,y,r):err('solid collision',object=q[-1])
  for q in nearby(spbin,x,r):
   if not any(not active.get(g,True) for g in q[4]) and overlap(q,x,y,r):err('spike collision',object=q[-1])
  trace.append([t,x,y])
 return dict(section=s['name'],mode=mode,offset=offset,gravity_scale=gravity_scale,errors=dict(count),first=first,exit_y=y,samples=len(trace)),trace
if __name__=='__main__':
 offset=float(sys.argv[1]) if len(sys.argv)>1 else 0
 gs=float(sys.argv[2]) if len(sys.argv)>2 else 1
 out=[];traces=[]
 for s in P['sections']:
  res,tr=replay(s,offset,gs);out.append(res);traces.append(dict(section=s['name'],points=tr))
 suffix='' if offset==0 and gs==1 else f'-{offset}-{gs}'
 (ROOT/f'work/sync-replay{suffix}.json').write_text(json.dumps(out,indent=2))
 if not suffix:
  (ROOT/'work/sync-replay-paths.json').write_text(json.dumps(traces,separators=(',',':')))
  (ROOT/'work/sync-replay-sha256.txt').write_text(hashlib.sha256((ROOT/'outputs/v8-1573528-sync.gmd').read_bytes()).hexdigest())
 print(json.dumps([r for r in out if r['errors']],indent=2));print('model replay failures',sum(bool(r['errors']) for r in out))
