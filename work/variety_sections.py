"""UFO-specific hold/release/drop passages selected on measured song attacks."""
import math
import numpy as np
import sync_sections as S
M=S.M; R=S.R; BEAT=S.BEAT

def ufo_latches(L,s):
    times=S.note_times(s)
    # Different lengths and different approach heights, with ordinary UFO
    # flight between the passages. All starts and releases use audio attacks.
    starts=[min(range(1,len(times)-3),key=lambda i:abs(times[i]-(s['t0']+b*BEAT))) for b in (5,15,24)]
    ends=[min(range(i+1,len(times)-1),key=lambda j:abs(times[j]-(times[i]+hold))) for i,hold in zip(starts,(.46,.85,.30))]
    windows=list(zip(starts,ends));assert all(a<b for a,b in windows)
    states=[(0.,15.,0.,[])]
    for i,(a,b) in enumerate(zip(times,times[1:])):
        dt=b-a;nxt={}
        dash=next(((j,k) for j,k in windows if j<=i<k),None)
        if i==0:choices=['intro']
        elif dash:choices=['dash' if i==dash[0] else 'held']
        elif i in ends:choices=['release']
        else:choices=['coast','hop']
        for cost,y,vy,path in states:
            for act in choices:
                if act=='intro':ny,nv,lo,hi=15.,0.,15.,15.
                elif act in ('dash','held'):ny,nv,lo,hi=y,0.,y,y
                else:ny,nv,lo,hi=S.motion('ufo',y,0 if act=='release' else vy,1 if act=='hop' else 0,dt)
                if hi>275:continue
                if dash and y<65:continue
                # A release must really drop, and the following hop must be
                # airborne rather than a free bounce off the level floor.
                if act=='release' and ny<30:continue
                target=S.contour(s,b,'ufo')
                c=cost+((ny-target)/95)**2*dt+.015*(act=='hop')
                if i and ny==15:c+=.7
                key=(round(ny/2),round(nv/10))
                item=(c,ny,nv,path+[(a,act)])
                if key not in nxt or c<nxt[key][0]:nxt[key]=item
        assert nxt,('no safe UFO latch score',i,a)
        states=sorted(nxt.values(),key=lambda p:p[0])[:1200]
    score=min(states,key=lambda p:p[0])[3];tail=times[-1]
    pts=[];t=s['t0'];y=15.;vy=0.;dashes=[];hops=[]
    for i,(a,act) in enumerate(score):
        b=score[i+1][0] if i+1<len(score) else tail
        if act=='dash':
            L.orb(1704,a,y,**{'6':0,'99':0});L.event(a,'dash','ufo',orb_id=1704,audio_attack=True)
            dashes.append(dict(start=a,y=y,id=1704));vy=0.
        elif act=='release':
            L.event(a,'release','ufo',orb_id=1704,audio_attack=True);dashes[-1]['end']=a;vy=0.
        elif act=='hop':
            L.event(a,'hop','ufo',gravity=-1,audio_attack=True);vy=420.;hops.append(a)
        while t<b-1e-8:
            nt=min(t+1/240,b);dt=nt-t
            if act not in ('intro','dash','held'):
                y+=vy*dt-.5*1244.16*dt*dt;vy-=1244.16*dt
                if y<15:y=15.;vy=0.
            t=nt;pts.append([t,y,-1,15,'ufo'])
    pts+=R.finish_flight(L,s,tail,y,vy);L.path(s,pts)
    s['dash_windows']=dashes;s['note_score']=score
    # Each latch contains a level throat that rejects a normal hop. At its
    # far end the ceiling turns down, demanding a release and delayed catch.
    for j,w in enumerate(dashes):
        R.corridor(L,s,w['start']+.12,w['end']-.07,6,24 if j!=1 else 0,24,'UFO held latch '+str(j+1))
        L.gate(s,w['end']+.14,10,6,'UFO release drop')
        catch=next(t for t in hops if t>w['end'])
        L.slot(s,catch+.20,24,6,'UFO late-hop catch')
        w['catch_time']=catch
        L.phrase(s,(w['start']-s['t0'])/BEAT,(catch-s['t0'])/BEAT,'UFO hold release drop '+str(j+1),'dash beneath lintel / release into gap / late UFO hop')
    for j,t in enumerate(hops):
        if t>tail-.4:continue
        if any(w['start']-.2<t<w['end']+.5 for w in dashes):continue
        L.slot(s,t+.21,14 if j%3 else 30,5.5,'UFO offbeat pocket')
        if j in (2,8,13):L.gate(s,t+.35,10,6,'UFO floating crossing')
    for t in np.arange(s['t0']+.7,tail-.2,.17):
        L.safe_spike(s,float(t),0,True,.6);L.safe_spike(s,float(t),300,False,.6)
