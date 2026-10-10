"""Atmosphere passes for MELTDOWN v2 (Flamewall / Avernus technique).

Measured from the references (refs/*, layers.py, glow tables):
  * back: dark wall, broad bottom-weighted red haze, far silhouettes in the fog
  * mid: black machinery lit from below, hot glows around fire/lava, lit panels
  * front: embers (Avernus ~52 small + ~26 medium bright glows per screen, mostly
    T1-T3, scale med ~0.35), dim additive haze, black framing silhouettes
Everything opaque in front of gameplay layers is kept clear of gameplay.
"""
import math, random
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, triangulate
from shapely.strtree import STRtree
import v2lib as L

GLOW_L, GLOW_M, GLOW_S = 1888, 1886, 1887     # game-drawn soft glows (Avernus workhorses)
GRAD_V = 1011                                 # 30x30 vertical gradient, opaque at the bottom
GRAD_V_SMALL = 1291                           # 15x20 vertical gradient
GRAD_CORNER = 1012                            # 30x30 corner radial
SQUARE, TRI, CIRCLE = 211, 693, 3637
SMOKE, DRIP = 1849, 1853
WAVE_TONGUES = (157, 158, 159)                # d_wave caps (Flamewall fire tongues)
CHAIN = 3050


class Ctx:
    def __init__(self, B, S, terrain, play, lights, beats, rng):
        self.B = B; self.S = S; self.terrain = terrain; self.play = play; self.lights = lights
        self.beats = beats; self.rng = rng
        parts = list(play.geoms) if hasattr(play, 'geoms') else [play]
        self.play_tree = STRtree(parts); self.play_parts = parts
        self.report = {}

    def near_play(self, geom, margin):
        g = geom.buffer(margin) if margin else geom
        for i in self.play_tree.query(g):
            part = self.play_parts[i] if not hasattr(i, 'intersects') else i
            if part.intersects(g):
                return True
        return False


# ------------------------------------------------------------------ colours
def channels(B):
    c = B.color
    return dict(
        haze=c(650, (150, 27, 8), False, .31),       # back light: normal alpha (must cover the opaque rear wall)
        haze_cloud=c(678, (160, 30, 9), False, .24),  # cloudy variation in the back light
        haze_hi=c(651, (92, 10, 22), False, .22),    # crimson veil in front of the far silhouettes
        glowair=c(676, (150, 27, 8), True, .46),     # additive air glow (corridors, lava band)
        backing=c(677, (0, 0, 0), False, .62),       # dark backing behind hazards
        far=c(652, (15, 5, 4), False, 1),            # far silhouettes
        far_rim=c(653, (88, 26, 10), False, 1),      # far silhouettes' lit lower edges
        hot=c(654, (255, 78, 16), True, .55),        # hot glow around fire / lava
        core=c(655, (255, 222, 160), True, .90),     # white-hot cores
        lava=c(656, (255, 128, 34), False, 1),       # lava surface
        crust=c(657, (34, 7, 4), False, 1),          # lava crust
        tongue=c(658, (255, 87, 7), True, .80),      # fire tongues (Flamewall value)
        tongue_dim=c(673, (150, 30, 4), True, .60),
        ember=c(659, (255, 79, 20), True, 1),        # embers (Avernus 1887 (255,79,57)/(255,135,48))
        ember_hi=c(660, (255, 150, 60), True, 1),
        smoke=c(661, (16, 7, 6), False, .42),        # smoke (dark, translucent)
        smoke_lit=c(662, (58, 14, 8), True, .40),
        fg=c(663, (4, 2, 2), False, 1),              # foreground silhouettes
        fg_rim=c(664, (150, 42, 12), False, 1),
        front=c(665, (70, 13, 4), True, .45),        # front additive haze
        mace=c(666, (9, 4, 4), False, 1),            # chains / maces
        mace_rim=c(667, (190, 64, 18), False, 1),
        panel=c(668, (255, 124, 42), True, .85),     # hanging light panels
        frame=c(669, (7, 3, 3), False, 1),
        shaft=c(670, (190, 62, 14), True, .30),      # light shafts
        drip=c(671, (255, 112, 26), True, .90),
        shadow=c(672, (0, 0, 0), False, .55),        # soft black glows (Avernus T3 shadows)
        spark=c(674, (255, 238, 196), True, 1),      # additive white-hot specks
        lava_hot=c(679, (255, 236, 190), False, 1),  # opaque white-hot lines (lava surface, lamp edges)
        wall_ramp=c(680, (9, 3, 3), False, 1),       # feathered extension of the rear wall at the entry
        flare_wall=c(681, (255, 238, 222), False, 1),  # exit: rear wall burns out to white
        flare=c(682, (255, 196, 140), True, .60),
        bokeh=c(675, (255, 96, 30), True, .38),
    )


# ------------------------------------------------------------------ helpers
def glow_chain(B, pts, ch, z, order, scale, oid=GLOW_L, groups=(), ldm=True, step=.45, base=40.0):
    """Overlapping glow blobs along a polyline, spaced ~45% of their own width."""
    out = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(seg / (base * scale * step)))
        for i in range(n):
            q = i / n
            out.append(B.add(oid, x0 + (x1 - x0) * q, y0 + (y1 - y0) * q, ch, z, order, scale, groups=groups, ldm=ldm))
    return out


