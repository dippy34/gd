"""OBSIDIAN CHOIR // AURORA -- designed decoration for the V6 layout.

Rules this build follows:
  * one clear idea per screen, and most of the frame stays black
  * every decorative object sits BEHIND the gameplay (z <= -1) apart from a few
    deliberate foreground pieces in the open cube parts
  * the corridor is the hero: near-black fill, neon outline, and a soft halo
    traced along its real silhouette
  * shapes are placed on the beat, not scattered
Only object ids attested in the reference levels on disk are used.
"""
import sys, math, random, json, time
sys.path.insert(0, '.')
from kocmoc_terrain import Terrain
from gmd import compress, write_gmd
from gdparse import parse_header, parse_ks38
import outline as OL

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 7
rng = random.Random(SEED)
BEAT = 60 / 170.0
PHASE = 0.134
SPEEDS = [(0, 251.16), (22.72223529411765, 311.58), (28.369294117647062, 251.16),
          (34.01635294117647, 468.0), (56.60458823529412, 251.16)]
def xt(t):
    x = 0.0
    for i, (st, v) in enumerate(SPEEDS):
        stop = SPEEDS[i + 1][0] if i + 1 < len(SPEEDS) else t
        if t > st: x += (min(t, stop) - st) * v
    return x
T_END = 58.6

# ------------------------------------------------------------------ channels
NEON, FILL, HAZARD, LABEL = 1, 2, 3, 4        # the layout's own channels
VOID, HAZE, FAR, SHAFT, STAR, BLOOM, VIGN, FLASH, RIM, DEEP, NODE, SILHO = range(20, 32)
PALETTE = [
    (VOID,  (0, 0, 0),       0, 1.0),   (HAZE,  (10, 15, 28),    0, 1.0),
    (FAR,   (38, 60, 102),   1, 1.0),   (SHAFT, (52, 92, 148),   1, 1.0),
    (STAR,  (255, 255, 255), 1, 1.0),   (BLOOM, (120, 190, 255), 1, 1.0),
    (VIGN,  (0, 0, 0),       0, 0.75),  (FLASH, (255, 255, 255), 1, 1.0),
    (RIM,   (170, 214, 255), 1, 1.0),   (DEEP,  (9, 14, 32),     0, 1.0),
    (NODE,  (215, 238, 255), 1, 1.0),   (SILHO, (3, 4, 8),       0, 1.0),
]
LAYOUT_CH = [(NEON, (170, 215, 255), 0, 1.0), (FILL, (4, 5, 9), 0, 1.0),
             (HAZARD, (255, 255, 255), 0, 1.0), (LABEL, (120, 150, 190), 0, 1.0)]

SECTIONS = [('intro', 0, 5707), ('teaser', 5707, 7466), ('build', 7466, 8885),
            ('drop', 8885, 19456), ('outro', 19456, 20500)]
def section_at(x):
    for s in SECTIONS:
        if s[1] <= x < s[2]: return s[0]
    return 'outro'

# ------------------------------------------------------------------- emitter
objs = []
_g = [200]
def group():
    _g[0] += 1; return _g[0]

def add(oid, x, y, **p):
    d = {'1': str(oid), '2': round(x, 3), '3': round(y, 3)}
    d.update({k.lstrip('p'): v for k, v in p.items()})
    objs.append(d); return d

def deco(oid, x, y, color, *, z=-1, zo=0, sx=1.0, sy=None, rot=0, val=None,
         group_id=0, ldm=False):
    p = dict(p21=color, p22=color, p20=4, p24=z, p25=zo, p64=1, p67=1, p121=1,
             p134=1, p128=round(sx, 4), p129=round(sy if sy is not None else sx, 4))
    if rot: p['p6'] = round(rot, 2)
    if val is not None:
        p['p41'] = 1; p['p43'] = f"0a1a{round(max(.02, val), 3)}a0a0"
        p['p42'] = 1; p['p44'] = p['p43']
    if group_id: p['p57'] = group_id
    if ldm: p['p103'] = 1
    return add(oid, x, y, **p)

def colour(x, ch, rgb, dur=1.0, y=-520, op=1.0):
    objs.append({'1': '899', '2': round(x, 3), '3': y, '23': ch, '7': rgb[0],
                 '8': rgb[1], '9': rgb[2], '10': dur, '35': op, '20': 5})
