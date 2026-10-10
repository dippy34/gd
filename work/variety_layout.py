"""Dark v8: earlier first half, newer second half, targeted balance corrections.

Uses cached song onsets, finite player envelopes, and native gameplay objects.
The exported score is a diagnostic route, not a native completion claim.
"""
import base64, bisect, copy, inspect, json, math
import numpy as np
import branching_layout as B
from gdparse import load, parse_header, parse_ks38
from gmd import read_gmd, write_gmd, compress
M=B.M; ROOT=M.ROOT; BEAT=M.B

class PhraseLevel(B.BranchLevel):
    def envelope(self,s,a,b,pad=0):
        extra=5.5 if s['mode']=='wave' else 12 if s['name']=='UNDERTOW' else 0
        lo,hi=super().envelope(s,a,b,pad+extra)
        if s.get('dash_robust_points'):
            for t,y,g,r,mode in s['dash_robust_points']:
                x=M.xt(t)
                if a-r-.1<=x<=b+r+.1:
                    lo=min(lo,y-r-pad);hi=max(hi,y+r+pad)
        return lo,hi
    def timing_door(self,s,t,width,pad,kind,decoy=False,side=1):
        # New rooms don't inherit the old four-dividers-per-input template.
        if s.get('custom_structure'):return
        super().timing_door(s,t,width,max(0,pad-(.65 if s['mode'] not in ('ship','wave') else 0)),kind,False,side)
    def fit_gate(self,s,t,width,pad,kind='precision',floating=False):
        if s.get('custom_structure'):return
        super().fit_gate(s,t,width,pad,kind,floating)
    def gate(self,s,t,w,pad,kind):
        M.Level.timing_door(self,s,t,w,pad,kind,False)
    def slot(self,s,t,w,pad,kind):
        M.Level.fit_gate(self,s,t,w,pad,kind,True)
    def phrase(self,s,a,b,style,interaction):
        self.phrases.append(dict(section=s['name'],beat0=a,beat1=b,style=style,interaction=interaction))

def finish_flight(L,s,t,y,vy=0):
    L.portal(10,t,y);L.portal(99,t,y);L.portal(12,t+.06,y)
    return [[float(tt),max(15,min(285,y+min(0,vy)*(tt-t)-.5*M.G*(tt-t)**2)),-1,15,'cube'] for tt in np.arange(t,s['t1'],1/240)]

def corridor(L,s,a,b,pad,depth=0,step=18,kind='channel'):
    """A continuous finite-body corridor, or two suspended banks."""
    for x in np.arange(M.xt(a),M.xt(b),step):
        right=min(x+step,M.xt(b));lo,hi=L.envelope(s,x,right,pad)
        if lo>2:L.rect(float(x),float(right),max(0,lo-depth) if depth else 0,lo,kind+' lower')
        if hi<298:L.rect(float(x),float(right),hi,min(300,hi+depth) if depth else 300,kind+' upper')

def wave_hold(L,s):
    # Three recognizable held sections with automatic gravity bends, then
    # manual offbeat pairs. Size never changes in this replacement room.
    t0=s['t0'];tail=s['t1']-.8;t=t0;y=15.;g=-1;held=True;direction=1;pts=[]
    targets=[248,72,218,163,252,48,225,95,259,183,242,54,202,148,257,64,233,104,249,171,218,43,253,78,196,128,262,53,224,91,251,175,239,61,207,139,256,74,229,117,250,48,212,83]
    automatic={0,1,2,8,9,10,18,19,20,28,29}
    L.event(t,'turn','wave',down=True)
    turns=[]
    for j,goal in enumerate(targets):
        if t>=tail-1e-8:break
        if direction*(goal-y)<s['speed']*.095:goal=min(265,y+55) if direction>0 else max(35,y-55)
        ideal=t+(goal-y)/(direction*s['speed'])
        candidates=[float(q) for q in M.AT if q>t+.095 and abs(q-ideal)<.038 and 34<y+direction*s['speed']*(q-t)<266]
        nt=min(candidates,key=lambda q:abs(q-ideal)) if candidates else ideal
        nt=min(nt,tail)
        for tt in np.arange(t,nt,1/240):pts.append([float(tt),y+direction*s['speed']*(tt-t),g,5,'wave'])
        y+=direction*s['speed']*(nt-t);t=nt
        if t>=tail-1e-8:break
        direction*=-1
        if j in automatic:
            g*=-1;L.portal(11 if g>0 else 10,t,y)
            turns.append(dict(t=t,automatic=True))
        else:
            held=not held;L.event(t,'turn','wave',down=held,gravity=g)
            turns.append(dict(t=t,automatic=False))
    assert abs(t-tail)<1e-6,('wave score short',t,tail)
    pts+=finish_flight(L,s,tail,y);L.path(s,pts);s['automatic_turns']=turns
    # A held slalom, detached cantilevers, short precision burst, open crossing,
    # and final held thread are structurally distinct and never reused.
    for a,b,style,pad,depth in [(1.1,7.1,'gravity slalom',10,0),(7.5,12.8,'hanging switchbacks',9,28),(13.4,18.5,'paired needle passage',8,0),(19.2,24.6,'separated crossing',10,38),(25.1,29.7,'held exit thread',9,0)]:
        L.phrase(s,a,b,style,'hold through gravity bends / manual edge pairs')
        corridor(L,s,t0+a*BEAT,min(t0+b*BEAT,tail-.12),pad,depth,14,style)
        if depth:
            for beat in (a+.2,(a+b)/2,b-.2):L.gate(s,t0+beat*BEAT,10,8,style+' checkpoint')

