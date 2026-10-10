"""Authored mixed-mode layout. Native coordinates; no old gameplay retained.

Normal speed throughout. Portal changes follow the original song phrases.
Wave turn intervals and all flip gates are explicitly measured in this module.
"""
import math,bisect
B=60/170
PHASE=.134
SPEED=311.58
DROP=PHASE+96*B
END=59.10
SECTIONS=[
    {'mode':'wave','t0':0,'t1':PHASE+32*B,'gap':144},
    {'mode':'ball','t0':PHASE+32*B,'t1':PHASE+64*B},
    {'mode':'spider','t0':PHASE+64*B,'t1':DROP},
    {'mode':'wave','t0':DROP,'t1':PHASE+128*B,'gap':136},
    {'mode':'ship','t0':PHASE+128*B,'t1':PHASE+144*B,'gap':200},
    {'mode':'ball','t0':PHASE+144*B,'t1':END},
]
def xt(t):return t*SPEED
def tx(x):return x/SPEED
def interpolate(points,x):
    xs=[p[0] for p in points];i=max(0,min(len(points)-2,bisect.bisect_right(xs,x)-1))
    a,b=points[i:i+2];q=max(0,min(1,(x-a[0])/(b[0]-a[0])))
    return a[1]+q*(b[1]-a[1])