def pulse(x, ch, rgb, fi=0.0, hold=0.04, fo=0.26, y=-560):
    objs.append({'1': '1006', '2': round(x, 3), '3': y, '7': rgb[0], '8': rgb[1],
                 '9': rgb[2], '45': fi, '46': hold, '47': fo, '48': 0, '52': 0,
                 '51': ch, '20': 5})
def move(x, g, dx, dy, dur, y=-600, easing=2):
    objs.append({'1': '901', '2': round(x, 3), '3': y, '51': g, '28': dx, '29': dy,
                 '10': dur, '30': easing, '20': 5})
def rotate(x, g, centre, turns=1, dur=60, y=-640):
    objs.append({'1': '1346', '2': round(x, 3), '3': y, '51': g, '71': centre,
                 '10': dur, '68': 0, '69': turns, '20': 5})

# ids, all attested in the reference levels on disk
ORB, DOT, STARSPR, LINE, THINLINE = 1888, 1764, 3625, 1754, 1753
GRAD_V, GRAD_C, GRAD_D = 1292, 1011, 1272
RINGSEG = (997, 998, 999)
SPIRAL = (1058, 1060, 1061)
BLOCK, CLOUD = 1, 129

# ------------------------------------------------------------- building blocks
def ring(cx, cy, r, color, *, n=None, size=1.1, val=.5, z=-3, zo=-200,
         squash=1.0, arc=math.tau, a0=0.0, group_id=0, ldm=True):
    # spacing well under the orb radius, so the orbs fuse into a continuous line
    n = n or max(40, int(arc * r / 6.0))
    for i in range(n):
        a = a0 + arc * i / n
        deco(ORB, cx + math.cos(a) * r, cy + math.sin(a) * r * squash, color,
             z=z, zo=zo, sx=size * rng.uniform(.9, 1.12), val=val, group_id=group_id,
             ldm=ldm and i % 2 == 1)
    return n

def shaft(x, y, ang, length, color, *, width=1.8, val=.28, z=-3, zo=-260,
          spacing=11.0, taper=True, ldm=True):
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    n = max(2, int(length / spacing)); k = 0
    for i in range(n + 1):
        t = i / n
        w = width * ((1 - t * .62) if taper else 1.0) + 1.15
        deco(ORB, x + ca * length * t, y + sa * length * t, color,
             z=z, zo=zo, sx=w, val=val * (1 - .5 * t), ldm=ldm)
        k += 1
    return k

def disc(cx, cy, r, color, *, val=.30, z=-5, zo=-600, layers=6):
    for i in range(layers):
        t = i / max(1, layers - 1)
        deco(ORB, cx, cy, color, z=z, zo=zo - i, sx=r / 20 * (0.45 + t * 1.15),
             val=val * (1 - t * .62), ldm=i > 2)
    return layers

def rim_arc(cx, cy, r, color, *, arc=math.tau, a0=0.0, z=-3, zo=-140,
            thick=1.5, val=.85, squash=1.0, seg=90):
    """A hard-edged arc drawn as short tangent lines -- the one crisp element in
    a frame that is otherwise all bloom."""
    n = 0
    for i in range(seg):
        a = a0 + arc * (i + .5) / seg
        step = arc * r / seg
        deco(LINE, cx + math.cos(a) * r, cy + math.sin(a) * r * squash, color,
             z=z, zo=zo, sx=(step * 1.5) / 30, sy=thick,
             rot=math.degrees(a) + 90, val=val, ldm=i % 2 == 1)
        n += 1
    return n

def silhouette_disc(cx, cy, r, *, z=-3, zo=-150):
    """A hard black circle that eats the light behind it -- gives the soft glows
    an edge to read against."""
    n = max(18, int(r / 5))
    for i in range(n):
        a = math.tau * i / n
        deco(BLOCK, cx + math.cos(a) * r * .55, cy + math.sin(a) * r * .55, SILHO,
             z=z, zo=zo, sx=r / 34, rot=math.degrees(a), val=1.0, ldm=True)
    deco(BLOCK, cx, cy, SILHO, z=z, zo=zo, sx=r / 22, val=1.0)
    return n + 1

