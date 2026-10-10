"""Audio-constrained replacement rooms, using measured attacks before geometry.

The beam solvers choose inputs only at detected attacks. They enforce finite
player bounds and then sample the selected route at 240 Hz. This is an
approximate physics diagnostic, not a native verification run.
"""
import bisect, json, math
import numpy as np
import rebalance_layout as R
M=R.M; ROOT=M.ROOT; BEAT=M.B
ON=M.AUDIO['onsets']; AT=M.AT
features=np.load(ROOT/'work/music/features-1573528.npz')
tt=features['time']; ff=features['contrast']; mask=(tt>5)&(tt<210)
comb=[]
for bpm in np.arange(130.95,131.15,.001):
    z=np.sum(ff[mask]*np.exp(2j*np.pi*tt[mask]/(60/bpm)))
    comb.append((abs(z),float(bpm),float((np.angle(z)/(2*np.pi)*(60/bpm))%(60/bpm))))
_,TEMPO,PHASE=max(comb)
MAJOR_TIMES=[]
for n in range(508):
    expected=PHASE+n*60/TEMPO
    near=[o for o in ON if abs(o['time']-expected)<.095]
    MAJOR_TIMES.append(max(near,key=lambda o:o['strength'])['time'] if near else expected)
AUDIO_MAP=dict(song=1573528,refined_bpm=TEMPO,phase=PHASE,
    analysis='Refined spectral-flux comb, then individually detected beat attacks; new flight inputs selected only from measured onsets.',
    onset_count=len(AT),major_times=MAJOR_TIMES,
    limit='Spectral peak times have finite analysis resolution; no native audio-latency calibration.')

def attack(t):
    return float(AT[np.argmin(abs(AT-t))])

def major(t):
    return min(MAJOR_TIMES,key=lambda q:abs(q-t))

def note_times(s):
    # Retain detected secondary percussion. No silent synthetic inputs.
    return [s['t0']]+[float(q) for q in AT if s['t0']+.12<q<s['t1']-.96]+[s['t1']-.8]

def contour(s,t,mode):
    b=(t-s['t0'])/BEAT
    if mode=='ship':
        keys=([0,3,7,11,14,19,22,26,30,32],[15,135,225,74,176,242,103,63,188,120]) if s['name']=='PARALLAX' else ([0,4,8,12,17,20,24,28,32],[15,214,106,243,65,178,246,94,160])
    elif mode=='wave':
        keys=([0,3,7,10,14,18,22,26,30,32],[15,180,63,235,100,48,206,117,180,140]) if s['name']=='BLINDFOLD' else ([0,4,7,12,16,21,25,29,32],[15,225,102,181,62,242,142,72,180])
    else:
        keys=([0,4,8,12,17,20,25,29,32],[15,123,227,98,184,60,238,150,85]) if s['name']=='OFFBEAT' else ([0,3,7,11,15,19,23,27,32],[15,165,70,242,128,205,55,175,110])
    return float(np.interp(b,*keys))

def motion(mode,y,vy,action,dt):
    if mode=='ship':
        a=1000 if action else -1000
        tc=max(0,min(dt,((300 if a>0 else -300)-vy)/a))
        ny=y+vy*tc+.5*a*tc*tc+(vy+a*tc)*(dt-tc)
        nv=max(-300,min(300,vy+a*dt))
        test=[y,ny]
        if 0<-vy/a<dt:test.append(y-vy*vy/(2*a))
        return ny,nv,min(test),max(test)
    if action:
        vy={1:420.,141:637.2*.72,36:637.2}[action]
    g=1244.16
    ny=y+vy*dt-.5*g*dt*dt;nv=vy-g*dt
    hi=max(y,ny,y+vy*vy/(2*g) if 0<vy/g<dt else -1)
    if ny<15:ny=15.;nv=0.
    return ny,nv,min(y,ny),hi

