import sys, textwrap
from PIL import Image, ImageDraw, ImageFont
D, OUT = sys.argv[1], sys.argv[2]
F = 'C:/Windows/Fonts/'
ft = ImageFont.truetype(F + 'segoeuib.ttf', 52); fs = ImageFont.truetype(F + 'segoeui.ttf', 26)
fn = ImageFont.truetype(F + 'segoeuib.ttf', 44); fb = ImageFont.truetype(F + 'segoeuib.ttf', 25); fc = ImageFont.truetype(F + 'segoeui.ttf', 24)
fl = ImageFont.truetype(F + 'segoeuib.ttf', 20)
PAPER = (238, 236, 231); INK = (32, 32, 30); MUTED = (110, 108, 102)
design = [
    ('sopp', 'Sopp', 'skulptur-07', 'Snu soppen',
     'Hatten opp: lyset fell ned gjennom gitteret rundt stilken og legg ein ring av lys på bordet.',
     'Snudd, står på den flate toppen: lyset går opp gjennom stilken mot vegg og tak.',
     '355 × 357 × 132 mm · 16 delar · 3 ark · 0,60 kg · MDF 3 mm, gråkvit · stilk ø 116'),
    ('skygge', 'Skygge', 'skulptur-03', 'Drei skyggen',
     'Skyggen mot deg: LED-modulen sit høgt i hatten, lyset fell under skyggen ned på tastaturet.',
     'Skyggen mot veggen: lampa vert ein silhuett, og lyset teiknar ein boge på veggen bak skjermen.',
     '242 × 336 × 191 mm · 15 delar · 3 ark · 0,52 kg · MDF 3 mm, mørkegrøn · fot om lag 170 cm²'),
    ('kapsel', 'Kapsel', 'skulptur-12', 'Sving kapselen',
     'Kapselen ut over bordet: ei lang, lineær kjelde over tastaturet, slik formsøket peika på.',
     'Svinga inn mot veggen på messingringen: veggen bak skjermen lyser, kontrasten fell.',
     '157 × 368 × 192 mm · 18 delar · 2 ark · 0,45 kg · MDF 3 mm, kvit · fot om lag 55 cm²'),
]
TW, TH = 440, 425
TX = 640
W = TX + 4 * TW + 5 * 14
rowh = TH + 40
H = 210 + len(design) * (rowh + 24) + 120
c = Image.new('RGB', (W, H), PAPER); d = ImageDraw.Draw(c)
d.text((40, 30), 'Northern · skulptur skoren i slicerman', font=ft, fill=INK)
d.text((40, 104), 'Tre skulpturformer frå «skulptur»-lista, skorne til eggekartong av 3 mm plater. Cellene står loddrett og er lameller:', font=fs, fill=INK)
d.text((40, 140), 'lyset går rett opp og ned, og du ser aldri lyskjelda frå sida. Éi handling skiftar mellom arbeid og stemning.', font=fs, fill=INK)
for i, lab in enumerate(['arbeid', 'arbeid · lys', 'stemning · lys', 'stemning']):
    d.text((TX + 14 + i * (TW + 14), 186), lab.upper(), font=fl, fill=MUTED)
y = 214
for key, namn, kjelde, grep, arb, stem, tal in design:
    A = Image.open(f'{D}/{key}-a/ut/ark.png'); S = Image.open(f'{D}/{key}-s/ut/ark.png')
    tiles = [A.crop((0, 0, 600, 580)), A.crop((600, 0, 1200, 580)), S.crop((600, 0, 1200, 580)), S.crop((0, 0, 600, 580))]
    for i, t in enumerate(tiles):
        t = t.crop((0, 30, 600, 580)).resize((TW, int(TW * 550 / 600)))
        c.paste(t, (TX + 14 + i * (TW + 14), y))
    d.text((40, y), namn, font=fn, fill=INK)
    d.text((40, y + 58), kjelde, font=fc, fill=MUTED)
    d.text((40, y + 100), grep, font=fb, fill=INK)
    yy = y + 140
    for lab, txt in (('Arbeid', arb), ('Stemning', stem)):
        d.text((40, yy), lab, font=fb, fill=INK); yy += 34
        for ln in textwrap.wrap(txt, 44):
            d.text((40, yy), ln, font=fc, fill=INK); yy += 31
        yy += 8
    for ln in textwrap.wrap(tal, 46):
        d.text((40, yy), ln, font=fc, fill=MUTED); yy += 30
    y += rowh + 24
d.text((40, y + 10), 'Ikkje prøvd: lux på arbeidsfeltet, blending målt, LED-modul og batteri. Bileta viser kvar lyset går, ikkje kor mykje. Ingenting er skore.', font=fc, fill=MUTED)
d.text((40, y + 46), 'Alle tre held dei harde reglane i motoren (grip, delar, orden, klem, gods, plate, snittspor) og alle 11 eigne krav, i begge stillingar.', font=fc, fill=MUTED)
c = c.crop((0, 0, W, y + 100))
c.save(OUT, optimize=True)
print(OUT, c.size)