def bars(x0, x1, ybase, color, *, up=True, z=-3, zo=-180, seed_shift=0.0,
         hmin=40, hmax=280):
    """A skyline of thin slabs -- black mass with a lit top edge."""
    n = 0; x = x0
    while x < x1:
        w = rng.uniform(16, 52)
        h = (hmin + (hmax - hmin) * abs(math.sin(x * 0.0021 + seed_shift)) ** 2) * rng.uniform(.6, 1.2)
        d = 1 if up else -1
        deco(BLOCK, x + w / 2, ybase + d * h / 2, VOID, z=z, zo=zo,
             sx=w / 30, sy=h / 30, val=1.0, ldm=False); n += 1
        deco(LINE, x + w / 2, ybase + d * h, color, z=z, zo=zo + 4,
             sx=w / 30, sy=1.4, val=.55, ldm=True); n += 1
        for q in range(int(w / 12)):
            deco(ORB, x + 6 + q * 12, ybase + d * h, color, z=z, zo=zo + 3,
                 sx=.8, val=.16, ldm=True); n += 1
        if rng.random() < .30:
            deco(ORB, x + w / 2, ybase + d * h, color, z=z, zo=zo + 3,
                 sx=rng.uniform(.7, 1.5), val=.35, ldm=True); n += 1
        x += w + rng.uniform(26, 90)
    return n

def starfield(x0, x1, y0, y1, count, *, streak=0.0):
    n = 0
    for _ in range(count):
        x = rng.uniform(x0, x1); y = rng.uniform(y0, y1)
        b = rng.random()
        if streak > 0 and rng.random() < .45:
            deco(LINE, x, y, STAR, z=-1, zo=-40, sx=rng.uniform(.6, 2.4) * streak,
                 sy=rng.uniform(.25, .8), val=rng.uniform(.20, .75), ldm=True); n += 1
        elif b < .12:
            deco(STARSPR, x, y, STAR, z=-1, zo=-38, sx=rng.uniform(.05, .11),
                 val=rng.uniform(.5, 1.1)); n += 1
        elif b < .40:
            deco(ORB, x, y, STAR, z=-1, zo=-42, sx=rng.uniform(.10, .34),
                 val=rng.uniform(.25, .8), ldm=rng.random() < .5); n += 1
        else:
            deco(DOT, x, y, STAR, z=-1, zo=-44, sx=rng.uniform(.06, .22),
                 val=rng.uniform(.18, .7), ldm=True); n += 1
    return n

def haze_band(x0, x1, y, height, color, val=.5, z=-5, zo=-900):
    n = 0; x = x0
    while x < x1:
        w = 240
        deco(GRAD_V, x + w / 2, y, color, z=z, zo=zo, sx=w / 15, sy=height / 10,
             val=val, ldm=True); n += 1
        x += w * .92
    return n

def vignette(x0, x1):
    n = 0; x = x0
    while x < x1:
        w = 320
        deco(GRAD_V, x + w / 2, 640, VIGN, z=7, zo=500, sx=w / 15, sy=26, rot=180,
             val=1.0, ldm=True)
        deco(GRAD_V, x + w / 2, -330, VIGN, z=7, zo=500, sx=w / 15, sy=26,
             val=1.0, ldm=True)
        n += 2; x += w * .9
    return n