def flight_score(s,mode):
    times=note_times(s)
    # cost, y, velocity, previous button, [(time, action), ...]
    states=[(0.,15.,0.,False,[])]
    for i,(a,b) in enumerate(zip(times,times[1:])):
        nxt={};dt=b-a
        for cost,y,vy,held,path in states:
            if i==0:
                choices=[False] if mode=='ship' else [0]
            elif mode=='ship':choices=[False,True]
            elif i in ((5,14,23) if s['name']=='OFFBEAT' else (4,12,19,28)):
                choices=[0,1,141 if i%2 else 36]
            else:choices=[0,1]
            for act in choices:
                if i==0:ny,nv,lo,hi=15.,0.,15.,15.
                else:ny,nv,lo,hi=motion(mode,y,vy,act,dt)
                if lo<15.-1e-6 or hi>277:continue
                target=contour(s,b,mode)
                # Open large arcs follow the room's changing contour. Input
                # changes incur a small cost, avoiding the old hover spam.
                c=cost+((ny-target)/95)**2*dt
                c+=.025*(act!=held) if mode=='ship' else .018*bool(act)
                if mode=='ufo' and ny==15 and i:c+=.55
                key=(round(ny/2),round(nv/10),bool(act))
                item=(c,ny,nv,bool(act),path+[(a,act)])
                if key not in nxt or c<nxt[key][0]:nxt[key]=item
        assert nxt,('no audio-constrained flight route',s['name'],i,a,len(states))
        states=sorted(nxt.values(),key=lambda p:p[0])[:900]
    return min(states,key=lambda p:p[0])[4],times[-1]

def ship_notes(L,s):
    score,tail=flight_score(s,'ship');pts=[];t=s['t0'];y=15.;vy=0.;held=False
    for i,(a,act) in enumerate(score):
        b=score[i+1][0] if i+1<len(score) else tail
        if i and bool(act)!=held:
            held=bool(act);L.event(a,'thrust','ship',down=held,audio_attack=True)
        while t<b-1e-8:
            nt=min(t+1/240,b);dt=nt-t
            if i:y,vy,_,_=motion('ship',y,vy,held,dt)
            t=nt;pts.append([t,y,-1,15,'ship'])
    pts+=R.finish_flight(L,s,tail,y,vy);L.path(s,pts)
    s['note_score']=score
    styles=([(1.3,7.6,0,15,'rising intake'),(8.1,13.8,35,12,'low cantilever crossing'),(14.4,22.2,0,15,'high arch'),(23,29.9,32,12,'split descent')]
        if s['name']=='PARALLAX' else [(1.3,6.7,42,11,'long lift fins'),(7.2,13.8,0,11,'folded arch'),(14.4,23.1,28,12,'braking shelves'),(23.8,29.9,0,11,'rising exit trench')])
    for a,b,depth,pad,name in styles:
        R.corridor(L,s,s['t0']+a*BEAT,min(s['t0']+b*BEAT,tail-.1),pad,depth,20,name)
        if depth:
            for beat in (a+.15,b-.15):L.gate(s,s['t0']+beat*BEAT,10,9,name+' crossing')
        L.phrase(s,a,b,name,'thrust and release on measured song attacks')
    for tt in np.arange(s['t0']+.8,tail-.2,.19):
        lo,hi=L.envelope(s,M.xt(tt)-4,M.xt(tt)+4,6)
        if lo>13:L.safe_spike(s,float(tt),lo-10,True,.25,2)
        if hi<287:L.safe_spike(s,float(tt),hi+10,False,.25,2)

