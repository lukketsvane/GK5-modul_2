# -*- coding: utf-8 -*-
"""
studie.py  ·  konseptarket (lampeverktøyet på rett grunnlag)

Eitt ark per konsept: stemning og arbeid i same rom og same eksponering, isolux på bord og vegg,
lysfordelinga i snitt, tala mot kravspesifikasjonen og kroppen (masse, velt, fot, kjøling, batteri).

Grunnlaget er prosjektet sitt eige: briefen, kravspesifikasjonen (350 lx på feltet, høgst 7,5 W,
1,2 kg og 200 cm²) og rommet i lysskisse.py. Lyset kan vere retta og reflektert, ikkje berre ei
lambertsk opning. Kroppsmåla er henta frå northern-lampe/felles.py og formsok/motor.py.

  from studie import *
  konseptark('Namn', 'Éi setning.', g, kropp=dict(...), fil='ark.png')

g(t) -> (lys, kropp) som elles: t = 0 er stemning, t = 1 er arbeid.
"""
import os, sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.measure import find_contours

_DER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DER)
import lysskisse as ls
from lysskisse import *

# ------------------------------------------------------------------ kropp

def kroppstal(delar, kontakt, W=5.0, kjoleflate_cm2=None, grep=None):
    """Masse, tyngdepunkt, velt, fot, kjøling og batteri.
    delar: [(kg, (x, y, h)), ...] med h over bordplata. kontakt: [(x, y), ...] der lampa rører bordet.
    kjoleflate_cm2: metallflate som kan leie bort varmen. grep: (høgd i m, kraft i N) for handlinga."""
    m = sum(d[0] for d in delar)
    tp = sum(d[0] * np.array(d[1], float) for d in delar) / m
    P = np.array(kontakt, float)
    if len(P) >= 3:
        from scipy.spatial import ConvexHull
        hv = P[ConvexHull(P).vertices]
        fot = ConvexHull(P).volume * 1e4
        inn = min(float(np.dot(tp[:2] - a, np.array([-(c - a)[1], (c - a)[0]]) / np.linalg.norm(c - a))) for a, c in zip(hv, np.roll(hv, -1, 0)))
    else:
        fot, inn = 0.0, 0.0
    d = dict(masse=m, tp_hogd=float(tp[2]), velt=math.degrees(math.atan2(inn, max(tp[2], 1e-6))), fot=fot, W=W,
             timar=ls.CELLE / W, kjol_krav=0.7 * W / (10.0 * 15.0) * 1e4, kjol=kjoleflate_cm2)
    if grep:
        d['F_velt'] = m * 9.81 * inn / max(grep[0], 0.02); d['F_grep'] = grep[1]
    return d

def stamme(hogd, kraft=10.0, svikt_mm=2.0, E=200e9, flyt=235e6 / 2):
    """Minste diameter (mm) på ei rund, massiv stamme som ber handlinga: frå svikt og frå styrke.
    Stivleiken styrer nesten alltid (funn frå northern-lampe). E: stål 200e9, aluminium 70e9."""
    d_stiv = (64 * kraft * hogd ** 3 / (3 * E * svikt_mm / 1000) / math.pi) ** 0.25
    d_sterk = (32 * kraft * hogd / (math.pi * flyt)) ** (1 / 3)
    return dict(stiv=d_stiv * 1000, sterk=d_sterk * 1000, vel=max(d_stiv, d_sterk) * 1000)

def sirkel(x, y, r, n=24):
    a = np.arange(n) / n * 2 * math.pi
    return [(x + r * math.cos(v), y + r * math.sin(v)) for v in a]

# ------------------------------------------------------------------ lysfordeling i snitt