def poly_fill(B, shape, ch, z, order, groups=(), ldm=False):
    """Fill a polygon with solid squares/triangles (exact edges, no overlap seams on opaque channels)."""
    if shape.is_empty:
        return 0
    if shape.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return sum(poly_fill(B, g, ch, z, order, groups, ldm) for g in shape.geoms if g.geom_type in ('Polygon', 'MultiPolygon'))
    if shape.geom_type != 'Polygon' or shape.area < .5:
        return 0
    xmin, ymin, xmax, ymax = shape.bounds
    if abs(shape.area - (xmax - xmin) * (ymax - ymin)) < .01:
        B.add(SQUARE, (xmin + xmax) / 2, (ymin + ymax) / 2, ch, z, order, (xmax - xmin + .6) / 30, (ymax - ymin + .6) / 30,
              groups=groups, ldm=ldm)
        return 1
    n = 0
    for tri in triangulate(shape):
        cut = tri.intersection(shape)
        if cut.area < .5:
            continue
        if cut.geom_type == 'Polygon' and len(cut.exterior.coords) == 4:
            n += triangle(B, *list(cut.exterior.coords)[:3], ch, z, order, groups, ldm)
        else:
            n += poly_fill(B, cut, ch, z, order, groups, ldm)
    return n


def triangle(B, a, b, c, ch, z, order, groups=(), ldm=False):
    """Exact triangle from two right-triangle sprites (693), as MELTDOWN's builder does."""
    pts = [a, b, c]
    i = max(range(3), key=lambda i: math.dist(pts[i], pts[(i + 1) % 3]))
    a, b, c = pts[i], pts[(i + 1) % 3], pts[(i + 2) % 3]
    ux, uy = b[0] - a[0], b[1] - a[1]; length = math.hypot(ux, uy)
    if length < .01:
        return 0
    q = ((c[0] - a[0]) * ux + (c[1] - a[1]) * uy) / (length * length)
    r = (a[0] + q * ux, a[1] + q * uy)
    n = 0
    for end in (a, b):
        u = (end[0] - r[0], end[1] - r[1]); v = (c[0] - r[0], c[1] - r[1])
        w = math.hypot(*u); hgt = math.hypot(*v)
        if min(w, hgt) < .05:
            continue
        theta = math.atan2(-u[1], -u[0]); dy = (-math.sin(theta), math.cos(theta))
        o = B.add(TRI, r[0] + (u[0] + v[0]) / 2, r[1] + (u[1] + v[1]) / 2, ch, z, order, (w + .9) / 30, (hgt + .9) / 30,
                  -math.degrees(theta), groups, ldm=ldm)
        if v[0] * dy[0] + v[1] * dy[1] < 0:
            o['5'] = '1'
        n += 1
    return n


def bar(B, x1, y1, x2, y2, w, ch, z, order, groups=(), ldm=False):
    return B.add(SQUARE, (x1 + x2) / 2, (y1 + y2) / 2, ch, z, order, math.hypot(x2 - x1, y2 - y1) / 30, w / 30,
                 -math.degrees(math.atan2(y2 - y1, x2 - x1)), groups, ldm=ldm)


# ------------------------------------------------------------------ 3. back haze
def back_haze(ctx, ch):
    """Broad bottom-weighted light behind the machinery. Order in the B5 layer:
    wall -40, bricks -34, LIGHT -33, far silhouettes -32, VEIL -31 (so distant
    shapes read dark against the light and the veil lifts them into the fog).
    Tiles are butted exactly with identical values: no additive seams."""
    B = ctx.B; n = 0
    W = 150.0
    x = L.START
    while x < L.END:
        w = min(W, L.END - x)
        cx = x + w / 2
        lo, hi = L.band(cx)
        hgt = (hi - lo) * .62
        B.add(GRAD_V, cx, lo - 20 + hgt / 2, ch['haze'], -5, -33, w / 30, hgt / 30)
        vh = (hi - lo) * 1.0
        B.add(GRAD_V, cx, lo - 40 + vh / 2, ch['haze_hi'], -5, -31, w / 30, vh / 30)
        n += 2
        x += w
    # cloudy light: soft blobs of different sizes so gaps between machinery show variation, not flat colour
    xc = L.START
    while xc < L.END:
        lo, hi = L.band(xc)
        yc = lo + (hi - lo) * ctx.rng.random() ** 1.6 * .7
        B.add(GLOW_L, xc, yc, ch['haze_cloud'], -5, -33, ctx.rng.uniform(2.2, 5.0), ldm=True); n += 1
        xc += ctx.rng.uniform(35, 75)
    # horizon light: where the rear wall is open, a warm band behind the far silhouettes
    xh = L.START
    while xh < L.END:
        lo, hi = L.band(xh)
        yh = lo + (hi - lo) * .42
        if not ctx.terrain.covers(Point(xh, yh)):
            B.add(GLOW_L, xh, yh, ch['haze'], -5, -33, 4.2, ldm=True); n += 1
        xh += 78
    for kind, g, inten, sig in ctx.lights:
        if kind in ('seam', 'lamp'):
            continue
        c = g.centroid
        s = min(4.5, max(1.2, sig / 45))
        for k in range(3):
            ang = k * 2.399963
            B.add(GLOW_L, c.x + math.cos(ang) * sig * .35, c.y + math.sin(ang) * sig * .25, ch['haze_hi'], -5, -31,
                  s * (1 - .18 * k), ldm=True)
            n += 1
    ctx.report['back_haze'] = n