def wave_skips(L,s):
    """A grounded skip, lifted burst, falling shelf crossing, and late exit.

    Native ground contact provides deliberate no-input glides. The
    middle has unequal tap packets, without repeating the later gravity room.
    """
    t0=s['t0'];tail=s['t1']-.8;v=s['speed'];y=15.;t=t0;pts=[];held=False
    # Each pair is an authored press/release beat. All entries remain normal
    # size/down gravity, distinguishing this room from FAULTLINE's held flips.
    pairs=[(.35,1.85),(3.6,4.15),(4.5,5.0),(5.4,6.6),
           (8.5,9.05),(9.35,10.05),(10.65,11.55),
           (14.4,15.75),(16.4,16.9),(17.3,17.85),(18.35,19.0),
           (21.25,22.0),(22.65,23.1),(23.65,24.65),
           (26.7,27.95),(28.6,29.2)]
    edges=sorted([(M.snap(t0+a*BEAT,.025),True) for a,b in pairs]+[(M.snap(t0+b*BEAT,.025),False) for a,b in pairs])
    ground=[];ei=0;ground_start=None
    while t<tail-1e-8:
        if ei<len(edges) and edges[ei][0]<=t+1e-8:
            held=edges[ei][1];L.event(t,'turn','wave',down=held);ei+=1
        nt=min(t+1/240,edges[ei][0] if ei<len(edges) else tail,tail);dt=nt-t
        ny=y+(1 if held else -1)*v*dt
        if ny<=15:
            ny=15.
            if ground_start is None:ground_start=t
        elif ground_start is not None:
            if t-ground_start>.08:ground.append((ground_start,t))
            ground_start=None
        assert ny<278,('wave skip height',t,ny)
        t=nt;y=ny;pts.append([t,y,-1,5,'wave'])
    if ground_start is not None:ground.append((ground_start,t))
    pts+=finish_flight(L,s,tail,y);L.path(s,pts);s['ground_glides']=ground
    # Unequal floating structures create broad diagonal skips, compact tap
    # windows, and resting gutters. No continuous repeated sawtooth tube.
    for a,b,style,depth,pad in [(1.0,3.0,'single rising keystone',32,12),(3.65,6.7,'three skipped ledges',25,10),(8.6,12.0,'staggered upper teeth',35,11),(14.6,19.15,'suspended staircase',27,10),(21.4,24.8,'broken horizontal lintels',36,11),(26.85,29.5,'final diagonal cut',24,10)]:
        L.phrase(s,a,b,style,'manual unequal press/release packets and ground glides')
        corridor(L,s,t0+a*BEAT,min(t0+b*BEAT,tail-.15),pad,depth,18,style)
        for beat in (a+.08,b-.08):L.gate(s,t0+beat*BEAT,10,10,style+' crossing')
    # A wrong extra press during each rest meets a low roof. Native ground
    # movement is kept clear; the next takeoff has its own rising exit slit.
    for a,b in ground:
        if b-a<.14 or a<t0+.4:continue
        L.rect(M.xt(a+.05),M.xt(b-.03),44,66,'wave ground-glide canopy')
    for tt in np.arange(t0+.6,tail-.2,.23):
        # Only admit floor hazards during genuine airborne crossings.
        L.safe_spike(s,float(tt),0,True,.45,5)