def polar(lys):
    """cd per 1000 lm ut, i loddrett plan gjennom lampa og midten av arbeidsfeltet.
    Vinkel 0 er rett ned, 90 er vassrett mot feltet, 180 er rett opp."""
    pkt = []
    for l in lys:
        pkt += [p for p in l.pts] if not isinstance(l, ls.Ark) else [l.Pf.mean(0)]
    c = np.mean(pkt, 0)
    h = ls.FELT - c; h[2] = 0; h = h / max(np.linalg.norm(h), 1e-9)
    g = np.radians(np.arange(0, 361, 2.0))
    D = np.sin(g)[:, None] * h + np.cos(g)[:, None] * np.array([0, 0, -1.0])
    I = np.zeros(len(g))
    arka = [l for l in lys if isinstance(l, ls.Ark)]
    for l in lys:
        if isinstance(l, ls.Ark):
            for q in range(l.S):
                co = D @ l.nl[q].T
                x = 1 - np.clip(D @ l.rr[q].T, -1, 1); sg = l.sg[q][None]
                gg = np.exp(-(2 * x + x * x / 3) / (2 * sg * sg)) / (2 * math.pi * sg * sg)
                I += np.where(co > 0, l.Fl[q][None] * (l.rd[q][None] * co / math.pi + l.rs[q][None] * gg), 0.0).sum(1) * (l.rgb @ ls.LUM)
        else:
            Il = l.I(D)
            for a in arka:
                if l in a.kjelder:
                    O = np.broadcast_to(l.pts[0], D.shape).copy()
                    Il = np.where(np.isfinite(a.prim.t(O, D)), 0.0, Il)
            I += Il
    lm = sum(getattr(l, 'lm_ut', l.lm) for l in lys)
    return np.degrees(g), I * 1000.0 / max(lm, 1e-9)

# ------------------------------------------------------------------ isolux

def _prosjiser(P, n):
    v = P - ls.KAM.C
    z = v @ ls.KAM.f
    x = (v @ ls.KAM.r) / z / ls.KAM.h; y = (v @ ls.KAM.u) / z / ls.KAM.h
    return np.stack([(x + 1) / 2 * n, (1 - y) / 2 * n], 1), z

def _felt(lys, kropp):
    """Lux frå lampa åleine på eit fint rutenett på bord og vegg."""
    R = ls.rom()
    okkl = ls.STATISK + list(kropp) + [l.prim for l in lys]
    Ed = ls.E_direkte(R.P, R.N, lys, okkl); Ei, _ = R.radiositet(Ed)
    kb, kv, _ = R.kart
    bx = np.linspace(-0.7, 0.7, 113); by = np.linspace(0.0, 0.7, 57)
    BX, BY = np.meshgrid(bx, by, indexing='ij')
    Pb = np.stack([BX.ravel(), BY.ravel(), np.full(BX.size, ls.ZB)], 1)
    Eb = ls.E_direkte(Pb, np.tile([0, 0, 1.0], (len(Pb), 1)), lys, okkl) + kb.oppslag(Pb, Ei[kb.sl].reshape(kb.nu, kb.nv, 3))
    vx = np.linspace(-1.1, 1.1, 111); vz = np.linspace(ls.ZB, ls.ZB + 1.1, 56)
    VX, VZ = np.meshgrid(vx, vz, indexing='ij')
    Pv = np.stack([VX.ravel(), np.full(VX.size, ls.YV), VZ.ravel()], 1)
    Ev = ls.E_direkte(Pv, np.tile([0, -1.0, 0], (len(Pv), 1)), lys, okkl) + kv.oppslag(Pv, Ei[kv.sl].reshape(kv.nu, kv.nv, 3))
    return dict(bx=bx, by=by, Eb=(Eb @ ls.LUM).reshape(BX.shape), vx=vx, vz=vz, Ev=(Ev @ ls.LUM).reshape(VX.shape), okkl=okkl)