# ------------------------------------------------------------------ 4. far silhouettes
def far_silhouettes(ctx, ch):
    """Distant foundry shapes in the fog: stacks, girder towers, gantry cranes with
    hanging hooks. Drawn behind the haze tiles so the fog lifts them (aerial depth)."""
    B = ctx.B; rng = ctx.rng; shapes = []
    x = L.START + 40
    while x < L.END - 60:
        lo, hi = L.band(x)
        kind = rng.choice(['stack', 'stack', 'tower', 'crane', 'stack_pair'])
        base = lo - 30
        if kind in ('stack', 'stack_pair'):
            for dx in ([0] if kind == 'stack' else [-38, 30]):
                w = rng.uniform(34, 58); top = base + rng.uniform(.55, .95) * (hi - lo + 60)
                p = Polygon([(x + dx - w / 2, base), (x + dx + w / 2, base), (x + dx + w * .42, top), (x + dx - w * .42, top)])
                shapes.append(p)
                shapes.append(box(x + dx - w * .5, top - 6, x + dx + w * .5, top + 5))          # collar
                shapes.append(box(x + dx - w * .47, base + (top - base) * .38, x + dx + w * .47, base + (top - base) * .38 + 7))
        elif kind == 'tower':
            w = rng.uniform(70, 100); top = base + rng.uniform(.6, .9) * (hi - lo + 60)
            for sx in (-1, 1):
                shapes.append(LineString([(x + sx * w / 2, base), (x + sx * w * .3, top)]).buffer(4, cap_style=2))
            y = base; k = 0
            while y < top - 30:
                y2 = y + 48
                f0 = (y - base) / (top - base); f1 = (y2 - base) / (top - base)
                xl0 = x - w / 2 + (w * .2) * f0; xr0 = x + w / 2 - (w * .2) * f0
                xl1 = x - w / 2 + (w * .2) * f1; xr1 = x + w / 2 - (w * .2) * f1
                shapes.append(LineString([(xl0, y), (xr1, y2)] if k % 2 else [(xr0, y), (xl1, y2)]).buffer(2.2, cap_style=2))
                shapes.append(LineString([(xl1, y2), (xr1, y2)]).buffer(2.5, cap_style=2))
                y = y2; k += 1
        else:  # crane: mast + boom + hanging hook
            top = base + rng.uniform(.7, .95) * (hi - lo + 60)
            shapes.append(box(x - 9, base, x + 9, top))
            span = rng.uniform(140, 220) * rng.choice([-1, 1])
            shapes.append(LineString([(x, top - 8), (x + span, top - 20)]).buffer(6, cap_style=2))
            hx = x + span * rng.uniform(.55, .9)
            drop = rng.uniform(60, 150)
            shapes.append(LineString([(hx, top - 17), (hx, top - 17 - drop)]).buffer(1.2, cap_style=2))
            shapes.append(Point(hx, top - 22 - drop).buffer(9).difference(box(hx - 3, top - 26 - drop, hx + 10, top - 16 - drop)))
        x += rng.uniform(180, 320)
    n = 0
    for s in shapes:
        s = s.intersection(box(L.START, -260, L.END, 760))
        n += poly_fill(B, s, ch['far'], -5, -32, ldm=True)
    ctx.report['far_silhouettes'] = n


# ------------------------------------------------------------------ 5. hot glows and shafts
def hot_glows(ctx, ch):
    """Light at every real heat source: chained blobs, cores and rising shafts.
    Blending only (additive), on B2 behind the player like MELTDOWN's own glows;
    anything whose light would sit on top of gameplay objects drops to B4 instead."""
    B = ctx.B; n = 0
    for kind, g, inten, sig in ctx.lights:
        zz = -3 if ctx.near_play(g, sig * .8) else 1
        if kind == 'fire':
            c = g.centroid
            n += len(glow_chain(B, [(c.x - sig * .6, c.y - sig * .15), (c.x + sig * .6, c.y - sig * .15)], ch['hot'], zz, 30,
                                min(2.2, sig / 40)))
            n += len(glow_chain(B, [(c.x - sig * .35, c.y + sig * .05), (c.x + sig * .35, c.y + sig * .05)], ch['core'], zz, 31,
                                min(1.4, sig / 70), oid=GLOW_M, base=32))
            # heat rising above the fire bed: soft blobs shrinking upward (no hard-edged shafts)
            for k in range(5):
                B.add(GLOW_L, c.x + ctx.rng.uniform(-12, 12), c.y + sig * (.35 + .32 * k), ch['shaft'], zz, 28,
                      min(3.2, sig / 34) * (1 - .15 * k), ldm=True)
                n += 1
        elif kind == 'stream':
            (x0, y0), (x1, y1) = list(g.coords)
            n += len(glow_chain(B, [(x0, y0), (x1, y1)], ch['hot'], zz, 30, 1.6))
            n += len(glow_chain(B, [(x0, y0), (x1, y1)], ch['core'], zz, 31, .7, oid=GLOW_M, base=32))
        elif kind == 'furnace':
            c = g.centroid
            n += len(glow_chain(B, [(c.x, c.y - 120), (c.x, c.y + 110)], ch['hot'], zz, 29, 2.2, step=.6))
        elif kind == 'lamp':
            c = g.centroid
            B.add(GLOW_M, c.x, c.y, ch['hot'], zz, 30, 1.1, ldm=True); n += 1
            for k in range(3):
                B.add(GLOW_L, c.x, c.y - 30 - 34 * k, ch['shaft'], zz, 27, 1.5 + .35 * k, ldm=True); n += 1
    ctx.report['hot_glows'] = n