def build():
    objects=[];rects=[];hazards=[];controls=[];routes=[];portals=[]
    def obj(oid,x,y,**kw):
        d={'1':oid,'2':round(x,6),'3':round(y,6),'20':0,'64':1,'67':1,'96':1}
        d.update(kw);objects.append({str(k):str(v) for k,v in d.items()});return objects[-1]
    def solid(a,b,lo,hi):
        if hi-lo<.01:return
        n=max(1,math.ceil((b-a)/90));m=max(1,math.ceil((hi-lo)/90))
        w=(b-a)/n;h=(hi-lo)/m
        for i in range(n):
            for j in range(m):
                obj(1,a+(i+.5)*w,lo+(j+.5)*h,**{'128':w/30,'129':h/30,'21':1,'22':2})
        rects.append([a,b,lo,hi])
    def spike(x,y,up):
        obj(8,x,y+15 if up else y-15,**{'6':0 if up else 180,'21':3})
        hazards.append({'x':x,'surface_y':y,'up':up})
    def portal(oid,x,y):
        # Tall visible portals intersect every valid incoming trajectory.
        # Width stays native; y scaling only expands their vertical coverage.
        obj(oid,x,y,**{'128':1,'129':3.4,'13':1,'21':1004,'22':1004})
        portals.append({'id':oid,'x':x,'y':y})
    waves=[]
    for si,s0 in enumerate(SECTIONS):
        s=dict(s0);s['x0']=xt(s['t0']);s['x1']=xt(s['t1']);a,b=s['x0'],s['x1']
        if si:
            portal({'wave':660,'ball':47,'spider':1331,'ship':13}[s['mode']],a+10,150)
            portal(10,a+45,150)
        if s['mode']=='wave':
            # A full-size wave uses 45-degree legs. Each return pair has the
            # same length, preventing gradual vertical drift through a phrase.
            initial_y=15 if si==0 else 45
            entry=a+SPEED*((PHASE if si==0 else 0)+.25*B)
            low=initial_y+entry-a
            points=[(a,initial_y)]
            points.append((entry,low))
            x=entry;direction=1;idx=0
            pairs=([1.5,1.75,1.5,1.75,1.25,1.75,1.5,1.75,1.5,1.625] if si==0 else
                   [1.5,1.75,1.25,1.75,1.5,1.75,1.5,1.75,1.5,1.625])
            durations=[d for d in pairs for _ in range(2)]
            y=low
            while x<b-.001:
                length=durations[idx%len(durations)]*B*SPEED
                nx=min(b,x+length);ny=y+direction*(nx-x)
                points.append((nx,ny))
                if nx<b-.01:controls.append({'x':nx,'time':tx(nx),'mode':'wave','down':direction<0,'kind':'turn'})
                x,y=nx,ny;direction*=-1;idx+=1
            # Transition buffers open gradually on both ends. Full-width wall
            # spacing is measured vertically; the validator also checks the
            # diagonal distance and finite player box.
            wall=[];step=7.5
            x=a
            while x<b:
                xx=min(x+step,b);mid=(x+xx)/2;c=interpolate(points,mid)
                edge=min(mid-a,b-mid)
                expand=max(0,1-edge/190)*100
                lo=max(-25,c-s['gap']/2-expand);hi=min(355,c+s['gap']/2+expand)
                if mid-a<220:lo=min(lo,0)
                if b-mid<190:lo=min(lo,30);hi=max(hi,275)
                solid(x,xx,-90,lo);solid(x,xx,hi,420)
                wall.append([x,xx,lo,hi])
                x=xx
            s['points']=points;s['walls']=wall;s['turn_intervals_beats']=durations
            waves.append(s)
        elif s['mode'] in ['ball','spider']:
            solid(a,b,-60,30)
            if si==5:
                # The ship may enter high. Taper the ceiling after its portal,
                # while normal gravity settles the ball onto the lower rail.
                for j in range(16):
                    left=a+j*15;right=left+15
                    solid(left,right,330-90*(j+.5)/16,390)
                solid(a+240,b,240,360)
            else:solid(a,b,240,360)
            intervals=[2,2.5,2,2,2.5,2] if s['mode']=='ball' else [1.5,2,1.5,2.5,2,1.5,2]
            t=s['t0']+1.10;up=True;i=0;flips=[]
            last=s['t1']-1.05
            if si==5:last=min(last,PHASE+160*B-.85)
            while t<last:
                x=xt(t);lead=86 if s['mode']=='ball' else 60
                spike(x+lead,30 if up else 240,up)
                if i%3==2:spike(x+lead+30,30 if up else 240,up)
                flips.append({'x':x,'time':t,'from_floor':up})
                controls.append({'x':x,'time':t,'mode':s['mode'],'kind':'tap','from_floor':up})
                up=not up;t+=intervals[i%len(intervals)]*B;i+=1
            s['flips']=flips
            # Restore down gravity before each following mode, with enough
            # runway to reach the lower rail and release the previous input.
            portal(10,b-190,150)
            if si==5:portal(10,xt(PHASE+160*B),150)
        elif s['mode']=='ship':
            start_y=waves[-1]['points'][-1][1]
            points=[];wall=[];step=15
            for i in range(math.ceil((b-a)/step)+1):
                x=min(b,a+i*step);u=(x-a)/(b-a)
                y=155+40*math.sin(u*math.tau*1.5)
                q=min(1,(x-a)/270);y=start_y*(1-q)+y*q
                points.append((x,y))
            x=a
            while x<b:
                xx=min(x+step,b);c=interpolate(points,(x+xx)/2)
                expand=max(0,1-min(x-a,b-x)/240)*100
                lo=max(0,c-s['gap']/2-expand);hi=min(330,c+s['gap']/2+expand)
                if x-a<180:lo=0;hi=330
                if b-x<180:lo=min(lo,30);hi=max(hi,275)
                solid(x,xx,-60,lo);solid(x,xx,hi,390)
                wall.append([x,xx,lo,hi]);x=xx
            s['points']=points;s['walls']=wall
        routes.append(s)
    # Native free-mode removes game-mode-specific invisible floor/ceiling
    # changes. Camera Y remains at 165; all playable surfaces fit on screen.
    obj(2925,0,-450,**{'111':1,'112':1,'113':10,'114':.5,'370':1,'20':5})
    obj(1764,0,165,**{'57':900,'121':1,'134':1,'128':.01,'129':.01,'21':60,'22':60,'24':-5})
    obj(1914,1,-450,**{'71':900,'101':2,'155':1,'10':0,'20':5})
    obj(3600,xt(END),165,**{'20':5})
    return objects,{'sections':routes,'speed_schedule':[[0,SPEED]],'beat':B,'phase':PHASE,
        'drop_time':DROP,'end_time':END,'end_x':xt(END),'rectangles':rects,
        'hazards':hazards,'controls':sorted(controls,key=lambda x:x['x']),
        'portals':portals,'initial_mode':'wave','camera_y':165}
