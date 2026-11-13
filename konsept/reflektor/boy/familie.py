# -*- coding: utf-8 -*-
"""Familien BØY: reflektoren som eit ark som berre er bøygd (enkeltkrumt, utfaldbart).

  python familie.py            siste generasjon: tal.md, tal.csv, brett og par i denne mappa
  python familie.py gen1       berre tala for generasjon 1 (i gen1/)
  python familie.py gen2       berre tala for generasjon 2 (i gen2/)
  python familie.py gen3 0     siste generasjon utan bilete

Motoren er lampe(): parametrar inn, lysgrep ut. Bygd på konsept/reflektor/_mal.py.
Eit lysgrep er g(t) -> (lys, kropp). t = 0 er stemning, t = 1 er arbeid.
"""
import sys, os, math
HER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HER, '..', '..', 'lysskisse'))
from lysskisse import *

FOT = (0.47, 0.48)                 # same fot som i malen: til høgre for skjermen
C0 = (0.47, 0.40, 0.41)            # arksenter i malen (x, y, høgd over bordet)
VEGGMAL = b(0.0, YV, 0.45)         # veggen bak skjermen

# ------------------------------------------------------------------ bøyeformer (alle utfaldbare)

def kappa_s(k1, h=0.125):
    """S-form: krumminga går lineært frå -k1 til +k1 over arket. Vendepunkt i midten."""
    return lambda s: k1 * np.clip(s / h, -1.5, 1.5)

def kappa_trau(f):
    """Parabeltrau med brennvidd f: krumminga er størst i botnen og avtek utover."""
    return lambda s: 1.0 / (2 * f) / (1 + (s / (2 * f)) ** 2) ** 1.5

def kappa_rull(k0, L, teikn=1.0):
    """Rull (spiral): krumminga veks eksponentielt mot den eine kanten."""
    return lambda s: teikn * k0 * np.exp(np.clip(s / L, -6, 6))

def kappa_bolgje(A, lam):
    """Bølgjeblekk: krumminga skiftar forteikn med bølgjelengd lam."""
    return lambda s: A * np.cos(2 * PI * s / lam)

def kappa_to(k_a, k_b, u0=0.0, mjuk=0.015, knekk=0.0):
    """To soner med kvar si krumming og ein mjuk bøy (knekk i grader) i skiljet u0.
    Sona u < u0 har krumming k_a, sona u > u0 har k_b."""
    def f(s):
        w = sig((s - u0) / mjuk)
        return k_a * (1 - w) + k_b * w + math.radians(knekk) * np.exp(-0.5 * ((s - u0) / mjuk) ** 2) / (mjuk * math.sqrt(2 * PI))
    return f

def kjegle(alfa, r0, hol=True):
    """Kjegleflate: toppunktet ligg r0 under arksenteret (langs -v), halv toppvinkel alfa i grader.
    Krummingsradius på tvers er r * tan(alfa), altså stramast nær toppunktet. Utfaldbar."""
    sa, ca = math.sin(math.radians(alfa)), math.cos(math.radians(alfa))
    def f(U, V):
        r = np.hypot(U, V + r0); psi = np.arctan2(U, V + r0) / sa
        X = r * sa * np.sin(psi)
        Y = r * (ca * ca + sa * sa * np.cos(psi)) - r0
        Z = r * sa * ca * (1 - np.cos(psi))
        return X, Y, (Z if hol else -Z)
    return f

def skaal(R):
    """Dobbeltkrum skål (paraboloide). IKKJE utfaldbar: kan ikkje lagast ved å bøye."""
    return lambda U, V: (U, V, (U ** 2 + V ** 2) / (2 * R))

# ------------------------------------------------------------------ motoren

def _rot(v, fra, til):
    """Minste rotasjon som tek einingsvektoren fra til til, brukt på v."""
    ax = np.cross(fra, til); sn = np.linalg.norm(ax); cs = float(fra @ til)
    if sn < 1e-9: return v
    ax = ax / sn
    return v * cs + np.cross(ax, v) * sn + ax * (ax @ v) * (1 - cs)

