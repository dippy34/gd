"""Independent 240 Hz ballistic clearance model, not the native game engine.

Uses full 30u cube AABB against blocks and conservative 24u AABB against full
spike triangles. Orb impulse estimates are documented in the revision notes.
"""
import json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
plan=json.loads((ROOT/'work/cube-plan.json').read_text())
def simulate(phrase,vjump=604.8,gravity=2727.35,offset=0):
    j=phrase['start_x'];end=phrase.get('end_x',min(j+690,5700 if j<5700 else 8880))
    platforms=[p for p in plan['platforms'] if j-100<p[1] and p[0]<end+30]
    spikes=[p for p in plan['spikes'] if j-100<p[0]<end+30]
    orbs=[p for p in plan['orbs'] if j-100<p[1]<end+30]
    clicks=[dict(a,x=a['x']+offset) for a in phrase['inputs']]
    x=j-70;y=15;v=0;grounded=True;dt=1/240;dx=251.16*dt
    errors=[];path=[];triggered=[];ci=0;landings=[]
    while x<end:
        prevy=y;prevx=x
        if ci<len(clicks) and x>=clicks[ci]['x']:
            a=clicks[ci];ci+=1
            if a['action']=='jump':
                if not grounded:errors.append(['airborne_jump',round(x,3),round(y,3)])
                else:v=vjump;grounded=False
            else:
                oid=36 if a['action']=='yellow' else 141
                near=[o for o in orbs if o[0]==oid and math.hypot(x-o[1],y-o[2])<=32]
                if not near:errors.append(['missed_orb',round(x,3),round(y,3)])
                else:
                    v=590.85 if oid==36 else 418.5;grounded=False;triggered.append(near[0])
        if not grounded:v-=gravity*dt
        y+=v*dt;x+=dx
        landed=False
        for a,b,bottom,top in platforms:
            if x+15<=a or x-15>=b:continue
            if prevy-15>=top-.1 and y-15<=top and v<=0:
                y=top+15;v=0;landed=True
                if not grounded:landings.append([round(x,2),top])
            elif y+14.9>bottom and y-14.9<top:
                errors.append(['block_collision',round(x,3),round(y,3),[a,b,bottom,top]])
                return {'ok':False,'errors':errors,'path':path}
        if y<15:y=15;v=0;landed=True
        if y<=15+.01:landed=True
        grounded=landed
        for sx,sy in spikes:
            # Maximum triangle height below the player's 24u-wide inner box.
            horizontal=max(0,abs(x-sx)-12)
            h=30-2*horizontal
            if horizontal<15 and y-12<sy+h and y+12>sy:
                errors.append(['spike_collision',round(x,3),round(y,3),sx])
                return {'ok':False,'errors':errors,'path':path}
        if len(path)==0 or x-path[-1][0]>3:path.append([round(x,3),round(y,3)])
    return {'ok':not errors,'errors':errors,'path':path,'landings':landings,'orb_hits':len(triggered)}

if __name__=='__main__':
    nominal=[];robust=[]
    for phrase in [dict(start_x=70,end_x=5680,name='intro continuous',inputs=[a for a in plan['inputs'] if a['x']<5680]),dict(start_x=7640,end_x=8880,name='build continuous',inputs=[a for a in plan['inputs'] if a['x']>7570])]:
        r=simulate(phrase);nominal.append({'name':phrase['name'],'start_x':phrase['start_x'],**r})
        valid=[]
        for delta in range(-10,11,2):
            if simulate(phrase,offset=delta)['ok']:valid.append(delta)
        tests=[]
        for v,g in [(585,2727.35),(625,2900),(604.8,2850),(604.8,2650)]:
            passes=[d for d in range(-16,17,2) if simulate(phrase,v,g,d)['ok']]
            tests.append({'jump':v,'gravity':g,'valid_offsets':passes})
        robust.append({'name':phrase['name'],'nominal_valid_offsets':valid,'variants':tests})
    report={'native_physics':False,'nominal':nominal,'sensitivity':robust}
    (ROOT/'work/cube-clearance.json').write_text(json.dumps(report,indent=2))
    for r,s in zip(nominal,robust):print(r['name'],round(r['start_x']),r['ok'],r['errors'][:2],s['nominal_valid_offsets'],[bool(t['valid_offsets']) for t in s['variants']])
    sys.exit(0 if all(r['ok'] for r in nominal) else 1)
