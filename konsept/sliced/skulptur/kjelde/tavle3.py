import sys
from PIL import Image, ImageDraw, ImageFont
# python tavle3.py <runde3-mappa> <ut.png>
D, OUT = sys.argv[1], sys.argv[2]
F = 'C:/Windows/Fonts/'
ft = ImageFont.truetype(F + 'segoeuib.ttf', 52); fs = ImageFont.truetype(F + 'segoeui.ttf', 26)
fn = ImageFont.truetype(F + 'segoeuib.ttf', 44); fb = ImageFont.truetype(F + 'segoeuib.ttf', 25); fc = ImageFont.truetype(F + 'segoeui.ttf', 24)
fl = ImageFont.truetype(F + 'segoeuib.ttf', 20); fk = ImageFont.truetype(F + 'segoeuib.ttf', 15)
PAPER = (238, 236, 231); INK = (32, 32, 30); MUTED = (110, 108, 102)

# (mappe, namn, konvolutt, handling, [(modus, ark, tekst)], tal)
design = [
    ('nikk-01b', 'Nikk', 'skulptur-01 · flat linse', 'Rull linsa i messingnavet',
     [('arbeid 0°', 'ark-arbeid.png', 'Gitteret ned: avskoren pøl på tastaturet, skjermen mørk. 3000 K.'),
      ('møte 100°', 'ark-mote.png', 'Opalfeltet bak gitteret mot andletet, ved sida av skjermen. 2700 K.'),
      ('kveld 160°', 'ark-kveld.png', 'Hovudet heller bakover: lys mot taket. 2200 K, dimma.'),
      ('møte · gråbeige', 'ark-mote-graabeige.png', 'Same møte i gråbeige #c9bfae: gitteret les mindre som grill.')],
     'linse 259 × 132 × 30 mm · 12 delar + 5 ekstra · 1 ark · 0,09 kg plater, om lag 1,4 kg heil · aksel 330 mm, fot Ø170 · svart #1d1d1d'),
    ('nikk-forrige', 'Nikk', 'skulptur-04 · rund tromme', 'Trykk messingknappen ned',
     [('arbeid −6°', 'ark-arbeid.png', 'Celler ned: pott over foten og venstre del av tastaturet. 3000 K.'),
      ('møte 85°', 'ark-mote.png', 'Opal-andlet Ø189 mot brukaren, veggvask ved skjermkanten. 2700 K.'),
      ('kveld 35°', 'ark-kveld.png', 'Halvt nikk: opalmåne over, svak veggvask. 2200 K.')],
     'hovud Ø184 × 52 mm · 14 delar + 3 ekstra · 1 ark · 0,11 kg plater, om lag 0,8 kg heil · 425 mm høg, fot Ø160 · mørkegrøn #3f4b42'),
    ('rokkestein', 'Rokkestein', 'skulptur-05 · flat stein', 'Løft framkanten: steinen rokkar',
     [('arbeid 0°', 'ark-arbeid.png', 'Nedre LED-rad: pøl på papiret og bordet, veggen mørk. 3000 K.'),
      ('kveld og møte −30°', 'ark-kveld.png', 'Øvre rad tek over: glorie på veggen ved skjermen. 2400 K, 35 %.')],
     'hovud 254 × 132 × 44 mm · 8 delar, alle opal · 1 ark · om lag 1,0 kg heil · 275 mm høg, fot Ø130 · grøn berar #3f4b42'),
    ('hei', 'Hei', 'skulptur-11 · hatten utan stilk', 'Lett på hatten',
     [('arbeid 0°', 'ark-hei-arbeid.png', 'Tre nedlys: brei pøl fram mot tastaturet, veggen mørk. 3000 K.'),
      ('møte og kveld −20°', 'ark-hei-mote.png', 'Opplys: varm vifte på veggen bak, hatten gløder. 2700–2200 K.')],
     'hatt 146 × 204 × 63 mm · 11 delar + 6 opalskiver · 1 ark · 0,10 kg plater, om lag 0,85 kg heil · 306 mm høg, fot Ø130 · mørkegrøn'),
    ('nikk', 'Nikk', 'skulptur-03 · velta, eit nebb', 'Vipp hovudet om messingknappen',
     [('arbeid 0°', 'ark-arbeid.png', 'LED-lista midt i hatten: flekk på bordet, mjuk vask bak. 3000 K.'),
      ('møte og kveld 25°', 'ark-mote.png', 'Opalnasen mot andletet, lampa vridd 35° på foten. 2700–2200 K.'),
      ('møte · andletsprøve', 'ark-andlet-mote.png', 'Kula der brukaren sit får ei varm side.')],
     'hovud 94 × 181 × 96 mm · 10 delar (7 MDF + 3 opal) · 2 ark · 0,16 kg plater, om lag 0,7 kg heil · 445 mm høg, fot Ø120 · gråbeige #c9bfae'),
]