# ------------------------------------------------------------------ 6. lava sea behind the UFO hall
def lava_floor(ctx, ch):
    """Molten floor under the UFO hall (behind all gameplay): crust, a thin white-hot
    surface line, Flamewall-style fire tongues and a glow band. Tongues and glow
    are dimmed wherever a hazard sits close above, so outlines stay readable."""
    B = ctx.B; rng = ctx.rng; n = 0
    a, b, y = 22560, L.END - 110, 0.0
    x = a
    while x < b:
        w = min(90, b - x)
        B.add(SQUARE, x + w / 2, y - 60, ch['crust'], -3, -30, (w + .5) / 30, 120 / 30); n += 1
        B.add(SQUARE, x + w / 2, y - 2, ch['lava'], -3, -26, (w + .5) / 30, 4 / 30); n += 1
        B.add(SQUARE, x + w / 2, y - 1, ch['lava_hot'], -3, -25, (w + .5) / 30, 1.5 / 30); n += 1
        x += w
    x = a
    while x < b:
        near = ctx.near_play(Point(x, y + 20), 42)
        oid = rng.choice(WAVE_TONGUES)
        s = rng.uniform(.55, 1.15) * (.55 if near else 1)
        B.add(oid, x, y + 9 * s, ch['tongue_dim'] if near else ch['tongue'], -3, -28, s * rng.uniform(.9, 1.4),
              s * rng.uniform(.8, 1.7), fx=rng.random() < .5, ldm=True)
        n += 1
        if not near and rng.random() < .5:
            B.add(1764, x + rng.uniform(-8, 8), y + rng.uniform(1, 6), ch['core'], -3, -25, rng.uniform(.2, .45), ldm=True)
            n += 1
        x += rng.uniform(14, 26)
    xs = a
    while xs < b:
        near = ctx.near_play(Point(xs, y + 30), 50)
        B.add(GLOW_L, xs, y + 12, ch['tongue_dim'] if near else ch['hot'], -3, -27, 1.5 if near else 1.9, ldm=True); n += 1
        B.add(GLOW_L, xs + 20, y + 55, ch['glowair'], -3, -27, 3.0, ldm=True); n += 1
        xs += 34
    ctx.report['lava_floor'] = n


# ------------------------------------------------------------------ 7. embers
def embers(ctx, ch):
    """Rising embers, rank-matched to Avernus: bright 1887 (~52/screen, scale med .34)
    and 1886 (~26/screen, scale med .36), weighted toward the bottom and the fires.
    Most sit on B2 (behind the player); a quarter drift on T1 in front, all additive."""
    B = ctx.B; rng = ctx.rng
    groups = [B.group() for _ in range(8)]
    speeds = [(rng.uniform(120, 260), rng.uniform(-60, 40)) for _ in groups]
    n = 0
    screens = (L.END - L.START) / 570
    count_s = int(52 * screens * .85); count_m = int(26 * screens * .85)
    fires = [g.centroid for k, g, i, s in ctx.lights if k in ('fire', 'stream', 'furnace')]

    def sample_scale(med, p10, p90, mx):
        u = rng.random()
        if u < .5:
            v = p10 + (med - p10) * (u / .5) ** .8
        else:
            v = med + (p90 - med) * ((u - .5) / .4) if u < .9 else p90 + (mx - p90) * ((u - .9) / .1) ** 2
        return max(.05, v)

    def place():
        for _ in range(40):
            if rng.random() < .45 and fires:
                c = rng.choice(fires)
                x = c.x + rng.gauss(0, 90); y = c.y + abs(rng.gauss(0, 120))
            else:
                x = rng.uniform(L.START, L.END)
                lo, hi = L.band(x, 40)
                y = lo + (hi - lo) * rng.random() ** 1.8          # bottom-weighted
            if L.START <= x <= L.END:
                return x, y
        return None

    for oid, count, med, p10, p90, mx in [(GLOW_S, count_s, .34, .18, 1.17, 2.37), (GLOW_M, count_m, .36, .06, 1.0, 1.33)]:
        for i in range(count):
            p = place()
            if p is None:
                continue
            x, y = p
            s = sample_scale(med, p10, p90, mx)
            front = rng.random() < .25
            z = 5 if front else 1
            if front and s > .6:
                s *= .6
            gi = rng.randrange(len(groups))
            c = ch['ember_hi'] if rng.random() < .3 else ch['ember']
            B.add(oid, x, y, c, z, 40 + i % 5, s, groups=(groups[gi],), ldm=True)
            n += 1
            if rng.random() < .15:
                B.add(1764, x, y, ch['spark'], z, 46, rng.uniform(.14, .28), groups=(groups[gi],), ldm=True)
                n += 1
    # slow rise across the whole drop (~16 s), in two legs with a sideways sway
    t0 = L.tx(L.START); t1 = L.tx(L.END)
    for g, (dy, dx) in zip(groups, speeds):
        half = (t1 - t0) / 2
        B.move(g, L.START - 300, dx * .5, dy * .5, half, easing=0)
        B.move(g, L.xt(t0 + half) - 300, -dx * .3, dy * .5, half, easing=0)
    ctx.report['embers'] = n
    ctx.ember_groups = groups


