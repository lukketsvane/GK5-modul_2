# -*- coding: utf-8 -*-
"""Formfamilien FRESNEL: fresnelspegelen frå overheadprojektoren (285 x 285 mm, f = 187,1 mm)
og det han lærer oss om ein stor, flat, retta reflektor. Bygd på konsept/reflektor/_mal.py.

  python familie.py            siste generasjon (SISTE): tal.md, tal.csv, merkte brett (px=200) og par-bilete
  python familie.py --gen 1    søk i generasjon 1 (berre tal, skriv gen1.csv og gen1.md)
  python familie.py --gen 2    søk i generasjon 2
  python familie.py --gen 3    søk i generasjon 3 (same lysgrep som bretta)
  python familie.py --tal      siste generasjon utan bilete

Eit lysgrep er g(t) -> (lys, kropp). t = 0 er stemning, t = 1 er arbeid. Sjå konsept/lysskisse/API.md.

Motoren i denne fila er funksjonen plate(): parametrar inn (kvar plata står, kvar kjelda står,
kvar speglinga skal, brennvidd, spreiing, omriss), geometri ut. Alt som heiter noko med t,
kan vere eit tal eller ein funksjon av t. Det er slik éi rørsle blir ein overgang.
"""
import sys, os, csv, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *
import lysskisse as _ls

F0 = 0.1871                 # brennvidda til kofferplata
N_SOK = 16                  # fliser langs kanten i søk. 16 og 30 gjev same tal innanfor 1 % (prøvd)
N_FIN = 26                  # til brett og endeleg tabell
N = N_SOK

def _v(x, t):
    return x(t) if callable(x) else x

def gli(a, c):
    """Lineær rørsle frå a (stemning) til c (arbeid)."""
    a = np.asarray(a, float); c = np.asarray(c, float)
    return lambda t: a * (1 - t) + c * t

def trinn(a, c, tk=0.5):
    """Byte i eitt steg (vending, hakk)."""
    return lambda t: a if t < tk else c

VEGGMAAL = b(0.0, YV, 0.45)       # veggen bak skjermen, same punkt som i malen

def plate(t, c, a, s, mot, f=F0, spreiing=2.5, storleik=(0.285, 0.285), klipp=None, form=None,
          flate=None, kjelde=(20, 40, 45), snudd=False, bakside=MORK, fot=None, n=None, lmdel=1.0, ekstra=None):
    """Ei kjelde lyser på ein retta reflektor.
    c: senter i plata. a: retning frå plata mot kjelda (einingsvektor). s: avstand plate til kjelde i meter.
    mot: punktet speglinga av midtstrålen skal treffe. f: brennvidd (None gjev vanleg ark, då gjeld form og flate).
    spreiing: sigma i grader (2,5 rein plate, 8 til 14 med diffusorark). storleik, klipp: omriss.
    kjelde: (sigma, kutt, brønn) i grader for strålen frå kjelda. snudd: baksida vender mot kjelda.
    fot: (x, y) for foten. lmdel: del av budsjettet som går til denne kjelda. ekstra(t, W, K) -> fleire strøk."""
    W, K = watt(t)
    c = np.asarray(_v(c, t), float); a = nrm(_v(a, t)); s = float(_v(s, t)); mot = np.asarray(_v(mot, t), float)
    kp = c + s * a
    sk, kutt, bronn = kjelde
    k = straale(kp, c, W * float(_v(lmdel, t)) * LMW_KJELDE, K, spreiing=sk, kutt=kutt, opning=0.02, bronn=bronn)
    til = nrm(mot - c)
    nn = nrm(a + til)
    tvers = np.cross(a, til)
    opp = nrm(tvers) if np.linalg.norm(tvers) > 1e-6 else None      # u ligg i innfallsplanet, v på tvers
    if snudd: nn = -nn
    nf = N if n is None else n
    if f is not None:
        ar = fresnelspegel(k, c, nn, f=f, storleik=storleik, spreiing=_v(spreiing, t), n=nf, klipp=klipp, opp=opp, bakside=bakside)
    else:
        ar = ark(k, c, nn, storleik, form=form, klipp=klipp, n=nf, opp=opp, framside=flate or SATIN, bakside=bakside)
    lys = [k, ar]
    if ekstra is not None: lys += ekstra(t, W, K)
    kropp = []
    if fot is not None:
        kropp = [syl(b(fot[0], fot[1], 0), b(fot[0], fot[1], 0.04), 0.06)]
    return lys, kropp

