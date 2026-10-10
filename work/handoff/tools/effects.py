"""Set-piece effects. Everything takes the camera centre so it lands inside the
band the player can actually see."""
import math

def build(ctx):
    """ctx supplies: deco, group, rotate, move, colour, pulse, rng, ids, channels."""
    deco = ctx['deco']; group = ctx['group']; rotate = ctx['rotate']; move = ctx['move']
    rng = ctx['rng']
    ORB, DOT, STARSPR, LINE, GRAD, BLOCK = ctx['ORB'], ctx['DOT'], ctx['STARSPR'], ctx['LINE'], ctx['GRAD'], ctx['BLOCK']
    SPIRAL = ctx['SPIRAL']
    E = {}

    def trail(pts, color, *, size=1.2, val=.4, z=-3, zo=-300, spacing=10.0,
              group_id=0, ldm_every=2):
        n = 0
        for i in range(len(pts) - 1):
            x0, y0 = pts[i]; x1, y1 = pts[i + 1]
            L = math.hypot(x1 - x0, y1 - y0)
            steps = max(1, int(L / spacing))
            for k in range(steps):
                t = k / steps
                deco(ORB, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, color, z=z, zo=zo,
                     sx=size * rng.uniform(.88, 1.14), val=val, group_id=group_id,
                     ldm=(n % ldm_every == 1))
                n += 1
        return n
    E['trail'] = trail

    def ring(cx, cy, r, color, *, size=1.2, val=.4, z=-3, zo=-300, squash=1.0,
             arc=math.tau, a0=0.0, group_id=0, spacing=8.5, ldm_every=2):
        n = max(24, int(arc * r / spacing))
        for i in range(n):
            a = a0 + arc * i / n
            deco(ORB, cx + math.cos(a) * r, cy + math.sin(a) * r * squash, color,
                 z=z, zo=zo, sx=size * rng.uniform(.9, 1.12), val=val,
                 group_id=group_id, ldm=(i % ldm_every == 1))
        return n
    E['ring'] = ring

    def arc_line(cx, cy, r, color, *, arc=math.tau, a0=0.0, z=-3, zo=-280,
                 thick=1.4, val=.8, squash=1.0, seg=80, group_id=0):
        for i in range(seg):
            a = a0 + arc * (i + .5) / seg
            step = arc * r / seg
            deco(LINE, cx + math.cos(a) * r, cy + math.sin(a) * r * squash, color,
                 z=z, zo=zo, sx=(step * 1.6) / 30, sy=thick,
                 rot=math.degrees(math.atan2(math.cos(a) * squash, -math.sin(a))),
                 val=val, group_id=group_id, ldm=(i % 2 == 1))
        return seg
    E['arc_line'] = arc_line

    # ------------------------------------------------------------ black hole
    def filled_black(cx, cy, r, colour_id, *, z=-3, zo=0, group_id=0):
        """An opaque black disc. d_small_ball is a filled circle, so one object
        does the job cleanly -- a grid of squares left visible seams."""
        deco(DOT, cx, cy, colour_id, z=z, zo=zo, sx=r * 2 / 8.0, val=1.0,
             group_id=group_id)
        deco(DOT, cx, cy, colour_id, z=z, zo=zo + 1, sx=r * 1.9 / 8.0, val=1.0,
             group_id=group_id)
        return 2
    E['filled_black'] = filled_black

    def black_hole(x, cy, R, colours, *, tilt=None, jets=True, z=-3, zo=-340,
                   spin=True, intensity=1.0):
        """A hard black core, a thin tilted accretion disc that passes in front of
        it and behind it, the photon ring, spiral in-fall and polar jets."""
        HOT, RIM, DIM, CORE = colours
        n = 0
        tilt = rng.uniform(9, 20) if tilt is None else tilt
        squash = math.sin(math.radians(tilt))
        gdisc = group(); gback = group(); gspin = group(); gcore = group()
        # the far half of the disc, behind the core
        for k in range(3):
            rr = R * (0.95 + k * 0.22)
            n += ring(x, cy, rr, HOT if k == 0 else RIM, size=1.5 - k * .2,
                      val=(.66 - k * .16) * intensity, squash=squash,
                      arc=math.pi, a0=0.0, z=z, zo=zo - 30 - k, spacing=6.5,
                      group_id=gback)
        # the core, opaque, drawn over the far half
        n += filled_black(x, cy, R * .52, CORE, z=z, zo=zo, group_id=gcore)
        # the photon ring hugging it
        n += arc_line(x, cy, R * .55, HOT, z=z, zo=zo + 4, thick=1.3,
                      val=1.0 * intensity, seg=150)
        n += ring(x, cy, R * .60, HOT, size=1.0, val=.42 * intensity, z=z,
                  zo=zo + 3, spacing=7.0)
        # the near half of the disc, in front of the core
        for k in range(3):
            rr = R * (0.95 + k * 0.22)
            m = max(34, int(math.pi * rr / 6.5))
            for i in range(m):
                a = math.pi + math.pi * i / m
                doppler = .5 + .9 * (0.5 + 0.5 * math.cos(a))
                deco(ORB, x + math.cos(a) * rr, cy + math.sin(a) * rr * squash,
                     HOT if k == 0 else RIM, z=z, zo=zo + 6 + k,
                     sx=(1.5 - k * .2) * rng.uniform(.9, 1.1),
                     val=(.66 - k * .16) * doppler * intensity,
                     group_id=gdisc, ldm=(i % 2 == 1)); n += 1
        n += arc_line(x, cy, R * .95, HOT, arc=math.pi, a0=math.pi, z=z, zo=zo + 9,
                      thick=1.2, val=.85 * intensity, squash=squash, seg=120)
        # spiral in-fall
        for arm in range(rng.randint(3, 5)):
            a0 = rng.uniform(0, math.tau); pts = []
            for i in range(46):
                t = i / 45
                a = a0 + t * 3.4
                rr = R * (2.2 - 1.5 * t)
                pts.append((x + math.cos(a) * rr,
                            cy + math.sin(a) * rr * math.sin(math.radians(tilt)) * 1.5))
            n += trail(pts, DIM, size=.85, val=.20 * intensity, z=z, zo=zo - 40,
                       spacing=8.0, group_id=gspin)
        # polar jets
        if jets:
            for s in (1, -1):
                for i in range(34):
                    t = i / 33
                    deco(ORB, x + rng.uniform(-6, 6) * (1 + t * 4),
                         cy + s * (R * .5 + t * R * 3.0),
                         HOT if t < .3 else RIM, z=z, zo=zo - 60,
                         sx=(1.4 - t * .8) * 1.4, val=(.5 - .42 * t) * intensity,
                         ldm=(i % 2 == 1)); n += 1
        if spin:
            rotate(max(0, x - 420), gspin, gcore, turns=1, dur=rng.uniform(26, 60))
        return n
    E['black_hole'] = black_hole

    # ---------------------------------------------------------------- aurora
    def aurora(x0, x1, cy, colours, *, bands=4, amp=70, z=-5, zo=-720, val=.15):
        """Wavy ribbons of light, each band offset and dimmer than the last."""
        n = 0
        for b in range(bands):
            ph = rng.uniform(0, 6.3); k = rng.uniform(.0032, .0068)
            off = (b - bands / 2) * rng.uniform(22, 46)
            col = colours[b % len(colours)]
            pts = []
            x = x0
            while x < x1:
                pts.append((x, cy + off + amp * math.sin(x * k + ph)
                            + amp * .35 * math.sin(x * k * 2.3 + ph * 1.7)))
                x += 26
            # a bright thin core inside a soft halo, so it reads as a ribbon
            # instead of a smear
            n += trail(pts, col, size=2.4, val=val * .28 * (1 - b * .18),
                       z=z, zo=zo - b - 2, spacing=17, ldm_every=1)
            n += trail(pts, col, size=.42, val=min(1.0, val * 3.4) * (1 - b * .18),
                       z=z, zo=zo - b, spacing=7, ldm_every=2)
        return n
    E['aurora'] = aurora

    # ----------------------------------------------------------- warp tunnel
    def warp_tunnel(x, cy, colours, *, rings=9, rmax=520, z=-5, zo=-760):
        HOT, RIM, DIM, _ = colours
        n = 0; g = group(); gc = group()
        deco(DOT, x, cy, DIM, z=z, zo=zo, sx=.05, val=.05, group_id=gc); n += 1
        for i in range(rings):
            t = (i + 1) / rings
            n += ring(x, cy, rmax * t ** 1.7, RIM if i % 2 else HOT, size=1.1 + t,
                      val=.34 * (1 - t * .55), z=z, zo=zo - i, squash=.72,
                      group_id=g, spacing=7.5)
        for i in range(16):
            a = math.tau * i / 16
            pts = [(x + math.cos(a) * rmax * .1, cy + math.sin(a) * rmax * .07),
                   (x + math.cos(a) * rmax, cy + math.sin(a) * rmax * .72)]
            n += trail(pts, DIM, size=1.0, val=.14, z=z, zo=zo - 20, spacing=7)
        rotate(max(0, x - 400), g, gc, turns=1, dur=rng.uniform(30, 70))
        return n
    E['warp_tunnel'] = warp_tunnel

    # ---------------------------------------------------------- grid horizon
    def grid_horizon(x, cy, color, *, w=1100, z=-5, zo=-800, val=.20):
        n = 0
        hor = cy + rng.choice([-150, 150])
        depth = 1 if hor < cy else -1
        for i in range(11):
            t = (i / 10) ** 2.1
            yy = hor - depth * t * 300
            deco(LINE, x + w / 2, yy, color, z=z, zo=zo, sx=w / 30,
                 sy=.8 + t * 1.2, val=val * (.35 + t), ldm=(i % 2 == 1)); n += 1
        for i in range(19):
            u = (i - 9) / 9.0
            for k in range(9):
                t = (k / 8) ** 2.1
                yy = hor - depth * t * 300
                deco(DOT, x + w / 2 + u * w * .5 * (t * .92 + .08), yy, color,
                     z=z, zo=zo, sx=.16 + t * .2, val=val * (.3 + t), ldm=True); n += 1
        return n
    E['grid_horizon'] = grid_horizon

    # --------------------------------------------------------- constellation
    def constellation(x, cy, color, *, spread=260, stars=9, z=-3, zo=-260):
        n = 0
        pts = [(x + rng.uniform(-spread, spread), cy + rng.uniform(-150, 150))
               for _ in range(stars)]
        pts.sort()
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay)
            deco(LINE, (ax + bx) / 2, (ay + by) / 2, color, z=z, zo=zo,
                 sx=L / 30, sy=.55, rot=math.degrees(math.atan2(by - ay, bx - ax)),
                 val=.30, ldm=True); n += 1
        for (px, py) in pts:
            deco(ORB, px, py, color, z=z, zo=zo + 2, sx=rng.uniform(.5, 1.0), val=.85); n += 1
            deco(STARSPR, px, py, color, z=z, zo=zo + 3, sx=rng.uniform(.06, .11), val=1.0); n += 1
            n += 0
        return n + len(pts)
    E['constellation'] = constellation

    # ------------------------------------------------------------- lightning
    def lightning(x, cy, color, *, length=420, z=-3, zo=-240, val=.7, forks=3):
        n = 0
        def bolt(px, py, ang, ln, w, depth):
            nonlocal n
            steps = max(3, int(ln / 40))
            for i in range(steps):
                seg = ln / steps
                na = ang + rng.uniform(-26, 26)
                nx = px + math.cos(math.radians(na)) * seg
                ny = py + math.sin(math.radians(na)) * seg
                deco(LINE, (px + nx) / 2, (py + ny) / 2, color, z=z, zo=zo,
                     sx=seg / 30, sy=w, rot=na, val=val, ldm=(i % 2 == 1)); n += 1
                deco(ORB, nx, ny, color, z=z, zo=zo - 1, sx=w * .9, val=val * .5,
                     ldm=True); n += 1
                if depth and rng.random() < .32:
                    bolt(nx, ny, na + rng.choice([-52, 52]), ln * .42, w * .6, depth - 1)
                px, py, ang = nx, ny, na
        bolt(x, cy + rng.choice([-160, 160]), rng.choice([-90, 90]) + rng.uniform(-24, 24),
             length, 1.5, forks)
        return n
    E['lightning'] = lightning

    # -------------------------------------------------------------- orbiters
    def orbiters(x, cy, colours, *, z=-3, zo=-300):
        HOT, RIM, DIM, _ = colours
        n = 0; gc = group()
        deco(DOT, x, cy, DIM, z=z, zo=zo, sx=.05, val=.05, group_id=gc); n += 1
        deco(ORB, x, cy, HOT, z=z, zo=zo + 2, sx=2.2, val=.55); n += 1
        for k in range(rng.randint(2, 4)):
            g = group()
            r = rng.uniform(70, 230); sq = rng.uniform(.35, 1.0)
            n += ring(x, cy, r, DIM, size=.8, val=.10, squash=sq, z=z, zo=zo - 8,
                      spacing=6.5, ldm_every=1)
            a = rng.uniform(0, 6.3)
            for j in range(rng.randint(1, 3)):
                aa = a + j * 2.1
                deco(ORB, x + math.cos(aa) * r, cy + math.sin(aa) * r * sq, RIM,
                     z=z, zo=zo + 1, sx=rng.uniform(1.0, 1.9), val=.75, group_id=g); n += 1
            rotate(max(0, x - 380), g, gc, turns=1, dur=rng.uniform(9, 26))
        return n
    E['orbiters'] = orbiters

    # ----------------------------------------------------------------- comet
    def comet(x, cy, colours, *, z=-3, zo=-250):
        HOT, RIM, DIM, _ = colours
        n = 0; g = group()
        ang = rng.uniform(-34, 34) + 180
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        for i in range(46):
            t = i / 45
            deco(ORB, x + ca * t * 620, cy + sa * t * 620, HOT if t < .12 else RIM,
                 z=z, zo=zo - i, sx=(1.9 - t * 1.5) * 1.25, val=.8 * (1 - t) ** 1.6,
                 group_id=g, ldm=(i % 2 == 1)); n += 1
        move(max(0, x - 500), g, -ca * 420, -sa * 420, rng.uniform(3.5, 7.0))
        return n
    E['comet'] = comet

    # ----------------------------------------------------------------- nebula
    def nebula(x, cy, colours, *, w=900, z=-5, zo=-860):
        HOT, RIM, DIM, _ = colours
        n = 0
        for i in range(rng.randint(4, 8)):
            cx = x + rng.uniform(-w / 2, w / 2); yy = cy + rng.uniform(-190, 190)
            r = rng.uniform(70, 210)
            for k in range(3):
                deco(ORB, cx, yy, (DIM, RIM, HOT)[k % 3], z=z, zo=zo - k,
                     sx=r / 20 * (.5 + k * .45), val=(.075 - k * .02), ldm=k > 0); n += 1
        return n
    E['nebula'] = nebula

    # ------------------------------------------------------------- shockwave
    def shockwave(x, cy, colours, *, n_rings=5, z=-5, zo=-700):
        HOT, RIM, DIM, _ = colours
        n = 0
        for k in range(n_rings):
            r = 130 + k * 175
            n += ring(x + k * 26, cy, r, HOT if k < 2 else RIM, size=1.5 - k * .16,
                      val=(.42 - k * .07), squash=rng.uniform(.78, 1.0), z=z,
                      zo=zo - k, spacing=7)
            if k < 2:
                n += arc_line(x + k * 26, cy, r, HOT, z=z, zo=zo - k + 2,
                              thick=1.2, val=.55 - k * .15, seg=130)
        return n
    E['shockwave'] = shockwave

    # --------------------------------------------------------------- eclipse
    def eclipse(x, cy, R, colours, *, z=-3, zo=-320):
        """A black disc with a blazing corona -- the simplest strong image there
        is, and it reads instantly at any size."""
        HOT, RIM, DIM, CORE = colours
        n = 0
        for k in range(5):                      # corona
            n += ring(x, cy, R * (1.02 + k * .16), HOT if k < 2 else RIM,
                      size=1.5 + k * .5, val=(.42 - k * .07), z=z, zo=zo - 20 - k,
                      spacing=6.5)
        for i in range(34):                     # ragged corona streamers
            a = math.tau * i / 34 + rng.uniform(-.05, .05)
            ln = R * rng.uniform(.35, 1.5)
            pts = [(x + math.cos(a) * R * 1.02, cy + math.sin(a) * R * 1.02),
                   (x + math.cos(a) * (R * 1.02 + ln), cy + math.sin(a) * (R * 1.02 + ln))]
            n += trail(pts, RIM, size=.9, val=.18, z=z, zo=zo - 30, spacing=5.5)
        n += filled_black(x, cy, R, CORE, z=z, zo=zo)
        n += arc_line(x, cy, R * 1.005, HOT, z=z, zo=zo + 4, thick=1.4, val=1.0, seg=170)
        return n
    E['eclipse'] = eclipse

    # ---------------------------------------------------------------- pulsar
    def pulsar(x, cy, colours, *, z=-3, zo=-300, arms=3, length=460):
        HOT, RIM, DIM, _ = colours
        n = 0
        g = group(); gc = group()
        deco(DOT, x, cy, DIM, z=z, zo=zo, sx=.05, val=.05, group_id=gc); n += 1
        for k in range(arms):
            a = math.tau * k / arms + rng.uniform(-.2, .2)
            for s in (1, -1):
                for i in range(46):
                    t = i / 45
                    deco(ORB, x + math.cos(a) * s * t * length,
                         cy + math.sin(a) * s * t * length * .8,
                         HOT if t < .18 else RIM, z=z, zo=zo - 10,
                         sx=(1.0 - t * .7) * 1.1, val=.75 * (1 - t) ** 1.9,
                         group_id=g, ldm=(i % 2 == 1)); n += 1
        for k in range(3):
            deco(ORB, x, cy, HOT, z=z, zo=zo + 4, sx=1.4 + k * 1.6,
                 val=.85 - k * .25); n += 1
        rotate(max(0, x - 400), g, gc, turns=1, dur=rng.uniform(8, 20))
        return n
    E['pulsar'] = pulsar

    # ------------------------------------------------------------------ rift
    def rift(x, cy, colours, *, z=-3, zo=-260, height=460):
        """A jagged tear of light, brightest at the middle."""
        HOT, RIM, DIM, CORE = colours
        n = 0
        pts = []
        y = cy - height / 2
        px = x
        while y < cy + height / 2:
            pts.append((px, y))
            px += rng.uniform(-26, 26); y += rng.uniform(24, 46)
        n += trail(pts, HOT, size=1.0, val=.9, z=z, zo=zo + 3, spacing=5)
        n += trail(pts, RIM, size=3.0, val=.16, z=z, zo=zo, spacing=9)
        for (bx, by) in pts[::2]:
            for s in (1, -1):
                ln = rng.uniform(30, 120)
                a = rng.uniform(-40, 40) + (0 if s > 0 else 180)
                p2 = (bx + math.cos(math.radians(a)) * ln, by + math.sin(math.radians(a)) * ln)
                n += trail([(bx, by), p2], RIM, size=.7, val=.35, z=z, zo=zo + 1, spacing=4.5)
        return n
    E['rift'] = rift

    # ------------------------------------------------- the great black hole
    def great_black_hole(x, cy, R, colours, *, z=-3, zo=-420, tilt=11.0,
                         front=0.0):
        """The centrepiece: a hole big enough that the corridor is silhouetted
        against it. Edge-on accretion disc with a Doppler-bright leading side,
        the lensed image of the far side arching over and under the core, star
        streams falling in, and polar jets. The disc and the streams turn on
        separate Rotate triggers so it never sits still."""
        HOT, RIM, DIM, CORE = colours
        n = 0
        sq = math.sin(math.radians(tilt))
        gdisc = group(); gstream = group(); glens = group(); gcore = group()

        # the outer bloom the whole thing sits in
        for k in range(5):
            deco(ORB, x, cy, DIM, z=-5, zo=zo - 300 - k, sx=R / 16 * (1.0 + k * .55),
                 val=.16 - k * .028, ldm=k > 1); n += 1

        # far half of the disc, occluded by the core
        for k in range(5):
            rr = R * (1.55 + k * 0.21)
            m = max(40, int(math.pi * rr / 7.0))
            for i in range(m):
                a = math.pi * i / m
                dop = .40 + 1.05 * (0.5 + 0.5 * math.cos(a))
                deco(ORB, x + math.cos(a) * rr, cy + math.sin(a) * rr * sq,
                     HOT if k < 2 else RIM, z=z, zo=zo - 40 - k,
                     sx=(2.1 - k * .22), val=(.60 - k * .09) * dop,
                     group_id=gdisc, ldm=(i % 2 == 1)); n += 1

        # the lensed image of the far side, arching over and under the core
        for s in (1, -1):
            for k in range(3):
                rr = R * (1.06 + k * .12)
                m = max(46, int(math.pi * rr / 8.0))
                for i in range(m):
                    a = (0 if s > 0 else math.pi) + math.pi * i / m
                    deco(ORB, x + math.cos(a) * rr, cy + math.sin(a) * rr * (0.92 - k * .06),
                         HOT if k == 0 else RIM, z=z, zo=zo - 12 - k,
                         sx=1.7 - k * .3, val=(.50 - k * .13),
                         group_id=glens, ldm=(i % 2 == 1)); n += 1
            n += arc_line(x, cy, R * 1.06, HOT, arc=math.pi * .96,
                          a0=(0.09 if s > 0 else math.pi + 0.09), z=z, zo=zo - 8,
                          thick=1.3, val=.75, squash=0.92, seg=110)

        # the core and the photon ring
        n += filled_black(x, cy, R, CORE, z=z, zo=zo, group_id=gcore)
        n += arc_line(x, cy, R * 1.012, HOT, z=z, zo=zo + 6, thick=1.7, val=1.0, seg=200)
        n += ring(x, cy, R * 1.06, HOT, size=1.3, val=.45, z=z, zo=zo + 4, spacing=7)

        # near half of the disc, passing in front of the core
        for k in range(5):
            rr = R * (1.55 + k * 0.21)
            m = max(40, int(math.pi * rr / 7.0))
            for i in range(m):
                a = math.pi + math.pi * i / m
                dop = .40 + 1.05 * (0.5 + 0.5 * math.cos(a))
                deco(ORB, x + math.cos(a) * rr, cy + math.sin(a) * rr * sq,
                     HOT if k < 2 else RIM, z=z, zo=zo + 10 + k,
                     sx=(2.1 - k * .22), val=(.60 - k * .09) * dop,
                     group_id=gdisc, ldm=(i % 2 == 1)); n += 1
        n += arc_line(x, cy, R * 1.55, HOT, arc=math.pi, a0=math.pi, z=z, zo=zo + 16,
                      thick=1.5, val=.9, squash=sq, seg=140)

        # star streams falling in
        for arm in range(7):
            a0 = math.tau * arm / 7 + rng.uniform(-.2, .2)
            for j in range(46):
                t = j / 45
                a = a0 + t * 3.1
                rr = R * (4.6 - 3.0 * t)
                px = x + math.cos(a) * rr
                py = cy + math.sin(a) * rr * (0.30 + 0.55 * (1 - t))
                deco(STARSPR, px, py, HOT if t > .8 else RIM, z=z, zo=zo - 80,
                     sx=0.05 + 0.05 * t, val=.45 + .55 * t, group_id=gstream,
                     ldm=(j % 2 == 1)); n += 1

        # polar jets
        for s in (1, -1):
            for i in range(40):
                t = i / 39
                deco(ORB, x + rng.uniform(-4, 4) * (1 + t * 5),
                     cy + s * (R * 1.15 + t * R * 3.4), HOT if t < .22 else RIM,
                     z=z, zo=zo - 120, sx=(1.9 - t * 1.2) * 1.4,
                     val=(.55 - .48 * t), ldm=(i % 2 == 1)); n += 1

        # In a wave section the corridor covers most of the screen, so the hole's
        # bright features are mirrored in FRONT of the gameplay on an additive
        # channel. Light passing in front reads; an opaque core never would, so
        # only the glow is duplicated and the core stays behind.
        if front > 0:
            gf = group()
            # only the two features that make a black hole recognisable: the
            # photon ring and the edge-on disc cutting through it
            n += arc_line(x, cy, R * 1.015, HOT, z=7, zo=305, thick=2.4,
                          val=min(1.0, front * 2.2), seg=210)
            n += arc_line(x, cy, R * 1.10, HOT, z=7, zo=304, thick=1.2,
                          val=min(1.0, front * 1.3), seg=180)
            for k in range(3):
                rr = R * (1.55 + k * 0.34)
                m = max(40, int(math.tau * rr / 8.0))
                for i in range(m):
                    a = math.tau * i / m
                    dop = .35 + 1.15 * (0.5 + 0.5 * math.cos(a))
                    deco(ORB, x + math.cos(a) * rr, cy + math.sin(a) * rr * sq,
                         HOT if k == 0 else RIM, z=7, zo=300 - k,
                         sx=(1.7 - k * .3), val=front * (1.0 - k * .30) * dop,
                         group_id=gf, ldm=(i % 2 == 1)); n += 1
            n += arc_line(x, cy, R * 1.55, HOT, z=7, zo=303, thick=1.6,
                          val=min(1.0, front * 1.8), squash=sq, seg=170,
                          group_id=gf)
            rotate(max(0, x - 900), gf, gcore, turns=1, dur=13)
        rotate(max(0, x - 900), gdisc, gcore, turns=1, dur=13)
        rotate(max(0, x - 900), gstream, gcore, turns=1, dur=26)
        rotate(max(0, x - 900), glens, gcore, turns=1, dur=52)
        return n
    E['great_black_hole'] = great_black_hole
    return E
