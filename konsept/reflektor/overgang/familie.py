# -*- coding: utf-8 -*-
"""Familien OVERGANG: korleis éi og same lampe går frå stemningslys til arbeidslys.

  python familie.py              tal.md, tal.csv, overgang.csv og bretta (px=200) for GREP (generasjon 3 og fire referansar)
  python familie.py par          par-NAMN.png for dei tre beste (px=240, steg 0, 0,5 og 1)
  python familie.py sok 3        overgang(g, n=7) på generasjon 3, skriv journal-gen3.jsonl (1 og 2 likeins)
  python familie.py tal          berre tal.md, tal.csv og overgang.csv (px=0)

Bygd på ../_mal.py. Kroppen er underordna: flat, hol eller fresnel reflektor og enkle strøk.
Det som varierer, er mekanismen. Eit lysgrep er g(t) -> (lys, kropp), t = 0 stemning, t = 1 arbeid.
"""
import sys, os, json, math, time
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *
import lysskisse as _ls

# ------------------------------------------------------------------ felles geometri (som i malen)

FOT = (0.47, 0.48)                      # foten står til høgre for skjermen
KP = b(FOT[0], FOT[1], 0.05)            # kjelda i foten
C = b(0.47, 0.40, 0.41)                 # arksenter, framfor skjermplanet
VM = b(0.0, YV, 0.45)                   # veggmålet: veggen bak skjermen
D_OPP = nrm(C - KP)                     # strålen frå foten opp mot arket
KROPP = [syl(b(FOT[0], FOT[1], 0), b(FOT[0], FOT[1], 0.05), 0.06)]

def rot(v, akse, grader):
    a = nrm(akse); th = math.radians(grader); v = np.asarray(v, float)
    return v * math.cos(th) + np.cross(a, v) * math.sin(th) + a * (a @ v) * (1 - math.cos(th))

def nmot(kp, c, mot):
    """Normalen som speglar lyset frå kp via c mot «mot»."""
    return nrm(nrm(kp - c) + nrm(mot - c))

def kjelde(t, kp=KP, mot=C, spr=10, andel=1.0):
    W, K = watt(t)
    return straale(kp, mot, W * LMW_KJELDE * andel, K, spreiing=spr, kutt=2 * spr, opning=0.02, bronn=40)

N0 = nmot(KP, C, VM)                    # arket speglar mot veggen
N1 = nmot(KP, C, FELT)                  # arket speglar mot feltet
_a = np.cross(N0, N1)
VINKEL = math.degrees(math.atan2(np.linalg.norm(_a), N0 @ N1))     # 36,4 grader mellom dei to stillingane
AKSE = nrm(_a)                          # vippeaksen: éin hengsel går frå vegg til felt

# ------------------------------------------------------------------ mekanismane

def dimmar(t):
    """Referanse: fast ark mot feltet, berre watten endrar seg."""
    k = kjelde(t)
    return [k, ark(k, C, N1, 0.25, framside=SATIN)], KROPP

def vipp(t, side=SATIN, form=None, storleik=0.25, n0=None, spr=10, nfl=22):
    """Vippe arket om éin hengsel: speglinga går frå veggen bak skjermen til feltet."""
    k = kjelde(t, spr=spr)
    na = N0 if n0 is None else n0
    ax = np.cross(na, N1); vk = math.degrees(math.atan2(np.linalg.norm(ax), na @ N1))
    n = rot(na, ax, vk * t)
    return [k, ark(k, C, n, storleik, form=form, framside=side, opp=nrm(ax), n=nfl)], KROPP

def vend(t, retning=1, vinkel=180.0, bak=MATT):
    """Vende arket i ein gaffel: matt bakside ned i stemning, satinert framside ned i arbeid."""
    k = kjelde(t)
    gaffel = nrm(np.cross(N1, (0, 0, 1)))                  # vassrett akse i arkplanet
    n = rot(N1, gaffel, retning * vinkel * (1 - t))
    return [k, ark(k, C, n, 0.25, framside=SATIN, bakside=bak, opp=gaffel)], KROPP

