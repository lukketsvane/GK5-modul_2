# -*- coding: utf-8 -*-
"""Set saman den samla innsendinga 26.11 til éin PDF med bokmerke.

Del 2 (Moodle 17.11) og del 3 (konseptgjennomgangen) blir tekne inn uendra frå PDF-ane som alt finst.
Dei nye sidene blir skrivne ut med hovudlaus Chrome (1127 x 797 px per ark) og sette saman med pypdf.
Oversikta blir skriven til slutt, når sidetala er kjende.

  python lag_innsending.py
"""
import os, sys, shutil, subprocess, tempfile
from pypdf import PdfWriter, PdfReader

HER = os.path.dirname(os.path.abspath(__file__))
LEV = os.path.normpath(os.path.join(HER, '..'))
CHROME = next((c for c in (r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                           shutil.which('google-chrome') or '', shutil.which('chromium') or '') if c and os.path.exists(c)), None)
UTFIL = os.path.join(HER, 'GK5_modul2_Iver_R_Finne_innsending_26-11.pdf')

DELAR = [  # (nøkkel, bokmerke, kjelde)
    ('d1', 'Del 1 · Erstatningsoppgåve for studieturen', 'del1-erstatningsoppgave.html'),
    ('d2', 'Del 2 · Moodle 17.11: fase 1, formføringsplansje og tre konsept', os.path.join(LEV, '04_moodle', 'GK5_Northern_Moodle_17-11.pdf')),
    ('d3', 'Del 3 · Konseptgjennomgang 18.11', os.path.join(LEV, '06_konseptgjennomgang', 'presentasjon.pdf')),
    ('d4', 'Del 4 · Formføring Raup', 'del4-formfoering-raup.html'),
    ('d5', 'Del 5 · Prosesslogg', 'del5-prosesslogg.html'),
]


def skriv_ut(html, pdf, profil):
    url = 'file:///' + html.replace('\\', '/').lstrip('/')
    arg = [CHROME, '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={profil}',
           '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw', '--virtual-time-budget=4000',
           f'--print-to-pdf={pdf}', url]
    if os.name != 'nt' and os.geteuid() == 0:
        arg.insert(1, '--no-sandbox')
    subprocess.run(arg, check=True, capture_output=True, timeout=120)


def omfang(start, tal):
    return f'{start}' if tal == 1 else f'{start}–{start + tal - 1}'


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    with tempfile.TemporaryDirectory() as tmp:
        profil = os.path.join(tmp, 'profil')
        lesarar, sidetal, side = [], {}, 2  # side 1 er oversikta
        for nokkel, merke, kjelde in DELAR:
            if kjelde.endswith('.html'):
                pdf = os.path.join(tmp, nokkel + '.pdf')
                skriv_ut(os.path.join(HER, kjelde), pdf, profil)
            else:
                pdf = kjelde
            r = PdfReader(pdf)
            lesarar.append((merke, r, side))
            sidetal[nokkel] = omfang(side, len(r.pages))
            if nokkel == 'd2':
                sidetal['d2a'] = omfang(side, 7)
            print(merke, sidetal[nokkel])
            side += len(r.pages)
        mal = open(os.path.join(HER, 'del0-oversikt.mal.html'), encoding='utf-8').read()
        oversikt = os.path.join(HER, 'del0-oversikt.html')
        with open(oversikt, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(mal.format(n=side - 1, **sidetal))
        pdf0 = os.path.join(tmp, 'd0.pdf')
        skriv_ut(oversikt, pdf0, profil)
        w = PdfWriter()
        r0 = PdfReader(pdf0)
        if len(r0.pages) != 1:
            print('ÅTVARING: oversikta gav', len(r0.pages), 'sider')
        w.add_page(r0.pages[0])
        w.add_outline_item('Oversikt', 0)
        for merke, r, start in lesarar:
            for p in r.pages:
                w.add_page(p)
            w.add_outline_item(merke, start - 1)
        w.add_metadata({'/Title': 'GK5 modul 2 · Northern · samla innsending 26.11.2026', '/Author': 'Iver R. Finne'})
        with open(UTFIL, 'wb') as fh:
            w.write(fh)
    print('skrive', UTFIL, round(os.path.getsize(UTFIL) / 1e6, 2), 'MB', len(PdfReader(UTFIL).pages), 'sider')
