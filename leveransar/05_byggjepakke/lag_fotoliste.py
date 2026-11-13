# -*- coding: utf-8 -*-
"""Fotoliste for skissemodellane, A4 i same stil som byggjepakken.

Bileta skal kunne setjast rett inn på side 10 til 13: legg dei i leveransar/03_konsept/foto/ med namna i lista,
køyr leveransar/03_konsept/lys/bygg_konsept.py og leveransar/04_moodle/lag_pdf.py.

Kameraplassen er den same som i rendringane (KAM i konsept/lysskisse/lysskisse.py):
98 cm til høgre for skjermmidten, 1,40 m framfor bordkanten, 80 cm over bordplata, sikta på skjermfoten, 43° biletvinkel.

  python lag_fotoliste.py
"""
import os, sys
import lag_byggjepakke as bp
from lag_byggjepakke import t, tekstblokk, side_svg, html, skriv_pdf

HER = os.path.dirname(os.path.abspath(__file__))


def s_oppsett(W, H):
    m = 12
    g = [t(m, 30, 'Fotoliste: same rom, same kamera, tre modellar', 'tittel')]
    g.append(t(m, 38, 'Bileta skal kunne samanliknast med rendringane på side 10 til 13. Difor står kameraet der rendrekameraet står.', 'ingress'))
    g.append(t(m, 50, 'KAMERAPLASSEN', 'mono'))
    kam = ['98 cm til høgre for skjermmidten, 1,40 m framfor bordkanten,',
           '80 cm over bordplata. Sikt på skjermfoten.',
           'Telefonen på stativ eller ein bokstabel, så han står heilt i ro.',
           'Bruk 2× zoom: det gjev om lag same biletvinkel som rendringane (43°).',
           'Kvadratisk format (1:1), eller beskjer kvadratisk etterpå.',
           'Merk kameraplassen med teip på golvet, så du finn han att.']
    g.append(tekstblokk(m, 56, kam, 'brod'))
    g.append(t(m, 90, 'LYS OG INNSTILLINGAR', 'mono'))
    lys = ['Mørkt rom. Skjermen på, mørkt tema, låg lysstyrke.',
           'Lås eksponering og fokus: hald fingeren på skjermen til AE/AF-lås.',
           'Ingen blits. Same innstilling for alle tre modellane.',
           'Ta først eitt bilete utan lampe, berre skjermen. Det er referansen.',
           'Sit på plassen sjølv, eller la stolen stå med eit mørkt plagg over.']
    g.append(tekstblokk(m, 96, lys, 'brod'))
    x2 = m + (W - 2 * m) * 0.52
    g.append(t(x2, 50, 'BILETA PER MODELL', 'mono'))
    rader = [('1', 'stemning', 'kameraplassen, lampa i stemning', 'side 11 til 13, venstre'),
             ('2', 'arbeid', 'kameraplassen, lampa i arbeid', 'side 11 til 13, høgre'),
             ('3', 'overgang', 'kameraplassen, gesten halvvegs', 'presentasjonen'),
             ('4', 'gest', 'handa i rørsla, nært, romlys på', 'presentasjonen'),
             ('5', 'kropp', 'modellen frå sida i romlys, rolig bakgrunn', 'side 10 og presentasjonen'),
             ('6', 'felt', 'arbeid, A4-arket i feltet rett ovanfrå', 'jamnheita (F3)'),
             ('7', 'auge-25, -47, -60', 'frå augehøgda 25, 47 og 60 cm over bordet', 'blendinga (F1)')]
    y = 56
    for s_, dx in (('NR', 0), ('FILNAMN', 7), ('KVA', 38), ('TIL', 98)):
        g.append(t(x2 + dx, y, s_, 'mono grå'))
    for i, (nr, namn, kva, til) in enumerate(rader):
        yy = y + 6 + i * 6
        g.append(t(x2, yy, nr, 'brod'))
        g.append(t(x2 + 7, yy, namn, 'brod svart'))
        g.append(t(x2 + 38, yy, kva, 'brod'))
        g.append(t(x2 + 98, yy, til, 'brod'))
    g.append(tekstblokk(x2, y + 54, ['Filnamna får bokstaven til modellen først: A-stemning.jpg, B-arbeid.jpg,',
                                     'C-kropp.jpg og så vidare. Legg dei i leveransar/03_konsept/foto/.',
                                     'Bilete 1, 2 og 5 blir sette inn på sidene når konseptsidene blir laga på nytt.',
                                     'Bilete 3, 4 og 7 er til presentasjonen 18.11. Bilete 6 er til målinga.'], 'liten', lh=4.2))
    g.append(t(m, H - 24, 'Kameraplassen er rendrekameraet i lysmodellen (KAM i konsept/lysskisse/lysskisse.py). Biletvinkelen med 2× zoom er eit overslag.', 'liten'))
    return ''.join(g)


