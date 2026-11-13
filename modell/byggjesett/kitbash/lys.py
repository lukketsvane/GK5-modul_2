# -*- coding: utf-8 -*-
"""lys.py · lyset for kvart lysgrep i kitbash-settet, rekna i lysmotoren med same tal som A, B, C og D

Kvart grep er g(t) -> (lys, kropp), t = 0 stemning (1,25 W, 2200 K) og t = 1 arbeid (5 W, 3000 K), slik
konsept/lysskisse/API.md seier. Tala kjem frå ruta.rekn (same nøklar som tre.rekn), skalerte til 350 lx på feltet.
Grepa som alt finst, er importerte og ikkje kopierte: fresnel-familien (plate, knekk2), B og C frå konsept/tre,
ruta og vindaugsdioden frå konsept/film. Nye her: plata fast med vindaugsdiode (to kanalar), band (LED-stripe mot plata),
hovudet som skjerm og arket som røyr.

Plassane er dei same som i kitbash.py (meter her, mm der). Ingenting er målt. Fotontalet er lågt (grovt gitter først).

  python lys.py            alle grep -> tal_lys.json
  python lys.py over-band  berre eitt grep
"""
import os, sys, math, json, time
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
ROT = os.path.dirname(os.path.dirname(os.path.dirname(HER)))


def _skaansam():
    try:
        import ctypes
        k = ctypes.windll.kernel32; h = k.GetCurrentProcess()
        k.SetPriorityClass(h, 0x4000)            # under normal
        k.SetProcessAffinityMask(h, 0xFC)
    except Exception:
        pass


_skaansam()
os.environ.setdefault('LYSSKISSE_POLGE', '0')
for p in ('konsept/lysskisse', 'konsept/film', 'konsept/tre'):
    sys.path.insert(0, os.path.join(ROT, *p.split('/')))
import lysskisse as ls
from lysskisse import b, nrm, watt, straale, fresnelspegel, royr, syl, skive, FELT, YV, LMW, LMW_KJELDE
import ruta
import rute as rutemod
import tre
fre = tre.fre

N_FOTON = 600_000
OVER_C, OVER_A = fre.OVER_C, fre.OVER_A
KP_OVER = OVER_C + 0.12 * OVER_A
VEGG_OVER = b(0.0, YV, 0.60)
BRONN50 = (40, 50, 50)                         # naken diode i brønn på 50°, som i B Over
C_FOT = b(0.44, 0.36, 0.47); KP_FOT = b(0.44, 0.41, 0.05); VEGG_FOT = b(0.10, YV, 0.55)
VINDAUGE_FOT = dict(x0=0.17, x1=0.71, h0=0.26, h1=0.86, kol=2, rad=3, sprosse=0.09)
KROPP_OVER = [syl(b(0.0, 0.568, 0.31), b(0.0, 0.568, 0.645), 0.02)]
KROPP_FOT = [syl(b(0.44, 0.44, 0.0), b(0.44, 0.44, 0.016), 0.079), syl(b(0.44, 0.478, 0.02), b(0.44, 0.478, 0.35), 0.02)]


def fresnel_fast(W, K, c, kp, mot, spreiing=12, kjelde=BRONN50, klipp=None):
    """Kjelda i kp lyser på fresnelplata i c, som speglar midtstrålen mot «mot». Same oppskrift som fre.plate, med eigen watt."""
    sk, kutt, bronn = kjelde
    k = straale(kp, c, W * LMW_KJELDE, K, spreiing=sk, kutt=kutt, opning=0.02, bronn=bronn)
    a = nrm(kp - c); til = nrm(mot - c); tv = np.cross(a, til)
    opp = nrm(tv) if np.linalg.norm(tv) > 1e-6 else None
    return [k, fresnelspegel(k, c, nrm(a + til), spreiing=spreiing, n=fre.N, klipp=klipp, opp=opp)]