def skyv(t, slag='hol', nar=0.10, fjern=None, spr=None):
    """Skyve kjelda langs stamma (strålen er stamma): nær arket i stemning, nede i foten i arbeid."""
    fjern = float(np.linalg.norm(KP - C)) if fjern is None else fjern
    s = nar + (fjern - nar) * t
    kp = C - D_OPP * s
    if slag == 'fresnel':
        k = kjelde(t, kp=kp, spr=15 if spr is None else spr)
        a = fresnelspegel(k, C, N1, spreiing=8)
    else:
        k = kjelde(t, kp=kp, spr=10 if spr is None else spr)
        a = ark(k, C, N1, 0.25, form=boy(1 / 0.6), framside=SATIN)
    return [k, a], KROPP + [syl(KP, kp - 0.02 * D_OPP, 0.004)]

def skyv_bue(t, lengd=0.20, hol=True, spr=6):
    """Kjelda glir på ei skinne under ein boge. Kvar strålen treff bogen, avgjer kvar lyset går."""
    nm = rot(N0, AKSE, VINKEL / 2)
    kappa = math.radians(VINKEL) / lengd * (1 if hol else -1)
    ex = nrm(np.cross(AKSE, nm))
    u = (lengd / 2) * (1 - 2 * t) * (1 if hol else -1)
    x = math.sin(kappa * u) / kappa; z = (1 - math.cos(kappa * u)) / kappa
    p = C + ex * x + nm * z
    kp = p - D_OPP * 0.37
    k = kjelde(t, kp=kp, mot=p, spr=spr)
    a = ark(k, C, nm, (lengd + 0.14, 0.16), form=boy(kappa), framside=SATIN, opp=AKSE)
    return [k, a], [syl(kp - np.array([0, 0, 0.05]), kp, 0.03)]

def boy_sym(t, k0=-3.0, k1=1 / 0.6):
    """Bøye arket symmetrisk: kuv i stemning, hol i arbeid. Krumminga er t."""
    k = kjelde(t)
    return [k, ark(k, C, N1, (0.25, 0.25), form=boy(k0 + (k1 - k0) * t), framside=SATIN)], KROPP

def klemt(kappa, u0):
    """Ark klemt i kanten u0 og bøygd med konstant krumming derifrå (utfaldbart)."""
    def f(U, V):
        if abs(kappa) < 1e-6: return U, V, np.zeros_like(U)
        th = kappa * (U - u0)
        return u0 + np.sin(th) / kappa, V, (1 - np.cos(th)) / kappa
    return f

def boy_klemt(t, hol=True, w=0.25, slutt=0.0, side=SATIN):
    """Arket er klemt i éin kant og blir bøygd: flatt mot feltet i arbeid, krumma mot veggen i stemning."""
    k = kjelde(t)
    u0 = -w / 2 if hol else w / 2
    kmax = math.radians(VINKEL) / (w / 2) * (1 if hol else -1)        # midten av arket peikar då mot veggen
    kap = kmax * (1 - t) + slutt * t
    return [k, ark(k, C, N1, (w, w), form=klemt(kap, u0), framside=side, opp=AKSE)], KROPP

def drei(t, slag='to', r0=0.085, d=0.34, spr=6):
    """Dreie ei skive i sitt eige plan. Strålen treff utanfor sentrum.
    «to»: halve skiva er matt, halve satinert. «hol»: halve skiva er klipt bort, lyset går i taket."""
    k = kjelde(t, spr=spr)
    ex0, _ = ortho(N1)
    cd = C - ex0 * r0
    rull = 180.0 * (1 - t)
    a1 = ark(k, cd, N1, d, rull=rull, klipp=lambda u, v: u > 0, framside=SATIN)
    lys = [k, a1]
    if slag == 'to':
        a2 = ark(k, cd, N1, d, rull=rull, klipp=lambda u, v: u <= 0, framside=MATT)
        k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)      # motoren trekkjer berre frå det siste arket
        lys.append(a2)
    return lys, KROPP

def hev(t, lag=0.12, hog=None):
    """Heve og senke arket langs strålen: lågt gjev lysøy ved foten, høgt når feltet."""
    hog = float(np.linalg.norm(C - KP)) if hog is None else hog
    c = KP + D_OPP * (lag + (hog - lag) * t)
    k = kjelde(t, mot=c)
    return [k, ark(k, c, N1, 0.25, framside=SATIN)], KROPP + [syl(KP, c, 0.004)]