def s_maaling(W, H):
    m = 12
    g = [t(m, 30, 'Måletabell for skissemodellane', 'tittel')]
    g.append(t(m, 38, 'Lux med ein luxmålar eller ein lux-app på telefonen, sensoren rett opp, same app for alle tre. Skriv føreseiinga før du måler.', 'ingress'))
    g.append(t(m, 50, 'FEM PUNKT I FELTET 60 × 40 CM, ARBEID', 'mono'))
    # skisse av feltet med fem punkt
    fx, fy, fw, fh = m + 4, 56, 60, 40
    g.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" class="tynn"/>')
    pkt = [(0.1, 0.1), (0.9, 0.1), (0.5, 0.5), (0.1, 0.9), (0.9, 0.9)]
    for i, (a, b) in enumerate(pkt):
        cx, cy = fx + a * fw, fy + b * fh
        g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.6" fill="#000"/>')
        g.append(t(cx + 2.5, cy + 1, str(i + 1), 'mono svart'))
    g.append(t(fx + fw / 2, fy - 2, 'skjermen', 'mono grå', 'middle'))
    g.append(t(fx + fw / 2, fy + fh + 5, 'brukaren', 'mono grå', 'middle'))
    g.append(tekstblokk(fx + fw + 8, fy + 4, ['Punkta ligg 3 cm inn frå hjørna.',
                                              'Jamnheit = lågaste delt på snittet',
                                              'av dei fem. Referansen er 0,6.'], 'liten', lh=4))
    ty = 112
    kol = [('MODELL', 0), ('FØRESEIING', 26), ('1', 62), ('2', 80), ('3', 98), ('4', 116), ('5', 134), ('SNITT', 152), ('JAMNHEIT', 176),
           ('MOT AUGET 25 / 47 / 60 CM, SER DU LYSKJELDA?', 202)]
    for s_, dx in kol:
        g.append(t(m + dx, ty, s_, 'mono'))
    for i, (mod, fore) in enumerate((('A Skiva', 'U over 0,5'), ('B Over', 'U 0,35 til 0,55'), ('C Vindauge', 'skjerm < 0,15'))):
        for r in range(2):
            y = ty + 4 + (2 * i + r + 1) * 8
            g.append(f'<line x1="{m}" y1="{y}" x2="{W - m}" y2="{y}" class="haar"/>')
            if r == 0:
                g.append(t(m, y - 2.4, mod, 'brod svart'))
                g.append(t(m + 26, y - 2.4, fore, 'brod'))
            else:
                g.append(t(m, y - 2.4, '   stemning', 'brod'))
    g.append(tekstblokk(m, ty + 62, ['Føreseiingane er frå byggjepakken: A med bogen over 0,5, flat under 0,45. B 0,46 (0,35 til 0,55) med diffusorark, under 0,05 utan.',
                                     'C: vindauget står i ro medan feltet kjem fram, og skjermen får under 0,15 av feltet heile vegen. Lux-appar er unøyaktige i absolutt nivå;',
                                     'bruk tala til å samanlikne modellane med kvarandre, ikkje med kravet på 350 lx.'], 'liten', lh=4.2))
    return ''.join(g)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    W, H = 297, 210
    sider = [side_svg(W, H, s_oppsett(W, H), 'Fotoliste', 1, 2), side_svg(W, H, s_maaling(W, H), 'Måletabell', 2, 2)]
    hf = os.path.join(HER, 'fotoliste-A4.html'); open(hf, 'w', encoding='utf-8').write(html(sider, W, H))
    skriv_pdf(hf, os.path.join(HER, 'fotoliste-A4.pdf')); print('skrive fotoliste-A4.pdf')