def lampe(t, form=None, rull=0.0, storleik=0.25, c=C0, kp=None, mot=None, ref=None, side=SATIN, bak=MORK,
          spreiing=10, kutt=None, flat=None, n=22, klipp=None, kropp=None, W=None, treff=(0.0, 0.0),
          tone=None, ekstra=None, fot=FOT, stralar=None, gli=0.0):
    """Éi lita LED med linse lyser på eit bøygd ark.
    form: boy(...), kjegle(...) eller None (flatt).
    rull: dreier bøyen i arkplanet. 0: krumminga går på tvers av kastet (styrer breidda), 90: langs kastet (styrer nær og fjern).
    c: arksenter (x, y, høgd over bordet). kp: kjeldeplass (x, y, høgd), standard er foten.
    mot: punktet speglinga frå arksenteret skal gå mot.
    ref: siktepunktet der arkramma er definert (standard feltmidten). Arket er éin stiv kropp: ramma følgjer med
         når arket blir vippa (minste rotasjon), så bøyeaksen hoppar ikkje. Sjå funn.md om ortho() i motoren.
    treff: (du, dv) i arkkoordinatar. Strålen siktar på dette punktet på arket i staden for senteret.
    flat: (på tvers, langs kastet) gjev ein vifteforma stråle, sigma i grader, i same ramme som arket.
    fot: (x, y) for foten. Stamma står 55 mm bak fotsenteret.
    gli: arket er skove gli meter langs u i sitt eige plan. Strålen står i ro og treffer då arkkoordinaten u = gli.
    stralar: [(du, dv, andel), ...] gjev fleire lysdiodar i same fot, kvar med sitt siktepunkt og sin del av watten.
    ekstra: liste med fleire lys."""
    Wt, K = watt(t)
    Wt = Wt if W is None else W
    mot = FELT if mot is None else np.asarray(mot, float)
    ref = FELT if ref is None else np.asarray(ref, float)
    c = b(*c); kp = b(fot[0], fot[1], 0.05) if kp is None else b(*kp)
    n_ref = nrm(nrm(kp - c) + nrm(ref - c))
    ex_ref = nrm(np.cross(nrm(c - kp), n_ref))          # på tvers av innfallsplanet
    nn = nrm(nrm(kp - c) + nrm(mot - c))
    ex = _rot(ex_ref, n_ref, nn); ey = np.cross(nn, ex)
    cr, sr = math.cos(math.radians(rull)), math.sin(math.radians(rull))
    exr = cr * ex + sr * ey; eyr = np.cross(nn, exr)
    if kutt is None: kutt = 2 * (spreiing if flat is None else max(flat))
    ks = []
    for du, dv, andel in (stralar or [(treff[0], treff[1], 1.0)]):
        if andel <= 1e-6: continue
        sikt = c + du * exr + dv * eyr
        ks.append(straale(kp, sikt, Wt * andel * LMW_KJELDE, K, spreiing=spreiing, flat=flat, kutt=kutt, opning=0.02,
                          bronn=40, opp=np.cross(nrm(sikt - kp), ex_ref)))
    a = ark(ks, c - gli * exr, nn, storleik, form=form, klipp=klipp, n=n, opp=np.cross(nn, ex), rull=rull,
            framside=side, bakside=bak, tone=tone)
    if kropp is None:
        kropp = [syl(b(fot[0], fot[1], 0), b(fot[0], fot[1], 0.05), 0.06),
                 syl(b(fot[0], fot[1] + 0.055, 0.05), b(fot[0], fot[1] + 0.055, float(c[2] - ZB)), 0.004)]
    return ks + [a] + list(ekstra or []), kropp

def to_retning(c=C0, fot=FOT, A=None, B=None, kp=None):
    """Bøyeretninga som fører normalen frå adresse A (feltet) til adresse B (veggen).
    Gjev (rull i grader, vinkel i grader). Med rull slik ligg sone B på +u-sida ved kuv bøy (negativ krumming)."""
    A = FELT if A is None else A; B = VEGGMAL if B is None else B
    cc = b(*c); kp = b(fot[0], fot[1], 0.05) if kp is None else b(*kp)
    nA = nrm(nrm(kp - cc) + nrm(A - cc)); nB = nrm(nrm(kp - cc) + nrm(B - cc))
    ex = nrm(np.cross(nrm(cc - kp), nA)); ey = np.cross(nA, ex)
    d = nB - nA
    return math.degrees(math.atan2(d @ ey, d @ ex)), math.degrees(math.acos(np.clip(nA @ nB, -1, 1)))