# ------------------------------------------------------------------ arkitekturar (kvar plate og kjelde bur)

STAV_C = b(0.47, 0.40, 0.45)            # plata på toppen av ei loddrett stong til høgre for skjermen
NED = (0.0, 0.0, -1.0)                  # kjelda sit på stonga rett under plata og lyser opp
LENE_A = (0.0, -0.7071, -0.7071)        # kjelda sit framfor og under plata: det som går forbi, treffer veggen
OVER_C = b(0.0, 0.36, 0.62)             # plata over skjermkanten, midt framfor brukaren
OVER_A = nrm((0.0, 0.40, -0.90))        # kjelda på skjermkanten
AKS_C = b(0.44, 0.38, 0.50)             # plata i enden av ei skrå stong som òg er den optiske aksen
AKS_FOT = b(0.33, 0.30, 0.0)

def paraboloide(f):
    return lambda U, V: (U, V, (U * U + V * V) / (4 * f))

def renne(f):
    """Parabelrenne bøygd av eitt ark: krum langs u, rett langs v. Utfaldbar."""
    return boy(lambda u: (1 / (2 * f)) / (1 + (u / (2 * f)) ** 2) ** 1.5)

def rund(d):
    return lambda u, v: u * u + v * v <= (d / 2) ** 2

def ring(d_hol):
    return lambda u, v: u * u + v * v >= (d_hol / 2) ** 2

SPEGEL = dict(rd=0.03, rs=0.85, sigma=2.5)

# ------------------------------------------------------------------ generasjon 1: kvar kan plata bu?

GEN1 = [
    ('stav-zoom',   'plate på stav, kjelda glir 250 til 120 mm, rein plate',
        lambda t: plate(t, STAV_C, NED, gli(0.25, 0.12), FELT, fot=(0.47, 0.40))),
    ('stav-ark',    'same, med diffusorark (10 grader)',
        lambda t: plate(t, STAV_C, NED, gli(0.25, 0.12), FELT, spreiing=10, fot=(0.47, 0.40))),
    ('stav-vipp',   'kjelda fast 120 mm, plata vippar frå veggen til feltet',
        lambda t: plate(t, STAV_C, NED, 0.12, gli(VEGGMAAL, FELT), fot=(0.47, 0.40))),
    ('stav-spill',  'vid kjelde (30 grader), glir 300 til 120 mm: spillet går i taket',
        lambda t: plate(t, STAV_C, NED, gli(0.30, 0.12), FELT, kjelde=(30, 60, 62), fot=(0.47, 0.40))),
    ('lene',        'kjelda framfor og under, 45 grader: spillet går på veggen',
        lambda t: plate(t, b(0.47, 0.42, 0.42), LENE_A, gli(0.28, 0.12), FELT, kjelde=(30, 60, 62), fot=(0.47, 0.30))),
    ('lene-hol',    'same, med hol på 100 mm i plata',
        lambda t: plate(t, b(0.47, 0.42, 0.42), LENE_A, gli(0.25, 0.12), FELT, klipp=ring(0.10), fot=(0.47, 0.30))),
    ('aksial',      'kjelda på den optiske aksen, stonga er aksen (Perle)',
        lambda t: plate(t, AKS_C, nrm(AKS_FOT - AKS_C), gli(0.25, 0.10), AKS_FOT, fot=(0.33, 0.30))),
    ('over',        'plata over skjermkanten, kjelda på skjermkanten',
        lambda t: plate(t, OVER_C, OVER_A, gli(0.24, 0.11), FELT)),
    ('stav-ansikt', 'plata snur frå veggen til ansiktet, kjelda 250 mm, ark 14 grader',
        lambda t: plate(t, STAV_C, NED, 0.25, gli(VEGGMAAL, AUGE), spreiing=14, fot=(0.47, 0.40))),
    ('vend',        'matt bakside i stemning, fresnel i arbeid',
        lambda t: plate(t, STAV_C, NED, 0.12, FELT, snudd=(t < 0.5), bakside=MATT, fot=(0.47, 0.40))),
    ('mini',        'pressa fresnel diameter 150 mm, f 100 mm, kjelda glir 130 til 65 mm',
        lambda t: plate(t, STAV_C, NED, gli(0.13, 0.065), FELT, f=0.10, storleik=0.15, kjelde=(25, 50, 55), fot=(0.47, 0.40))),
    ('renne',       'parabelrenne bøygd av ark, 285 x 100 mm, satin',
        lambda t: plate(t, STAV_C, NED, gli(0.30, 0.20), FELT, f=None, form=renne(0.26), storleik=(0.285, 0.10), flate=SATIN, kjelde=(14, 28, 40), fot=(0.47, 0.40))),
    ('rund200',     'plata maskert til diameter 200 mm',
        lambda t: plate(t, STAV_C, NED, gli(0.25, 0.12), FELT, klipp=rund(0.20), fot=(0.47, 0.40))),
    ('stripe',      'plata maskert til 285 x 100 mm',
        lambda t: plate(t, STAV_C, NED, gli(0.25, 0.12), FELT, klipp=lambda u, v: np.abs(v) <= 0.05, kjelde=(20, 40, 45), fot=(0.47, 0.40))),
    ('koffert',     'VELTAR: plata flat på bordet, kjelda på stolpen over, som projektoren',
        lambda t: plate(t, b(0.47, 0.30, 0.01), (0, 0, 1.0), gli(0.19, 0.12), b(0.47, 0.30, 1.7))),
    ('skaal',       'KAN IKKJE LAGAST ved bøying: ekte paraboloide, same brennvidd',
        lambda t: plate(t, STAV_C, NED, gli(0.25, 0.12), FELT, f=None, form=paraboloide(F0), storleik=0.285, flate=SPEGEL, fot=(0.47, 0.40))),
]

