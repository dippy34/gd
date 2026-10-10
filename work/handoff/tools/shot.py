"""Preview through the real camera: the window centre comes from cam.py."""
import sys, json; sys.path.insert(0,'.')
from PIL import Image, ImageDraw
import render as R
from gdparse import load
from kocmoc_terrain import Terrain
import cam
R.load_atlas()
names = R.load_names('../research/objectids.yml')
names[1887]='__glow_small'; names[1886]='__glow_med'; names[1888]='__glow_large'
path = sys.argv[1]; tag = sys.argv[2]; xs = json.loads(sys.argv[3])
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 2
head, objs = load(path)
pal = R.Palette(head, objs)
cam_y = cam.make(Terrain())
tiles = []
for a in xs:
    cy = cam_y(a + 300)
    R.render(objs, pal, names, a, a + 600, cy - 165, cy + 165, ppu=1.0, out='/tmp/_t.png')
    tiles.append((a, cy, Image.open('/tmp/_t.png').copy()))
w, h = tiles[0][2].size
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * (h + 15)), (16, 16, 18))
d = ImageDraw.Draw(sheet)
for i, (a, cy, im) in enumerate(tiles):
    sheet.paste(im, (i % cols * w, i // cols * (h + 15) + 15))
    d.text((i % cols * w + 5, i // cols * (h + 15) + 2), f"x {a}   camera y {cy:.0f}",
           fill=(200, 200, 210))
sheet.save(f'shots/{tag}.png')
print('sheet', sheet.size)
