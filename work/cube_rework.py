"""Authored cube phrases; positions use the existing 170 BPM song lattice.
No random obstacle generation. Model checking lives in a separate module.
"""
import math

def build_cube():
    objects=[];plans=[];platforms=[];inputs=[];hazards=[];orbs=[]
    B=251.16*60/170
    def obj(oid,x,y,**kw):
        d={'1':oid,'2':round(x,6),'3':round(y,6),'20':0,'64':1,'67':1}
        d.update(kw);objects.append({str(k):str(v) for k,v in d.items()});return objects[-1]
    def platform(a,b,top,bottom=0):
        # Full-size native solid blocks plus fractional end pieces. All faces
        # have a collision box that coincides with the decorated silhouette.
        n=math.ceil((b-a)/30);w=(b-a)/n
        m=math.ceil((top-bottom)/30);h=(top-bottom)/m
        for i in range(n):
            for j in range(m):
                obj(1,a+(i+.5)*w,bottom+(j+.5)*h,**{'128':w/30,'129':h/30,'21':1,'22':2,'96':1})
        platforms.append([a,b,bottom,top])
    def spike(x,y=0):
        obj(8,x,y+15,**{'21':3});hazards.append([x,y])
    def orb(oid,x,y):
        obj(oid,x,y,**{'21':1004,'22':1004});orbs.append([oid,x,y])
    def click(x,kind='jump'):
        inputs.append({'x':x,'action':kind})
    def phrase(j,kind):
        begin=len(inputs)
        if kind=='terraces':
            click(j);platform(j+50,j+205,30)
            click(j+2*B);platform(j+2*B+50,j+2*B+205,60)
        elif kind=='yellow_drop_pink':
            click(j);orb(36,j+60,82);click(j+60,'yellow')
            for x in [j+70,j+100]:spike(x)
            platform(j+137,j+285,60)
            orb(141,j+330,65);click(j+330,'pink')
            for x in [j+365,j+395]:spike(x)
        elif kind=='step_down':
            click(j);platform(j+50,j+177,30)
            click(j+148);platform(j+198,j+315,60)
            platform(j+325,j+470,30)
            click(j+445);spike(j+505)
        elif kind=='low_rebound':
            click(j);spike(j+43)
            orb(141,j+80,70);click(j+80,'pink')
            spike(j+126);platform(j+164,j+282,30)
            platform(j+85,j+260,165,135)
            click(j+400);spike(j+444)
        elif kind=='double_orb':
            click(j);orb(36,j+60,82);click(j+60,'yellow')
            orb(141,j+136,136);click(j+136,'pink')
            for x in [j+70,j+100,j+130,j+160]:spike(x)
            platform(j+212,j+370,60)
        elif kind=='three_rises':
            for i in range(3):
                click(j+i*133);platform(j+i*133+50,j+i*133+151,30*(i+1))
            platform(j+427,j+556,30)
        elif kind=='vault_return':
            click(j);platform(j+50,j+185,30)
            click(j+160);orb(36,j+220,112);click(j+220,'yellow')
            for x in [j+222,j+252,j+282]:spike(x)
            platform(j+304,j+460,60)
        elif kind=='portal_setup':
            click(j);spike(j+45)
            orb(141,j+70,78);click(j+70,'pink')
            platform(j+145,j+235,30)
        plans.append({'start_x':j,'name':kind,'inputs':inputs[begin:]})
    for i,kind in enumerate(['terraces','yellow_drop_pink','step_down','low_rebound','double_orb','three_rises','vault_return','portal_setup']):
        phrase(251.16*(.134+(3+8*i)*60/170),kind)
    phrase(7680,'step_down')
    phrase(8260,'double_orb')
    return objects,{'phrases':plans,'platforms':platforms,'spikes':hazards,'orbs':orbs,
        'inputs':sorted(inputs,key=lambda q:q['x']),'nominal_speed':251.16,
        'scope':[[0,5680],[7570,8830]],'wave_route_changed':False}