def _stiv(p, fi, flytt):
    """Roter punkt om den loddrette aksen gjennom foten og flytt."""
    F = np.array([FOT[0], FOT[1], 0.0]); cs, sn = math.cos(math.radians(fi)), math.sin(math.radians(fi))
    q = np.asarray(p, float) - F
    return F + np.array([cs * q[0] - sn * q[1], sn * q[0] + cs * q[1], q[2]]) + np.array([flytt[0], flytt[1], 0.0])

def _retn(v, fi):
    cs, sn = math.cos(math.radians(fi)), math.sin(math.radians(fi))
    return np.array([cs * v[0] - sn * v[1], sn * v[0] + cs * v[1], v[2]])

def drei_fot(t, fi0=-50.0, flytt0=(0.0, 0.0), side=SATIN, form=None):
    """Dreie heile lampa på foten (og eventuelt flytte ho): strålen sveipar frå bak skjermen til feltet."""
    fi = fi0 * (1 - t); fl = (flytt0[0] * (1 - t), flytt0[1] * (1 - t))
    kp = _stiv(KP, fi, fl); c = _stiv(C, fi, fl); n = _retn(N1, fi)
    k = kjelde(t, kp=kp, mot=c)
    fot = [syl(_stiv(b(FOT[0], FOT[1], 0), fi, fl), _stiv(b(FOT[0], FOT[1], 0.05), fi, fl), 0.06)]
    return [k, ark(k, c, n, 0.25, framside=side, form=form)], fot

def kryss(t, arbeid_vegg=0.0):
    """Kryssdimme to kjelder: éi lyser rett på veggen bak skjermen, éi lyser på arket mot feltet."""
    W, K = watt(t)
    fa = t * (1 - arbeid_vegg)                               # delen av watten som går til arket
    lys = []
    if fa > 1e-6:
        k = straale(KP, C, W * fa * LMW_KJELDE, K, spreiing=10, kutt=20, opning=0.02, bronn=40)
        lys += [k, ark(k, C, N1, 0.25, framside=SATIN)]
    if 1 - fa > 1e-6:
        pv = b(0.44, 0.53, 0.05)
        lys.append(straale(pv, VM, W * (1 - fa) * LMW, K, flat=(28, 14), kutt=50, opning=(0.06, 0.02), bronn=45))
    return lys, KROPP

def fald_ving(t, w=0.25):
    """Opne ein fald: halve arket står mot veggen i stemning og faldar seg flatt mot feltet i arbeid."""
    k = kjelde(t)
    th = math.radians(VINKEL) * (1 - t)
    def f(U, V):
        pos = U > 0
        return np.where(pos, U * math.cos(th), U), V, np.where(pos, U * math.sin(th), 0.0)
    return [k, ark(k, C, N1, (w, w), form=f, framside=SATIN, opp=AKSE)], KROPP

def fresnel_vipp(t, s=0.26, spr=8):
    """Vippe fresnelplata frå overheadprojektoren, med diffusorark oppå."""
    kp = C - D_OPP * s
    k = kjelde(t, kp=kp, spr=15)
    n = rot(N0, AKSE, VINKEL * t)
    return [k, fresnelspegel(k, C, n, spreiing=spr, opp=AKSE)], KROPP + [syl(KP, kp - 0.02 * D_OPP, 0.004)]

def spegel_vipp(t):
    """Vippe frontflatespegelen frå overheadprojektoren (blank, 12 x 14 cm)."""
    return vipp(t, side=BLANK, storleik=(0.12, 0.14), spr=5, nfl=30)

def vipp_ansikt(t):
    """Veltar: stemninga er ansiktslys. Arket vippar frå auget til feltet."""
    return vipp(t, n0=nmot(KP, C, AUGE))

def skaal(t, kmax=3.0):
    """Kan ikkje lagast: ei skål som går frå kuv til hol. Dobbeltkrumma, arket må tøyast."""
    k = kjelde(t)
    kap = kmax * (2 * t - 1)
    f = lambda U, V: (U, V, kap * (U * U + V * V) / 2)
    return [k, ark(k, C, N1, 0.25, form=f, framside=SATIN)], KROPP