# ------------------------------------------------------------------ generasjon 2: nytt grep, fordi jamnheita stivna på 0,02
#
# Generasjon 1 viste at plata avbildar kjelda si eiga lysfordeling på feltet. Ei kjelde som ligg nær plata, lyser berre
# på midten av ho, og feltet får ein flekk. Grepa her er difor ulike måtar å fylle plata jamt på: vid kjelde, kjelde
# langt unna slik at strålane kryssar (kjelda i foten), plata som glir i høgda, ark oppå, og omriss som rettar opp skeivskapen.

KRYSS_C = b(0.47, 0.40, 0.55)           # plata 55 cm over bordet, kjelda i foten 50 cm under
SMAL = (12, 24, 40)                     # kjelde med linse, om lag pluss minus 14 grader
VID = (40, 62, 64)                      # naken diode i grunn brønn
STONG = lambda h: [syl(b(0.47, 0.46, 0), b(0.47, 0.46, h), 0.004)]

def med_stong(res, h):
    lys, kropp = res
    return lys, kropp + STONG(h)

def hogd(t, spreiing):
    """Plata glir på stonga frå 17 til 55 cm. Kjelda står i foten, og vinkelen på plata er fast."""
    h = 0.17 + 0.38 * t
    c = b(0.47, 0.40, h)
    mot = c + (FELT - KRYSS_C) * (h / 0.55)
    return med_stong(plate(t, c, NED, h - 0.05, mot, spreiing=spreiing, kjelde=SMAL, fot=(0.47, 0.40)), 0.57)