def skjermlux(lys, kropp):
    """Lux frå lampa midt på skjermflata (sløringslys). Ikkje med i tal()."""
    okkl = [p for p in STATISK if p is not SKJERM] + list(kropp) + [l.prim for l in lys]
    return float(E_direkte(b(0, 0.449, 0.265)[None], np.array([[0.0, -1.0, 0.0]]), lys, okkl)[0] @ LUM)

def auge_i(lys, kropp, h):
    """Lysaste del av arket sett frå eit auge i høgd h over bordet (kravet F1 gjeld 25 til 60 cm)."""
    okkl = [p for p in STATISK + list(kropp) + [l.prim for l in lys] if p not in PERSON]
    return max([l.L_mot(b(0, -0.15, h), okkl) for l in lys if isinstance(l, Ark)] + [0.0])

def vipp(t, fra=None, til=None):
    """Overgang ved å vippe: speglinga flyttar seg frå veggen bak skjermen til arbeidsfeltet."""
    fra = VEGGMAL if fra is None else fra; til = FELT if til is None else til
    return fra * (1 - t) + til * t

def begge(r):
    """Watt for å nå 350 lx på feltet og 100 lx på veggen samstundes (same fordeling, berre skalert)."""
    return r['W'] * max(350 / max(r['felt'], 1e-9), 100 / max(r['vegg'], 1e-9))

def skriv(rader):
    for r in rader:
        print('%-15s felt %4.0f  U %.2f  W350 %5.2f  vegg %3.0f  Wbegge %5.2f  ansikt %3.0f  auge %5.0f  auge350 %5.0f | stemning: auge %5.0f felt %3.0f vegg %3.0f | lik %.2f  strekk %.2f %%'
              % (r['namn'], r['felt'], r['jamnheit'], r['W350'], r['vegg'], begge(r), r['ansikt'], r['auge'], r['auge350'],
                 r['s_auge'], r['s_felt'], r['s_vegg'], r['likskap'], r['strekk'] * 100))

# ------------------------------------------------------------------ generasjon 1: kva gjer bøying med lyset?
# Fast: fot, arkplass, rundt ark Ø 250 mm, SATIN, kjelde i foten med 10° spreiing, overgang ved vipp.
# Variert: berre bøyen (forteikn, styrke, akse, konstant eller varierande krumming).

def g1(**kw):
    return lambda t: lampe(t, mot=vipp(t), **kw)

GEN1 = [
    ('flat',           g1()),
    ('hol-breidd',     g1(form=boy(1 / 0.6))),
    ('hol-kast',       g1(form=boy(1 / 0.6), rull=90)),
    ('hol-kast-stram', g1(form=boy(1 / 0.3), rull=90)),
    ('kuv-breidd',     g1(form=boy(-1 / 0.6))),
    ('kuv-kast',       g1(form=boy(-1 / 0.6), rull=90)),
    ('kuv-kast-stram', g1(form=boy(-1 / 0.25), rull=90)),
    ('s-kast',         g1(form=boy(kappa_s(1 / 0.3)), rull=90)),
    ('s-kast-snudd',   g1(form=boy(kappa_s(-1 / 0.3)), rull=90)),
    ('trau-kast',      g1(form=boy(kappa_trau(0.15)), rull=90)),
    ('rull-kast',      g1(form=boy(kappa_rull(2.0, 0.05, -1)), rull=90)),
    ('bolgje-breidd',  g1(form=boy(kappa_bolgje(20.0, 0.06)))),
    ('kjegle-hol',     g1(form=kjegle(30, 0.30, True))),
    ('kjegle-kuv',     g1(form=kjegle(30, 0.30, False))),
    ('VELT-ansikt',    lambda t: lampe(t, mot=vipp(t, til=AUGE), form=boy(1 / 0.6), rull=90)),
    ('UMOGLEG-skaal',  g1(form=skaal(0.6))),
]

# ------------------------------------------------------------------ generasjon 2: nye grep
# Generasjon 1 stivna: bøyen åleine flytta watt (2,1 til 3,5 W) og jamnheit (0,21 til 0,49) mot kvarandre,
# veggen stod på 30 til 40 lx, og luminansen mot auget stod på 970 cd/m² eller sprakk.
# Nye grep: (1) heile arket framfor skjermplanet og sikte 10 cm forbi feltmidten, (2) to adresser frå éi flate
# (ei sone mot feltet, ein mjuk bøy, ei sone mot veggen), (3) overgang ved at strålen vandrar, ved to diodar
# eller ved at arket blir bøygd, (4) storleik, overflate, høgd og kjeldeplass som identitet.