def ship_arcs(L,s):
    # Bang-bang arcs use physical braking distance to select sparse thrust
    # changes. Unlike the old quarter-beat hover controller, each movement
    # crosses a substantial part of the chamber.
    t0=s['t0'];tail=s['t1']-.8;t=t0;y=15.;vy=0.;g=-1;held=True;acc=1000.;pts=[];j=0
    goals=([239,55,211,104,253,39,181,76,246,119,223,44,261,92,194,58,238,112,253,47,206,82,243,64,219,98] if s['name']=='PARALLAX' else
           [194,86,259,45,228,117,248,62,201,34,263,137,231,71,251,43,184,103,258,57,216,125,246,39,233,88])
    automatic={4,11,18,23} if s['name']=='UNDERTOW' else set()
    L.event(t,'thrust','ship',down=True);switches=[];last=t;scheduled=math.inf
    while t<tail-1e-8:
        # Once braking towards the opposite extremum is needed, flip force.
        forecast=y+vy*abs(vy)/2000
        goal=goals[j%len(goals)]
        def projected(dt):
            velocity=max(-300,min(300,vy+acc*dt))
            return y+vy*dt+.5*acc*dt*dt+velocity*abs(velocity)/2000
        soon=projected(.032)
        hit=(acc>0 and soon>=goal) or (acc<0 and soon<=goal)
        if hit and t-last>.22 and math.isinf(scheduled):
            a,b=0.,.032
            for _ in range(16):
                mid=(a+b)/2
                if (projected(mid)>=goal if acc>0 else projected(mid)<=goal):b=mid
                else:a=mid
            scheduled=max(t,M.snap(t+(a+b)/2,.024))
        if t>=scheduled-1e-8:
            if j in automatic:
                g*=-1;L.portal(11 if g>0 else 10,t,y)
            else:
                held=not held;L.event(t,'thrust','ship',down=held,gravity=g)
            switches.append(dict(t=t,y=y,automatic=j in automatic));acc*=-1;j+=1;last=t;scheduled=math.inf
        dt=min(1/240,tail-t,scheduled-t);y+=vy*dt+.5*acc*dt*dt;vy=max(-300,min(300,vy+acc*dt));t+=dt
        assert 14<=y<=280,(s['name'],t,y)
        pts.append([t,y,g,15,'ship'])
    pts+=finish_flight(L,s,tail,y,vy);L.path(s,pts);s['arc_switches']=switches
    if s['name']=='PARALLAX':
        styles=[(1.4,9,'long lift duct',0,11),(9.6,16.5,'low cutback wings',34,9),(17.1,23.5,'wide rising arch',0,11),(24.1,29.9,'descending exit blades',28,9)]
    else:
        styles=[(1.4,6.5,'suspended intake',40,10),(7,14.2,'inverted arch',0,10),(14.8,21.2,'staggered suspended forks',28,9),(21.8,29.8,'deep braking trench',0,11)]
    for a,b,style,depth,pad in styles:
        L.phrase(s,a,b,style,'long thrust / deliberate release / braking arc')
        corridor(L,s,t0+a*BEAT,min(t0+b*BEAT,tail-.1),pad,depth,20,style)
        if depth:
            for beat in (a+.15,b-.15):L.gate(s,t0+beat*BEAT,10,8,style+' end')
    # Landing on a bank cannot bypass the route: teeth run along its contact
    # faces and are admitted only if the full route body clears their bounds.
    for beat in np.arange(1.8,29.7,.31):
        tt=t0+float(beat)*BEAT;lo,hi=L.envelope(s,M.xt(tt)-4,M.xt(tt)+4,6)
        if lo>12:L.safe_spike(s,tt,max(0,lo-10),True,.24,2)
        if hi<288:L.safe_spike(s,tt,min(300,hi+10),False,.24,2)