GEN2 = [
    ('stav-vid',     'vid kjelde på stonga, glir 187 til 140 mm under plata, rein plate',
        lambda t: plate(t, STAV_C, NED, gli(0.187, 0.14), FELT, kjelde=VID, fot=(0.47, 0.40))),
    ('stav-vid-ark', 'same, med diffusorark (10 grader)',
        lambda t: plate(t, STAV_C, NED, gli(0.187, 0.14), FELT, spreiing=10, kjelde=VID, fot=(0.47, 0.40))),
    ('kryss',        'kjelda i foten 500 mm under plata, strålane kryssar, plata vippar frå vegg til felt, rein plate',
        lambda t: med_stong(plate(t, KRYSS_C, NED, 0.50, gli(VEGGMAAL, FELT), kjelde=SMAL, fot=(0.47, 0.40)), 0.57)),
    ('kryss-ark',    'same, med diffusorark (8 grader)',
        lambda t: med_stong(plate(t, KRYSS_C, NED, 0.50, gli(VEGGMAAL, FELT), spreiing=8, kjelde=SMAL, fot=(0.47, 0.40)), 0.57)),
    ('hogd',         'VELTAR: plata glir i høgda 17 til 55 cm, rein plate. Brennpunktet går gjennom bordet',
        lambda t: hogd(t, 2.5)),
    ('hogd-ark',     'plata glir i høgda 17 til 55 cm, diffusorark (10 grader)',
        lambda t: hogd(t, 10)),
    ('over-vid',     'plata over skjermkanten, vid kjelde glir 187 til 140 mm',
        lambda t: plate(t, OVER_C, OVER_A, gli(0.187, 0.14), FELT, kjelde=VID)),
    ('over-vipp',    'plata over skjermkanten vippar frå veggen bak skjermen til feltet, ark 10 grader',
        lambda t: plate(t, OVER_C, OVER_A, 0.14, gli(b(0.0, YV, 0.60), FELT), spreiing=10, kjelde=VID)),
    ('stripe-tvers', 'plata maskert til 285 x 150 mm (smal på tvers av innfallsplanet), vid kjelde',
        lambda t: plate(t, STAV_C, NED, gli(0.187, 0.14), FELT, klipp=lambda u, v: np.abs(v) <= 0.075, kjelde=VID, fot=(0.47, 0.40))),
    ('lene-hol60',   'kjelda framfor og under (45 grader), hol på 60 mm: midten av strålen går på veggen',
        lambda t: plate(t, b(0.47, 0.42, 0.42), LENE_A, gli(0.187, 0.14), FELT, klipp=ring(0.06), kjelde=VID, fot=(0.47, 0.30))),
    ('vippzoom',     'kopla rørsle: plata vippar frå vegg til felt medan kjelda glir 187 til 140 mm, ark 10 grader',
        lambda t: plate(t, STAV_C, NED, gli(0.187, 0.14), gli(VEGGMAAL, FELT), spreiing=10, kjelde=VID, fot=(0.47, 0.40))),
    ('ansikt-vid',   'plata snur frå veggen til ansiktet, vid kjelde 250 mm under, ark 14 grader',
        lambda t: plate(t, STAV_C, NED, 0.25, gli(VEGGMAAL, AUGE), spreiing=14, kjelde=VID, fot=(0.47, 0.40))),
    ('ansikt-kryss', 'plata snur frå veggen til ansiktet, kjelda i foten, ark 14 grader',
        lambda t: med_stong(plate(t, KRYSS_C, NED, 0.50, gli(VEGGMAAL, AUGE), spreiing=14, kjelde=SMAL, fot=(0.47, 0.40)), 0.57)),
    ('kryss-mini',   'pressa fresnel diameter 200 mm, f 150 mm, kjelda i foten, 8 grader',
        lambda t: med_stong(plate(t, KRYSS_C, NED, 0.50, gli(VEGGMAAL, FELT), f=0.15, storleik=0.20, spreiing=8, kjelde=(8, 16, 40), fot=(0.47, 0.40)), 0.57)),
    ('kryss-renne',  'parabelrenne bøygd av ark, 285 x 160 mm, satin, kjelda i foten',
        lambda t: med_stong(plate(t, KRYSS_C, NED, 0.50, gli(VEGGMAAL, FELT), f=None, form=renne(0.194), storleik=(0.285, 0.16), flate=SATIN, kjelde=SMAL, fot=(0.47, 0.40)), 0.57)),
    ('perleskaal',   'KAN IKKJE LAGAST ved bøying: holspegel diameter 240 mm, f 260 mm (frå frøet Perle), satin',
        lambda t: med_stong(plate(t, KRYSS_C, NED, 0.50, gli(VEGGMAAL, FELT), f=None, form=paraboloide(0.26), storleik=0.24, flate=SATIN, kjelde=(8, 16, 40), fot=(0.47, 0.40)), 0.57)),
]
# ------------------------------------------------------------------ generasjon 3: det som stod att, bygd ut til ulike kroppar
#
# Generasjon 2 og skannet (skann.py) viste tre ting. (1) Kjelda i foten, 50 cm under plata, fyller plata jamt og gjev ein
# kropp med tre former. (2) Jamnheita kjem frå arket oppå plata, ikkje frå plata: 8 grader gjev 0,20, 12 grader 0,42 og
# 14 grader 0,48. (3) Det same arket lyser opp plata mot auget: 28, 312 og 854 cd/m² ved 350 lx. Difor ark på 10 til 12
# grader her. Kroppane under skil seg i kva som rører seg, kvar veggstrøket kjem frå, og kva flata er laga av.

HOG_C = b(0.47, 0.40, 0.60)
FORBI = b(-0.04, 0.25, 0.0)             # speglinga siktar 4 cm forbi feltmidten, bort frå lampa
TETT = (8, 16, 40)                      # kjelde med smal linse: alt lyset treffer plata