def wave_notes(L,s):
    times=note_times(s);grounded=s['name']=='BLINDFOLD'
    states=[(0.,15.,False,[])]
    for i,(a,b) in enumerate(zip(times,times[1:])):
        nxt={};dt=b-a
        for cost,y,held,path in states:
            for act in ([False] if i==0 else [False,True]):
                ny=y+(1 if act else -1)*s['speed']*dt
                if i==0:ny=15
                if grounded:ny=max(15,ny)
                if not 15<=ny<=274:continue
                c=cost+((ny-contour(s,b,'wave'))/90)**2*dt+.035*(act!=held)
                if grounded and ny==15:c+=.07
                key=(round(ny,1),act);item=(c,ny,act,path+[(a,act)])
                if key not in nxt or c<nxt[key][0]:nxt[key]=item
        assert nxt,('no note wave route',s['name'],i)
        states=sorted(nxt.values(),key=lambda q:q[0])[:600]
    score=min(states,key=lambda q:q[0])[3];pts=[];t=s['t0'];y=15.;g=-1;held=False;turns=0;glides=[];ground_start=None
    for i,(a,direction_up) in enumerate(score):
        b=score[i+1][0] if i+1<len(score) else times[-1]
        want_held=direction_up if g<0 else not direction_up
        if i and held!=want_held:
            turns+=1
            if not grounded and turns in (5,6,14,15):
                g*=-1;L.portal(11 if g>0 else 10,a,y)
            else:held=want_held;L.event(a,'turn','wave',down=held,gravity=g,audio_attack=True)
        while t<b-1e-8:
            nt=min(t+1/240,b);dt=nt-t
            if i:y+=(1 if direction_up else -1)*s['speed']*dt
            if grounded:y=max(15,y)
            if y==15 and ground_start is None:ground_start=t
            if y>15 and ground_start is not None:
                if t-ground_start>.08:glides.append((ground_start,t))
                ground_start=None
            t=nt;pts.append([t,y,g,5,'wave'])
    # If the second wave starts on the floor, its launch is held from room
    # entry; the first short silent approach uses a native safe ground glide.
    pts+=R.finish_flight(L,s,times[-1],y);L.path(s,pts);s['ground_glides']=glides;s['note_score']=score
    for a,b,depth,pad,name in ([(1.3,5.5,30,10,'lift and skip'),(6.1,11.2,24,9,'offset teeth'),(11.9,18.7,35,10,'broken bridge'),(19.4,24.3,26,9,'low cut and rebound'),(25.1,29.6,32,10,'late diagonal exit')]
       if grounded else [(1.4,7.1,0,10,'held gravity fold'),(7.8,13.6,33,10,'separated banks'),(14.3,20.6,0,10,'long crossing'),(21.3,29.6,27,10,'inverted cutbacks')]):
        R.corridor(L,s,s['t0']+a*BEAT,min(s['t0']+b*BEAT,times[-1]-.12),pad,depth,18,name)
        if depth:
            for beat in (a+.1,b-.1):L.gate(s,s['t0']+beat*BEAT,10,10,name+' end')
        L.phrase(s,a,b,name,'measured note changes with unequal diagonal lengths')
    if grounded:
        for a,b in glides:
            if b-a>.2 and a>s['t0']+.4:L.rect(M.xt(a+.06),M.xt(b-.04),44,65,'ground-glide roof')
    for tt in np.arange(s['t0']+.6,times[-1]-.2,.21):L.safe_spike(s,float(tt),0,True,.4,5)

def ufo_notes(L,s):
    score,tail=flight_score(s,'ufo');pts=[];t=s['t0'];y=15.;vy=0.;inputs=[]
    for i,(a,act) in enumerate(score):
        b=score[i+1][0] if i+1<len(score) else tail
        if act:
            if act==1:L.event(a,'hop','ufo',gravity=-1,audio_attack=True)
            else:L.orb(act,a,y,**{'99':0});L.event(a,'orb','ufo',orb_id=act,audio_attack=True)
            inputs.append(a);vy={1:420.,141:637.2*.72,36:637.2}[act]
        while t<b-1e-8:
            nt=min(t+1/240,b);dt=nt-t
            if i:
                y+=vy*dt-.5*1244.16*dt*dt;vy-=1244.16*dt
                if y<15:y=15.;vy=0.
            t=nt;pts.append([t,y,-1,15,'ufo'])
    pts+=R.finish_flight(L,s,tail,y,vy);L.path(s,pts);s['note_score']=score
    for i,tt in enumerate(inputs):
        if tt>tail-.4:continue
        next_t=inputs[i+1] if i+1<len(inputs) else tail
        L.slot(s,tt+min((next_t-tt)*.58,.31),14 if i%3 else 34,5.5,'ufo note catch')
        if i in (3,8,14,19):L.gate(s,tt+.35,10,6,'ufo offbeat crossing')
    for a,b,name in ([(1,8,'stepped ascent'),(8,15,'orb boosted canopy'),(15,23,'long fall catch'),(23,30,'low-to-high coda')]
       if s['name']=='OFFBEAT' else [(1,6,'early lift'),(6,13,'hanging pocket descent'),(13,22,'uneven orb relay'),(22,30,'late catch staircase')]):L.phrase(s,a,b,name,'hop / orb boost / omitted note')
    for tt in np.arange(s['t0']+.6,tail-.2,.15):
        L.safe_spike(s,float(tt),0,True,.6);L.safe_spike(s,float(tt),300,False,.6)