def vindauge_paa(led, W, K, v=None):
    """Vindaugsdioden frå D Ruta (ruta.vindaugsdiode), flytta til led. Vindauget v ligg på veggen."""
    gml = ruta.BJELKE
    ruta.BJELKE = np.asarray(led, float) - np.array([0.0, 0.016, 0.0])
    try:
        k = ruta.vindaugsdiode(W, K, N=N_FOTON, v=v or ruta.VINDAUGE)
    finally:
        ruta.BJELKE = gml
    g_siste['rekneskap'] = getattr(k, 'rekneskap', None)
    return k.lys()


g_siste = {}


def to_kanalar(t, q=0.2, W_s=1.25):
    """Som i g_ruta: vindauget har W_s i stemning og q · 5 W i arbeid. Resten går til arbeidslyset."""
    W, K = watt(t); Wv = min(W_s * (q * 5.0 / W_s) ** float(t), W)
    return W, K, Wv, W - Wv


# ------------------------------------------------------------------ grepa
def g_over_vipp(t):
    return fre.plate(t, OVER_C, OVER_A, 0.12, fre.gli(VEGG_OVER, FELT), spreiing=12, kjelde=BRONN50)


def g_over_vindauge(t):
    W, K, Wv, Wp = to_kanalar(t)
    lys = vindauge_paa(b(0.0, 0.575, 0.659), Wv, K)
    if Wp > 0.02:
        lys += fresnel_fast(Wp, K, OVER_C, KP_OVER, FELT)
    return lys, KROPP_OVER


def band_lys(W, K, mot, spreiing=2.5, n=5, halv=0.12):
    """LED-stripa på skjermkanten som n punktkjelder langs x, alle mot plata over. Plata speglar midtstrålen mot «mot»."""
    c = OVER_C; a = nrm(KP_OVER - c); til = nrm(mot - c); nn = nrm(a + til); opp = nrm(np.cross(a, til)); lys = []
    for x in np.linspace(-halv, halv, n):
        d = np.array([x, 0.0, 0.0])
        k = straale(KP_OVER + d, c + d, W / n * LMW_KJELDE, K, spreiing=BRONN50[0], kutt=BRONN50[1], opning=(2 * halv / n, 0.008), bronn=BRONN50[2])
        lys += [k, fresnelspegel(k, c, nn, spreiing=spreiing, n=fre.N, opp=opp)]
    return lys


def band(spreiing=2.5, n=5, halv=0.12, vipp=True):
    """Bandet åleine. Plata vippar frå veggen til feltet (eller står fast mot feltet, då er handlinga ein dimmar)."""
    def g(t):
        W, K = watt(t)
        return band_lys(W, K, VEGG_OVER * (1 - t) + FELT * t if vipp else FELT, spreiing, n, halv), KROPP_OVER
    return g


def band_vindauge(q=0.2, spreiing=2.5, n=5, halv=0.12):
    """Bandet fast mot feltet og vindaugsdioden på toppen av armen. Knotten flyttar watten: ingenting sveipar over skjermen."""
    def g(t):
        W, K, Wv, Wp = to_kanalar(t, q)
        lys = vindauge_paa(b(0.0, 0.575, 0.659), Wv, K)
        if Wp > 0.02:
            lys += band_lys(Wp, K, FELT, spreiing, n, halv)
        return lys, KROPP_OVER
    return g


def vindauge_q(q):
    """Plata fast med punktdiode og vindaugsdiode, med delen q av watten til vindauget i arbeid."""
    def g(t):
        W, K, Wv, Wp = to_kanalar(t, q)
        lys = vindauge_paa(b(0.0, 0.575, 0.659), Wv, K)
        if Wp > 0.02:
            lys += fresnel_fast(Wp, K, OVER_C, KP_OVER, FELT)
        return lys, KROPP_OVER
    return g