# ================================================================ composition
def build():
    t0 = time.time()
    T = Terrain()
    import cam, effects
    cam_y = cam.make(T)
    stats = {}
    def mark(k, n): stats[k] = stats.get(k, 0) + (n or 0)
    ctx = dict(deco=deco, group=group, rotate=rotate, move=move, colour=colour,
               pulse=pulse, rng=rng, ORB=ORB, DOT=DOT, STARSPR=STARSPR, LINE=LINE,
               GRAD=GRAD_V, BLOCK=BLOCK, SPIRAL=SPIRAL)
    FX = effects.build(ctx)
    PAL = (NODE, RIM, SHAFT, VOID)          # hot / rim / dim / core

    # ---- 1. the corridor halo, two layers -------------------------------
    segs = OL.segments(T.cells, tol=11.0, min_len=10.0)
    n = 0
    for (x0, y0, x1, y1) in segs:
        L = math.hypot(x1 - x0, y1 - y0)
        sec = section_at((x0 + x1) / 2)
        wave = sec in ('teaser', 'drop')
        for layer, (sp, size, val, zo) in enumerate(
                [(17.0 if wave else 20.0, 1.05 if wave else 1.25, .26 if wave else .30, -30),
                 (46.0, 2.6 if wave else 2.2, .055, -70)]):
            steps = max(1, int(L / sp))
            for i in range(steps + 1):
                t = i / steps
                deco(ORB, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, BLOOM,
                     z=-1, zo=zo, sx=size * rng.uniform(.85, 1.15),
                     val=val * rng.uniform(.75, 1.25), ldm=(layer == 1 or i % 3 == 2))
                n += 1
        deco(ORB, x1, y1, NODE, z=-1, zo=-24, sx=1.5, val=.42); n += 1
    mark('halo', n)
    print(f"  halo: {n} objects on {len(segs)} silhouette runs  [{time.time()-t0:.0f}s]")

    # ---- 2. continuous background, anchored to the camera ----------------
    n = 0
    x = -360.0
    while x < 20560:
        cy = cam_y(x)
        w = 150.0
        # a dark navy floor to the frame, at the bottom of what is actually seen
        deco(GRAD_V, x + w / 2, cy - 178, DEEP, z=-5, zo=-980, sx=w / 15, sy=11,
             val=.22, ldm=True); n += 1
        # starfield, built the way KOCMOC builds one: tiny bright star sprites
        # at scale ~0.05 packed into tight clumps (its own stars sit a median of
        # 3.2 units apart), not an even scatter of soft blobs
        sec = section_at(x)
        for _ in range(rng.randint(1, 3)):
            ccx = x + rng.uniform(0, w); ccy = cy + rng.uniform(-176, 176)
            cr = rng.uniform(16, 62)
            for _ in range(rng.randint(7, 20)):
                a = rng.uniform(0, math.tau); d = cr * math.sqrt(rng.random())
                deco(STARSPR, ccx + math.cos(a) * d, ccy + math.sin(a) * d * rng.uniform(.6, 1.3),
                     STAR, z=-1, zo=-38, sx=rng.uniform(.038, .105),
                     val=rng.uniform(.55, 1.15), ldm=rng.random() < .45)
                n += 1
        for _ in range(rng.randint(3, 7)):           # loose stars between clumps
            deco(STARSPR, x + rng.uniform(0, w), cy + rng.uniform(-180, 180), STAR,
                 z=-1, zo=-38, sx=rng.uniform(.035, .09),
                 val=rng.uniform(.4, 1.0), ldm=rng.random() < .5); n += 1
        for _ in range(rng.randint(2, 4)):           # the few bright ones, with a halo
            bx = x + rng.uniform(0, w); by = cy + rng.uniform(-176, 176)
            deco(ORB, bx, by, STAR, z=-1, zo=-42, sx=rng.uniform(.30, .85),
                 val=rng.uniform(.35, .75)); n += 1
            deco(STARSPR, bx, by, STAR, z=-1, zo=-36, sx=rng.uniform(.09, .17),
                 val=1.15); n += 1
        for _ in range(rng.randint(3, 7)):           # dim dust, pure texture
            deco(DOT, x + rng.uniform(0, w), cy + rng.uniform(-185, 185), STAR,
                 z=-3, zo=-300, sx=rng.uniform(.35, 1.5),
                 val=rng.uniform(.025, .085), ldm=True); n += 1
        if sec in ('drop', 'teaser'):                # speed streaks
            for _ in range(rng.randint(2, 5)):
                deco(LINE, x + rng.uniform(0, w), cy + rng.uniform(-180, 180), STAR,
                     z=-1, zo=-40, sx=rng.uniform(.8, 3.0), sy=rng.uniform(.22, .55),
                     val=rng.uniform(.25, .8), ldm=True); n += 1
        # one slow far layer for parallax
        if rng.random() < .45:
            g = group()
            for _ in range(rng.randint(6, 14)):
                deco(STARSPR, x + rng.uniform(0, w), cy + rng.uniform(-185, 185), STAR,
                     z=-5, zo=-940, sx=rng.uniform(.03, .07),
                     val=rng.uniform(.18, .5), group_id=g, ldm=True); n += 1
            move(max(0, x - 400), g, rng.uniform(-60, 60), rng.uniform(-26, 26),
                 rng.uniform(10, 24))
        x += w
    mark('stars', n)
    print(f"  background + stars: {n}  [{time.time()-t0:.0f}s]")

    # ---- 3. authored set-pieces ------------------------------------------
    def C(px): return cam_y(px)

    # intro: a planet low, a city of towers, an aurora, a first black hole
    mark('sky', disc(520, C(520) - 250, 480, FAR, val=.52, z=-5, zo=-640))
    mark('sky', FX['ring'](520, C(520) - 250, 470, NODE, size=1.4, val=.40,
                           z=-3, zo=-160, spacing=5))
    mark('sky', FX['arc_line'](520, C(520) - 250, 470, NODE, arc=math.pi * .8,
                               a0=math.pi * .10, val=.92, z=-3, zo=-150, seg=150))
    for i in range(5):
        mark('sky', shaft(1150 - i * 90, C(1150) + 190, -26 + i * 1.6, 700, SHAFT,
                          width=2.4, val=.15))
    mark('sky', bars(760, 2000, -60, RIM, up=True, zo=-260, hmin=55, hmax=190))
    mark('sky', FX['aurora'](250, 2600, C(1400) + 105, (RIM, SHAFT, FAR), bands=4, amp=52))
    mark('sky', FX['constellation'](2250, C(2250) + 40, NODE, spread=230))
    mark('sky', FX['orbiters'](2750, C(2750) + 55, PAL))
    mark('sky', FX['black_hole'](3350, C(3350) + 30, 150, PAL, intensity=.85))
    mark('sky', bars(3750, 4900, -60, RIM, up=True, zo=-250, seed_shift=1.4,
                     hmin=45, hmax=175))
    for i in range(5):
        mark('sky', shaft(4050 + i * 100, C(4050) + 200, -36 - i * 1.4, 720, SHAFT,
                          width=2.2, val=.17))
    mark('sky', FX['grid_horizon'](4400, C(4400), SHAFT, w=1200))
    mark('sky', disc(5150, C(5150) + 120, 300, FAR, val=.40, z=-5, zo=-660))
    mark('sky', FX['ring'](5150, C(5150) + 120, 250, RIM, size=1.3, val=.34,
                           z=-3, zo=-300, spacing=6))
    mark('sky', FX['comet'](5450, C(5450) + 120, PAL))
    mark('sky', FX['constellation'](900, C(900) - 20, NODE, spread=200, stars=7))
    mark('sky', FX['orbiters'](4750, C(4750) - 30, PAL))
    mark('sky', FX['eclipse'](4300, C(4300) + 30, 120, PAL))
    mark('sky', FX['pulsar'](1150, C(1150) + 30, PAL))

    # teaser: the corridor arrives, everything turns to 45 degrees
    mark('sky', FX['warp_tunnel'](5820, C(5820), PAL, rings=8, rmax=440))
    for i in range(6):
        mark('sky', shaft(6100 + i * 95, C(6100) + 210, -45, 780, SHAFT,
                          width=1.9, val=.20))
    mark('sky', FX['aurora'](6250, 7500, C(6800) - 20, (RIM, SHAFT), bands=3, amp=64))
    mark('sky', FX['orbiters'](7050, C(7050) + 30, PAL))
    mark('sky', FX['black_hole'](6500, C(6500) - 10, 130, PAL, intensity=.9))
    mark('sky', FX['constellation'](6250, C(6250) + 40, NODE, spread=200, stars=8))

    # build: the darkest stretch, one growing black hole and lightning
    mark('sky', bars(7500, 8880, -60, RIM, up=True, zo=-250, seed_shift=5.0,
                     hmin=60, hmax=215))
    mark('sky', FX['black_hole'](8180, C(8180) + 20, 210, PAL, intensity=.7))
    mark('sky', FX['lightning'](7760, C(7760), RIM, length=340))
    mark('sky', FX['lightning'](8560, C(8560), RIM, length=380))
    mark('sky', FX['orbiters'](8650, C(8650) - 40, PAL))
    mark('sky', FX['eclipse'](8400, C(8400) + 20, 150, PAL))
    for i in range(5):
        mark('sky', shaft(7620 + i * 140, C(7620) + 200, -33 - i * 1.2, 760, SHAFT,
                          width=2.0, val=.15))

    # ---- 4. the drop: one event per phrase, tightening ---------------------
    mark('drop', FX['shockwave'](8990, C(8990), (FLASH, NODE, RIM, VOID), n_rings=5))
    mark('drop', disc(8990, C(8990), 620, FAR, val=.24, z=-5, zo=-760))

    # the centrepiece: a hole big enough to silhouette the corridor, on the last
    # wave stretch, where the palette has gone gold
    BH_X = 17750.0
    # centre it on the average camera height over the stretch it is on screen,
    # so it does not slide out of frame as the corridor climbs and falls
    BH_Y = sum(C(BH_X + d) for d in range(-500, 501, 50)) / 21.0
    mark('drop', FX['great_black_hole'](BH_X, BH_Y, 150, (FLASH, NODE, RIM, VOID),
                                        front=.50))
    # the corridor steps back so the hole can be the brightest thing on screen,
    # then comes back up once it has passed
    for (tt, ch, rgb, d) in [(51.55, NEON,  (150, 118,  76), 1.1),
                             (51.55, BLOOM, (104,  84,  56), 1.1),
                             (51.55, SHAFT, (120, 100,  70), 1.1),
                             (51.55, FLASH, (255, 252, 244), .6),
                             (51.55, NODE,  (255, 244, 224), .6),
                             (51.55, RIM,   (236, 214, 176), .6),
                             (55.30, NEON,  (255, 232, 192), 1.4),
                             (55.30, BLOOM, (255, 222, 184), 1.4),
                             (55.30, SHAFT, (170, 128,  92), 1.4)]:
        colour(xt(tt), ch, rgb, dur=d)

    kinds = ['blackhole', 'eclipse', 'warp', 'pulsar', 'planet', 'constellation',
             'lightning', 'comet', 'orbiters', 'rift', 'blackhole', 'shock',
             'grid', 'aurora', 'eclipse', 'fan']
    tcur = 34.01635294117647 + 8 * BEAT
    idx = 0; last = None
    while tcur < 56.6:
        x = xt(tcur); cy = C(x + 300)
        if abs(x + 340 - BH_X) < 1250:       # give the centrepiece room
            tcur += (8 * BEAT) if tcur < 50.5 else (4 * BEAT)
            continue
        pool = [k for k in kinds if k != last]
        kind = pool[(idx * 7 + SEED) % len(pool)]
        last = kind; idx += 1
        if kind == 'blackhole':
            mark('drop', FX['black_hole'](x + 320, cy + rng.choice([-30, 20, 60]),
                                          rng.uniform(120, 230), PAL,
                                          intensity=rng.uniform(.8, 1.15)))
        elif kind == 'aurora':
            mark('drop', FX['aurora'](x - 100, x + 1300, cy + rng.choice([-120, 120]),
                                      (RIM, SHAFT, FAR), bands=4, amp=rng.uniform(50, 90)))
        elif kind == 'warp':
            mark('drop', FX['warp_tunnel'](x + 340, cy, PAL, rings=9,
                                           rmax=rng.uniform(400, 640)))
        elif kind == 'grid':
            mark('drop', FX['grid_horizon'](x, cy, SHAFT, w=1300))
        elif kind == 'planet':
            r = rng.uniform(280, 460); yy = cy + rng.choice([-1, 1]) * rng.uniform(180, 260)
            mark('drop', disc(x + 340, yy, r, FAR, val=.46, z=-5, zo=-660))
            mark('drop', FX['ring'](x + 340, yy, r * .78, NODE, size=1.3, val=.46,
                                    z=-5, zo=-540, spacing=5))
            mark('drop', FX['arc_line'](x + 340, yy, r * .78, NODE,
                                        arc=math.pi * .85, a0=rng.uniform(0, 6.2),
                                        val=.85, z=-5, zo=-530, seg=130))
        elif kind == 'constellation':
            mark('drop', FX['constellation'](x + 340, cy, NODE, spread=300, stars=11))
        elif kind == 'lightning':
            for k in range(rng.randint(2, 3)):
                mark('drop', FX['lightning'](x + 150 + k * 320, cy, RIM,
                                             length=rng.uniform(300, 460)))
        elif kind == 'comet':
            mark('drop', FX['comet'](x + 500, cy + rng.uniform(-120, 120), PAL))
        elif kind == 'orbiters':
            mark('drop', FX['orbiters'](x + 340, cy + rng.uniform(-70, 70), PAL))
        elif kind == 'fan':
            a0 = rng.uniform(-64, -34)
            for i in range(rng.randint(6, 10)):
                mark('drop', shaft(x + i * 78, cy + 215, a0 - i * 1.8, 820, SHAFT,
                                   width=2.3, val=.19, z=-5, zo=-700))
        elif kind == 'eclipse':
            mark('drop', FX['eclipse'](x + 340, cy + rng.uniform(-60, 60),
                                       rng.uniform(90, 180), PAL))
        elif kind == 'pulsar':
            mark('drop', FX['pulsar'](x + 340, cy + rng.uniform(-60, 60), PAL))
        elif kind == 'rift':
            mark('drop', FX['rift'](x + 300, cy, PAL))
        else:
            mark('drop', FX['shockwave'](x + 320, cy, PAL, n_rings=4))
        tcur += (8 * BEAT) if tcur < 50.5 else (4 * BEAT)

    # outro: the planet comes back, huge and warm
    mark('sky', disc(20080, C(20080) - 300, 620, FAR, val=.58, z=-5, zo=-640))
    mark('sky', FX['ring'](20080, C(20080) - 300, 500, NODE, size=1.5, val=.46,
                           z=-3, zo=-160, spacing=5))
    mark('sky', FX['arc_line'](20080, C(20080) - 300, 500, NODE, arc=math.pi * .85,
                               a0=math.pi * .07, val=.92, z=-3, zo=-150, seg=150))
    for i in range(6):
        mark('sky', shaft(20080, C(20080) - 300, 18 + i * 24, 760, SHAFT,
                          width=2.6, val=.16, taper=False))
    mark('sky', bars(19500, 20500, -60, RIM, up=True, zo=-250, seed_shift=4.2,
                     hmin=45, hmax=165))
    mark('sky', FX['aurora'](19450, 20560, C(20000) + 110, (RIM, SHAFT), bands=3, amp=48))

    # ---- 5. vignette, framed on the camera --------------------------------
    n = 0; x = -360.0
    while x < 20560:
        cy = cam_y(x)
        deco(GRAD_V, x + 160, cy + 300, VIGN, z=7, zo=500, sx=22, sy=17, rot=180,
             val=1.0, ldm=True)
        deco(GRAD_V, x + 160, cy - 300, VIGN, z=7, zo=500, sx=22, sy=17,
             val=1.0, ldm=True)
        n += 2; x += 300
    mark('vignette', n)
    print(f"  set-pieces: sky {stats.get('sky',0)} + drop {stats.get('drop',0)}  [{time.time()-t0:.0f}s]")

    # ---- 6. the beat -------------------------------------------------------
    nt = 0
    t = PHASE; beat = 0
    while t < T_END:
        x = xt(t)
        if beat % 2 == 0: pulse(x, NEON, (255, 255, 255), 0, .03, .30); nt += 1
        if beat % 4 == 0: pulse(x, BLOOM, (235, 248, 255), 0, .04, .34); nt += 1
        if beat % 8 == 0: pulse(x, NODE, (255, 255, 255), 0, .05, .45); nt += 1
        if beat % 8 == 4: pulse(x, RIM, (220, 240, 255), 0, .04, .40); nt += 1
        if beat % 16 == 0: pulse(x, STAR, (255, 255, 255), 0, .06, .5); nt += 1
        if beat % 16 == 8: pulse(x, SHAFT, (180, 215, 255), 0, .05, .6); nt += 1
        t += BEAT; beat += 1
    for ch in (NEON, BLOOM, NODE, STAR, RIM, FLASH, SHAFT):
        pulse(xt(34.01635294117647), ch, (255, 255, 255), 0, .10, .85); nt += 1
    for (tt, ch, rgb, d) in [
        (0.0,   NEON,  (170, 215, 255), .1),  (0.0,  BLOOM, (110, 175, 255), .1),
        (0.0,   SHAFT, (52, 92, 148),   .1),  (0.0,  FAR,   (38, 60, 102),   .1),
        (0.0,   RIM,   (170, 214, 255), .1),  (0.0,  NODE,  (215, 238, 255),  .1),
        (20.0,  BLOOM, (140, 205, 255), 3.0), (22.7, NEON,  (200, 232, 255), 1.4),
        (22.7,  SHAFT, (70, 120, 190),  1.4),
        (28.4,  NEON,  (120, 160, 255), 2.0), (28.4, BLOOM, (86, 130, 255),  2.0),
        (28.4,  FAR,   (24, 38, 82),    2.0), (28.4, SHAFT, (36, 60, 120),   2.0),
        (28.4,  RIM,   (120, 150, 240), 2.0),
        (34.0,  NEON,  (245, 252, 255), .18), (34.0, BLOOM, (215, 240, 255), .18),
        (34.0,  SHAFT, (120, 170, 230), .18), (34.0, FAR,   (70, 104, 160),  .18),
        (34.0,  RIM,   (235, 248, 255), .18),
        (38.0,  BLOOM, (140, 210, 255), 3.2), (38.0, NEON,  (185, 226, 255), 3.2),
        (38.0,  RIM,   (170, 220, 255), 3.2),
        (44.0,  BLOOM, (170, 150, 255), 3.5), (44.0, NEON,  (198, 190, 255), 3.5),
        (44.0,  SHAFT, (108, 96, 190),  3.5), (44.0, RIM,   (188, 170, 255), 3.5),
        (50.0,  BLOOM, (255, 214, 150), 3.5), (50.0, NEON,  (255, 228, 186), 3.5),
        (50.0,  SHAFT, (170, 128, 92),  3.5), (50.0, FAR,   (110, 78, 60),   3.5),
        (50.0,  RIM,   (255, 220, 168), 3.5),
        (56.6,  NEON,  (255, 240, 216), 2.4), (56.6, BLOOM, (255, 226, 190), 2.4),
        (56.6,  SHAFT, (150, 118, 96),  2.4), (56.6, RIM,   (255, 232, 200), 2.4),
    ]:
        colour(xt(tt), ch, rgb, dur=d); nt += 1
    mark('triggers', nt)
    print(f"  triggers: {nt}")
    return T, stats