def ufo_packets(L,s):
    t0=s['t0'];tail=s['t1']-.8;t=t0;y=15.;vy=0.;g=-1;pts=[];events=[]
    # Pick actual audio attacks around authored interval families. Two short
    # hops build altitude, then a long coast crosses a suspended pocket.
    targets=[105,188,245,77,151,223,49,121,204,259,99,171,235,58,144,217,84,166,244,39,119,190,252,72,155,225,52,134,214,265,90,176,237,61]
    nt=t0+.10;j=0
    while t<tail-1e-8:
        if t>=nt-1e-8:
            vy=420.;L.event(t,'hop','ufo',gravity=-1);events.append(t)
            want=targets[j%len(targets)];j+=1
            candidates=[]
            for delta in np.arange(.225,.96,.0125):
                ideal=t+float(delta);tt=M.snap(ideal,.022);dt=tt-t
                yy=y+420*dt-.5*1244.16*dt*dt
                peak=y+420**2/(2*1244.16)
                if 25<yy<207 and peak<281 and dt>.22:
                    candidates.append((abs(yy-want)+12*abs(delta/BEAT-round(delta/BEAT*4)/4),tt))
            assert candidates,('no safe ufo hop',t,y)
            nt=min(candidates)[1]
        to=min(t+1/240,nt,tail);dt=to-t
        y+=vy*dt-.5*1244.16*dt*dt;vy-=1244.16*dt
        if y<15 and t<t0+.11:y=15.;vy=0.
        assert 14.9<=y<=282,('ufo bounds',t,y)
        t=to;pts.append([t,y,g,15,'ufo'])
    pts+=finish_flight(L,s,tail,y,vy);L.path(s,pts)
    for j,tt in enumerate(events):
        if tt>tail-.35:continue
        # The short / long movement pairs get a single suspended throat at a
        # different part of each arc, not matching cages around every click.
        dt=events[j+1]-tt if j+1<len(events) else .5
        gate_t=tt+min(dt*.58,.33)
        L.slot(s,gate_t,28 if dt>.6 else 12,5,'ufo catch pocket')
        if j%3==1:L.gate(s,gate_t+.18,9,6,'offbeat crossbar')
    for a,b,style in [(1,8,'two-hop ascent'),(8,15,'long coast beneath canopy'),(15,23,'late catch pockets'),(23,30,'compressed final burst')]:
        L.phrase(s,a,b,style,'uneven hop packets / extended free fall')
    for tt in np.arange(t0+.8,tail,.13):
        L.safe_spike(s,float(tt),0,True,.6);L.safe_spike(s,float(tt),300,False,.6)

