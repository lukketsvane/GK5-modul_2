# -*- coding: utf-8 -*-
"""samle.py · set mekanikk (tal_mek.json), lys (tal_lys.json) og brett (tal_brett.json) saman til éin tabell

  python samle.py      skriv tal.csv, tal.md og brett-merkt.png

Krava er dei i kravspesifikasjonen, slik konsept/lysskisse/API.md og konsept/tre/00-tre-konsept.md les dei:
F3 350 lx på feltet innanfor 5 W, jamnheit 0,6 (referanse), F6 100 til 150 lx på veggen bak skjermen,
F1 3000 og F5 1500 cd/m² mot auget i arbeid, 500 i stemning, F2 ein overgang og ikkje ein dimmar (likskap under 0,9),
F8 1,2 kg, F9 200 cm², dytt 3 N og trykk 5 N utan å velte (formsøket sitt mål), handtaket innan 70 cm.
"""
import os, sys, json, csv
from PIL import Image, ImageDraw, ImageFont

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(os.path.dirname(os.path.dirname(HER)))
MONO = r'C:\Windows\Fonts\consola.ttf'
SERIF = os.path.join(ROT, 'leveransar', '01_fase1_sider', 'fonts', 'EBGaramond12-Regular.otf')
F_DYTT, F_TRYKK, REKK = 3.0, 5.0, 700


def k(x, d=1):
    return ('%.*f' % (d, x)).replace('.', ',')


def les():
    mek = json.load(open(os.path.join(HER, 'tal_mek.json'), encoding='utf-8'))
    lys = json.load(open(os.path.join(HER, 'tal_lys.json'), encoding='utf-8'))
    rader = []
    for m in mek:
        r = dict(m); l = lys.get(m['lys'], {})
        if 'W350' in l:
            auge = max(l['auge25'], l['auge47'], l['auge60']); s_auge = max(l['s_auge25'], l['s_auge47'], l['s_auge60'])
            r.update(W350=l['W350'], U0=l['jamnheit'], bak350=l['bak350'], skjerm=l['skjerm350'] / 350.0, ansikt350=l['ansikt350'],
                     auge25=l['auge25'], auge47=l['auge47'], auge60=l['auge60'], auge=auge, s_bak=l['s_bak'], s_auge=s_auge,
                     s_felt=l['s_felt'], likskap=l['likskap'], sprang=l['sprang'], topp=l['topp'], timar=l['timar'])
        fell = []
        if 'W350' in r:
            if r['W350'] > 5.0: fell.append('F3 watt')
            if r['U0'] < 0.6: fell.append('jamnheit')
            if not 100 <= r['bak350'] <= 150: fell.append('F6 vegg')
            if r['auge'] > 3000: fell.append('F1 blending')
            elif r['auge'] > 1500: fell.append('F5 luminans')
            if r['s_auge'] > 500: fell.append('F5 stemning')
            if r['likskap'] > 0.9: fell.append('F2 dimmar')
            elif r['sprang'] > 0.2: fell.append('F2 sveipar')
            if r['skjerm'] > 0.30: fell.append('lys på skjermen')
        else:
            fell.append('lyset er ikkje rekna')
        if r['masse_g'] > 1200: fell.append('F8 masse')
        if r['fotavtrykk_cm2'] > 200: fell.append('F9 fotavtrykk')
        if r['stotte'] == 'vegg': fell.append('F8 kan ikkje flyttast')
        if r['stotte'] == 'klype': fell.append('lastar skjermen')
        if r.get('dytt_N') is not None and r['dytt_N'] < F_DYTT: fell.append('veltar ved dytt')
        if r.get('trykk_N') is not None and r['trykk_N'] < F_TRYKK: fell.append('veltar ved trykk')
        if r['rekk_mm'] > REKK: fell.append('rekkjevidd')
        if any('skjermen' in f and 'inn' in f for f in r.get('flagg', [])): fell.append('går inn i skjermen')
        r['fell'] = fell
        rader.append(r)
    return rader, lys


