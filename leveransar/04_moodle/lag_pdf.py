# -*- coding: utf-8 -*-
"""Set saman Moodle-innleveringa 17.11 til éin PDF: sidene 01 til 13 i rekkjefølgje, med tekst og figurar som vektor.

Kvar HTML-side blir skriven ut med hovudlaus Chrome (éi side per ark, 1127 x 797 px, A4-forhold),
og sidene blir sette saman med pypdf. Ein PNG av første og siste side blir lagd til kontroll.

  python lag_pdf.py
"""
import os, sys, subprocess, tempfile
from pypdf import PdfWriter, PdfReader

HER = os.path.dirname(os.path.abspath(__file__))
LEV = os.path.normpath(os.path.join(HER, '..'))
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
UTFIL = os.path.join(HER, 'GK5_Northern_Moodle_17-11.pdf')

SIDER = [
    '01_fase1_v2/side-1-debrief.html',
    '01_fase1_v2/side-2-bransjeresearch.html',
    '01_fase1_v2/side-3-3b-analyse.html',
    '01_fase1_v2/side-4-kravspesifikasjon.html',
    '01_fase1_v2/side-5-berekraftshandling.html',
    '01_fase1_v2/side-6-prosjektplan.html',
    '01_fase1_v2/side-7-bedriftsbesok.html',
    '02_formfoering/side-8-formfoering-sortiment.html',
    '02_formfoering/side-9-formfoering-ny-lampe.html',
    '03_konsept/side-10-tre-konsept.html',
    '03_konsept/side-11-konsept-a-skiva.html',
    '03_konsept/side-12-konsept-b-over.html',
    '03_konsept/side-13-konsept-c-vindauge.html',
]


def skriv_ut(html, pdf, profil):
    url = 'file:///' + os.path.join(LEV, html).replace('\\', '/')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--no-first-run', f'--user-data-dir={profil}',
                    '--no-pdf-header-footer', '--run-all-compositor-stages-before-draw', '--virtual-time-budget=4000',
                    f'--print-to-pdf={pdf}', url], check=True, capture_output=True, timeout=120)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    w = PdfWriter()
    with tempfile.TemporaryDirectory() as tmp:
        for i, s in enumerate(SIDER, 1):
            pdf = os.path.join(tmp, f'{i:02d}.pdf')
            skriv_ut(s, pdf, os.path.join(tmp, 'profil'))
            r = PdfReader(pdf)
            if len(r.pages) != 1:
                print('ÅTVARING:', s, 'gav', len(r.pages), 'sider')
            for p in r.pages:
                w.add_page(p)
            print(f'{i:02d}', s, len(r.pages), 'side')
        w.add_metadata({'/Title': 'GK5 modul 2 · Northern · innlevering 17.11.2026', '/Author': 'Iver R. Finne'})
        with open(UTFIL, 'wb') as fh:
            w.write(fh)
    print('skrive', UTFIL, round(os.path.getsize(UTFIL) / 1e6, 2), 'MB', len(PdfReader(UTFIL).pages), 'sider')
    try:
        import fitz
        d = fitz.open(UTFIL)
        for n in (0, len(d) - 1):
            d[n].get_pixmap(dpi=96).save(os.path.join(HER, f'kontroll-side-{n + 1}.png'))
        print('kontrollbilete skrivne')
    except Exception as e:
        print('kontrollbilete vart ikkje laga:', e)
