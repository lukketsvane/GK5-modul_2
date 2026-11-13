# -*- coding: utf-8 -*-
"""
maaleark.py  ·  måleark for delane frå settet som K1 byggjer på: tretten mål å ta med skyvelære og vekt

Teikninga er dei enkle lekamane frå k1.py (måla frå foto). Skriv ut, mål, og før tala inn i modell/byggjesett/maal.json
eller i toppen av k1.py. Køyr så k1.py på nytt.

  python maaleark.py        skriv k1/maaleark.png og k1/maaleark.pdf
"""
import os, sys, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', 'cad'))
import k1 as K
import teikning as Tg
from PIL import Image

MM, A4, font = Tg.MM, Tg.A4, Tg.font
px = lambda r: tuple(int(x * MM) for x in r)

def tal(x): return ('%g' % round(x, 1)).replace('.', ',')

MAAL = [   # bokstav, kva, rekna med, ± frå foto, ankerpunkt på teikninga, forskyving av ballongen (mm på arket)
    ('A', 'tappen: diameter', K.TAPP_D, K.pm('P01', 'tapp_d'), (-K.KAPPE_B / 2 - K.TAPP_L * 0.7, K.AY, K.ZP), (-22, -12)),
    ('B', 'tappen: kor langt han stikk ut', K.TAPP_L, K.pm('P01', 'tapp_lengd'), (-K.KAPPE_B / 2 - K.TAPP_L, K.AY, K.ZP), (-26, 6)),
    ('C', 'kappa: breidd (langs tappen)', K.KAPPE_B, K.pm('P01', 'kappe_breidd'), (0, K.AY - 10, K.ZP + K.KAPPE_H / 2), (-6, -22)),
    ('D', 'kappa: djupn (på tvers av tappen)', K.KAPPE_H, K.pm('P01', 'kappe_hogd'), (K.KAPPE_B / 2, K.AY, K.ZP - 30), (26, -10)),
    ('E', 'armrøyret: brei side', K.PROFIL_B, K.pm('P01', 'profil_breidd'), (K.PROFIL_T / 2, K.AY, K.AZ + 150), (26, 0)),
    ('F', 'armrøyret: smal side', K.PROFIL_T, K.pm('P01', 'profil_tjukk'), (0, K.AY - K.PROFIL_B / 2, K.AZ + 110), (-28, 4)),
    ('G', 'festeplata: breidd', K.PLATE_B, K.pm('P02', 'breidd'), (-K.PLATE_B / 2 + 4, K.AY - 27.5, K.AZ - K.PLATE_NED + 8), (-26, 10)),
    ('H', 'festeplata: lengd', K.PLATE_L, K.pm('P02', 'lengd'), (K.PLATE_B / 2 - 4, K.AY - 27.5, K.AZ + K.PLATE_L - K.PLATE_NED - 4), (-30, -8)),
    ('I', 'festeplata: tjukn', K.PLATE_T, 1.0, (K.PLATE_B / 2, K.AY - 26.5, K.AZ - K.PLATE_NED + 30), (24, 8)),
    ('J', 'frå hengselbolten ned til kanten av plata', K.PLATE_NED, 10.0, (-K.PLATE_B / 2 + 4, K.AY - 27.5, K.AZ - 20), (-30, -2)),
    ('K', 'kanalen armen står i: breidd', K.KANAL_B, 4.0, (K.KANAL_B / 2, K.AY + 20, K.AZ + 10), (26, -6)),
    ('L', 'frå hengselbolten til tappen', K.BOLT_TIL_TAPP, 15.0, (K.PROFIL_T / 2, K.AY + 5, K.AZ + 230), (30, 8)),
    ('M', 'vekta av armen og hengselet saman, i gram', None, None, None, None),
]

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    os.makedirs(K.UT, exist_ok=True)
    S = [s[2] for s in K.sett()]
    im, dr = Tg.side('Måleark: delane frå settet som K1 byggjer på', 1)
    v = Tg.Vising(S, Tg.ISO)
    f = v.teikn(dr, px((14, 24, 128, 196)))
    for b, kva, verdi, pm, p, d in MAAL:
        if p is None: continue
        q = f(v.punkt(p)); Tg.ballong(dr, q, (q[0] + d[0] * MM, q[1] + d[1] * MM), b)
    x0 = int(136 * MM); y = int(26 * MM)
    kol = (x0, x0 + int(10 * MM), x0 + int(92 * MM), x0 + int(112 * MM), x0 + int(126 * MM))
    for x, t in zip(kol, ('', 'Mål i mm', 'Rekna med', '±', 'Målt')): dr.text((x, y), t, font=font(9, True), fill=(0, 0, 0))
    y += int(7 * MM)
    for b, kva, verdi, pm, p, d in MAAL:
        dr.text((kol[0], y), b, font=font(10, True), fill=(0, 0, 0)); dr.text((kol[1], y), kva, font=font(9), fill=(0, 0, 0))
        if verdi is not None:
            dr.text((kol[2], y), tal(verdi), font=font(9), fill=(0, 0, 0)); dr.text((kol[3], y), tal(pm), font=font(9), fill=(0, 0, 0))
        dr.line([kol[4], y + int(4.4 * MM), kol[4] + int(22 * MM), y + int(4.4 * MM)], fill=(0, 0, 0), width=1)
        y += int(9.2 * MM)
    y += int(4 * MM)
    for t in ('Bruk skyvelære. Mål tre gonger og skriv snittet.', 'Stemmer A til D innanfor 0,5 mm, kan salen trykkjast som han er.',
              'Elles: rett tala øvst i k1.py og køyr skriptet på nytt.', 'Veg M: er røyret av stål, blir lampa om lag 250 g tyngre enn rekna.',
              'Sjå òg etter hol i festeplata. Finst dei, kan plata skruast rett i sokkelen.'):
        dr.text((x0, y), t, font=font(9), fill=(0, 0, 0)); y += int(5.4 * MM)
    im.save(os.path.join(K.UT, 'maaleark.png'))
    im.convert('RGB').save(os.path.join(K.UT, 'maaleark.pdf'), resolution=Tg.DPI)
    print('maaleark.png')