GEN1 = [
    ('dimmar',        dimmar),
    ('vipp',          vipp),
    ('vend-a',        lambda t: vend(t, 1)),
    ('vend-b',        lambda t: vend(t, -1)),
    ('skyv-hol',      lambda t: skyv(t, 'hol')),
    ('skyv-fresnel',  lambda t: skyv(t, 'fresnel', nar=0.08, fjern=0.26)),
    ('skyv-bue',      skyv_bue),
    ('boy-sym',       boy_sym),
    ('boy-klemt-hol', lambda t: boy_klemt(t, True)),
    ('boy-klemt-kuv', lambda t: boy_klemt(t, False)),
    ('drei-to',       lambda t: drei(t, 'to')),
    ('drei-hol',      lambda t: drei(t, 'hol')),
    ('hev',           hev),
    ('drei-fot',      drei_fot),
    ('flytt',         lambda t: drei_fot(t, fi0=-75.0, flytt0=(0.10, 0.10))),
    ('kryss',         kryss),
    ('fald-ving',     fald_ving),
    ('fresnel-vipp',  fresnel_vipp),
    ('spegel-vipp',   spegel_vipp),
    ('VELT vipp-ansikt', vipp_ansikt),
    ('UMOGLEG skaal', skaal),
]

# ------------------------------------------------------------------ generasjon 2: strålen går til veggen, arket skjer han
#
# Oppstilling B. Foten står framme til høgre, og kjelda lyser bakover og opp mot veggen over skjermen.
# Arket står i strålen framfor skjermplanet. Det arket fangar, går til feltet. Resten held fram til veggen.

FOT2 = (0.62, 0.22)
KP2 = b(FOT2[0], FOT2[1], 0.05)
WT = b(0.25, YV, 0.80)                  # veggmålet til den frie strålen. Strålen går 17 cm til høgre for skjermkanten
D_B = nrm(WT - KP2)
C2 = KP2 + D_B * 0.375                  # arksenter, om lag 33 cm over bordet
N2 = nmot(KP2, C2, FELT)
KROPP2 = [syl(b(FOT2[0], FOT2[1], 0), b(FOT2[0], FOT2[1], 0.05), 0.06)]
EX2, EY2 = ortho(N2)

def kjelde2(t, spr=8, andel=1.0):
    W, K = watt(t)
    return straale(KP2, C2, W * LMW_KJELDE * andel, K, spreiing=spr, kutt=2 * spr, opning=0.02, bronn=40)

def skjer(t, ut=0.27, retning=None, d=0.25, side=SATIN, klipp=None, form=None, spr=8, t_slutt=1.0):
    """Skyve arket inn i strålen i sitt eige plan. Delen som er inne, går til feltet, resten til veggen."""
    k = kjelde2(t, spr=spr)
    e = EX2 if retning is None else retning
    c = C2 + e * ut * (1 - t * t_slutt)
    return [k, ark(k, c, N2, d, framside=side, klipp=klipp, form=form)], KROPP2

def drei_b(t, r0=0.085, d=0.34, spr=6, klipp=None, start=180.0):
    """Dreie ei klipt skive i strålen: den klipte halvdelen slepp lyset til veggen."""
    k = kjelde2(t, spr=spr)
    cd = C2 - EX2 * r0
    kl = (lambda u, v: u > 0) if klipp is None else klipp
    return [k, ark(k, cd, N2, d, rull=start * (1 - t), klipp=kl, framside=SATIN)], KROPP2

def spjeld(t, side=SATIN, d=0.25, forteikn=1):
    """Spjeld: arket står på høgkant i strålen i stemning og blir vridd til arbeidsvinkelen."""
    k = kjelde2(t)
    ax = nrm(np.cross(D_B, nrm(FELT - C2)))
    inn = math.degrees(math.acos(abs(-D_B @ N2)))            # innfallsvinkelen i arbeid
    n = rot(N2, ax, -forteikn * (90 - inn) * (1 - t))
    return [k, ark(k, C2, n, d, framside=side, opp=ax)], KROPP2

def vipp_b(t, side=SATIN):
    """Vippe i oppstilling B: frå veggen (arket speglar strålen attende mot veggen bak skjermen) til feltet."""
    k = kjelde2(t)
    n0 = nmot(KP2, C2, VM)
    ax = np.cross(n0, N2); vk = math.degrees(math.atan2(np.linalg.norm(ax), n0 @ N2))
    return [k, ark(k, C2, rot(n0, ax, vk * t), 0.25, framside=side, opp=nrm(ax))], KROPP2