# ------------------------------------------------------------------ 8. smoke
def smoke(ctx, ch):
    B = ctx.B; rng = ctx.rng; n = 0
    groups = [B.group() for _ in range(3)]
    srcs = [g.centroid for k, g, i, s in ctx.lights if k in ('fire', 'furnace', 'stream', 'hub')]
    for c in srcs:
        for k in range(rng.randint(5, 9)):
            x = c.x + rng.gauss(0, 70); y = c.y + 60 + abs(rng.gauss(0, 110))
            s = rng.uniform(1.4, 3.2)
            lit = rng.random() < .35
            B.add(SMOKE, x, y, ch['smoke_lit'] if lit else ch['smoke'], -3, 45 + k, s, s * rng.uniform(.8, 1.2),
                  rng.uniform(-12, 12), groups=(rng.choice(groups),), fx=rng.random() < .5, ldm=True)
            n += 1
    t0 = L.tx(L.START); t1 = L.tx(L.END)
    for i, g in enumerate(groups):
        B.move(g, L.START - 300, -80 - 30 * i, 90 + 25 * i, t1 - t0, easing=0)
    ctx.report['smoke'] = n


# ------------------------------------------------------------------ 9. chains, maces, hanging lights (B4)
def hangers(ctx, ch):
    """Avernus maces on chains and Flamewall hanging light panels, hung from above the
    top of the view wherever the background is open (not behind a wall mass) and
    clear of gameplay. B4: behind every gameplay layer. Chains swing on rotate triggers."""
    B = ctx.B; rng = ctx.rng; n = 0
    x = L.START + rng.uniform(30, 90)
    placed = 0
    while x < L.END - 30:
        lo, hi = L.band(x)
        kind = rng.choices(['mace', 'panel', 'chain'], [.42, .38, .20])[0]
        anchor = hi + 30
        length = rng.uniform(.16, .34) * (hi - lo) + 20
        bottom = anchor - length - (70 if kind == 'mace' else 95 if kind == 'panel' else 0)
        weight = box(x - 34, bottom, x + 34, bottom + (70 if kind == 'mace' else 95 if kind == 'panel' else 20))
        chain_line = LineString([(x, bottom), (x, hi)])
        hidden = ctx.terrain.covers(weight) and ctx.terrain.covers(chain_line)
        if hidden or ctx.near_play(weight, 14) or ctx.near_play(chain_line, 8):
            x += rng.uniform(30, 60)
            continue
        if kind in ('mace', 'chain'):
            g = B.group(); cg = B.group()
            B.add(1764, x, anchor, ch['mace'], -5, 0, .02, groups=(cg,))
            links = int(length / 14)
            for j in range(links):
                B.add(CHAIN, x, anchor - 4 - j * 14, ch['mace'], -3, 60, .55, .62, groups=(g,), ldm=True); n += 1
            if kind == 'mace':
                my = anchor - 12 - links * 14 - 18
                r = rng.uniform(13, 21)
                B.add(CIRCLE, x, my - r * .12, ch['mace_rim'], -3, 60, r * 1.03 / 25, groups=(g,)); n += 1
                B.add(CIRCLE, x, my, ch['mace'], -3, 62, r / 25, groups=(g,)); n += 1
                for k in range(8):
                    ang = k * math.pi / 4 + .2
                    tipx = x + math.cos(ang) * r * 1.8; tipy = my + math.sin(ang) * r * 1.8
                    bx = x + math.cos(ang + .36) * r * .82; by = my + math.sin(ang + .36) * r * .82
                    cx2 = x + math.cos(ang - .36) * r * .82; cy2 = my + math.sin(ang - .36) * r * .82
                    n += triangle(B, (tipx, tipy), (bx, by), (cx2, cy2), ch['mace'], -3, 61, (g,))
                B.add(GLOW_L, x, my - r * 1.4, ch['hot'], -3, 55, 1.4, groups=(g,), ldm=True); n += 1
            sw = rng.uniform(4, 8) * rng.choice([-1, 1])
            t_start = max(L.START, x - 650)
            B.rotate(g, cg, t_start, sw, 1.2, easing=0)
            B.rotate(g, cg, t_start + 480, -2 * sw, 1.5, easing=0)
            B.rotate(g, cg, t_start + 1100, sw, 1.2, easing=0)
        else:
            ph = rng.uniform(48, 88); pw = rng.uniform(12, 20)
            top = anchor - length
            for sx in (-1, 1):
                bar(B, x + sx * pw * .35, anchor, x + sx * pw * .35, top, 1.6, ch['frame'], -3, 58); n += 1
            B.add(SQUARE, x, top - ph / 2, ch['frame'], -3, 59, (pw + 6) / 30, (ph + 6) / 30); n += 1
            B.add(GRAD_V, x, top - ph / 2, ch['panel'], -1, -8, pw / 30, ph / 30, fy=True); n += 1
            B.add(SQUARE, x, top - 3, ch['lava_hot'], -3, 61, pw / 30, 2.2 / 30); n += 1
            n += len(glow_chain(B, [(x, top - ph * .2), (x, top - ph * .9)], ch['hot'], -1, -9, 1.1, oid=GLOW_M, base=32))
            for k in range(3):
                B.add(GLOW_L, x, top - ph - 20 - 36 * k, ch['shaft'], -1, -9, 1.2 + .4 * k, ldm=True); n += 1
        placed += 1
        x += rng.uniform(90, 170)
    ctx.report['hangers'] = n
    ctx.report['hangers_placed'] = placed