def _teikn_isolux(im, F, niv_bord, niv_vegg, font):
    n = im.size[0]
    dr = ImageDraw.Draw(im, 'RGBA'); sett = []
    for E, ax0, ax1, niv, plan in ((F['Eb'], F['bx'], F['by'], niv_bord, 'bord'), (F['Ev'], F['vx'], F['vz'], niv_vegg, 'vegg')):
        for lv in niv:
            beste = None
            for c in find_contours(E, lv):
                a = np.interp(c[:, 0], np.arange(len(ax0)), ax0); bb = np.interp(c[:, 1], np.arange(len(ax1)), ax1)
                W = np.stack([a, bb, np.full(len(a), ls.ZB + 0.002)], 1) if plan == 'bord' else np.stack([a, np.full(len(a), ls.YV - 0.002), bb], 1)
                p, z = _prosjiser(W, n)
                ok = ls.synleg(W, ls.KAM.C, [q for q in F['okkl'] if q not in (ls.BORD, ls.VEGG, ls.ARK)]) & (z > 0)
                seg = []
                for (x, y), v in zip(p, ok):
                    if v: seg.append((x, y))
                    else:
                        if len(seg) > 1: dr.line(seg, fill=(235, 232, 225, 120), width=max(1, n // 400))
                        seg = []
                if len(seg) > 1: dr.line(seg, fill=(235, 232, 225, 120), width=max(1, n // 400))
                syn = p[ok]
                if len(syn) > 12 and (beste is None or len(syn) > len(beste)): beste = syn
            if beste is not None:
                x, y = beste[np.argmax(beste[:, 0])] if plan == 'bord' else beste[np.argmin(beste[:, 1])]
                x, y = (x + 6, y - font.size // 2) if plan == 'bord' else (x - font.size, y - font.size - 4)
                if 0 < x < n - 4 * font.size and 0 < y < n - font.size and all(abs(x - a) > 3 * font.size or abs(y - c) > font.size for a, c in sett):
                    dr.text((x, y), f'{lv:g} lx', font=font, fill=(235, 232, 225, 190)); sett.append((x, y))

# ------------------------------------------------------------------ arket

def _rette_tal(kjelde, maal):
    """Lagar ei utgåve av skrifta der tala er rette (lnum) som standard."""
    from fontTools.ttLib import TTFont
    f = TTFont(kjelde)
    byt = {}
    gs = f['GSUB'].table
    for fr in gs.FeatureList.FeatureRecord:
        if fr.FeatureTag == 'lnum':
            for li in fr.Feature.LookupListIndex:
                for st in gs.LookupList.Lookup[li].SubTable:
                    st = getattr(st, 'ExtSubTable', st)
                    if hasattr(st, 'mapping'): byt.update(st.mapping)
    for t in f['cmap'].tables:
        for kode, glyf in list(t.cmap.items()):
            if glyf in byt: t.cmap[kode] = byt[glyf]
    os.makedirs(os.path.dirname(maal), exist_ok=True)
    f.save(maal)

def _f(st, kursiv=True):
    namn = 'EBGaramond12-Italic.otf' if kursiv else 'EBGaramond12-Regular.otf'
    kjelde = os.path.join(_DER, '..', '..', 'leveransar', '01_fase1_sider', 'fonts', namn)
    maal = os.path.join(_DER, '_skrift', namn.replace('.otf', '-rette-tal.otf'))
    if not os.path.exists(kjelde): return ImageFont.load_default()
    if not os.path.exists(maal):
        try: _rette_tal(kjelde, maal)
        except Exception: return ImageFont.truetype(kjelde, st)
    return ImageFont.truetype(maal, st)

def _tal(x, d=0):
    return f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',')

def _ok(v):
    return '' if v else 'ikkje halde: '

def konseptark(namn, setning, g, kropp=None, fil='ark.png', px=560, ss=2, handling=''):
    """Lagar konseptarket og gjev tala attende. kropp: resultat frå kroppstal(), eller None."""
    S, A = {}, {}
    for t, d in ((0.0, S), (1.0, A)):
        lys, kr = g(t)
        d['tal'] = ls.tal(lys, kr)
        d['felt'] = _felt(lys, kr)
        d['polar'] = polar(lys)
        d['img'] = Image.fromarray(ls.framkall(ls.luminans(lys, kr, px, ss), px)).resize((2 * px, 2 * px), Image.LANCZOS) if ss == 1 else \
            Image.fromarray(ls.framkall(ls.luminans(lys, kr, 2 * px, max(1, ss // 2)), 2 * px))
    _, m = ls.overgang(g, n=5)
    a, s = A['tal'], S['tal']
    Ea = max(a['E_felt'], 1e-9); W350 = a['W'] * 350 / Ea
    Lmaks = lambda d: max(d.get('L_auge25', 0), d['L_lampe'], d.get('L_auge60', 0), d['L_flate'])   # auge 25, 47 og 60 cm over bordet
    La = Lmaks(a) * 350 / Ea; Lst = Lmaks(s)
    vegg350 = a['E_bak'] * 350 / Ea
    lik = ls.likskap(s['_fordeling'], a['_fordeling'])
    n = 2 * px; k = n / 1120.0; marg = int(70 * k); W_ = 2 * n + 3 * marg; H_ = n + 2 * marg + int(640 * k)
    P = lambda v: int(round(v * k))
    ark = Image.new('RGB', (W_, H_), (0, 0, 0))
    fs = _f(max(14, n // 52), False)
    _teikn_isolux(S['img'], S['felt'], (25, 50, 100), (25, 50, 100), fs)
    _teikn_isolux(A['img'], A['felt'], (100, 350, 700), (50, 100, 150), fs)
    ark.paste(S['img'], (marg, marg)); ark.paste(A['img'], (2 * marg + n, marg))
    dr = ImageDraw.Draw(ark)
    kvit, graa = (240, 236, 228), (150, 145, 138)
    fh, fb, fl = _f(P(50)), _f(P(31), False), _f(P(25), False)
    y0 = marg + n + P(46)
    dr.text((marg, y0), namn, font=_f(P(64)), fill=kvit)
    dr.text((marg, y0 + P(84)), setning, font=fb, fill=graa)
    if handling: dr.text((marg, y0 + P(126)), handling, font=fb, fill=graa)
    kol = [(marg, 'stemning', [
        f"{_tal(s['W'], 2)} W · {_tal(s['lm'])} lm ut · {2200} K",
        f"{_tal(s['E_bak'])} lx på veggen bak skjermen",
        f"{_tal(s['E_felt'])} lx på arbeidsfeltet",
        f"{_ok(Lst <= 500)}{_tal(Lst)} cd/m² mot auget (krav 500)",
        f"{_tal(ls.CELLE / s['W'], 1)} timar per celle"]),
           (marg + int(0.265 * W_), 'arbeid', [
        f"{_ok(W350 <= 7.5)}{_tal(W350, 1)} W for 350 lx på feltet (tak 7,5 W)",
        f"jamnheit {_tal(a['U'], 2)} (referanse 0,6)",
        f"{_ok(La <= 1500)}{_tal(La)} cd/m² mot auget ved 350 lx, auge 25 til 60 cm",
        f"{_ok(100 <= vegg350)}{_tal(vegg350)} lx på veggen bak skjermen (krav 100 til 150)",
        f"{_tal(a['E_ansikt'] * 350 / Ea)} lx på ansiktet · {_tal(ls.CELLE / W350, 1)} timar per celle",
        f"{_tal(a['E_skjerm'] * 350 / Ea)} lx på skjermflata ved 350 lx ({_tal(a['E_skjerm'] / Ea, 2)} av feltet)"]),
           (marg + int(0.545 * W_), 'overgang', [
        f"likskap {_tal(lik, 2)} (over 0,9 er ein dimmar)",
        f"{_ok(m['topp'] <= 1.0)}lysaste mellomsteg {_tal(m['topp'], 2)} av endepunktet",
        f"største sprang {_tal(m['sprang'], 2)} · jamn auke {_tal(m['jamn_auke'] * 100)} %"] + ([
        f"{_ok(kropp['masse'] <= 1.2 and kropp['fot'] <= 200)}{_tal(kropp['masse'], 2)} kg · fot {_tal(kropp['fot'])} cm²",
        f"velt {_tal(kropp['velt'])}° · tyngdepunkt {_tal(kropp['tp_hogd'] * 100)} cm"
        + (f" · kjøling {_tal(kropp['kjol'])} av {_tal(kropp['kjol_krav'] * W350 / kropp['W'])} cm²" if kropp.get('kjol') else '')] if kropp else []))]
    yk = y0 + P(200)
    for x, hovud, linjer in kol:
        dr.text((x, yk), hovud, font=fh, fill=kvit)
        dr.line([x, yk + P(66), x + int(dr.textlength(hovud, font=fh)) + P(30), yk + P(64)], fill=kvit, width=max(1, P(2)))
        for i, tx in enumerate(linjer):
            dr.text((x, yk + P(92) + i * P(44)), tx, font=fl, fill=kvit if (i == 0 or 'ikkje halde' in tx) else graa)
    # polar
    cx, cy, r = W_ - marg - P(185), yk + P(150), P(150)
    topp = max(S['polar'][1].max(), A['polar'][1].max(), 1.0)
    skala = next(v for v in (100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 50000) if v >= topp)
    for ring in (1, 2, 3):
        rr = r * ring / 3
        dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(70, 66, 60), width=1)
    dr.line([cx, cy - r - 8, cx, cy + r + 8], fill=(60, 56, 52), width=1); dr.line([cx - r - 8, cy, cx + r + 8, cy], fill=(60, 56, 52), width=1)
    for (gr, I), farge, bredd in ((S['polar'], (125, 120, 114), max(1, P(2))), (A['polar'], (240, 236, 228), max(1, P(3)))):
        pts = [(cx + r * min(i, skala) / skala * math.sin(math.radians(v)), cy + r * min(i, skala) / skala * math.cos(math.radians(v))) for v, i in zip(gr, I)]
        dr.line(pts + pts[:1], fill=farge, width=bredd, joint='curve')
    fp = _f(P(20), False)
    dr.text((cx - r, cy + r + P(14)), 'lysfordeling i snitt', font=fp, fill=graa)
    dr.text((cx - r, cy + r + P(40)), f'ytste ring {skala} cd per 1000 lm', font=fp, fill=graa)
    dr.text((cx - r, cy - r - P(34)), 'opp', font=fp, fill=graa); dr.text((cx + P(40), cy + r - P(10)), 'mot feltet', font=fp, fill=graa)
    ark.save(fil)
    return dict(W350=W350, auge350=La, stemning_auge=Lst, vegg350=vegg350, likskap=lik, jamnheit=a['U'], overgang=m,
                skjerm350=a['E_skjerm'] * 350 / Ea, skjerm_del=a['E_skjerm'] / Ea, arbeid=a, stemning=s)

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    sys.path.insert(0, os.path.join(_DER, '..', 'reflektor'))
    import _mal as mal
    kr = kroppstal([(0.85, (0.47, 0.48, 0.028)), (0.08, (0.47, 0.50, 0.22)), (0.22, (0.47, 0.40, 0.41))], sirkel(0.47, 0.48, 0.06),
                   W=5.0, kjoleflate_cm2=290)
    r = konseptark('Prøve', 'Hol reflektor som vippar frå veggen til feltet.', mal.GREP[1][1], kropp=kr,
                   fil=os.path.join(_DER, 'ark-prove.png'), px=int(sys.argv[1]) if len(sys.argv) > 1 else 280, ss=1,
                   handling='Handlinga: vipp skiva.')
    print({k: (round(v, 2) if isinstance(v, float) else '...') for k, v in r.items()})