def dash_finale(L,s):
    t0=s['t0'];t1=s['t1'];roof=270.;L.rect(s['x0'],s['x1'],roof,300,'finale ceiling')
    # Horizontal green dashes enter near the jump apex. Gravity changes are
    # separate blue-orb inputs after release, eliminating implicit pink-dash
    # state changes. Every held passage exits into a follow-up orb decision.
    score=[(1.25,'dash',.62,141,.17),(5.25,'blue',0,0,0),
           (7.5,'dash',.37,36,.145),(11,'pink',0,0,0),
           (13.5,'dash',.78,84,.18),(18,'pink',0,0,0),
           (20.25,'dash',.46,36,.17),(24.25,'blue',0,0,0),
           (26.75,'blue',0,0,0),(29.25,'tap',0,0,0)]
    events=[];windows=[]
    for beat,kind,hold,catch,delay in score:
        jt=M.snap(t0+beat*BEAT,.035);events.append((jt,'jump',0))
        if kind=='dash':
            # A near-apex entry is less sensitive to where the orb is hit.
            ot=jt+.205;release=M.snap(ot+hold,.028)
            ct=release+delay
            events.extend([(ot,'dash',1704),(release,'release',1704),(ct,'orb',catch)])
            windows.append(dict(start=ot,end=release,id=1704,catch_time=ct,catch_id=catch))
        elif kind in ('blue','pink'):
            events.append((jt+.17,'orb',84 if kind=='blue' else 141))
    events.sort();ei=0;t=t0;y=15.;vy=0.;g=-1;grounded=True;dashing=False;pts=[]
    while t<t1-1e-8:
        if ei<len(events) and events[ei][0]<=t+1e-8:
            et,kind,oid=events[ei];ei+=1
            if kind=='jump':
                assert grounded,('finale airborne takeoff',et,y)
                vy=-g*637.2;grounded=False;L.event(et,'jump','cube')
            elif kind=='dash':
                L.orb(oid,et,y,**{'6':0,'99':0});L.event(et,'dash','cube',orb_id=oid);dashing=True;vy=0.
            elif kind=='release':
                dashing=False;vy=0.;L.event(et,'release','cube',orb_id=oid)
            else:
                L.orb(oid,et,y,**{'6':180 if g>0 else 0,'99':0});L.event(et,'orb','cube',orb_id=oid)
                if oid==84:g*=-1;vy=g*637.2*.4
                else:vy=-g*637.2*(.72 if oid==141 else 1)
                grounded=False
            continue
        to=min(t1,t+1/240,events[ei][0] if ei<len(events) else t1);dt=to-t
        if not dashing and not grounded:
            y+=vy*dt+.5*g*M.G*dt*dt;vy+=g*M.G*dt
            if g<0 and y<=15:y=15.;vy=0.;grounded=True
            if g>0 and y>=roof-15:y=roof-15;vy=0.;grounded=True
        t=to;pts.append([t,y,g,15,'cube'])
    assert g==-1
    L.path(s,pts);s['dash_windows']=windows
    # Reserve an envelope for modest release-momentum uncertainty rather than
    # carving all banks around one zero-velocity assumption. Nominal inputs
    # still need to reach the same follow-up orbs inside their touch radii.
    variants=[]
    for dv in (-50.,50.):
        ei=0;t=t0;y=15.;vy=0.;g=-1;grounded=True;dashing=False
        while t<t1-1e-8:
            if ei<len(events) and events[ei][0]<=t+1e-8:
                et,kind,oid=events[ei];ei+=1
                if kind=='jump':vy=-g*637.2;grounded=False
                elif kind=='dash':dashing=True;vy=0.;grounded=False
                elif kind=='release':dashing=False;vy=-g*dv
                else:
                    if oid==84:g*=-1;vy=g*637.2*.4
                    else:vy=-g*637.2*(.72 if oid==141 else 1)
                    grounded=False
                continue
            to=min(t1,t+1/240,events[ei][0] if ei<len(events) else t1);dt=to-t
            if not dashing and not grounded:
                y+=vy*dt+.5*g*M.G*dt*dt;vy+=g*M.G*dt
                if g<0 and y<=15:y=15.;vy=0.;grounded=True
                if g>0 and y>=roof-15:y=roof-15;vy=0.;grounded=True
            t=to;variants.append([t,y,g,15,'cube'])
    s['dash_robust_points']=variants
    for i,w in enumerate(windows):
        # Broad horizontal tunnel; a constricted release-to-orb transfer is
        # the challenge. Neither the dash entry nor a hidden wall is a choke.
        corridor(L,s,w['start']+.16,w['end']-.095,12,24 if i in (1,3) else 0,30,'held runway '+str(i+1))
        L.gate(s,w['end']+.105,8,4.8,'release timing throat')
        L.gate(s,w['catch_time']+.12,8,4.8,'release then orb catch')
        L.slot(s,w['catch_time']+.24,14,5.5,'follow-up catch window')
        L.phrase(s,(w['start']-t0)/BEAT,(w['catch_time']-t0)/BEAT,'dash and catch '+str(i+1),'hold / release / delayed catch orb')
    dash_jumps={round(w['start']-.205,6) for w in windows}
    for et,kind,oid in events:
        if kind=='jump':
            # Launch challenge is separate from the dash orb's activation box.
            L.gate(s,et+.09,8,7 if round(et,6) in dash_jumps else 4.8,'finale launch')
        elif kind=='orb' and not any(abs(et-w['catch_time'])<1e-6 for w in windows):
            L.gate(s,et+.12,8,4.8,'isolated gravity catch')
    for tt in np.arange(t0+.5,t1-.35,.11):
        L.safe_spike(s,float(tt),0,True,.60,3);L.safe_spike(s,float(tt),roof,False,.60,3)