def spider_notes(L,s):
    s['custom_structure']=True
    # Both use the familiar false rails, but have different transfer scores.
    score=([(1,'flip',216),(2,'orb',141),(3.5,'flip',30),(4.5,'flip',246),
        (6,'orb',36),(7.5,'flip',60),(8.5,'flip',210),(9.5,'flip',0),
        (10.5,'orb',141),(12,'flip',264),(13,'flip',45),(14.5,'orb',36),
        (16,'flip',228),(17,'flip',75),(18,'orb',141),(19.5,'flip',246),(21,'flip',0)]
        if s['name']=='BLIND ELEVATOR' else
        [(1,'orb',36),(3,'flip',246),(4,'flip',54),(5,'orb',141),
         (6,'flip',198),(7,'orb',36),(9,'flip',15),(10,'flip',264),(11,'flip',72),
         (12,'orb',36),(14,'flip',228),(15,'flip',30),(16,'orb',141),
         (17,'flip',267),(18,'flip',90),(19,'orb',141),(21,'flip',222),
         (22,'orb',36),(24,'flip',45),(25,'flip',249),(26,'flip',0),
         (27,'orb',36),(29,'flip',210),(30,'flip',0)])
    states=[(0,[])]
    for i,(beat,kind,value) in enumerate(score):
        intended=s['t0']+beat*BEAT
        choices=[float(t) for t in AT if abs(t-intended)<.46]
        nxt=[]
        gap=(.42 if score[i-1][2]==36 else .32) if i and score[i-1][1]=='orb' else .23
        for t in choices:
            eligible=[p for p in states if not p[1] or t-p[1][-1][0]>=gap]
            if eligible:
                cost,path=min(eligible,key=lambda p:p[0])
                nxt.append((cost+abs(t-intended),path+[(t,kind,value)]))
        assert nxt,('no spaced spider note sequence',s['name'],i)
        states=nxt
    events=min(states,key=lambda p:p[0])[1]
    assert min(b[0]-a[0] for a,b in zip(events,events[1:]))>.21
    # Build uninterrupted support runs, with genuine openings under orb
    # arcs. There are no stacked colliders hidden behind fake line artwork.
    flips=[(t,v) for t,k,v in events if k=='flip'];runs=[];left=s['x0'];surf=0.;g=-1
    for j,(t,target) in enumerate(flips):
        runs.append((left,M.xt(t)+27,surf,g))
        left=M.xt(t)-25;surf=float(target);g*=-1
    runs.append((left,s['x1'],surf,g));assert g==-1 and surf==0
    for a,b,h,g in runs:
        L.rect(a,b,h if g>0 else h-18,h+18 if g>0 else h,'teleport shelf' if g>0 else 'island rail')
    ei=0;t=s['t0'];y=15.;vy=0.;g=-1;surface=0.;grounded=True;pts=[];orb_events=[]
    while t<s['t1']-1e-8:
        if ei<len(events) and events[ei][0]<=t+1e-8:
            et,kind,val=events[ei];ei+=1
            assert grounded,('spider input before landing',s['name'],et,y)
            if kind=='flip':
                g*=-1;surface=val;y=surface-15 if g>0 else surface+15
                L.event(et,'flip','spider',gravity=g,target=val,audio_attack=True)
            else:
                L.orb(val,et,y,**{'99':0,'445':1});L.event(et,'orb','spider',orb_id=val,audio_attack=True)
                vy=-g*637.2*(.72 if val==141 else 1);grounded=False;orb_events.append((et,val,g,surface))
            continue
        nt=min(t+1/240,s['t1'],events[ei][0] if ei<len(events) else s['t1']);dt=nt-t
        if not grounded:
            y+=vy*dt+.5*g*M.G*dt*dt;vy+=g*M.G*dt
            if g<0 and y<=surface+15:y=surface+15;vy=0.;grounded=True
            if g>0 and y>=surface-15:y=surface-15;vy=0.;grounded=True
        assert 15-1e-6<=y<=285+1e-6,(s['name'],t,y)
        t=nt;pts.append([t,y,g,15,'spider'])
    L.path(s,pts);s['orb_jumps']=[dict(t=t,id=oid,g=g,surface=h) for t,oid,g,h in orb_events]
    # Orb arcs have a mounted hazard on the current rail: teleporting instead
    # of using the orb meets a separate bank. The jump's peak has its own slot.
    for et,oid,g,surface in orb_events:
        L.gate(s,et+.11,8,4.2,'spider orb departure')
        L.slot(s,et+.22,22,4.2,'spider orb arc notch')
        L.safe_spike(s,et+.19,surface,g<0,.4,2)
    for et,_ in flips:
        shoulder=21.5/s['speed']
        L.gate(s,et-shoulder,8,3.2,'spider teleport entry')
        L.gate(s,et+shoulder,8,3.2,'spider teleport exit')
    # Two quiet straight rails carry the familiar wall-present / wall-absent
    # decision. Claim Touch prevents a toggle input becoming an extra flip.
    for beat in ([5.2,20.2] if s['name']=='BLIND ELEVATOR' else [12.2,22.2]):
        tt=attack(s['t0']+beat*BEAT)
        if min(abs(tt-e[0]) for e in events)<.18:tt+=.23
        p=min(pts,key=lambda p:abs(p[0]-tt));L.remember(s,tt,p[1],True,'?',gate_t=tt+.29)
    L.phrase(s,1,score[-1][0],'orb gaps and teleport rails','orb jump over mounted tooth / flip to opposite shelf / conditional switch')
    s['note_score']=events

