import sys
from PIL import Image
G, namn, s, a = sys.argv[1:5]
ut = Image.new("RGB", (2400, 580))
x = 0
for mappe in (s, a):
    ark = Image.open(f"{G}/{mappe}/ut/ark.png").convert("RGB")
    for rute in ((0, 0, 600, 580), (600, 0, 1200, 580)):
        ut.paste(ark.crop(rute), (x, 0))
        x += 600
ut.save(f"{G}/{namn}-par.png")
print(f"{G}/{namn}-par.png", ut.size)