def rot(v, akse, vinkel):
    k = nrm(akse); v = np.asarray(v, float)
    return v * math.cos(vinkel) + np.cross(k, v) * math.sin(vinkel) + k * (k @ v) * (1 - math.cos(vinkel))

def knekk(t, c=KRYSS_C, s=0.50, spreiing=12, kjelde=SMAL, flytt=0.03, flik=0.10):
    """Plata er delt langs ein diameter og knekt bakover. Den store delen lyser på feltet og fliken på veggen.
    Heile plata vippar som éin stiv kropp: i stemning lyser den store delen på veggen."""
    W, K = watt(t)
    a = nrm(NED); kp = c + s * a
    nf = nrm(a + nrm(FORBI - c)); nw = nrm(a + nrm(VEGGMAAL - c))
    r = nrm(np.cross(nf, nw)); phi = math.acos(float(np.clip(nf @ nw, -1, 1)))
    n1 = rot(nf, r, phi * (1 - t)); n2 = rot(nw, r, phi * (1 - t))
    e1 = np.cross(n1, r); e2 = np.cross(n2, r)
    sk, kutt, bronn = kjelde
    k = straale(kp, c + flytt * e1, W * LMW_KJELDE, K, spreiing=sk, kutt=kutt, opning=0.02, bronn=bronn)
    a1 = fresnelspegel(k, c, n1, spreiing=spreiing, n=N, opp=e1, klipp=lambda u, v: v >= 0)
    a2 = fresnelspegel(k, c, n2, spreiing=spreiing, n=N, opp=e2, klipp=lambda u, v: (v < 0) & (v > -flik))
    k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)     # motoren skriv over lm_ut når to ark deler kjelde. Retta her.
    return [k, a1, a2], [syl(b(0.47, 0.40, 0), b(0.47, 0.40, 0.04), 0.06)] + STONG(0.57)

def projektor(t):
    """Projektoren slik han står: plata flat på bordet, linse og spegel i hovudet 48 cm over. Linsa avbildar plata på feltet."""
    W, K = watt(t)
    pos = b(0.50, 0.30, 0.49)
    if t >= 0.5:
        mot = FELT; l = straale(pos, mot, W * LMW, K, maske=maske_bord(-0.3, 0.3, 0.05, 0.45), opning=0.035)
    else:
        mot = VEGGMAAL; l = straale(pos, mot, W * LMW, K, maske=maske_vegg(0.0, ZB + 0.45, 0.25), opning=0.035)
    nn = nrm(mot - pos)
    return [l], [skive(b(0.50, 0.30, 0.012), (0, 0, 1), 0.16), syl(b(0.64, 0.44, 0), b(0.64, 0.44, 0.50), 0.012), hovud(pos, nn, 0.05, 0.09)]

def kryss(t, c=KRYSS_C, mot=None, hstong=0.57, **kw):
    s = float(c[2] - ZB - 0.05)
    mot = gli(VEGGMAAL, FELT) if mot is None else mot
    return med_stong(plate(t, c, NED, s, mot, fot=(0.47, 0.40), **kw), hstong)