def new_rails(L,s):
    s['custom_structure']=True
    if s['mode']=='spider':
        M.RAILS['RECALL']=([1.5,2,2.5,5.25,5.875,8.75,9.25,9.875,10.375,13.5,14.125,16.75,17.25,17.75,20.5,21.125,24,24.5,25.125,27.75,28.25,28.875],
                           [246,30,186,75,267,0,207,54,252,15,174,90,237,0,267,42,198,72,249,18,222,0])
        M.rails(L,s)
        controls=[e for e in L.controls if s['t0']<=e['time']<s['t1'] and e['kind']=='flip']
        for j,e in enumerate(controls):
            shoulder=(19+2.1)/s['speed']
            L.gate(s,e['time']-shoulder,8,2.6,'packet entry shoulder');L.gate(s,e['time']+shoulder,8,2.6,'packet exit shoulder')
        for a,b in [(1.5,2.5),(5.25,5.875),(8.75,10.375),(13.5,14.125),(16.75,17.75),(20.5,21.125),(24,25.125),(27.75,28.875)]:
            L.phrase(s,a,b,'teleport packet','two to four flips followed by a long false-rail run')
    else:
        # Automatic transfers use native gravity portals; manual transfers
        # remain grounded ball flips. Long no-click intervals are meaningful.
        M.RAILS['FALSE FLOOR']=([1.5,2.75,5.5,7,9.75,11,13.75,15.5,18.25,19.75,22.5,24,26.75,28.25],
                               [174,60,258,15,210,96,276,42,186,0,246,84,225,30])
        src=inspect.getsource(M.rails)
        src=src.replace("g*=-1;L.event(et,'flip',mode,gravity=g,target=target)","g*=-1\n   auto=(ei-1) in {1,4,7,10,13}\n   if auto:L.portal(11 if g>0 else 10,et,y)\n   else:L.event(et,'flip',mode,gravity=g,target=target)")
        src=src.replace("else:vy=g*637.2*.3;grounded=False","else:vy=0 if auto else g*637.2*.3;grounded=False")
        ns=dict(M.__dict__);exec(src,ns);ns['rails'](L,s)
        for j,e in enumerate([e for e in L.controls if s['t0']<=e['time']<s['t1'] and e['kind']=='flip']):
            L.gate(s,e['time']+.12,8,4.8,'manual departure');L.slot(s,e['time']+.31,22,4.8,'suspended ball catch')
        for beat in (4,8.7,12.75,17,21.5,25.25,28.9):L.gate(s,s['t0']+beat*BEAT,12,5,'rail fork divider')
        L.phrase(s,1.5,29.5,'gravity relay','manual flip / automatic transfer / conditional wall decision')

def robot_steps(L,s):
    s['custom_structure']=True
    M.GROUND['NEEDLEWORK']=[(1.25,75,.27,0,0),(3.5,90,.07,0,0),(4.5,30,.055,0,0),
      (5.5,0,.045,0,0),(7.75,75,.29,0,0),(10.25,60,.065,141,.16),
      (12.5,15,.06,0,0),(13.5,0,.045,0,0),(16,90,.30,0,0),
      (18.25,105,.08,0,0),(19.25,45,.05,0,0),(21,0,.055,0,0),(22.25,0,.06,0,0)]
    M.ground(L,s)
    for j,e in enumerate(s['actions']):
        if e['hold']>.20:
            L.gate(s,e['t']-.095,8,3.6,'robot takeoff restraint')
            L.slot(s,e['t']+.15,40,3.2,'robot rise canopy')
            L.gate(s,e['t']+e['hold']+.09,8,6.0,'long release notch')
            L.slot(s,e['t']+e['hold']+.19,12,6.0,'long release exit')
        else:
            L.gate(s,e['t']-.095,8,3.6,'robot takeoff restraint')
            L.gate(s,e['t']+.105,8,3.8,'short stair lip')
            L.slot(s,e['landing']-.10,18,4.2,'falling stair catch')
            L.gate(s,e['t']+e['hold']+.12,8,7.0,'short release check')
    for a,b,style in [(1.25,3.5,'long climb'),(4.5,5.5,'two clipped stepdowns'),(7.75,10.25,'overhead leap and orb catch'),(12.5,13.5,'late drop pair'),(16,18.25,'held high terrace'),(19.25,22,'descending tap sequence')]:
        L.phrase(s,a,b,style,'variable robot hold / precise release / descending catch')