# ------------------------------------------------------------------ 10. foreground framing (T2)
OUTSIDE = [  # (x0, x1, floor, ceiling) of bounded gamemodes: space beyond these is never playable
    (16875, 18195, 0, 300), (18195, 20685, 30, 330), (22665, 24660, 0, 300),
]


def safe_region(ctx):
    """Where an opaque object may sit in front of gameplay layers: deep inside wall
    masses or beyond a bounded gamemode's floor/ceiling, and never within 45 units
    of any gameplay object."""
    parts = [ctx.terrain.buffer(-22)]
    for x0, x1, fl, ce in OUTSIDE:
        parts.append(box(x0, -400, x1, fl - 30))
        parts.append(box(x0, ce + 30, x1, 900))
    region = unary_union(parts).difference(ctx.play.buffer(45)).difference(ctx.reach.buffer(12))
    return region.intersection(box(L.START, -400, L.END, 900))


def foreground(ctx, ch):
    B = ctx.B; rng = ctx.rng; n = 0
    safe = safe_region(ctx)
    ctx.safe = safe
    tol = safe.buffer(1.5)
    kept = []; drips = []
    for edge in ('top', 'bottom'):
        x0 = L.START
        while x0 < L.END:
            w = rng.uniform(50, 130)
            x1 = min(L.END, x0 + w)
            pts = []
            x = x0
            while x < x1:
                lo, hi = L.band(x)
                if edge == 'top':
                    d = rng.uniform(6, 22)
                    if rng.random() < .09:
                        d += rng.uniform(30, 85)
                    pts.append((x, hi + 4 - d)); pts.append((min(x1, x + rng.uniform(3, 7)), hi + 4 - rng.uniform(0, 8)))
                else:
                    d = rng.uniform(4, 18)
                    if rng.random() < .07:
                        d += rng.uniform(20, 55)
                    pts.append((x, lo - 4 + d)); pts.append((min(x1, x + rng.uniform(3, 8)), lo - 4 + rng.uniform(0, 6)))
                x += rng.uniform(8, 20)
            lo1, hi1 = L.band(x1)
            if edge == 'top':
                pts.append((x1, hi1 + 4 - rng.uniform(4, 14)))
                poly = Polygon([(x0, hi1 + 70)] + pts + [(x1, hi1 + 70)]).buffer(0)
            else:
                pts.append((x1, lo1 - 4 + rng.uniform(3, 12)))
                poly = Polygon([(x0, lo1 - 70)] + pts + [(x1, lo1 - 70)]).buffer(0)
            if poly.is_valid and tol.covers(poly):
                kept.append(poly)
                if edge == 'top':
                    drips.extend(p for i, p in enumerate(pts) if i % 8 == 0)
            x0 = x1
    fg = unary_union(kept) if kept else Polygon()
    # Avernus rims: the lava below catches the lower edge of every hanging mass. The rim is
    # the full silhouette in a hot colour; the black body sits 2.5 units higher on top of it.
    from shapely import affinity
    tops = [k for k in kept if k.bounds[3] > L.band((k.bounds[0] + k.bounds[2]) / 2)[1]]
    if tops:
        rim = unary_union(tops)
        n += poly_fill(B, rim, ch['fg_rim'], 7, 9, ldm=True)
        body = unary_union([affinity.translate(k, 0, 2.5).intersection(k.buffer(0)) for k in tops] +
                           [k for k in kept if k not in tops])
        n += poly_fill(B, body, ch['fg'], 7, 10, ldm=False)
    else:
        n += poly_fill(B, fg, ch['fg'], 7, 10, ldm=False)
    for (x, y) in drips:
        if safe.covers(box(x - 4, y - 75, x + 4, y + 2)) and fg.buffer(1).contains(Point(x, y + 6)):
            B.add(DRIP, x, y - 34, ch['drip'], 7, 12, rng.uniform(.5, .9), rng.uniform(.7, 1.1), ldm=True)
            n += 1
    # soft black shadow glows inside the safe region (Avernus T3 technique)
    x = L.START
    while x < L.END:
        lo, hi = L.band(x)
        for y in (hi + 10, lo - 10):
            sc = rng.uniform(2.2, 3.4)
            if safe.covers(Point(x, y).buffer(sc * 35)):     # validator core radius: .6 x half-diagonal of an 80u orb
                B.add(GLOW_L, x, y, ch['shadow'], 9, -5, sc, ldm=True); n += 1
        x += rng.uniform(60, 110)
    ctx.report['foreground'] = n