def kryss_b(t, arbeid_vegg=0.3):
    """Fast ark med slissar i strålen: ein fast del går alltid til veggen. Berre watten endrar seg (referanse)."""
    k = kjelde2(t)
    kl = lambda u, v: np.floor((u + 0.2) / 0.02) % 10 >= 10 * arbeid_vegg
    return [k, ark(k, C2, N2, 0.25, framside=SATIN, klipp=kl)], KROPP2

def skjermlux(lys, kropp):
    """Lux frå lampa på framsida av skjermen (snitt, maks). Motoren måler ikkje dette sjølv."""
    xs = np.linspace(-0.24, 0.24, 9); zs = np.linspace(0.14, 0.39, 5)
    P = np.array([b(x, 0.449, z) for x in xs for z in zs]); N = np.tile([0.0, -1.0, 0.0], (len(P), 1))
    okkl = [p for p in STATISK if p is not SKJERM] + list(kropp) + [l.prim for l in lys]
    E = E_direkte(P, N, lys, okkl) @ LUM
    return float(E.mean()), float(E.max())

def fresnel_skjer(t, ut=0.30):
    """Fresnelplata frå overheadprojektoren blir skoven inn i veggstrålen, med diffusorark oppå."""
    k = kjelde2(t)
    return [k, fresnelspegel(k, C2 + EX2 * ut * (1 - t), N2, spreiing=8)], KROPP2

def fald_opp(t, uf=-0.015, w=0.25):
    """Flatt ark mot veggen i stemning. I arbeid faldar den største vengen seg mot feltet, og resten held veggen."""
    k = kjelde(t)
    th = math.radians(VINKEL) * t
    def f(U, V):
        pos = U > uf
        return np.where(pos, uf + (U - uf) * math.cos(th), U), V, np.where(pos, -(U - uf) * math.sin(th), 0.0)
    return [k, ark(k, C, N0, (w, w), form=f, framside=SATIN, opp=AKSE)], KROPP

def ring(t, r=0.085):
    """Fast ring mot veggen og ei skive i midten som vippar frå veggen til feltet."""
    k = kjelde(t)
    a1 = ark(k, C, N0, 0.30, klipp=lambda u, v: u * u + v * v > r * r, framside=SATIN, opp=AKSE)
    a2 = ark(k, C, rot(N0, AKSE, VINKEL * t), 2 * r, framside=SATIN, opp=AKSE)
    k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)          # motoren trekkjer berre frå det siste arket
    return [k, a1, a2], KROPP

def snigel(r0=0.09, rho=0.08):
    """Klipp: kanten er ein spiral, så dreiinga slepp strålen gradvis forbi."""
    return lambda u, v: np.hypot(u, v) > (r0 - rho) + 2 * rho * np.abs(np.arctan2(v, u)) / PI

SLISS40 = lambda u, v: ((u + 0.5) % 0.025) >= 0.010          # 40 % ope, 60 % ark
GEN2 = [
    ('skjer',         skjer),
    ('skjer-57',      lambda t: skjer(t, t_slutt=1 - 0.105 / 0.27)),
    ('skjer-slissa',  lambda t: skjer(t, klipp=SLISS40)),
    ('drei-b',        drei_b),
    ('drei-snigel',   lambda t: drei_b(t, r0=0.09, d=0.36, klipp=snigel())),
    ('spjeld',        spjeld),
    ('vipp-b',        vipp_b),
    ('fresnel-skjer', fresnel_skjer),
    ('kryss-b',       kryss_b),
    ('kryss-43',      lambda t: kryss(t, 0.43)),
    ('fald-opp',      fald_opp),
    ('ring',          ring),
    ('VELT skjer-matt',      lambda t: skjer(t, side=MATT)),
    ('UMOGLEG skjer-kuppel', lambda t: skjer(t, form=lambda U, V: (U, V, 4.0 * (U * U + V * V) / 2))),
]

# ------------------------------------------------------------------ generasjon 3: stemninga flyttar adresse
#
# Generasjon 2 synte at likskap under 0,3 og 100 lx på veggen i arbeid ikkje går saman så lenge stemninga bur
# på veggen nær skjermen. Her bur stemninga i taket, høgt på veggen eller på bordet, og arbeidet er felt + veggstrøk.

