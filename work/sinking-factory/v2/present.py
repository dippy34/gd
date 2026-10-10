"""Presentation images: before/after, versus references, strips overview, stats table."""
import sys, json, statistics as st
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refrender as RR, lookstats as LS
OUT = HERE.parents[1].parent / 'outputs'
SH = HERE / 'shots'
try:
    FONT = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 22)
    SMALL = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 17)
except Exception:
    FONT = SMALL = ImageFont.load_default()

def tile(path, size):
    return Image.open(path).convert('RGB').resize(size, Image.LANCZOS)

def label(img, xy, text, font=FONT):
    d = ImageDraw.Draw(img)
    x, y = xy
    d.rectangle((x, y, x + d.textlength(text, font=font) + 16, y + 30), fill=(0, 0, 0))
    d.text((x + 8, y + 4), text, fill=(255, 214, 170), font=font)

# 1. before / after
pairs = [('ship', 'Ship'), ('wave', 'Wave'), ('robot', 'Robot'), ('ufo', 'UFO')]
W, Hh = 900, 506
ba = Image.new('RGB', (W * 2 + 12, (Hh + 12) * len(pairs)), (12, 8, 8))
for i, (f, name) in enumerate(pairs):
    y = i * (Hh + 12)
    ba.paste(tile(SH / 'final-base' / f'{f}.png', (W, Hh)), (0, y))
    ba.paste(tile(SH / 'final' / f'{f}.png', (W, Hh)), (W + 12, y))
    label(ba, (10, y + 10), f'BEFORE  MELTDOWN / {name}')
    label(ba, (W + 22, y + 10), f'AFTER  MELTDOWN v2 / {name}')
ba.save(OUT / 'The Sinking Factory - MELTDOWN v2 Before-After.png')

# 2. versus references (same renderer, same glow stand-ins)
R = RR.R; R.load_atlas(); names = RR.load_names()
R.SYNTH.update({'__glow_small': 48, '__glow_med': 64, '__glow_large': 80})
for k in ('__glow_small', '__glow_med', '__glow_large'):
    R._cache.pop(k, None)
refs = []
for lvl_path, cx, cy, tag in [('refs/avernus-89496627.level', 23100, 165, 'Avernus (render)'), ('refs/avernus-89496627.level', 16300, 165, 'Avernus (render)'),
                              ('refs/flamewall-126242564.level', 72400, 820, 'Flamewall (render)'), ('refs/flamewall-126242564.level', 72900, 820, 'Flamewall (render)')]:
    lvl = RR.Level(HERE / lvl_path)
    f = SH / f'ref-{cx}.png'
    RR.shot(lvl, names, cx, cy, f, ppu=1.7)
    refs.append((f, f'{tag} x={cx}'))
mine = [(SH / 'final' / 'ufo.png', 'MELTDOWN v2 / UFO'), (SH / 'final' / 'robot.png', 'MELTDOWN v2 / Robot'),
        (SH / 'final' / 'wave.png', 'MELTDOWN v2 / Wave'), (SH / 'final' / 'moving-platform.png', 'MELTDOWN v2 / Moving platform')]
vr = Image.new('RGB', (W * 2 + 12, (Hh + 12) * 4), (12, 8, 8))
for i in range(4):
    y = i * (Hh + 12)
    vr.paste(tile(refs[i][0], (W, Hh)), (0, y)); label(vr, (10, y + 10), refs[i][1])
    vr.paste(tile(mine[i][0], (W, Hh)), (W + 12, y)); label(vr, (W + 22, y + 10), mine[i][1])
vr.save(OUT / 'The Sinking Factory - MELTDOWN v2 vs References.png')

# 3. strips overview
strips = sorted((SH / 'final').glob('strip-*.png'), key=lambda p: int(p.stem.split('-')[1]))
ims = [Image.open(p).convert('RGB') for p in strips]
width = 1800
scaled = [im.resize((width, int(im.height * width / im.width)), Image.LANCZOS) for im in ims]
ov = Image.new('RGB', (width, sum(s.height + 44 for s in scaled)), (12, 8, 8))
y = 0
titles = ['Furnace intake (ship)', 'Pressure duct (wave)', 'Smelter hall (robot + moving platform)', 'Turbine hall (UFO) and exit flare']
for s, t in zip(scaled, titles):
    label(ov, (10, y + 7), t)
    ov.paste(s, (0, y + 44)); y += s.height + 44
ov.save(OUT / 'The Sinking Factory - MELTDOWN v2 Full Section.png')

# 4. preview sheet copy
Image.open(SH / 'final' / 'sheet.png').save(OUT / 'The Sinking Factory - MELTDOWN v2 Preview.png')

# 5. stats table
ref = json.load(open(HERE / 'refs/video-targets.json'))
base = json.load(open(SH / 'final-base' / 'stats.json')); fin = json.load(open(SH / 'final' / 'stats.json'))
gameplay = [r for r in fin if r['name'] != 'UFO exit']; base_g = [r for r in base if r['name'] != 'UFO exit']
def med(rows, k): return st.median(r[k] for r in rows)
def grad(rows): return st.median((r['bands'][4] + r['bands'][5]) / 2 / max(.005, (r['bands'][0] + r['bands'][1]) / 2) for r in rows)
rows = [
    ('Near-black share of screen', 'black'), ('Bright share (>0.5)', 'bright'), ('Average brightness', 'mean'),
    ('Contrast (std)', 'std'), ('Edge density', 'edge'),
]
table = [['Measure', 'Avernus video', 'Flamewall video', 'MELTDOWN (before)', 'MELTDOWN v2']]
for title, k in rows:
    table.append([title, f"{ref['avernus'][k][1]:.3f}", f"{ref['flamewall'][k][1]:.3f}", f'{med(base_g, k):.3f}', f'{med(gameplay, k):.3f}'])
av_g = (ref['avernus']['bands'][4] + ref['avernus']['bands'][5]) / (ref['avernus']['bands'][0] + ref['avernus']['bands'][1])
fw_g = (ref['flamewall']['bands'][4] + ref['flamewall']['bands'][5]) / (ref['flamewall']['bands'][0] + ref['flamewall']['bands'][1])
table.append(['Bottom vs top brightness', f'{av_g:.2f}x', f'{fw_g:.2f}x', f'{grad(base_g):.2f}x', f'{grad(gameplay):.2f}x'])
(HERE / 'out' / 'stats-table.json').write_text(json.dumps(table, indent=1))
cw = [330, 170, 180, 200, 170]
img = Image.new('RGB', (sum(cw) + 20, 44 * len(table) + 20), (16, 10, 10))
d = ImageDraw.Draw(img)
for j, row in enumerate(table):
    x = 10
    for c, (cell, w) in enumerate(zip(row, cw)):
        col = (255, 214, 170) if j == 0 else (230, 230, 230) if c == 0 else (255, 150, 90) if c == 4 else (200, 190, 185)
        d.text((x + 6, 18 + j * 44), cell, fill=col, font=FONT if j == 0 or c == 4 else SMALL)
        x += w
    d.line((10, 54 + j * 44, sum(cw) + 10, 54 + j * 44), fill=(60, 40, 36))
img.save(OUT / 'The Sinking Factory - MELTDOWN v2 Measurements.png')
for r in table: print(r)
