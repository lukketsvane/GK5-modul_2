# -*- coding: utf-8 -*-
"""studie.py  ·  lysstudien for ei kitbash-lampe, i same oppsett som northern-lampe/form05/gen_d/studie_a.png

Éin kropp stor på svart: arbeid og stemning side om side med same kamera og same låste eksponering, mannekengen,
bordet, skjermen og veggen, isolux-kurver med lux-merke på bord og vegg, lysfordelinga i snitt (cd/klm) og tala i
små kursive liner under kvart bilete. Oppsettet er henta frå k_studie() i northern-lampe/form05/gen_d/val.py.
Rommet, kameraet, eksponeringa og tal() er lysmotoren sine (konsept/lysskisse/lysskisse.py), og kurvene og polarsnittet
er funksjonane i konsept/lysskisse/studie.py (importerte, ikkje kopierte).

  import studie
  r = studie.studie(g, 'Namn på lampa · kva ho er laga av', 'studie.png')

g(t) -> (lys, kropp) er eit lysgrep slik lysmotoren definerer det: t = 0 er stemning, t = 1 er arbeid.
Tittelen får alltid «rekna, ikkje målt» til slutt. Tala er tal() frå lysmotoren, uendra.
"""
import os, sys, math, json, time, importlib.util
sys.dont_write_bytecode = True
HER = os.path.dirname(os.path.abspath(__file__))
if HER not in sys.path: sys.path.insert(0, HER)
import miljo
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import bru

ls = bru.motor()
_ST = None
GEORGIA = r'C:\Windows\Fonts\georgiai.ttf'
KRAV = dict(felt=350.0, W=7.5, U=0.6, L_arbeid=3000.0, L_stemning=500.0, vegg=(100.0, 150.0), ansikt=50.0)     # grunnlag/04-kravspesifikasjon.md
NIV = (10, 25, 50, 100, 200)


def _st():
    """konsept/lysskisse/studie.py under eit anna namn (denne fila heiter òg studie)."""
    global _ST
    if _ST is None:
        spec = importlib.util.spec_from_file_location('lysskisse_studie', os.path.join(bru.LYSSKISSE, 'studie.py'))
        _ST = importlib.util.module_from_spec(spec); sys.modules['lysskisse_studie'] = _ST
        spec.loader.exec_module(_ST)
    return _ST


def _font(st):
    try: return ImageFont.truetype(GEORGIA, st)
    except Exception: return ImageFont.load_default()


def _nn(v, d=0):
    return f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')


def _bryt(dr, lines, font, maks):
    """Del liner som er for breie ved « · », så spalta ikkje går inn i neste bilete eller polarsnittet."""
    ut = []
    for i, l in enumerate(lines):
        if i == 0 or dr.textlength(l, font=font) <= maks or ' · ' not in l:
            ut.append(l); continue
        no = ''
        for bit in l.split(' · '):
            ny = bit if not no else no + ' · ' + bit
            if no and dr.textlength(ny, font=font) > maks:
                ut.append(no); no = bit
            else:
                no = ny
        ut.append(no)
    return ut


def _held(ok):
    return '' if ok else ': held ikkje'


def _kelvin(lys):
    """Fargetemperaturen til lyset ut av lampa, vekta med lumen."""
    w = np.array([max(getattr(l, 'lm_ut', l.lm), 0.0) for l in lys]); k = np.array([l.K for l in lys], float)
    return float((w * k).sum() / max(w.sum(), 1e-9))


def _auge(d):
    """Lysaste flate mot auget: lampa sett frå 25, 47 og 60 cm over bordet, og lysaste romflate."""
    return max(d.get('L_auge25', 0.0), d.get('L_auge47', d['L_lampe']), d.get('L_auge60', 0.0), d['L_flate'])


def rekn(g):
    """tal() for arbeid (t = 1) og stemning (t = 0), og dei avleidde tala arket viser. Gjev dict(arbeid, stemning, ...)."""
    ut = {}
    for namn, t in (('arbeid', 1.0), ('stemning', 0.0)):
        lys, kropp = g(t)
        d = ls.tal(lys, kropp)
        d['K'] = _kelvin(lys); d['L_auge'] = _auge(d)
        ut[namn] = d
    a, s = ut['arbeid'], ut['stemning']
    Ea = max(a['E_felt'], 1e-9)
    ut['W350'] = a['W'] * KRAV['felt'] / Ea
    ut['likskap'] = float(ls.likskap(s['_fordeling'], a['_fordeling']))
    ut['krav'] = dict(W350=bool(ut['W350'] <= KRAV['W']), jamnheit=bool(a['U'] >= KRAV['U']), auge_arbeid=bool(a['L_auge'] <= KRAV['L_arbeid']),
                      auge_stemning=bool(s['L_auge'] <= KRAV['L_stemning']), vegg=bool(KRAV['vegg'][0] <= a['E_bak'] <= KRAV['vegg'][1]),
                      ansikt=bool(a['E_ansikt'] >= KRAV['ansikt']))
    return ut