TAKM = b(0.30, 0.20, 1.78)              # taket over bordet (taket er 2,5 m over golvet, 1,78 m over bordplata)
HOGM = b(0.0, YV, 1.15)                 # veggen over veggsona (sona sluttar 78 cm over bordet)
BORDM = b(0.52, 0.10, 0.0)              # bordet framfor foten, utanfor arbeidsfeltet
HOVUD = b(0.47, 0.42, 0.57)             # toppen av lampa, over arket (arket når 54 cm)

def vaskar(lm, K, mot=VM, pos=None, vift=(28, 14)):
    """Veggvaskar frå foten: vifte mot veggen bak skjermen."""
    pos = b(0.44, 0.53, 0.05) if pos is None else pos
    return straale(pos, mot, lm, K, flat=vift, kutt=50, opning=(0.06, 0.02), bronn=45)

def stemningsstrok(adresse, lm, K):
    if adresse == 'tak':
        return straale(HOVUD, TAKM, lm, K, spreiing=18, kutt=36, opning=0.03, bronn=40)
    if adresse == 'hog':
        return straale(HOVUD, HOGM, lm, K, flat=(30, 10), kutt=45, opning=(0.05, 0.02), bronn=40)
    if adresse == 'bord':
        return straale(C + N1 * 0.02, BORDM, lm, K, spreiing=10, kutt=20, opning=0.02, bronn=40)
    return vaskar(lm, K)

def kryss3(t, adresse='tak', av=0.43):
    """Kryssdimme: stemningsstrøket (tak, høg vegg, bord) blir dimma ned medan arket mot feltet og vaskaren kjem opp."""
    W, K = watt(t)
    lys = []
    if t < 1 - 1e-6:
        lys.append(stemningsstrok(adresse, W * (1 - t) * (LMW_KJELDE if adresse == 'bord' else LMW), K))
    # arket står der heile tida (òg i stemning, då nesten utan lys), så det skuggar likt i alle steg
    k = straale(KP, C, max(W * t * (1 - av) * LMW_KJELDE, 1e-3), K, spreiing=10, kutt=20, opning=0.02, bronn=40)
    lys += [k, ark(k, C, N1, 0.25, framside=SATIN)]
    if t > 1e-6 and av > 0: lys.append(vaskar(W * t * av * LMW, K))
    return lys, KROPP

def fald3(t, opp_grader=25.0, ving=0.0):
    """Opne ein fald. Stemning: flatt ark som speglar høgt (vegg over sona eller tak).
    Arbeid: den eine vengen speglar mot feltet, den andre mot veggen bak skjermen. Faldlinja er parallell med vippeaksen.
    ving flyttar faldlinja (meter langs u): positiv gjev større veng mot veggen."""
    k = kjelde(t)
    nh = rot(N0, AKSE, -opp_grader)
    n_felt = rot(nh, AKSE, (opp_grader + VINKEL) * t)
    n_vegg = rot(nh, AKSE, opp_grader * t)
    a1 = ark(k, C, n_felt, 0.27, klipp=lambda u, v: u > ving, framside=SATIN, opp=AKSE)
    a2 = ark(k, C, n_vegg, 0.27, klipp=lambda u, v: u <= ving, framside=SATIN, opp=AKSE)
    k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)          # motoren trekkjer berre frå det siste arket
    return [k, a1, a2], KROPP

def vipp3(t, opp_grader=40.0):
    """Kontroll: éitt ark vippar frå taket til feltet. Ingen veggstrøk i arbeid."""
    return vipp(t, n0=rot(N0, AKSE, -opp_grader))

TAKM2 = b(0.55, 0.05, 1.78)             # taket over foten i oppstilling B
def spjeld3(t, storleik=(0.22, 0.30), inn=0.0):
    """Oppstilling B. Stemning: arket står tvers i strålen og speglar alt i taket.
    Ved å dreie det til arbeidsvinkelen fangar det mindre (kosinus), og resten går forbi til veggen."""
    k = kjelde2(t)
    n_s = nmot(KP2, C2, TAKM2)
    ax = np.cross(n_s, N2); vk = math.degrees(math.atan2(np.linalg.norm(ax), n_s @ N2))
    c = C2 + EX2 * inn * t
    return [k, ark(k, c, rot(n_s, nrm(ax), vk * t), storleik, framside=SATIN, opp=nrm(ax))], KROPP2