def new_finale(L,s):
    # The four hold lengths and catch chains differ, and the last blue chain
    # leads into a short final orb burst rather than the old empty floor.
    src=__import__('inspect').getsource(R.dash_finale)
    start=src.index('    score=[');end=src.index('\n    events=[]',start)
    src=src[:start]+'''    score=[(1.0,'dash',.31,141,.15),(4.0,'blue',0,0,0),
           (6.0,'dash',.48,36,.16),(9.5,'pink',0,0,0),
           (11.5,'dash',.29,84,.15),(15.0,'pink',0,0,0),
           (17.0,'dash',.43,36,.15),(21.0,'blue',0,0,0),
           (23.0,'blue',0,0,0),(25.0,'pink',0,0,0),
           (27.0,'blue',0,0,0),(29.0,'blue',0,0,0)]'''+src[end:]
    # For dash entries and ordinary orb catches, the actual note is the
    # activation, and the preparatory jump is the preceding half-beat.
    src=src.replace("jt=M.snap(t0+beat*BEAT,.035);events.append((jt,'jump',0))", "note=major(t0+beat*BEAT)\n        jt=note-(.205 if kind=='dash' else .17);events.append((jt,'jump',0))")
    src=src.replace("release=M.snap(ot+hold,.028)", "release=attack(ot+hold)\n            if release-ot<.19:release=ot+hold")
    src=src.replace("ct=release+delay", "ct=release+delay")
    src=src.replace("    events.sort();ei=0", "    events.extend([(major(t0+25*BEAT)+.145,'orb',36), (attack(major(t0+27*BEAT)+.20),'orb',84), (major(t0+29*BEAT)+.15,'orb',84)])\n    events.sort();ei=0")
    src=src.replace("12,24 if i in (1,3) else 0", "7,24 if i in (1,3) else 0")
    src=src.replace("w['end']+.105,8,4.8", "w['end']+.11,10,2.8")
    src=src.replace("w['catch_time']+.12,8,4.8", "w['catch_time']+.12,10,2.8")
    src=src.replace("w['catch_time']+.24,14,5.5", "w['catch_time']+.24,18,3.2")
    src=src.replace("8,7 if round(et,6) in dash_jumps else 4.8", "10,4.0 if round(et,6) in dash_jumps else 2.8")
    src=src.replace("et+.12,8,4.8", "et+.12,10,2.8")
    src=src.replace("et+.12,10,2.8", "et+.12,10,14 if et>t0+26*BEAT else 2.8")
    src=src.replace("for dv in (-50.,50.):", "for dv in (-35.,35.):")
    ns=dict(R.__dict__,major=major,attack=attack);exec(src,ns);ns['dash_finale'](L,s)