F2 = (0.47, 0.38)                  # foten flytta 10 cm fram: heile arket ligg framfor skjermplanet
CF = (0.47, 0.30, 0.41)
SIKT = b(-0.10, 0.25, 0)           # sikte 10 cm forbi feltmidten, bort frå lampa

def g2(til=None, **kw):
    kw.setdefault('fot', F2); kw.setdefault('c', CF)
    til = SIKT if til is None else til
    return lambda t: lampe(t, mot=vipp(t, til=til), ref=til, **kw)

def flytta(form, d):
    """Flytt ein bøy d meter langs u, slik at punktet som låg i u = d, no ligg i arksenteret.
    Referanseplanet (der boy() har helling null) følgjer ikkje med. Slik kan bøyen liggje midt på arket
    medan sona ved sida av er den som er sikta inn."""
    def f(U, V):
        X, Y, Z = form(U + d, V)
        return X - d, Y, Z
    return f

def pluss_trau(form, R):
    """Legg ei krumming på tvers oppå ein bøy. Resultatet er dobbeltkrumt og kan ikkje bøyast av eit ark."""
    def f(U, V):
        X, Y, Z = form(U, V)
        return X, Y, Z + V ** 2 / (2 * R)
    return f

def to(t, ov='gli', fot=F2, c=CF, st=(0.38, 0.25), uk=0.04, mjuk=0.02, kA=0.0, kB=0.0, hol=False, A=None, B=None,
       sb=(0.07, -0.04), led=(-0.07, 0.08), deling=0.6, trau=None, kp=None, vinkel=1.0, **kw):
    """To adresser frå éi flate: sone A speglar mot feltet, sone B mot veggen, med ein mjuk bøy imellom.
    Bøyeretninga og vinkelen kjem frå geometrien (to_retning). uk: bøyen sin plass på arket, meter frå arkmidten.
    sb: (stemning, arbeid) kvar strålemidten treffer, i meter frå bøyen (minus er sone A). Overgangen ov:
      'gli':   arket glir langs bøyeretninga, strålen står i ro.
      'vandr': dioden vippar, så strålen vandrar over arket. Arket står i ro.
      'kryss': to diodar i foten siktar på kvar si sone (led, meter frå bøyen), og watten blir flytta mellom dei.
               deling: del av watten til feltdioden i arbeid.
      'vipp':  arket vippar om bøyeaksen, strålen står i sb[1].
      'fast':  ingenting flyttar seg. Lampa er ein dimmar."""
    A = SIKT if A is None else A
    r, th = to_retning(c, fot, A=A, B=B, kp=kp)
    th *= vinkel
    if hol: r += 180
    u0 = max(0.10, 5 * mjuk)       # bøyen ligg u0 ute i boy()-tabellen, så sone A (ikkje bøyen) ligg i referanseplanet
    form = flytta(boy(kappa_to(kA, kB, u0, mjuk, th if hol else -th)), u0 - uk)
    if trau: form = pluss_trau(form, trau)
    kw.update(fot=fot, c=c, storleik=st, form=form, rull=r, ref=A, kp=kp)
    s = uk + sb[0] * (1 - t) + sb[1] * t
    if ov == 'gli':
        return lampe(t, mot=A, gli=s, **kw)
    if ov == 'vandr':
        return lampe(t, mot=A, treff=(s, 0.0), **kw)
    if ov == 'kryss':
        aA = deling * t
        return lampe(t, mot=A, stralar=[(uk + led[0], 0.0, aA), (uk + led[1], 0.0, 1 - aA)], **kw)
    if ov == 'vipp':
        Bm = VEGGMAL if B is None else B
        return lampe(t, mot=vipp(t, fra=Bm, til=A), treff=(uk + sb[1], 0.0), **kw)
    return lampe(t, mot=A, treff=(uk + sb[1], 0.0), **kw)

def flex(t):
    """Overgang ved å bøye: arket er kuv i stemning (R 0,25 m, lyset spreier seg) og hol i arbeid (R 0,6 m). Ingen vipp."""
    k = -4.0 * (1 - t) + (1 / 0.6) * t
    return lampe(t, fot=F2, c=CF, mot=SIKT, ref=SIKT, form=boy(k), rull=0)

