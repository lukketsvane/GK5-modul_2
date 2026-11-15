import sys, math, os
from pathlib import Path
from html import escape
from PIL import Image, ImageDraw, ImageFont
import ruta_c as C
from teikning import Vising

OUT = Path(__file__).resolve().parent / "referansar-c"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1800, 1350
VIEWS = [
    ("01_front", "FRONT", ((0, -1, 0), (1, 0, 0))),
    ("02_back", "BAKSIDE", ((0, 1, 0), (-1, 0, 0))),
    ("03_left", "VENSTRE SIDE", ((-1, 0, 0), (0, -1, 0))),
    ("04_right", "HØGRE SIDE", ((1, 0, 0), (0, 1, 0))),
    ("05_top", "OVANFRÅ", ((0, 0, 1), (1, 0, 0))),
    ("06_bottom", "UNDANFRÅ", ((0, 0, -1), (1, 0, 0))),
    ("07_iso_front_left", "FRAMME · VENSTRE", ((-1, -1.3, 0.9), (1, -0.8, 0))),
    ("08_iso_front_right", "FRAMME · HØGRE", ((1, -1.3, 0.9), (1, 0.8, 0))),
    ("09_iso_back_left", "BAK · VENSTRE", ((-1, 1.3, 0.9), (-1, -0.8, 0))),
    ("10_iso_back_right", "BAK · HØGRE", ((1, 1.3, 0.9), (-1, 0.8, 0))),
    ("11_low_oblique", "LÅG FRAMVINKEL", ((0.3, -1.5, 0.3), (1, 0.2, 0))),
    ("12_high_oblique", "HØG FRAMVINKEL", ((0.4, -0.7, 2.0), (1, 0.4, 0)))
]
font_name = "C:/Windows/Fonts/arial.ttf"
font_bold = "C:/Windows/Fonts/arialbd.ttf"
f_title = ImageFont.truetype(font_bold, 40)
f_small = ImageFont.truetype(font_name, 22)
f_micro = ImageFont.truetype(font_name, 18)
parts = [d[2] for d in C.delar()]
views = [v for v in VIEWS if len(sys.argv) == 1 or v[0] in sys.argv[1:]]
pngs = []
for index, (slug, title, direction) in enumerate(views, 1):
    v = Vising(parts, direction)
    x0, y0, x1, y1 = 75, 115, W - 75, H - 175
    b = v.max - v.min
    scale = min((x1 - x0) / b[0], (y1 - y0) / b[1])
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    mx, my = (v.min[0] + v.max[0]) / 2, (v.min[1] + v.max[1]) / 2
    def proj(p):
        return (cx + (p[0] - mx) * scale, cy - (p[1] - my) * scale)
    im = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(im)
    paths = []
    for weight, poly in v.liner:
        pts = [proj(p) for p in poly]
        if len(pts) < 2:
            continue
        d.line(pts, fill=(18, 18, 18), width=3 if weight > 1 else 2, joint="curve")
        path = " ".join(("M" if j == 0 else "L") + f"{p[0]:.2f},{p[1]:.2f}" for j, p in enumerate(pts))
        paths.append(f'<path d="{path}" stroke-width="{1.8 if weight > 1 else 1.0}"/>')
    d.text((80, 40), f"{slug[:2]} / {title}", font=f_title, fill=(10, 10, 10))
    d.line([(80,H-140),(W-80,H-140)],fill=(50,50,50),width=2)
    d.text((80,H-117),"RUTA  /  CAD REVISJON C  /  VINKEL 35°",font=f_small, fill=(30,30,30))
    d.text((80,H-78),"Ø158 FOT  ·  300 × 190 LYSPLATE  ·  Ø36 BJELKE  ·  AKSE H260",font=f_micro,fill=(50,50,50))
    d.text((W-320,H-80),"IKKJE I MÅLESTOKK",font=f_micro, fill=(70,70,70))
    png = OUT / f"{slug}.png"
    svg = OUT / f"{slug}.svg"
    im.save(png, optimize=True)
    body = "\n".join(paths)
    svg.write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<rect width="100%" height="100%" fill="white"/>
<g fill="none" stroke="#111" stroke-linecap="round" stroke-linejoin="round">{body}</g>
<g font-family="Arial,Helvetica,sans-serif" fill="#111">
<text x="80" y="76" font-size="40" font-weight="bold">{escape(slug[:2]+" / "+title)}</text>
<line x1="80" x2="{W-80}" y1="{H-140}" y2="{H-140}" stroke="#555"/>
<text x="80" y="{H-98}" font-size="22">RUTA / CAD REVISJON C / VINKEL 35°</text>
<text x="80" y="{H-59}" font-size="18">Ø158 FOT · 300 × 190 LYSPLATE · Ø36 BJELKE · AKSE H260</text>
<text x="{W-320}" y="{H-59}" font-size="18">IKKJE I MÅLESTOKK</text>
</g></svg>''',encoding="utf-8")
    pngs.append(png)
    print(f"{index}/{len(views)} {slug}: {len(paths)} edges",flush=True)
if len(views)>1:
    thumbs = []
    for p in sorted(OUT.glob("[0-9][0-9]_*.png")):
        im = Image.open(p)
        im.thumbnail((900,675))
        thumbs.append(im.copy())
    for page in range(0,len(thumbs),4):
        sheet=Image.new("RGB",(1800,1350),(255,255,255))
        for j,img in enumerate(thumbs[page:page+4]):
            sheet.paste(img,((j%2)*900,(j//2)*675))
        sheet.save(OUT / f"oversikt_{page//4+1:02d}.png",optimize=True)
    import zipfile
    with zipfile.ZipFile(OUT / "RUTA_CAD_referansar_C.zip","w",compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(OUT.glob("*")):
            if p.suffix in (".svg",".png") and not p.name.startswith("oversikt"):
                z.write(p,p.name)
    print("DONE",str(OUT),flush=True)
