import json, sys, math, textwrap
from PIL import Image, ImageDraw, ImageFont

D, OUT = sys.argv[1], sys.argv[2]
ann = json.load(open(f'{D}/ann.json'))
PAPER = (238, 236, 231); INK = (34, 34, 32); MUTED = (95, 95, 90)
ACOL = (232, 182, 112); BCOL = (64, 126, 136)
F = 'C:/Windows/Fonts/'
f_title = ImageFont.truetype(F + 'segoeuib.ttf', 54)
f_sub = ImageFont.truetype(F + 'segoeui.ttf', 29)
f_cap = ImageFont.truetype(F + 'segoeui.ttf', 27)
f_step = ImageFont.truetype(F + 'segoeuib.ttf', 40)
f_badge = ImageFont.truetype(F + 'segoeuib.ttf', 26)

W, M = 1600, 22
COLW = (W - 3 * M) // 2

caps = {
    's0': ('Delane', 'Rygg (hakket) opp, front (U-opninga) ned. 1–6: spora opnar seg opp mot ryggen. 21–26: spora opnar seg ned mot fronten. Store ringar 79 mm, U-former 67 mm, skiver 34 mm, vogge 53 mm.'),
    's1': ('1', 'Set 3 og 4 ståande på U-beina, hakket opp, om lag 14 mm frå kvarandre. Senk 23 og 24 ned i dei korte spora ved hakket.'),
    's2': ('2', 'Løft kjernen. Skyv 2 og 5 opp nedanfrå, utanfor 3 og 4.'),
    's3': ('3', 'Senk 22 og 25 ned ovanfrå, utanfor 23 og 24.'),
    's4': ('4', 'Skyv skivene 1 og 6 opp nedanfrå, ytst på 1–6-sida.'),
    's5': ('5', 'Senk skivene 21 og 26 ned ovanfrå, ytst på 21–26-sida.'),
    's6': ('6', 'Legg kula på sida i vogga. U-opninga er fronten.'),
    's7': ('✓', 'Sjekk rett framanfrå: platene skal danne eit jamt rutemønster.'),
}


def panel_img(key, width):
    im = Image.open(f'{D}/{key}.png').convert('RGBA')
    bg = Image.new('RGBA', im.size, PAPER + (255,)); bg.alpha_composite(im)
    k = width / im.size[0]
    return bg.convert('RGB').resize((width, round(im.size[1] * k)), Image.LANCZOS), k


def badge(dr, x, y, n, k):
    A = isinstance(n, int) and n <= 6
    col = ACOL if A else (BCOL if isinstance(n, int) else (170, 140, 100))
    txt = str(n)
    tw = dr.textlength(txt, font=f_badge)
    r = 25
    w = max(2 * r, tw + 26)
    dr.rounded_rectangle([x - w / 2 - 3, y - r - 3, x + w / 2 + 3, y + r + 3], radius=r + 3, fill=(255, 255, 255))
    dr.rounded_rectangle([x - w / 2, y - r, x + w / 2, y + r], radius=r, fill=col)
    dr.text((x, y + 1), txt, font=f_badge, fill=INK if A or not isinstance(n, int) else (255, 255, 255), anchor='mm')


def arrow(dr, p, q, k):
    (x0, y0), (x1, y1) = p, q
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L
    head = 34
    bx, by = x1 - ux * head, y1 - uy * head
    nx, ny = -uy, ux
    tri = [(x1, y1), (bx + nx * 19, by + ny * 19), (bx - nx * 19, by - ny * 19)]
    dr.line([(x0, y0), (bx, by)], fill=(255, 255, 255), width=17)
    dr.polygon([(x1 + ux * 5, y1 + uy * 5), (bx + nx * 25 - ux * 4, by + ny * 25 - uy * 4), (bx - nx * 25 - ux * 4, by - ny * 25 - uy * 4)], fill=(255, 255, 255))
    dr.line([(x0, y0), (bx, by)], fill=INK, width=9)
    dr.polygon(tri, fill=INK)


def annotate(img, key, k):
    dr = ImageDraw.Draw(img)
    for a in ann[key]['ann']:
        if a['arrow']:
            (x0, y0), (x1, y1) = a['arrow']
            sgn = 1 if y1 > y0 else -1
            arrow(dr, (x0 * k, (y0 + sgn * 40) * k), (x1 * k, y1 * k), k)
    for a in ann[key]['ann']:
        x, y = a['label']
        badge(dr, x * k, y * k, a['n'], k)
    return img


def caption(step, text, width):
    lines = textwrap.wrap(text, width=int(width / 14.2))
    h = 18 + max(48, 36 * len(lines)) + 16
    im = Image.new('RGB', (width, h), PAPER); dr = ImageDraw.Draw(im)
    x = 0
    if step and step != 'Delane':
        dr.ellipse([0, 12, 52, 64], fill=INK); dr.text((26, 38), step, font=f_step if step != '✓' else ImageFont.truetype(F + 'seguisym.ttf', 32), fill=PAPER, anchor='mm'); x = 68
    elif step == 'Delane':
        dr.text((0, 14), 'Delane', font=f_step, fill=INK); x = 160
    for i, ln in enumerate(lines):
        dr.text((x, 18 + i * 36), ln, font=f_cap, fill=INK)
    return im


tiles = []
p0, k0 = panel_img('s0', W - 2 * M); annotate(p0, 's0', k0)
c0 = caption('Delane', caps['s0'][1], W - 2 * M)
rows = []
for i in range(0, 8 - 1, 2):
    keys = ['s1', 's2', 's3', 's4', 's5', 's6', 's7'][i:i + 2]
    cells = []
    for key in keys:
        im, k = panel_img(key, COLW); annotate(im, key, k)
        cells.append((im, caption(caps[key][0], caps[key][1], COLW)))
    rows.append(cells)

head_h = 200
total = head_h + p0.size[1] + c0.size[1] + M + sum(max(a.size[1] + b.size[1] for a, b in r) + M for r in rows) + M
canvas = Image.new('RGB', (W, total), PAPER); dr = ImageDraw.Draw(canvas)
dr.text((M, 22), 'Bordkula 1:3 — montering', font=f_title, fill=INK)
dr.text((M, 100), 'Kula ståande med fronten ned:  1–6 kjem alltid nedanfrå ↑   ·   21–26 kjem alltid ovanfrå ↓', font=f_sub, fill=INK)
dr.text((M, 142), 'Spora er 1,08 mm og platene 0,8 mm. Dei skal gli inn utan press. Skyv rett, vri aldri.', font=f_sub, fill=MUTED)
y = head_h
canvas.paste(p0, (M, y)); y += p0.size[1]
canvas.paste(c0, (M, y)); y += c0.size[1] + M
dr.line([(M, y - M // 2), (W - M, y - M // 2)], fill=(205, 202, 195), width=2)
for r in rows:
    rh = 0
    for j, (im, cap) in enumerate(r):
        x = M + j * (COLW + M)
        canvas.paste(im, (x, y)); canvas.paste(cap, (x, y + im.size[1]))
        rh = max(rh, im.size[1] + cap.size[1])
    y += rh + M
canvas = canvas.crop((0, 0, W, y))
canvas.save(OUT, optimize=True)
print(OUT, canvas.size)