def glod_kryss(t):
    """Veltar: stemninga er ei naken glødande perle på toppen av lampa (kjelda er synleg som punkt, bryt R3 og F5)."""
    W, K = watt(t)
    lys = []
    if t < 1 - 1e-6: lys.append(glod(HOVUD, 0.012, W * (1 - t) * LMW, K))
    k = straale(KP, C, max(W * t * 0.57 * LMW_KJELDE, 1e-3), K, spreiing=10, kutt=20, opning=0.02, bronn=40)
    lys += [k, ark(k, C, N1, 0.25, framside=SATIN)]
    if t > 1e-6: lys.append(vaskar(W * t * 0.43 * LMW, K))
    return lys, KROPP

def fald3_kuppel(t):
    """Kan ikkje lagast: faldarket der vengen mot feltet òg er pressa til ei skål (dobbeltkrumma)."""
    k = kjelde(t)
    nh = rot(N0, AKSE, -40.0)
    kap = 6.0
    f = lambda U, V: (U, V, kap * (U * U + V * V) / 2)
    a1 = ark(k, C, rot(nh, AKSE, (40.0 + VINKEL) * t), 0.27, klipp=lambda u, v: u > 0, framside=SATIN, opp=AKSE, form=f)
    a2 = ark(k, C, rot(nh, AKSE, 40.0 * t), 0.27, klipp=lambda u, v: u <= 0, framside=SATIN, opp=AKSE)
    k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)
    return [k, a1, a2], KROPP

GEN3 = [
    ('kryss-tak',     lambda t: kryss3(t, 'tak')),
    ('kryss-tak-30',  lambda t: kryss3(t, 'tak', av=0.30)),
    ('kryss-hog',     lambda t: kryss3(t, 'hog')),
    ('kryss-bord',    lambda t: kryss3(t, 'bord')),
    ('fald-hog',      lambda t: fald3(t, 25.0)),
    ('fald-tak',      lambda t: fald3(t, 40.0)),
    ('fald-tak-veng', lambda t: fald3(t, 40.0, ving=0.03)),
    ('vipp-tak',      vipp3),
    ('spjeld-tak',    spjeld3),
    ('spjeld-tak-sm', lambda t: spjeld3(t, storleik=(0.16, 0.30))),
    ('VELT glod-kryss',     glod_kryss),
    ('UMOGLEG fald-kuppel', fald3_kuppel),
]

GEN = {1: GEN1, 2: GEN2, 3: GEN3}
_ALLE = dict(GEN1 + GEN2 + GEN3)
# Brettet: heile generasjon 3, og dei beste frå generasjon 1 og 2 som referanse (16 ruter, 4 x 4).
GREP = GEN3 + [(n, _ALLE[n]) for n in ('skjer', 'drei-snigel', 'skjer-57', 'vipp')]
BESTE = ['kryss-hog', 'skjer', 'drei-snigel']

# ------------------------------------------------------------------ søk og leveranse

def sok(greps, fil, n=7):
    """overgang(g, n) på kvart lysgrep. Skriv éi linje per grep til ein journal, så arbeidet overlever avbrot."""
    ferdig = set()
    if os.path.exists(fil):
        for l in open(fil, encoding='utf-8'):
            try: ferdig.add(json.loads(l)['namn'])
            except Exception: pass
    for namn, g in greps:
        if namn in ferdig: continue
        t0 = time.time()
        try:
            R, m = overgang(g, n=n)
        except Exception as e:
            print('%-18s FEIL %r' % (namn, e)); continue
        r = _ls._rad(namn, R[0], R[-1])
        sk = [skjermlux(*g(float(t))) for t in m['t']]
        rad = dict(namn=namn, topp=m['topp'], sprang=m['sprang'], jamn_auke=m['jamn_auke'], t=m['t'],
                   auge=m['auge'], felt=m['felt'], vegg=m['vegg'],
                   L_lampe=[x['L_lampe'] for x in R], L_flate=[x['L_flate'] for x in R],
                   ansikt=[x['E_ansikt'] for x in R], U=[x['U'] for x in R], spegl=[x['L_spegl'] for x in R],
                   lm=[x['lm'] for x in R], W=[x['W'] for x in R], skjerm_snitt=[x[0] for x in sk], skjerm_maks=[x[1] for x in sk],
                   fordeling=[x['_fordeling'].tolist() for x in R],
                   **{k: r[k] for k in ('W350', 'jamnheit', 'nytte', 'likskap', 'strekk', 's_auge', 's_vegg', 's_felt', 'ansikt') if k != 'ansikt'})
        with open(fil, 'a', encoding='utf-8') as fh: fh.write(json.dumps(rad) + '\n')
        print('%-18s topp %.2f sprang %.2f auke %.2f likskap %.2f | W350 %.2f U %.2f strekk %.3f | auge %s | felt %s | vegg %s | skjerm maks %s  (%.0f s)'
              % (namn, m['topp'], m['sprang'], m['jamn_auke'], r['likskap'], r['W350'], r['jamnheit'], r['strekk'],
                 [round(x) for x in m['auge']], [round(x) for x in m['felt']], [round(x) for x in m['vegg']], [round(x[1]) for x in sk], time.time() - t0), flush=True)