# ------------------------------------------------------------------ assemble
def header(T):
    H = parse_header(T.head)
    keep = parse_ks38(H['kS38'])
    def cid(entry):
        f = entry.split('_'); return dict(zip(f[0::2], f[1::2])).get('6')
    parts = ['_'.join(f"{k}_{v}" for k, v in c.items()) for c in keep]
    replaced = {str(c) for c, *_ in LAYOUT_CH}
    parts = [p for p in parts if cid(p) not in replaced]
    for c, rgb, bl, op in LAYOUT_CH + PALETTE:
        parts.append(f"1_{rgb[0]}_2_{rgb[1]}_3_{rgb[2]}_4_-1_5_{bl}_6_{c}_7_{op}_15_1_18_0_8_1")
    seen = set(); out = []
    for p in parts:
        c = cid(p)
        if c in seen: continue
        seen.add(c); out.append(p)
    H['kS38'] = '|'.join(out)
    H['kA6'] = '13'; H['kA7'] = '1'
    return ','.join(f"{k},{v}" for k, v in H.items())

if __name__ == '__main__':
    T, stats = build()
    gameplay = T.gameplay
    lvl = ';'.join([header(T)] + [','.join(f"{k},{v}" for k, v in o.items())
                                  for o in gameplay + objs]) + ';'
    open('../versions/v2-aurora.level', 'w').write(lvl)
    fields = {
        'kCEK': ('i', '4'), 'k2': ('s', 'OBSIDIAN CHOIR // AURORA'),
        'k3': ('s', 'VjMgbGF5b3V0LiBEZXNpZ25lZCBkZWNvcmF0aW9uOiBuZW9uIGNvcnJpZG9yLCB0cmFjZWQgaGFsbywgYmVhdC1wbGFjZWQgc2t5Lg=='),
        'k4': ('s', compress(lvl)), 'k8': ('i', '0'), 'k13': ('t', True),
        'k16': ('i', '1'), 'k18': ('i', '0'), 'k21': ('i', '2'), 'k45': ('i', '593661'),
        'k48': ('i', str(len(gameplay) + len(objs))), 'k50': ('i', '47'), 'k80': ('i', '0'),
    }
    out = '../versions/v2-aurora-designed-60k.gmd'
    write_gmd(out, fields)
    import os
    print(f"\n  decoration {len(objs)}  gameplay {len(gameplay)}  total {len(gameplay)+len(objs)}")
    print(f"  {stats}")
    print(f"  wrote {out}  ({os.path.getsize(out)/1e6:.2f} MB)")