GEN3 = [
    ('kryss-rein',   'kjelda i foten, plata 55 cm oppe vippar frå vegg til felt, rein plate',
        lambda t: kryss(t, kjelde=SMAL)),
    ('kryss-ark10',  'same, ark 10 grader, smal kjelde: lågast mot auget',
        lambda t: kryss(t, spreiing=10, kjelde=TETT)),
    ('kryss-ark12',  'plata 60 cm oppe, ark 12 grader, siktar litt forbi midten: jamnast',
        lambda t: kryss(t, c=HOG_C, mot=gli(VEGGMAAL, FORBI), hstong=0.62, spreiing=12, kjelde=SMAL)),
    ('kryss-rund',   'plata maskert til skive, diameter 285 mm, ark 12 grader',
        lambda t: kryss(t, mot=gli(VEGGMAAL, FORBI), storleik=0.285, spreiing=12, kjelde=SMAL)),
    ('kryss-knekk',  'plata delt og knekt: stor del mot feltet, flik mot veggen. Vippar som éin kropp',
        lambda t: knekk(t)),
    ('kryss-vend',   'matt bakside gløder i stemning, fresnel med ark 12 grader i arbeid',
        lambda t: kryss(t, mot=FORBI, snudd=(t < 0.5), bakside=MATT, spreiing=12, kjelde=SMAL)),
    ('kryss-mote',   'plata snur frå veggen til ansiktet, 0,3 W i møte, ark 14 grader',
        lambda t: kryss(t, mot=gli(VEGGMAAL, AUGE), spreiing=14, kjelde=SMAL, lmdel=0.06 ** t)),
    ('hogd-ark',     'plata glir i høgda frå 17 til 55 cm, ark 12 grader',
        lambda t: hogd(t, 12)),
    ('stav-zoom',    'vid kjelde glir på stonga 187 til 120 mm under plata, ark 12 grader',
        lambda t: plate(t, STAV_C, NED, gli(0.187, 0.12), FELT, spreiing=12, kjelde=VID, fot=(0.47, 0.40))),
    ('lene-hol',     'kjelda framfor og under, hol på 60 mm: midten av strålen går på veggen, ark 12 grader',
        lambda t: plate(t, b(0.47, 0.42, 0.42), LENE_A, gli(0.187, 0.14), FELT, klipp=ring(0.06), spreiing=12, kjelde=VID, fot=(0.47, 0.30))),
    ('over-vipp',    'plata over skjermkanten vippar frå veggen til feltet, ark 12 grader',
        lambda t: plate(t, OVER_C, OVER_A, 0.12, gli(b(0.0, YV, 0.60), FELT), spreiing=12, kjelde=VID)),
    ('mini',         'produktet: pressa fresnel, diameter 200 mm, f 150 mm, ark 12 grader',
        lambda t: kryss(t, mot=gli(VEGGMAAL, FORBI), f=0.15, storleik=0.20, spreiing=12, kjelde=(6, 12, 40))),
    ('renne',        'produktet: parabelrenne bøygd av ark, 285 x 160 mm, satin',
        lambda t: kryss(t, f=None, form=renne(0.194), storleik=(0.285, 0.16), flate=SATIN, kjelde=SMAL)),
    ('flatt-satin',  'samanlikning: flatt satinert ark i same storleik, utan fresnel',
        lambda t: kryss(t, f=None, storleik=(0.285, 0.285), flate=SATIN, kjelde=SMAL)),
    ('projektor',    'VELTAR: projektoren slik han står, plata flat på bordet, linsa avbildar ho på feltet',
        projektor),
    ('perleskaal',   'KAN IKKJE LAGAST ved bøying: holspegel diameter 240 mm, f 260 mm, satin',
        lambda t: kryss(t, f=None, form=paraboloide(0.26), storleik=0.24, flate=SATIN, kjelde=(8, 16, 40))),
]

# ------------------------------------------------------------------ søk: same tal på alle, fem steg langs overgangen