def liner(R):
    """Tallinene under bileta: (arbeid, stemning). Alt er tal() ved watten lysgrepet sjølv gjev."""
    a, s = R['arbeid'], R['stemning']; k = R['krav']
    Ea = max(a['E_felt'], 1e-9)
    la = [f"{_nn(a['lm'])} lm ut · {_nn(a['W'], 2 if a['W'] < 2 else 1)} W · {_nn(a['K'], 0)} K",
          f"{_nn(a['E_felt'])} lx snitt på feltet · jamnheit {_nn(a['U'], 2)} (krav 0,6){_held(k['jamnheit'])}",
          f"{_nn(a['L_auge'])} cd/m² mot auget (krav under 3 000){_held(k['auge_arbeid'])} · {_nn(a['E_skjerm'])} lx på skjermflata ({_nn(a['E_skjerm'] / Ea, 2)} av feltet)",
          f"{_nn(a['E_bak'])} lx på veggen bak skjermen (krav 100 til 150){_held(k['vegg'])} · {_nn(a['E_ansikt'])} lx på ansiktet (krav 50){_held(k['ansikt'])}",
          f"350 lx på feltet krev {_nn(R['W350'], 1)} W (tak 7,5 W){_held(k['W350'])}"]
    lm = [f"{_nn(s['lm'])} lm ut · {_nn(s['W'], 2 if s['W'] < 2 else 1)} W · {_nn(s['K'], 0)} K",
          f"{_nn(s['E_bak'])} lx på veggen bak skjermen · {_nn(s['E_felt'])} lx på feltet",
          f"{_nn(s['L_auge'])} cd/m² mot auget (krav under 500){_held(k['auge_stemning'])} · {_nn(s['E_skjerm'])} lx på skjermflata",
          f"{_nn(s['E_ansikt'])} lx på ansiktet · likskap {_nn(R['likskap'], 2)} (over 0,9 er ein dimmar)"]
    return la, lm