# ------------------------------------------------------------------ 11. front haze (T3)
def front_haze(ctx, ch):
    B = ctx.B; rng = ctx.rng; n = 0
    W = 150.0
    x = L.START
    while x < L.END:
        w = min(W, L.END - x); cx = x + w / 2
        lo, hi = L.band(cx)
        hgt = (hi - lo) * .62
        B.add(GRAD_V, cx, lo - 10 + hgt / 2, ch['front'], 9, 0, w / 30, hgt / 30, ldm=True)
        n += 1
        x += w
    x = L.START + 100
    while x < L.END:
        lo, hi = L.band(x)
        B.add(GLOW_L, x, lo + (hi - lo) * rng.uniform(.05, .45), ch['front'], 9, 1, rng.uniform(3.5, 6.0), ldm=True)
        n += 1
        x += rng.uniform(160, 260)
    ctx.report['front_haze'] = n


# ------------------------------------------------------------------ 12. beat pulses + fades
def pulses(ctx, ch):
    B = ctx.B; n = 0
    for i, b in enumerate(ctx.beats):
        major = i % 4 == 0
        x = b['x']
        B.pulse(ch['haze'], x, (210, 58, 14) if major else (185, 44, 10), .01, .05 if major else .02, .40 if major else .25)
        B.pulse(ch['hot'], x, (255, 140, 50) if major else (255, 112, 30), .01, .04 if major else .02, .30 if major else .20)
        B.pulse(ch['ember_hi'], x, (255, 214, 140), .01, .03, .22)
        B.pulse(ch['front'], x, (120, 26, 8) if major else (92, 18, 5), .01, .04, .35 if major else .22)
        B.pulse(ch['panel'], x, (255, 190, 110), .01, .03, .25)
        n += 5
    ctx.report['pulses'] = n


def fades(ctx):
    B = ctx.B
    B.alpha(L.ROOT_V2, 15300, 0, 0)
    B.alpha(L.ROOT_V2, 16600, .30, 1)
    # the exit flare carries the handoff to the original white section; hide the rest after it
    B.alpha(L.ROOT_V2, L.END + 40, .12, 0)


# ------------------------------------------------------------------ section seams
def entry_ramp(ctx, ch):
    """MELTDOWN's rear wall starts at x=16785, so when the drop zooms out to 0.75 the
    left of the screen showed a hard edge onto the plain background. A horizontal
    gradient wall feathers it in from x=16560."""
    B = ctx.B; n = 0
    lo, hi = -260, 720
    step = 120.0
    y = lo
    while y < hi:
        h = min(step, hi - y)
        # 1011 is opaque at its bottom; rotation -90 turns the opaque side to +x
        B.add(GRAD_V, 16785 - 112.5, y + h / 2, ch['wall_ramp'], -5, -39, (h + .5) / 30, 225 / 30, rot=-90)
        B.add(GRAD_V, 16785 - 60, y + h / 2, ch['haze'], -5, -33, (h + .5) / 30, 120 / 30, rot=-90, ldm=True)
        n += 2
        y += h
    ctx.report['entry_ramp'] = n


def exit_flare(ctx, ch):
    """The drop ends by handing over to the original level's white segment. Instead of
    a hard dark-to-white seam, the foundry burns out into white-hot light: a warm
    ramp over the rear wall and an additive flare in front of the machinery, both
    reaching full strength exactly at the seam."""
    B = ctx.B; n = 0
    lo, hi = -120, 470
    y = lo
    while y < hi:
        h = min(90.0, hi - y)
        B.add(GRAD_V, L.END - 100, y + h / 2, ch['flare_wall'], -5, -30, (h + .5) / 30, 200 / 30, rot=-90)
        B.add(GRAD_V, L.END - 75, y + h / 2, ch['flare'], -3, 80, (h + .5) / 30, 150 / 30, rot=-90, ldm=True)
        n += 2
        y += h
    for k in range(9):
        B.add(GLOW_L, L.END - 25, -20 + 45 * k, ch['flare'], 1, 60, 3.2, ldm=True); n += 1
    ctx.report['exit_flare'] = n