def tal_md(rader, lys):
    L = ['# Kitbash generasjon 1: tala', '',
         'Rekna 13.11.2026 med `kitbash.py mek` og `lys.py`. Modell, ikkje måling. Lyset er skalert til 350 lx på feltet, som for A, B, C og D.', '',
         '| Nr | Kropp | W for 350 lx | Jamnheit | Vegg bak skjermen | Skjermflata / felt | Mot auget, verst | Stemning: vegg / mot auget | Likskap / sprang | Masse | Fot eller last | Dytt / trykk | Rekk | Fell på |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in rader:
        if 'W350' in r:
            lysdel = [k(r['W350'], 2) + ' W', k(r['U0'], 2), k(r['bak350'], 0) + ' lx', k(r['skjerm'], 2), k(r['auge'], 0) + ' cd/m²',
                      k(r['s_bak'], 0) + ' lx / ' + k(r['s_auge'], 0), k(r['likskap'], 2) + ' / ' + k(r['sprang'], 2)]
        else:
            lysdel = ['–'] * 7
        fot = (k(r['masse_g'], 0) + ' g på skjermen') if r['stotte'] == 'klype' else ('på veggen' if r['stotte'] == 'vegg' else k(r['fotavtrykk_cm2'], 0) + ' cm²')
        dt = '–' if r.get('dytt_N') is None else (k(r['dytt_N'], 1) + ' / ' + ('–' if r.get('trykk_N') is None else k(r['trykk_N'], 1)) + ' N')
        L.append('| ' + ' | '.join([str(r['id']), r['namn']] + lysdel + [k(r['masse_g'], 0) + ' g', fot, dt, k(r['rekk_mm'] / 10, 0) + ' cm', ', '.join(r['fell']) or 'ingenting']) + ' |')
    L += ['', '## Lysgrepa', '', '| Grep | W for 350 lx | Jamnheit | Vegg bak | Skjermflata | Mot auget 25 / 47 / 60 cm | Stemning: vegg, mot auget | Likskap | Sprang |', '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for n, l in lys.items():
        if 'W350' not in l:
            L.append(f'| {n} | feil: {l.get("feil", "")} | | | | | | | |'); continue
        L.append('| %s | %s | %s | %s | %s | %s / %s / %s | %s lx, %s | %s | %s |' % (
            n, k(l['W350'], 2), k(l['jamnheit'], 2), k(l['bak350'], 0), k(l['skjerm350'], 0), k(l['auge25'], 0), k(l['auge47'], 0), k(l['auge60'], 0),
            k(l['s_bak'], 0), k(max(l['s_auge25'], l['s_auge47'], l['s_auge60']), 0), k(l['likskap'], 2), k(l['sprang'], 2)))
    open(os.path.join(HER, 'tal.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')


def tal_csv(rader):
    felt = ['id', 'namn', 'stotte', 'organ', 'handling', 'lys', 'W350', 'U0', 'bak350', 'skjerm', 'ansikt350', 'auge25', 'auge47', 'auge60', 's_bak', 's_auge', 's_felt',
            'likskap', 'sprang', 'topp', 'timar', 'masse_g', 'masse_sett_g', 'masse_cad_g', 'masse_ny_g', 'fotavtrykk_cm2', 'tipp_grader', 'dytt_N', 'trykk_N',
            'rekk_mm', 'hogd_mm', 'handtak', 'fell', 'nye', 'setning']
    with open(os.path.join(HER, 'tal.csv'), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';'); w.writerow(felt)
        for r in rader:
            w.writerow([('; '.join(r[x]) if isinstance(r.get(x), list) else ('' if r.get(x) is None else (k(r[x], 3) if isinstance(r[x], float) else r[x]))) for x in felt])


def merkt_brett(rader):
    """Brettet med nummer, namn og tre tal under kvar flis. Same flisene som brett.png."""
    px, luft, tekst = 512, 24, 92
    fn = ImageFont.truetype(SERIF, 30); fm = ImageFont.truetype(MONO, 17)
    im = Image.new('RGB', (4 * px + 5 * luft, 4 * (px + tekst) + 5 * luft), (0, 0, 0)); dr = ImageDraw.Draw(im)
    for r in rader[:16]:
        i = r['id'] - 1; x = luft + (i % 4) * (px + luft); y = luft + (i // 4) * (px + tekst + luft)
        im.paste(Image.open(os.path.join(HER, 'flis', '%02d.png' % r['id'])), (x, y))
        dr.text((x + 6, y + px + 2), '%d  %s' % (r['id'], r['namn']), font=fn, fill=(244, 244, 244))
        if 'W350' in r:
            l1 = '%s W · U0 %s · vegg %s lx · auge %s' % (k(r['W350'], 1), k(r['U0'], 2), k(r['bak350'], 0), k(r['auge'], 0))
        else:
            l1 = 'lyset er ikkje rekna'
        fot = ('%s g på skjermen' % k(r['masse_g'], 0)) if r['stotte'] == 'klype' else ('%s g på veggen' % k(r['masse_g'], 0) if r['stotte'] == 'vegg'
              else '%s g · %s cm² · dytt %s N' % (k(r['masse_g'], 0), k(r['fotavtrykk_cm2'], 0), k(r['dytt_N'], 1)))
        dr.text((x + 6, y + px + 42), l1, font=fm, fill=(168, 168, 168))
        dr.text((x + 6, y + px + 64), fot, font=fm, fill=(168, 168, 168))
    im.save(os.path.join(HER, 'brett-merkt.png'))


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    rader, lys = les()
    tal_md(rader, lys); tal_csv(rader); merkt_brett(rader)
    json.dump(rader, open(os.path.join(HER, 'tal.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for r in rader:
        print('%2d %-26s %s' % (r['id'], r['namn'], ', '.join(r['fell']) or 'held alt'))