def g_over_rute(t, lengd=0.30, djupn=0.19, v=190.0):
    """D Ruta med ruta frå CAD-en (300 × 190) på armen. Rekna som i D: bakbelyst rute med filmen ytst. CAD-ruta er kantbelyst (ANTAKING)."""
    W, K, Wv, Wp = to_kanalar(t)
    BJ = b(0.0, 0.526, 0.50); vr = math.radians(v)
    ut = np.array([0.0, math.sin(vr), math.cos(vr)]); e = np.array([0.0, math.cos(vr), -math.sin(vr)])
    lys = vindauge_paa(b(0.0, 0.575, 0.539), Wv, K)
    if Wp > 0.02:
        lys.append(rutemod.rute(BJ + e * djupn / 2, ut, e, (lengd, djupn), Wp * LMW_KJELDE, K, ruta.ford('ut')))
    return lys, [syl(b(0.0, 0.568, 0.20), b(0.0, 0.568, 0.52), 0.02), syl(BJ - np.array([lengd / 2, 0, 0]), BJ + np.array([lengd / 2, 0, 0]), 0.016)]


def g_fot_vipp(t, c=C_FOT, klipp=None):
    a = nrm(KP_FOT - c); s = float(np.linalg.norm(KP_FOT - c))
    lys, _ = fre.plate(t, c, a, s, fre.gli(VEGG_FOT, FELT), spreiing=12, kjelde=fre.SMAL, klipp=klipp)
    return lys, KROPP_FOT


def g_fot_knekk(t):
    a = nrm(KP_FOT - C_FOT); s = float(np.linalg.norm(KP_FOT - C_FOT))
    lys, _ = fre.knekk2(t, C_FOT, a, s, VEGG_FOT, FELT, spreiing=12, kjelde=fre.SMAL, flytt=0.03, flik=0.10)
    return lys, KROPP_FOT


def g_fot_vindauge(t):
    W, K, Wv, Wp = to_kanalar(t)
    lys = vindauge_paa(b(0.44, 0.490, 0.387), Wv, K, v=VINDAUGE_FOT)
    if Wp > 0.02:
        lys += fresnel_fast(Wp, K, C_FOT, KP_FOT, FELT, kjelde=fre.SMAL)
    return lys, KROPP_FOT


def g_fot_skive(t):
    return g_fot_vipp(t, c=b(0.44, 0.36, 0.55), klipp=lambda u, v: u * u + v * v <= 0.1425 ** 2)


# ruta på fot slik CAD-en står: same rekning som konsept/film/cad/lys_sjekk.py, med måla frå lampe.py skrivne inn her
# (lampe.py importerer cadquery). Hellinga går frå 80° i stemning til 35° i arbeid.
_RF = dict(YB=24.5, AKSE_H=260.0, X0=-231.0, X1=69.0, U_KANT=3.9, RUTE_D=190.0, RUTE_B=300.0, PLASS=(0.47, 0.30), INN=0.60, OPP=0.30, NED=0.60, KANT=0.10)
_FORD = {}
def g_fot_rute(t):
    if not _FORD:
        _FORD['opp'] = rutemod.utfordeling(innside='flat'); _FORD['ned'] = rutemod.utfordeling(film=None)
    W, K = watt(t); vinkel = 80.0 - 45.0 * float(t); r = _RF; tt = math.radians(vinkel)
    s = np.array([0.0, -math.cos(tt), -math.sin(tt)]); n = np.array([0.0, -math.sin(tt), math.cos(tt)])
    akse = np.array([0.0, r['YB'] / 1000, r['AKSE_H'] / 1000]); xm = 0.5 * (r['X0'] + r['X1']) / 1000
    c = b(r['PLASS'][0] + xm, r['PLASS'][1], 0) + akse + s * (r['U_KANT'] + r['RUTE_D'] / 2) / 1000
    lm = W * 100 * r['INN']; st = (r['RUTE_B'] / 1000, r['RUTE_D'] / 1000)
    opp = rutemod.rute(c + n * 0.002, n, s, st, lm * r['OPP'] / _FORD['opp']['verknad'], K, _FORD['opp'], 'opp')
    ned = rutemod.rute(c - n * 0.002, -n, s, st, lm * r['NED'] / _FORD['ned']['verknad'], K, _FORD['ned'], 'ned')
    kc = b(r['PLASS'][0] + xm, r['PLASS'][1], 0) + akse + s * (r['U_KANT'] + r['RUTE_D']) / 1000
    kant = ls.flate(kc - n * 0.003, -n, (r['RUTE_B'] / 1000, 0.004), lm * r['KANT'], K, opp=(1, 0, 0))
    for l in (opp, ned):
        l.lm = 0.0
    kant.lm = W * 100; kant.mater = True; kant.lm_ut = lm * r['KANT']
    return [opp, ned, kant], [syl(b(0.47, 0.30, 0.0), b(0.47, 0.30, 0.016), 0.079)]