# ------------------------------------------------------------------ soot / shading on the wall masses
def soot(ctx, ch):
    """Soft black shading over MELTDOWN's regular armour plates (Avernus shades with
    black gradients at partial opacity). Only deep inside wall masses, away from
    corridor edges and gameplay, and weighted to where the light field is low."""
    B = ctx.B; rng = ctx.rng; n = 0
    region = ctx.terrain.buffer(-34).difference(ctx.play.buffer(36)).difference(ctx.reach.buffer(12))
    x = L.START
    while x < L.END:
        lo, hi = L.band(x, 60)
        y = lo
        while y < hi:
            px = x + rng.uniform(-20, 20); py = y + rng.uniform(-20, 20)
            sc = rng.uniform(1.2, 2.4)
            # the glow's opaque core (~24u x scale, assuming the larger plausible orb size) must stay in the wall
            if region.covers(Point(px, py).buffer(sc * 35)):
                lv = ctx.light_at(px, py)
                if rng.random() < max(0, 1.05 - 1.1 * lv):
                    B.add(GLOW_L, px, py, ch['shadow'], -1, 24, sc, ldm=True); n += 1
            y += rng.uniform(40, 62)
        x += rng.uniform(40, 62)
    ctx.report['soot'] = n


# ------------------------------------------------------------------ corridor light (ship + wave)
def corridor_light(ctx, ch):
    """A warm glow running down the middle of the ship and wave corridors, behind the
    walls (B4). The walls stay black and the channel between them reads as lit air."""
    B = ctx.B; n = 0
    x = 16900.0
    while x < 20680:
        lo, hi = L.band(x)
        free = LineString([(x, lo), (x, hi)]).difference(ctx.terrain)
        segs = [free] if free.geom_type == 'LineString' else list(getattr(free, 'geoms', []))
        segs = [g for g in segs if g.length > 40]
        if segs:
            g = max(segs, key=lambda g: g.length)
            (x0, y0), (x1, y1) = g.coords[0], g.coords[-1]
            cy = (y0 + y1) / 2; span = abs(y1 - y0)
            B.add(GLOW_L, x, cy, ch['glowair'], -3, 50, min(3.4, max(1.4, span / 40)), ldm=True); n += 1
            if ctx.rng.random() < .35:
                B.add(GLOW_M, x + ctx.rng.uniform(-10, 10), cy + ctx.rng.uniform(-span * .2, span * .2), ch['hot'], -3, 51,
                      ctx.rng.uniform(.6, 1.1), ldm=True); n += 1
        x += 32
    ctx.report['corridor_light'] = n


def bokeh(ctx, ch):
    """Out-of-focus embers in front of everything (Avernus: bright 1888/1886 on T3)."""
    B = ctx.B; rng = ctx.rng; n = 0
    per_screen = 7
    count = int((L.END - L.START) / 570 * per_screen)
    g = B.group()
    for i in range(count):
        x = rng.uniform(L.START, L.END)
        lo, hi = L.band(x)
        y = lo + (hi - lo) * rng.random() ** 1.4
        B.add(GLOW_L if rng.random() < .6 else GLOW_M, x, y, ch['bokeh'], 9, 20 + i % 3, rng.uniform(.5, 1.15),
              groups=(g,), ldm=True)
        n += 1
    t0 = L.tx(L.START); t1 = L.tx(L.END)
    B.move(g, L.START - 300, -60, 140, t1 - t0, easing=0)
    ctx.report['bokeh'] = n


# ------------------------------------------------------------------ readability: dark backing behind hazards
HAZARD_IDS = {'94', '216', '217', '458', '8', '39', '103', '392', '1717', '1718'}
ORB_IDS = {'36', '84', '141', '1333', '1330', '1704', '1751', '35', '67', '140'}


def hazard_backing(ctx, ch):
    """Soft black backing behind every hazard cluster and orb, on B4 in front of the
    haze/lava/machinery but behind the gameplay layer. Keeps orange outlines
    readable over the brighter atmosphere (the references put hazards on dark)."""
    B = ctx.B; n = 0
    boxes = []
    for o in ctx.S:
        if o['1'] in HAZARD_IDS | ORB_IDS and '6' not in o.get('57', '').split('.'):
            x = float(o['2']); y = float(o['3'])
            if L.START <= x <= L.END:
                boxes.append(box(x - 15, y - 15, x + 15, y + 15))
    blobs = unary_union([b.buffer(12) for b in boxes])
    parts = list(blobs.geoms) if hasattr(blobs, 'geoms') else [blobs]
    for p in parts:
        minx, miny, maxx, maxy = p.bounds
        w = maxx - minx; hgt = maxy - miny
        if max(w, hgt) > 150:
            # long hazard rows: a chain of backings along the row
            steps = max(2, int(max(w, hgt) / 60))
            for i in range(steps + 1):
                q = i / steps
                cx = minx + w * q if w >= hgt else (minx + maxx) / 2
                cy = (miny + maxy) / 2 if w >= hgt else miny + hgt * q
                if p.buffer(20).contains(Point(cx, cy)):
                    B.add(GLOW_L, cx, cy, ch['backing'], -3, 70, min(2.4, max(1.3, min(w, hgt) / 26)), ldm=False); n += 1
        else:
            c = p.centroid
            B.add(GLOW_L, c.x, c.y, ch['backing'], -3, 70, min(2.6, max(1.3, max(w, hgt) / 34)), ldm=False); n += 1
    ctx.report['hazard_backing'] = n