def force_portals(L):
    ids={10,11,12,13,47,99,101,111,200,201,660,745,1331}
    paths=sorted(L.paths,key=lambda p:p[1]);xs=[p[1] for p in paths];passages=[]
    for o in list(L.objects):
        if int(o['1']) not in ids:continue
        x=float(o['2']);near=paths[max(0,bisect.bisect_left(xs,x-24)-1):bisect.bisect_right(xs,x+24)+1]
        near=[p for p in near if abs(p[1]-x)<=6+p[4]+1];assert near
        lo=max(0,min(p[2]-p[4] for p in near)-(18 if any(s['name']=='UNDERTOW' and s['x0']<x<s['x1'] for s in L.sections) else 6));hi=min(300,max(p[2]+p[4] for p in near)+(18 if any(s['name']=='UNDERTOW' and s['x0']<x<s['x1'] for s in L.sections) else 6));cy=(lo+hi)/2
        sy=max(1,math.ceil((hi-lo+4)/30*100)/100)
        o.update({'3':str(round(cy,5)),'128':'1','129':str(sy),'507':'1','372':'1'})
        L.objects.append(dict(o,**{'129':'1','121':'1','134':'1','13':'0','20':'12'}));o['135']='1'
        L.rect(x-6,x+6,-30,lo,'portal passage lower');L.rect(x-6,x+6,hi,330,'portal passage upper')
        passages.append(dict(id=int(o['1']),x=x,y=cy,a=x-6,b=x+6,lo=lo,hi=hi,scale_y=sy,conservative_core_height=30*sy))
    return passages

def blind_routes(L):
    from simple_layout import cut_rect
    old=json.loads((ROOT/'work/deception-plan.json').read_text())
    branches=[]
    s=next(s for s in L.sections if s['name']=='UNDERTOW')
    # Select a real broad arc with a solid cap, measured from the new path.
    candidates=[]
    for t,y,g,r,mode in s['points'][::12]:
        beat=(t-s['t0'])/BEAT
        if not 8<beat<12.4 or not 45<y<255:continue
        x=M.xt(t)
        if any(o['1'] in ('10','11') and x-22<float(o['2'])<x+194 for o in L.objects):continue
        length=168.;end_x=M.xt(t)+length+4
        end=min(s['points'],key=lambda p:abs(p[0]-(t+(length+4)/s['speed'])))[1]
        caps=[q for q in L.rects if not q.get('group') and q['a']<end_x+15 and q['b']>end_x-15 and q['lo']<y+15 and q['hi']>y-15]
        if caps and abs(end-y)>70:candidates.append((abs(end-y),t,y,end))
    assert candidates,'no measured blind-route site'
    _,t,y,end=max(candidates);x=M.xt(t);length=168.;half=25.
    cuts=[(x+float(dx),x+min(float(dx)+6,length),y-half,y+half) for dx in np.arange(0,length,6)]
    branches.append(dict(section='UNDERTOW',rule='continue level instead of braking into the arch',t=t,x=x,y=y,length=length,half_width=half,end_x=x+length+4,end_y=y,correct_y_at_end=end,cuts=cuts))
    cuts=[q for b in branches for q in b['cuts']]
    for q in cuts:L.rects=[rr for r in L.rects for rr in (cut_rect(r,q) if not r.get('group') else [r])]
    wall_groups={str(m['wall']) for m in L.random_locks}
    L.objects=[o for o in L.objects if o['1']!='1' and not(o['1']=='211' and o.get('57') in wall_groups)];rectangles=L.rects;L.rects=[]
    for r in rectangles:L.rect(r['a'],r['b'],r['lo'],r['hi'],r['kind'],r.get('group'))
    removed=[]
    for o in list(L.objects):
        if o['1']!='8':continue
        x,y=float(o['2']),float(o['3']);r=15*float(o.get('32',1))
        if any(x-r<q[1] and x+r>q[0] and y-r<q[3] and y+r>q[2] for q in cuts):L.objects.remove(o);removed.append((x,y))
    L.spikes=[s for s in L.spikes if not any(abs(s['x']-x)<.001 and abs(s['y']-y)<.001 for x,y in removed)]
    return branches

