"""Time-evaluated atlas previews of a Sinking Factory build.

Uses work/preview_memory.py (colour triggers, pulses, alpha, move and rotate
evaluated at the moment the camera reaches each shot) plus the handoff atlas
renderer. Shots are the in-game camera window (570x320 units / zoom).

usage: v2_preview.py LEVEL TAG [shots-json]
"""
import os, sys, json, math, importlib
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SF = HERE.parent; WORK = SF.parent


def load(level, manifest=None):
    os.environ['GD_PREVIEW_LEVEL'] = str(level)
    os.environ['GD_PREVIEW_PLAN'] = str(manifest or (HERE / 'out' / 'preview-plan.json'))
    sys.path.insert(0, str(WORK))
    if 'preview_memory' in sys.modules:
        P = importlib.reload(sys.modules['preview_memory'])
    else:
        import preview_memory as P
    R = P.R
    if 'FireSheet_01' not in R.SHEETS:
        R.SHEETS += ['FireSheet_01', 'GJ_ParticleSheet']
        R.load_atlas()
    # Game-drawn glow orbs: stand-in sizes (px at 2 px/unit). 1888 ~40u, 1886 ~32u,
    # 1887 ~24u at scale 1 -- inferred from how Avernus sizes haze vs embers; not a
    # native measurement, so glow-heavy previews are approximate.
    R.SYNTH.update({'__glow_small': 48, '__glow_med': 64, '__glow_large': 80})
    for k in ('__glow_small', '__glow_med', '__glow_large'):
        R._cache.pop(k, None)
    for o in P.objs:
        if o['1'] == '899' and '23' not in o:
            o['23'] = '1'
        if o['1'] in ['10', '11', '12', '13', '47', '111', '660', '745', '1331', '99', '101', '200', '201', '202', '203',
                      '1334', '36', '84', '141', '1330', '1333', '1704', '1751']:
            o['21'] = '99999'; o['22'] = '99999'
    return P


SHOTS = [  # name, x, camera y, zoom  (bounded modes use their gamemode window centre)
    ('Ship', 17400, 150, .75), ('Ship climb', 17930, 150, .75), ('Wave', 19155, 180, 1), ('Wave exit', 20190, 180, 1),
    ('Robot', 21465, 300, 1), ('Moving platform', 22190, 235, 1), ('UFO', 23520, 150, 1), ('UFO exit', 24300, 150, 1),
]


def shot(P, x, cy, zoom, out, ppu=1.7, t_offset=0.0, hide_ids=()):
    R = P.R
    oo, pal = P.snapshot(x, P.tx(x) + t_offset)
    pal._c[1010] = ((0, 0, 0), False, 1)
    pal._c[99999] = ((255, 255, 255), False, 1)
    oo = [o for o in oo if int(o['1']) not in (1755, 2909, 2921, 1520, 1934, 1913, 1914, 31) and
          not P.names.get(int(o['1']), '').startswith('edit_') and o['1'] not in hide_ids]
    hw, hh = 285 / zoom, 160 / zoom
    bg = pal.get(1000)[0]
    R.render(oo, pal, P.names, x - hw, x + hw, cy - hh, cy + hh, ppu=ppu, bg=bg, out=str(out))
    return out


def sheet(files, labels, out, cols=2, tile=(760, 428)):
    rows = math.ceil(len(files) / cols)
    img = Image.new('RGB', (cols * tile[0], rows * (tile[1] + 26)), (10, 8, 8))
    d = ImageDraw.Draw(img)
    for i, (f, lab) in enumerate(zip(files, labels)):
        im = Image.open(f).convert('RGB').resize(tile, Image.LANCZOS)
        x = (i % cols) * tile[0]; y = (i // cols) * (tile[1] + 26)
        img.paste(im, (x, y + 26)); d.text((x + 8, y + 7), lab, fill=(230, 200, 170))
    img.save(out)
    return out


if __name__ == '__main__':
    level = sys.argv[1]; tag = sys.argv[2]
    shots = json.loads(sys.argv[3]) if len(sys.argv) > 3 else SHOTS
    P = load(level)
    od = HERE / 'shots' / tag; od.mkdir(parents=True, exist_ok=True)
    files = []; labels = []
    sys.path.insert(0, str(HERE))
    import lookstats as LS
    rows = []
    for name, x, cy, zoom in shots:
        f = od / f"{name.replace(' ', '-').lower()}.png"
        shot(P, x, cy, zoom, f)
        s = LS.stats(Image.open(f)); s['name'] = name; rows.append(s)
        files.append(f); labels.append(f'{name}  x={x}')
        print(f"{name:16} mean={s['mean']:.3f} black={s['black']:.3f} bright={s['bright']:.3f} vbright={s['vbright']:.3f} "
              f"edge={s['edge']:.3f} lsv={s['largeScaleVar']:.3f} std={s['std']:.3f} bands={s['bands']} hue0-30={s['hue'][0]:.2f} 30-60={s['hue'][1]:.2f} 330-360={s['hue'][11]:.2f}", flush=True)
    sheet(files, labels, od / 'sheet.png')
    json.dump(rows, open(od / 'stats.json', 'w'), indent=1)
    import statistics as st
    keys = ['mean', 'black', 'bright', 'vbright', 'edge', 'largeScaleVar', 'std']
    print('MEDIAN        ' + ' '.join(f"{k}={st.median(r[k] for r in rows):.3f}" for k in keys))
    print('bands median  ' + ' '.join(f"{st.median(r['bands'][i] for r in rows):.3f}" for i in range(6)))