def overgangstabell():
    """Legg overgangstala frå journalane til i tal.md og skriv overgang.csv (same tal som journalane)."""
    J = {}
    for gen in (1, 2, 3):
        f = os.path.join(HER, 'journal-gen%d.jsonl' % gen)
        for l in open(f, encoding='utf-8'):
            r = json.loads(l); r['gen'] = gen; J[r['namn']] = r
            if 'skjerm_maks' not in r:                          # generasjon 1 lagra ikkje skjermlux i journalen
                g = _ALLE.get(r['namn'])
                r['skjerm_maks'] = [skjermlux(*g(float(t)))[1] for t in r['t']] if g and r['namn'] in dict(GREP) else []
    kol = ['namn', 'gen', 'topp', 'sprang', 'jamn_auke', 'likskap', 'W350', 'jamnheit']
    with open(os.path.join(HER, 'overgang.csv'), 'w', encoding='utf-8', newline='') as fh:
        import csv
        w = csv.writer(fh); w.writerow(kol + ['auge_steg', 'felt_steg', 'vegg_steg', 'skjerm_maks_steg'])
        for r in J.values():
            w.writerow([r[k] if k in ('namn', 'gen') else '%.4g' % r[k] for k in kol]
                       + [' '.join('%.0f' % x for x in r[k]) for k in ('auge', 'felt', 'vegg', 'skjerm_maks')])
    L = ['', '## Overgangen, sju steg (overgang(g, n=7)) for lysgrepa på brettet', '',
         '| Lysgrep | Gen. | Topp | Sprang | Jamn auke | Likskap | Mot auget, steg 0 til 6 (cd/m²) | Felt, lx | Vegg, lx | Skjermflata maks, lx |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for namn, _ in GREP:
        r = J[namn]
        L.append('| %s | %d | %.2f | %.2f | %.2f | %.2f | %s | %s | %s | %s |' % (namn, r['gen'], r['topp'], r['sprang'], r['jamn_auke'], r['likskap'],
                 ', '.join('%.0f' % x for x in r['auge']), ', '.join('%.0f' % x for x in r['felt']),
                 ', '.join('%.0f' % x for x in r['vegg']), ', '.join('%.0f' % x for x in r['skjerm_maks'])))
    L += ['', 'Topp: lysaste mellomsteg mot auget delt på lysaste endepunkt. Sprang: største endring i lysfordelinga mellom to nabosteg. '
          'Likskap: cosinus mellom lysfordelinga i stemning og arbeid. Skjermflata maks er rekna med skjermlux() i familie.py. '
          'Alle overgangstala for generasjon 1 til 3 ligg i overgang.csv og journal-gen*.jsonl. Modell, ikkje måling.', '']
    open(os.path.join(HER, 'tal.md'), 'a', encoding='utf-8').write(chr(10).join(L))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    a = sys.argv[1:]
    if a and a[0] == 'sok':
        gen = int(a[1]) if len(a) > 1 else max(GEN)
        sok(GEN[gen], os.path.join(HER, 'journal-gen%d.jsonl' % gen))
    elif a and a[0] == 'par':
        for namn in BESTE:
            par(_ALLE[namn], os.path.join(HER, 'par-%s.png' % namn), px=240, ss=1, steg=(0, 0.5, 1))
            print('par-%s.png' % namn, flush=True)
    else:
        familie(GREP, HER, px=0 if (a and a[0] == 'tal') else 200)
        overgangstabell()
        print(open(os.path.join(HER, 'tal.md'), encoding='utf-8').read())