def build():
    L=PhraseLevel()
    for orig in M.SECTIONS:
        s=dict(orig);a,b=s['x0'],s['x1'];L.rect(a,b,-30,0,'foundation');L.rect(a,b,300,330,'roof')
        if s['index']:
            L.portal(99,s['t0']+.025);L.portal({'cube':12,'robot':745,'ball':47,'wave':660,'ufo':111,'ship':13,'spider':1331}[s['mode']],s['t0']+.09)
        if not s['index'] or s['speed_index']!=M.SECTIONS[s['index']-1]['speed_index']:L.portal(200 if not s['speed_index'] else 201,s['t0'])
        if s['name']=='BLINDFOLD':wave_notes(L,s)
        elif s['name']=='FAULTLINE':wave_notes(L,s)
        elif s['name']=='PARALLAX':B.flight(L,s)
        elif s['mode']=='ship':ship_notes(L,s)
        elif s['name']=='OFFBEAT':M.flight(L,s)
        elif s['mode']=='ufo':ufo_latches(L,s)
        elif s['name']=='LAST WORD':new_finale(L,s)
        elif s['mode']=='spider':spider_notes(L,s)
        elif s['name']=='FALSE FLOOR':new_rails(L,s)
        elif s['name']=='NEEDLEWORK':robot_steps(L,s)
        elif s['name'] in M.GROUND:M.ground(L,s)
        elif s['name']=='CROSSCODE':M.crosscode(L,s)
        elif s['mode'] in ('ball','spider'):M.rails(L,s)
        else:B.flight(L,s)
        cg=900+s['index'];L.obj(1764,a+70,150,**{'57':cg,'121':1,'134':1,'135':1,'20':5})
        L.obj(2925,a+46 if s['index'] else 0,-420,**{'111':1,'112':1,'113':10,'114':.5,'370':1,'20':5})
        L.obj(1913,a+46 if s['index'] else 0,-420,**{'371':.82,'10':0,'20':5})
        L.obj(1914,a+47 if s['index'] else 1,-420,**{'71':cg,'101':2,'155':1,'36':1,'10':0,'20':5})
        L.label(s['name'],a+170,284,.16,6);L.sections.append(s)
    L.obj(3600,M.xt(M.END),150,**{'20':5})
    branches=blind_routes(L);passages=force_portals(L)
    for o in L.objects:
        if o['1'] in ('36','84','141','1704','1751'):o.update({'57':'8500','507':'1','372':'1'})
    L.obj(1007,0,-600,**{'51':8500,'35':.13,'10':0,'20':5})
    H,_=load(str(ROOT/'work/v8-nocturne-base.level'));header=parse_header(H)
    channels={int(c['6']):c for c in parse_ks38(header['kS38'])}
    # Back to the accepted nearly black structural palette. No coloured trim.
    for cid in (7,14,15,16,17):
        rgb=(34,36,30) if cid==7 else (12,14,12)
        channels[cid]={'1':str(rgb[0]),'2':str(rgb[1]),'3':str(rgb[2]),'4':'-1','5':'0','6':str(cid),'7':'1','15':'1','18':'0','8':'1'}
    header['kA14']='~'.join(str(q) for n,t in enumerate(MAJOR_TIMES) if t<M.END for q in (round(float(t),5),1 if n%4==0 else .6))+'~'
    header['kS38']='|'.join('_'.join(f'{k}_{v}' for k,v in c.items()) for c in channels.values())+'|'
    ser=lambda o:','.join(f'{k},{v}' for k,v in o.items());raw=';'.join([ser(header)]+[ser(o) for o in L.objects])+';'
    f=read_gmd(ROOT/'outputs/v8-1573528-restored.gmd');f['k4']=('s',compress(raw));f['k48']=('i',str(len(L.objects)));f['k14']=('f',False)
    write_gmd(ROOT/'work/variety-base.gmd',f);(ROOT/'work/v8-variety-base.level').write_text(raw)
    P=dict(sections=L.sections,controls=sorted(L.controls,key=lambda e:e['time']),paths=L.paths,rectangles=L.rects,spikes=L.spikes,orbs=L.orbs,memories=L.memories,random_locks=L.random_locks,gates=L.gates,moves=[],timing_features=L.timing_features,fakeouts=[],phrases=L.phrases,portal_passages=passages,branches=[],speed_schedule=[[s['t0'],s['speed']] for s in L.sections],end_time=M.END,end_x=M.xt(M.END),bpm=131,song=1573528,phase=M.PHASE,objects=len(L.objects),slow_percent=100*sum(s['t1']-s['t0'] for s in L.sections if not s['speed_index'])/M.END,validation_limit='Independent approximate physics and route checks; native completion and difficulty unverified.')
    P['branches']=branches
    P['sync_analysis']=AUDIO_MAP
    P['bpm']=AUDIO_MAP['refined_bpm']
    (ROOT/'work/variety-plan.json').write_text(json.dumps(P,separators=(',',':')))
    print(json.dumps(dict(objects=len(L.objects),inputs=len(L.controls),random_locks=len(L.random_locks),phrases=len(L.phrases))))

from sync_sections import *
from variety_sections import ufo_latches
if __name__=='__main__':build()