def over_skjerm(t, ov='gli'):
    """Lampa står bak skjermen. Stamma går opp forbi skjermkanten, dioden sit i stammetoppen og lyser på eit ark over skjermen."""
    kropp = [syl(b(0, 0.56, 0), b(0, 0.56, 0.05), 0.06), syl(b(0, 0.56, 0.05), b(0, 0.51, 0.45), 0.006),
             syl(b(0, 0.51, 0.45), b(0, 0.50, 0.66), 0.004)]
    return to(t, ov=ov, c=(0.0, 0.36, 0.62), kp=(0.0, 0.50, 0.45), A=FELT, B=b(0, YV, 0.60), spreiing=15, kropp=kropp)

LAG = dict(fot=F2, c=(0.47, 0.30, 0.20), spreiing=18)
STAMME = dict(fot=F2, c=CF, kp=(0.47, 0.40, 0.25), spreiing=17)

GEN2 = [
    ('flat-fram',     g2()),
    ('hol-fram',      g2(form=boy(1 / 0.6))),
    ('kjegle-fram',   g2(form=kjegle(30, 0.30, True))),
    ('stor-hol',      g2(form=boy(1 / 0.6), storleik=0.40, spreiing=16)),
    ('liten-kuv',     g2(form=boy(-1 / 0.3), storleik=0.12, spreiing=5)),
    ('blank-kuv',     g2(form=boy(-1 / 0.6), side=BLANK, n=30)),
    ('matt-hol',      g2(form=boy(1 / 0.6), side=MATT)),
    ('flex',          flex),
    ('laag-hol',      g2(form=boy(1 / 0.5), rull=90, til=b(-0.15, 0.25, 0), **LAG)),
    ('stamme-hol',    g2(form=boy(1 / 0.35), **STAMME)),
    ('to-gli',        lambda t: to(t, 'gli')),
    ('to-kryss',      lambda t: to(t, 'kryss')),
    ('to-vipp',       lambda t: to(t, 'vipp')),
    ('to-hog',        lambda t: to(t, 'gli', c=(0.47, 0.30, 0.55), spreiing=7.2)),
    ('over-skjerm',   over_skjerm),
    ('VELT-to-hol',   lambda t: to(t, 'gli', hol=True)),
    ('UMOGLEG-to-trau', lambda t: to(t, 'gli', trau=0.5)),
]

# ------------------------------------------------------------------ generasjon 3: overflata og to adresser på spegel
# Generasjon 2 viste at overflata flyttar meir enn bøyen: blank kuv gav jamnheit 0,60 og 194 cd/m² mot auget.
# Søk 7 til 10 (økt 2) viste to ting: (1) kuv spegel med R 0,6 m syner kjelda for eit auge 25 cm over bordet (3475 cd/m²),
# men ikkje med R 1,2 m. (2) To-adresse-arket med retta to() når 350 lx på feltet og 100 lx på veggen under 5 W
# når flata er blank (4,62 W), ikkje når ho er satin (5,55 W og 3944 cd/m² for det låge auget).
# Grep i generasjon 3: kor slak og kor stor spegelbøyen kan vere, folie frå byggjesettet som overflate,
# to adresser på spegel med tre overgangar (glid, to diodar, høgd), og satin som referanse.

FOLIE = dict(rd=0.04, rs=0.82, sigma=3.0)      # glatt aluminiumsfolie på papp (ANTAKING, ikkje målt)
KROLL = dict(rd=0.10, rs=0.70, sigma=8.0)      # krølla og glatta folie (ANTAKING, ikkje målt)
HOG = dict(c=(0.47, 0.30, 0.55), spreiing=7.2)

def spegel(R=None, side=BLANK, **kw):
    """Kuv spegel framfor skjermplanet. R: krummingsradius i meter (None er flatt). Overgang ved vipp frå veggen til feltet."""
    return g2(form=None if R is None else boy(-1 / R), side=side, n=30, **kw)