def sok(gen, namn, steg=(0.0, 0.25, 0.5, 0.75, 1.0)):
    """Går kvart lysgrep i fem steg og skriv ei rad per grep. Lagrar etter kvart grep, så eit avbrot ikkje kostar alt."""
    kol = ['namn', 'felt', 'jamnheit', 'nytte', 'W350', 'vegg', 'ansikt', 'auge', 'auge350', 'auge_ansikt50',
           's_auge', 's_felt', 's_vegg', 'likskap', 'strekk', 'topp', 'sprang', 'jamn_auke',
           'felt_t', 'jamnheit_t', 'auge_t', 'lampe_t', 'vegg_t', 'lm_t', 'skildring']
    fil = os.path.join(HER, namn + '.csv')
    rader = []
    with open(fil, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh); w.writerow(kol)
        for nm, tekst, g in gen:
            R = [tal(*g(float(t))) for t in steg]
            r = _ls._rad(nm, R[0], R[-1])
            L = np.array([max(x['L_lampe'], x['L_flate']) for x in R]); Ef = np.array([x['E_felt'] for x in R])
            spr = [1 - likskap(R[i]['_fordeling'], R[i + 1]['_fordeling']) for i in range(len(R) - 1)]
            r['topp'] = float(L[1:-1].max() / max(L[0], L[-1], 1e-9)); r['sprang'] = float(max(spr))
            r['jamn_auke'] = float((np.diff(Ef) > 0).mean())
            a = R[-1]
            r['auge_ansikt50'] = a['L_lampe'] * 50 / max(a['E_ansikt'], 1e-9)      # lampa mot auget når ansiktet har 50 lx
            r['felt_t'] = ' '.join('%.0f' % x for x in Ef); r['jamnheit_t'] = ' '.join('%.2f' % x['U'] for x in R)
            r['auge_t'] = ' '.join('%.0f' % x for x in L); r['vegg_t'] = ' '.join('%.0f' % x['E_vegg'] for x in R)
            r['lm_t'] = ' '.join('%.0f' % x['lm'] for x in R); r['skildring'] = tekst; r['tak'] = a['lm_tak']
            r['lampe_t'] = ' '.join('%.0f' % x['L_lampe'] for x in R)
            rader.append(r)
            w.writerow([r[k] if isinstance(r[k], str) else '%.4g' % r[k] for k in kol]); fh.flush()
            print('%-12s felt %4.0f lx  U %.2f  W350 %5.2f  vegg %3.0f  ansikt %3.0f  auge %5.0f | stemning: auge %5.0f felt %4.0f vegg %3.0f | lik %.2f  topp %.2f  sprang %.2f  strekk %.2f %%'
                  % (nm, r['felt'], r['jamnheit'], r['W350'], r['vegg'], r['ansikt'], r['auge'], r['s_auge'], r['s_felt'], r['s_vegg'],
                     r['likskap'], r['topp'], r['sprang'], r['strekk'] * 100), flush=True)
            print('             felt(t) %s | U(t) %s | auge(t) %s | lampe(t) %s | vegg(t) %s | ansikt50 %.0f | lm ut %.0f, i taket %.0f' % (r['felt_t'], r['jamnheit_t'], r['auge_t'], r['lampe_t'], r['vegg_t'], r['auge_ansikt50'], a['lm'], a['lm_tak']), flush=True)
    L = ['| Nr. | Lysgrep | Kva | Felt, lx | Jamnheit | W for 350 lx | Vegg, lx | Ansikt, lx | Mot auget | Stemning: mot auget | Stemning: felt | Stemning: vegg | Likskap | Topp | Sprang | Strekk | Felt langs vegen | Jamnheit langs vegen | Mot auget langs vegen | Lampa mot auget langs vegen |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for i, r in enumerate(rader):
        L.append(f"| {i+1} | {r['namn']} | {r['skildring']} | {r['felt']:.0f} | {r['jamnheit']:.2f} | {r['W350']:.2f} | {r['vegg']:.0f} | {r['ansikt']:.0f} | {r['auge']:.0f} | "
                 f"{r['s_auge']:.0f} | {r['s_felt']:.0f} | {r['s_vegg']:.0f} | {r['likskap']:.2f} | {r['topp']:.2f} | {r['sprang']:.2f} | {r['strekk']*100:.2f} % | {r['felt_t']} | {r['jamnheit_t']} | {r['auge_t']} | {r['lampe_t']} |")
    open(os.path.join(HER, namn + '.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    return rader

# ------------------------------------------------------------------ avgjerda etter generasjon 3 (avgjerd.py)
#
# Eitt ope spørsmål avgjorde tredjeplassen: kan veggstrøket i arbeid kome utan å halvere feltet? knekk() over er bunden
# til stonga. knekk2() er same kropp for kva plass som helst. Over skjermkanten slår han kryss-knekk på alle tal
# (avgjerd.md), så i den endelege lista står over-knekk der kryss-knekk stod. flytt må vere 0 over skjermen: med 3 cm
# siktar kjelda 14 grader skeivt, og auget ser den nakne dioden (35 000 til 139 000 cd/m², avgjerd-flytt3.md).

VEGG_OVER = b(0.0, YV, 0.60)

def knekk2(t, c, a, s, vegg, felt, spreiing=12, kjelde=SMAL, flytt=0.03, flik=0.10, fot=None, stong=None):
    """Plata er delt langs ein diameter og knekt. Den store delen lyser på feltet, fliken på veggen. Heile plata vippar.
    c: senter. a: retning frå plata mot kjelda. s: avstand til kjelda. vegg, felt: mål for fliken og den store delen i arbeid."""
    W, K = watt(t)
    c = np.asarray(c, float); a = nrm(a); kp = c + s * a
    nf = nrm(a + nrm(felt - c)); nw = nrm(a + nrm(vegg - c))
    r = nrm(np.cross(nf, nw)); phi = math.acos(float(np.clip(nf @ nw, -1, 1)))
    n1 = rot(nf, r, phi * (1 - t)); n2 = rot(nw, r, phi * (1 - t))
    e1 = np.cross(n1, r); e2 = np.cross(n2, r)
    sk, kutt, bronn = kjelde
    k = straale(kp, c + flytt * e1, W * LMW_KJELDE, K, spreiing=sk, kutt=kutt, opning=0.02, bronn=bronn)
    a1 = fresnelspegel(k, c, n1, spreiing=spreiing, n=N, opp=e1, klipp=lambda u, v: v >= 0)
    a2 = fresnelspegel(k, c, n2, spreiing=spreiing, n=N, opp=e2, klipp=lambda u, v: (v < 0) & (v > -flik))
    k.lm_ut = max(k.lm - a1.lm_inn - a2.lm_inn, 0.0)      # rettar motorfeil 2 (lm_ut blir skriven over av siste ark)
    kropp = []
    if fot is not None: kropp.append(syl(b(fot[0], fot[1], 0), b(fot[0], fot[1], 0.04), 0.06))
    if stong is not None: kropp += STONG(stong)
    return [k, a1, a2], kropp

OVER_KNEKK = ('over-knekk', 'plata over skjermkanten, delt og knekt: stor del mot feltet, flik 100 mm mot veggen over skjermen',
              lambda t: knekk2(t, OVER_C, OVER_A, 0.12, VEGG_OVER, FELT, kjelde=VID, flytt=0.0))

# Den endelege lista: generasjon 3 med over-knekk i staden for kryss-knekk. Same rekkjefølgje elles.
SISTE = [OVER_KNEKK if g[0] == 'kryss-knekk' else g for g in GEN3]

GENERASJONAR = {1: GEN1, 2: GEN2, 3: GEN3}
BESTE = ['over-vipp', 'kryss-rund', 'over-knekk']      # dei tre beste, sjå funn.md

def overgang_tabell(namn, steg=(0.0, 0.25, 0.5, 0.75, 1.0)):
    """Fem steg langs overgangen for dei tre beste, med same fliser som tabellen. Leggjast til i tal.md."""
    G = {nm: g for nm, _, g in SISTE}
    L = ['', '## Overgangen for dei tre beste', '',
         'Fem steg, t = 0, 0,25, 0,5, 0,75 og 1. Watt går 1,25, 1,77, 2,5, 3,54 og 5 W. «Mot auget» er det lysaste auget ser: lampa eller ei romflate.', '',
         '| Lysgrep | Felt, lx | Jamnheit | Vegg, lx | Ansikt, lx | Lampa mot auget, cd/m² | Mot auget, cd/m² | Topp | Sprang |',
         '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for nm in namn:
        R = [tal(*G[nm](float(t))) for t in steg]
        Lm = np.array([max(x['L_lampe'], x['L_flate']) for x in R])
        spr = max(1 - likskap(R[i]['_fordeling'], R[i + 1]['_fordeling']) for i in range(len(R) - 1))
        topp = float(Lm[1:-1].max() / max(Lm[0], Lm[-1], 1e-9))
        j = lambda f, key: ' '.join(f % x[key] for x in R)
        L.append(f"| {nm} | {j('%.0f', 'E_felt')} | {j('%.2f', 'U')} | {j('%.0f', 'E_vegg')} | {j('%.0f', 'E_ansikt')} | {j('%.0f', 'L_lampe')} | "
                 + ' '.join('%.0f' % x for x in Lm) + f" | {topp:.2f} | {spr:.2f} |")
        print(L[-1], flush=True)
    return L

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    arg = sys.argv[1:]
    if '--gen' in arg:
        i = int(arg[arg.index('--gen') + 1])
        sok(GENERASJONAR[i], 'gen%d' % i)
    else:
        N = N_FIN
        GREP = [(nm, g) for nm, _, g in SISTE]
        for r in familie(GREP, HER, px=0 if '--tal' in arg else 200):
            print('%-12s felt %4.0f lx  jamnheit %.2f  W for 350 lx %.2f  vegg %3.0f lx  auge %5.0f  stemning: auge %5.0f, vegg %3.0f lx  likskap %.2f  strekk %.2f %%'
                  % (r['namn'], r['felt'], r['jamnheit'], r['W350'], r['vegg'], r['auge'], r['s_auge'], r['s_vegg'], r['likskap'], r['strekk'] * 100), flush=True)
        L = overgang_tabell(BESTE)
        with open(os.path.join(HER, 'tal.md'), 'a', encoding='utf-8') as fh:
            fh.write('\n'.join(L) + '\n')
        if '--tal' not in arg:
            for nm in BESTE:
                par(dict(GREP)[nm], os.path.join(HER, 'par-%s.png' % nm), px=240, ss=1, steg=(0, 0.5, 1))
