import sys, json; sys.path.insert(0,'.')
from PIL import Image, ImageDraw
import render as R
from gdparse import load
R.load_atlas()
names = R.load_names('../research/objectids.yml')
names[1887]='__glow_small'; names[1886]='__glow_med'; names[1888]='__glow_large'
for i in (507,508,512,513,514,578,579,584,585,587,597): names.setdefault(i,'d_gradient_c_05_001.png')
for i in (468,1338,1339,1835,1836,1837,1155,1207,1224): names.setdefault(i,'blockOutline_06_001.png')
for i in (1353,1354,1743,1744,1790,1792,1804,1833): names.setdefault(i,'block009b_01_001.png')
for i in (94,136,569,902,1099,1202,1220,1510,1511,1755,1758,1760,1761,1892,2950): names.setdefault(i,'square_01_001.png')
path = sys.argv[1]; tag = sys.argv[2]
head, objs = load(path)
pal = R.Palette(head, objs)
wins = json.loads(sys.argv[3])
tiles = []
for (a, yc) in wins:
    R.render(objs, pal, names, a, a + 600, yc - 170, yc + 170, ppu=0.9, out='/tmp/_t.png')
    tiles.append((a, Image.open('/tmp/_t.png').copy()))
w, h = tiles[0][1].size
cols = 2; rows = (len(tiles) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * (h + 16)), (18, 18, 20))
d = ImageDraw.Draw(sheet)
for i, (a, im) in enumerate(tiles):
    sheet.paste(im, (i % cols * w, i // cols * (h + 16) + 16))
    d.text((i % cols * w + 6, i // cols * (h + 16) + 3), f"x {a}", fill=(210, 210, 220))
sheet.save(f'shots/{tag}-sheet.png')
print('sheet', sheet.size)