GEN3 = [
    ('spegel-kuv-0.6',  spegel(0.6)),
    ('spegel-kuv-1.2',  spegel(1.2)),
    ('spegel-kuv-2.0',  spegel(2.0)),
    ('spegel-flat',     spegel(None)),
    ('folie-kuv-1.2',   spegel(1.2, side=FOLIE)),
    ('kroll-kuv-0.6',   spegel(0.6, side=KROLL)),
    ('spegel-liten',    spegel(0.9, storleik=0.20, spreiing=8)),
    ('spegel-stor',     spegel(1.2, storleik=0.32, spreiing=13)),
    ('satin-flat',      g2()),
    ('to-spegel',       lambda t: to(t, 'gli', side=BLANK, n=30)),
    ('to-folie',        lambda t: to(t, 'gli', side=FOLIE, n=30)),
    ('to-spegel-kryss', lambda t: to(t, 'kryss', side=BLANK, n=30)),
    ('to-spegel-hog',   lambda t: to(t, 'gli', side=BLANK, n=30, **HOG)),
    ('to-satin-hog',    lambda t: to(t, 'gli', **HOG)),
    ('VELT-spegel-hol', g2(form=boy(1 / 0.3), side=BLANK, n=30)),
    ('UMOGLEG-to-trau', lambda t: to(t, 'gli', side=BLANK, n=30, trau=0.5)),
]

TRE = ['spegel-kuv-1.2', 'to-spegel', 'to-spegel-kryss']     # dei tre beste etter generasjon 3

def ekstra(G, fil):
    """Tal som tal() ikkje gjev: luminans mot auget i 25 og 60 cm (F1 gjeld 25 til 60 cm), lux på skjermflata, og watt for felt og vegg."""
    L = ['| Lysgrep | Arbeid: auge 25 cm | Arbeid: auge 60 cm | Arbeid: skjerm, lx | W for 350 lx og 100 lx på veggen | Stemning: auge 25 cm | Stemning: skjerm, lx |',
         '| --- | --- | --- | --- | --- | --- | --- |']
    for namn, g in G:
        la, ka = g(1.0); ls, ks = g(0.0); d = tal(la, ka)
        L.append('| %s | %.0f | %.0f | %.0f | %.2f | %.0f | %.0f |' % (namn, auge_i(la, ka, 0.25), auge_i(la, ka, 0.60), skjermlux(la, ka),
                 d['W'] * max(350 / d['E_felt'], 100 / max(d['E_vegg'], 1e-9)), auge_i(ls, ks, 0.25), skjermlux(ls, ks)))
        print(L[-1]); sys.stdout.flush()
    open(fil, 'w', encoding='utf-8').write('\n'.join(L) + '\n')

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    arg = sys.argv[1:]
    G3 = dict(GEN3)
    if arg and arg[0] in ('gen1', 'gen2'):
        G = {'gen1': GEN1, 'gen2': GEN2}[arg[0]]
        skriv(familie(G, os.path.join(HER, arg[0]), px=0))
    elif arg and arg[0] == 'ekstra':          # python familie.py ekstra: ekstra.md for generasjon 3
        ekstra(GEN3, os.path.join(HER, 'ekstra.md'))
    elif arg and arg[0] == 'overgang':        # python familie.py overgang: overgangen for dei tre beste i fem steg
        L = ['| Lysgrep | Topp | Sprang | Jamn auke | Mot auget, cd/m² | Felt, lx | Vegg, lx | Skjerm, lx |', '| --- | --- | --- | --- | --- | --- | --- | --- |']
        for namn in TRE:
            g = G3[namn]; _, m = overgang(g, n=5)
            skj = [skjermlux(*g(float(t))) for t in m['t']]
            L.append('| %s | %.2f | %.2f | %.2f | %s | %s | %s | %s |' % (namn, m['topp'], m['sprang'], m['jamn_auke'],
                     ' / '.join('%.0f' % x for x in m['auge']), ' / '.join('%.0f' % x for x in m['felt']),
                     ' / '.join('%.0f' % x for x in m['vegg']), ' / '.join('%.0f' % x for x in skj)))
            print(L[-1]); sys.stdout.flush()
        open(os.path.join(HER, 'overgang.md'), 'w', encoding='utf-8').write('Steg t = 0, 0,25, 0,5, 0,75, 1.\n\n' + '\n'.join(L) + '\n')
    elif arg and arg[0] == 'par':             # python familie.py par: par-bilete for dei tre beste
        for namn in TRE:
            par(G3[namn], os.path.join(HER, 'par-%s.png' % namn), px=240, ss=1, steg=(0, 0.5, 1))
            print('par', namn); sys.stdout.flush()
    else:                                     # python familie.py [gen3] [px]: tal.md, tal.csv og brett for generasjon 3
        px = int(arg[1]) if len(arg) > 1 else 200
        skriv(familie(GEN3, HER, px=px))