def studie(g, tittel, fil, nett=None, px=560, tal=None, ekstra_arbeid=(), ekstra_stemning=(), niv=NIV, stille=False):
    """Lag lysstudien og gje tala attende.
    g: lysgrep, g(t) -> (lys, kropp). t = 0 stemning, t = 1 arbeid.
    tittel: lina øvst. «rekna, ikkje målt» kjem alltid etter.
    nett: valfri kropp til biletet når lysgrepet berre har enkle skuggekroppar: liste med kroppar i romkoordinatar
          (bru.Plass.kropp(delar) eller bru.lekam(mesh)), eller funksjon t -> liste. Då teiknar og skuggar nettet i
          biletet og kurvene, medan tala framleis er tal() med kroppen frå lysgrepet. Det enklaste er å la lysgrepet
          gje nettet som kropp: då er bilete og tal same rekning.
    tal: resultatet frå rekn(g) om du alt har det. px: rekna oppløysing per bilete (560 som originalen, 300 til prøve).
    ekstra_arbeid / ekstra_stemning: fleire liner under bileta (masse, velt, gest). Ni liner får plass per spalte, pluss lina om kurvene.
    Skriv òg <fil utan .png>.json med tala."""
    st = _st(); t0 = time.time()
    R = tal or rekn(g)
    panel = {}
    fnt = _font(22)
    for lab, t in (('arbeid', 1.0), ('stemning', 0.0)):
        lys, kropp = g(t)
        kb = kropp if nett is None else list(nett(t) if callable(nett) else nett)
        hdr = ls.luminans(lys, kb, px, 1)
        im = Image.fromarray(ls.framkall(hdr, px)).resize((1200, 1200), Image.LANCZOS)      # låst eksponering, same kamera
        F = st._felt(lys, kb)
        st._teikn_isolux(im, F, tuple(niv), tuple(niv), fnt)
        ix = (np.abs(F['bx']) <= 0.3 + 1e-9); iy = (F['by'] >= 0.05 - 1e-9) & (F['by'] <= 0.45 + 1e-9)
        panel[lab] = dict(im=im, polar=st.polar(lys), E_felt_bilete=float(F['Eb'][np.ix_(ix, iy)].mean()))
        if not stille: print('  studie: %s ferdig (%.0f s)' % (lab, time.time() - t0), flush=True)
    Wd, Hd = 2 * 1200 + 3 * 80, 1200 + 2 * 80 + 600
    sh = Image.new('RGB', (Wd, Hd), 'black')
    sh.paste(panel['arbeid']['im'], (80, 80)); sh.paste(panel['stemning']['im'], (80 + 1280, 80))
    dr = ImageDraw.Draw(sh)
    fh, fb, fs = (_font(z) for z in (46, 31, 24))
    kvit, graa = (240, 236, 228), (170, 163, 152)
    dr.text((80, 22), '%s  ·  rekna, ikkje målt' % tittel, font=fs, fill=graa)
    y0 = 80 + 1200 + 60
    la, lm = liner(R)
    kurver = 'kurvene: ' + ' · '.join('%g' % v for v in niv) + ' lx på bord og vegg'
    la = _bryt(dr, la + list(ekstra_arbeid), fs, 1280 - 60)[:9] + [kurver]
    lm = _bryt(dr, lm + list(ekstra_stemning), fs, 1280 - 80 - 2 * 230 - 30)[:9] + [kurver]      # stemningsspalta stoggar før polarsnittet
    for x, head, w, lines in ((80, 'arbeid', 210, la), (80 + 1280, 'stemning', 270, lm)):
        dr.text((x, y0), head, font=fh, fill=kvit)
        dr.line([x, y0 + 64, x + w, y0 + 62], fill=kvit, width=2)
        for i, s_ in enumerate(lines):
            dr.text((x, y0 + 100 + i * 46), s_, font=fs if i else fb, fill=kvit if (i < 2 or 'held ikkje' in s_) else graa)
    # polar: lysfordeling i snitt gjennom lampa og midten av feltet, cd/klm (same teikning som k_studie)
    cx, cy, r = Wd - 80 - 230, y0 + 250, 150
    curves = [(panel['arbeid']['polar'], (245, 225, 200), 3, 'arbeid'), (panel['stemning']['polar'], (205, 165, 125), 2, 'stemning')]
    top = max(float(np.max(c_[0][1])) for c_ in curves)
    skalaer = (100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 50000)
    sc = next((v for v in skalaer if v >= top), skalaer[-1])
    for rr in (sc / 3, 2 * sc / 3, sc):
        rad = r * rr / sc; dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(90, 85, 78), width=1)
    dr.line([cx, cy - r - 8, cx, cy + r + 8], fill=(70, 66, 60), width=1); dr.line([cx - r - 8, cy, cx + r + 8, cy], fill=(70, 66, 60), width=1)
    for (gr, I), col, wdt, lab in curves:
        pts = [(cx + r * min(i, 1.1 * sc) / sc * math.sin(math.radians(g_)), cy + r * min(i, 1.1 * sc) / sc * math.cos(math.radians(g_))) for g_, i in zip(gr, I)]
        dr.line(pts + pts[:1], fill=col, width=wdt, joint='curve')
        tip = max(pts, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
        dr.text((min(tip[0] + 10, Wd - 150), tip[1] - 14), lab, font=fs, fill=col)
    dr.text((cx - r - 10, cy - r - 44), 'lysfordeling, snitt', font=fs, fill=graa)
    dr.text((cx + r * 0.71 + 6, cy + r * 0.71 + 2), f'{sc} cd/klm', font=fs, fill=(150, 142, 130))
    os.makedirs(os.path.dirname(os.path.abspath(fil)), exist_ok=True)
    sh.save(fil)
    ut = dict(tittel=tittel, merknad='rekna, ikkje målt', W350=R['W350'], likskap=R['likskap'], krav=R['krav'],
              arbeid={k: float(v) for k, v in R['arbeid'].items() if not k.startswith('_')},
              stemning={k: float(v) for k, v in R['stemning'].items() if not k.startswith('_')},
              liner_arbeid=la, liner_stemning=lm, sekund=round(time.time() - t0, 1), px=px)
    if nett is not None:                                   # biletet og tala har ulik kropp: sei frå kor mykje det gjer
        for lab in ('arbeid', 'stemning'):
            ut[lab]['E_felt_bilete'] = panel[lab]['E_felt_bilete']
        avvik = abs(panel['arbeid']['E_felt_bilete'] - R['arbeid']['E_felt']) / max(R['arbeid']['E_felt'], 1e-9)
        ut['avvik_bilete_tal'] = float(avvik)
        if avvik > 0.15 and not stille:
            print('  merk studie: kroppen i biletet (nett) gjev %.0f lx på feltet, tala %.0f lx. La lysgrepet bruke same kropp.' % (
                panel['arbeid']['E_felt_bilete'], R['arbeid']['E_felt']))
    json.dump(ut, open(os.path.splitext(fil)[0] + '.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if not stille: print('  studie:', fil, '(%.0f s)' % (time.time() - t0), flush=True)
    return ut