def wrap(txt, font, w):
    out, cur = [], ''
    for word in txt.split():
        t = (cur + ' ' + word).strip()
        if font.getlength(t) <= w: cur = t
        else: out.append(cur); cur = word
    if cur: out.append(cur)
    return out

TX = 650          # tekstspalta
TW = 360          # bilete-breidd
TH = int(TW * 550 / 600)
GAP = 14
NC = max(len(m) for _, _, _, _, m, _ in design)
W = TX + NC * (TW + GAP) + 26
LW = TX - 70      # breidd på tekst

# rekn høgda først
def teksthogd(handling, modes, tal):
    h = 58 + 40 + 34 * len(wrap(handling, fb, LW)) + 14
    for lab, _, txt in modes:
        h += 32 + 30 * len(wrap(txt, fc, LW)) + 8
    return h + 10 + 30 * len(wrap(tal, fc, LW))

rows = []
for key, namn, form, handling, modes, tal in design:
    bild = 30 + TH + 10 + TH
    rows.append(max(bild, teksthogd(handling, modes, tal)))
H = 250 + sum(r + 50 for r in rows) + 140
c = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(c)
d.text((40, 30), 'Northern · skulptur skoren i slicerman, runde 3', font=ft, fill=INK)
d.text((40, 104), 'Fem lamper der skulpturforma er konvolutten: forma er kappa og skoren til eit gitter av 3 mm plater som gøymer lyskjelda. Meir Northern: tynn line, rund fot,', font=fs, fill=INK)
d.text((40, 140), 'éin matt farge, messing som grep og opal som einaste lysande flate. Meir brief: éi handling skiftar arbeid, møte og kveld, og scena har tastatur, skjerm og andlet.', font=fs, fill=INK)
y = 210
for (key, namn, form, handling, modes, tal), rh in zip(design, rows):
    d.line((40, y, W - 26, y), fill=(205, 202, 195), width=2)
    y += 22
    # bilete: éi spalte per modus, HELT over LYS
    for i, (lab, ark, txt) in enumerate(modes):
        x = TX + i * (TW + GAP)
        d.text((x, y), lab.upper(), font=fl, fill=MUTED)
        A = Image.open(f'{D}/{key}/{ark}')
        for j, box in enumerate(((0, 30, 600, 580), (600, 30, 1200, 580))):
            t = A.crop(box).resize((TW, TH), Image.LANCZOS)
            yy = y + 30 + j * (TH + 10)
            c.paste(t, (x, yy))
            d.text((x + 8, yy + 6), ('HELT', 'LYS')[j], font=fk, fill=((90, 88, 84), (200, 198, 190))[j])
    # tekst
    d.text((40, y - 4), namn, font=fn, fill=INK)
    d.text((40, y + 54), 'konvolutt ' + form + f' · {key}/', font=fc, fill=MUTED)
    yy = y + 96
    for ln in wrap(handling, fb, LW):
        d.text((40, yy), ln, font=fb, fill=INK); yy += 34
    yy += 14
    for lab, _, txt in modes:
        d.text((40, yy), lab[0].upper() + lab[1:], font=fb, fill=INK); yy += 32
        for ln in wrap(txt, fc, LW):
            d.text((40, yy), ln, font=fc, fill=INK); yy += 30
        yy += 8
    yy += 10
    for ln in wrap(tal, fc, LW):
        d.text((40, yy), ln, font=fc, fill=MUTED); yy += 30
    y += rh + 28
d.line((40, y, W - 26, y), fill=(205, 202, 195), width=2)
d.text((40, y + 20), 'Ikkje prøvd: lux på arbeidsfeltet, blending målt, LED-modul og batteri. Bileta viser kvar lyset går, ikkje kor mykje. Ingenting er skore.', font=fc, fill=MUTED)
d.text((40, y + 56), 'Alle fem: ALT OK i motoren (harde reglar og krav). Renderaren teiknar berre tre punktlys og opal utan demping, så opalen er ikkje jamn og ansiktslyset er ikkje målt.', font=fc, fill=MUTED)
c = c.crop((0, 0, W, y + 110))
c.save(OUT, optimize=True)
print(OUT, c.size)