def g_fot_hovud(t):
    """Hovudet P03 med opninga ned: ei vanleg skjerma arbeidslampe. Handlinga er ein dimmar."""
    W, K = watt(t)
    return [straale(b(0.353, 0.433, 0.308), FELT, W * LMW, K, spreiing=25, kutt=50, opning=(0.14, 0.078), bronn=45)], KROPP_FOT


def g_fot_royr(t):
    """Prismearket som røyr Ø97 × 535 mm rundt ei diode. ANTAKING: 80 % kjem ut, jamt fordelt som eit glødande røyr."""
    W, K = watt(t)
    return [royr(b(0.44, 0.44, 0.03), b(0.44, 0.44, 0.55), 0.0485, W * LMW * 0.8, K)], [skive(b(0.44, 0.44, 0.004), (0, 0, 1), 0.079)]


GREP = [
    ('over-vipp', g_over_vipp), ('over-flik', tre._B), ('over-vindauge', g_over_vindauge),
    ('over-rute', g_over_rute), ('fot-vipp', g_fot_vipp), ('fot-knekk', g_fot_knekk), ('fot-vindauge', g_fot_vindauge),
    ('fot-skive', g_fot_skive), ('fot-rute', g_fot_rute), ('fot-linse', tre._C), ('fot-hovud', g_fot_hovud), ('fot-royr', g_fot_royr),
    ('ref-A', tre._A), ('ref-D', ruta.g_ruta(N=N_FOTON)),
    # bandet er tungt (fem kjelder mot plata), så det står sist
    ('over-band', band(2.5)), ('over-band-vindauge', band_vindauge(0.2)), ('over-band-vindauge-q30', band_vindauge(0.3)),
    ('over-vindauge-q30', vindauge_q(0.3)), ('over-band-ark6', band(6.0)), ('over-band-3', band(2.5, n=3)), ('over-band-kort', band(2.5, halv=0.06)),
]


def _j(o):
    if isinstance(o, (np.floating, np.integer)): return float(o)
    if isinstance(o, np.ndarray): return o.tolist()
    return str(o)


if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    fil = os.path.join(HER, 'tal_lys.json')
    ut = json.load(open(fil, encoding='utf-8')) if os.path.exists(fil) else {}
    kva = sys.argv[1:]
    for namn, g in GREP:
        if kva and namn not in kva:
            continue
        t0 = time.time()
        try:
            r = ruta.rekn(g, n=5)
            r = {k: v for k, v in r.items() if k not in ('konsept', 'namn')}; r['sek'] = round(time.time() - t0, 1)
            if g_siste.get('rekneskap') is not None and 'vindauge' in namn or namn == 'over-rute':
                r['vindauge_rekneskap'] = g_siste.get('rekneskap')
            ut[namn] = r
            print(ruta.linje(namn, r), ' (%.0f s)' % (time.time() - t0), flush=True)
        except Exception as e:
            import traceback; traceback.print_exc()
            ut[namn] = dict(feil=repr(e)); print(namn, 'FEIL', repr(e), flush=True)
        json.dump(ut, open(fil, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=_j)
