# Sveip mini · fastvare for micro:bit V2 (MicroPython 2.1.2, python.microbit.org)
#
# Messingpunktet framme er kopla til touch-logoen med ei fjør.
#   Kort trykk  lampa av og på, med ei kort toning.
#   Hald        lyset sveiper mellom arbeid (stamma, ned) og stemning (skjermen, opp) på 8 s.
#               Neste hald går andre vegen. Er lampa av, gjer eit hald ingenting.
#   Vipping     blir lampa vippa meir enn om lag 23° medan fingeren ligg på, går lyset attende
#               til der det var. Skuv og lyft blir ikkje oppdaga.
#
# Matrisa er lampa sett framanfrå: dei to øvste radene er skjermen, dei tre nedste radene til
# venstre er stamma, og kvar del lyser like sterkt som kanalen sin. Kortet står rotert 90° med
# klokka i lampa, så biletet blir snudd her.
# P0 (arbeid) og P1 (stemning) er PWM til ein LED-drivar, med 10 kΩ til GND på kvar.
# Summen av dei to er alltid den same, som i rev. B: lyset blir flytta, ikkje dempa.
# Blandinga blir lagra på kortet etter kvart sveip, og lampa startar med henne når straumen kjem.
#
# Berøringa: MicroPython 2.1.2 gjev rå målingar av touch-logoen (kvar 2. ms, mot ein fast terskel
# på 3500 tikk, utan kalibrering). Programmet filtrerer sjølv: ei berøring tel først etter
# KLEM runder på rad, og ho er over først når KLEM_UT ms har gått utan kontakt. Ligg kontakten
# fast (grunnlinja er over terskelen), eller ligg ein finger på når straumen kjem, blir han
# sett bort frå til han er borte.
from microbit import accelerometer, display, pin0, pin1, pin_logo, reset
from math import cos, pi
from time import sleep_ms, ticks_diff, ticks_ms

SVEIP = 8000       # ms for heile sveipet (F2: under 10 s)
KORT = 400         # ms: kortare berøring er av og på, lengre er sveip
TONING = 300       # ms for å slå av eller på, og for å gli attende etter vipping
RUNDE = 20         # ms per runde
KLEM = 3           # runder på rad med kontakt før ei berøring tel (om lag 60 ms)
KLEM_UT = 120      # ms utan kontakt før ei berøring er over
LANG = 15000       # ms: eit hald som varer lenger enn dette blir sett bort frå
ENDE = 0.15        # innanfor dette frå ein ende går neste hald den andre vegen frå enden
ROLEG = 200        # ms: tidskonstanten for tyngdevektoren, så eit trykk på messingen ikkje tel
FLYTTA = 400       # milli-g: så mykje må tyngdevektoren endre seg (om lag 23° vipping)
PWM_US = 256       # PWM-periode i µs (3,9 kHz). Vel saman med drivaren, sjå LES_MEG
FIL = "sveip.txt"
GRENSER = (0.5, 1.41, 2.83, 5.66, 11.3, 22.6, 45.3, 90.5, 181.0)   # mellom matrisenivåa, i 1/255
SKJERM = [(x, y) for y in (0, 1) for x in range(5)]
STAMME = [(x, y) for y in (2, 3, 4) for x in (0, 1, 2)]


def les():
    """Blandinga og retninga frå førre gong, eller arbeidslys om det ikkje finst noko."""
    try:
        with open(FIL) as f:
            b, r = f.read().split()
        return min(1.0, max(0.0, float(b))), (-1 if int(r) < 0 else 1)
    except (OSError, ValueError):
        return 0.0, 1


def lagre(b, r):
    try:
        with open(FIL, "w") as f:
            f.write("%.3f %d" % (b, r))
    except OSError:
        pass                                   # full eller øydelagd flash: lampa verkar likevel


def niva(f):
    """Del av fullt lys til nivå 0–9. Nivåa på matrisa doblar seg for kvart steg (1, 2, 4 … 255)."""
    v = f * 255
    n = 0
    for g in GRENSER:
        if v < g:
            break
        n += 1
    return n


def vis(arbeid, stemning):
    """x mot høgre og y nedover slik lampa står. Hjørnet under skjermen er alltid mørkt."""
    na, ns = niva(arbeid), niva(stemning)
    for x, y in STAMME:
        display.set_pixel(y, 4 - x, na)
    for x, y in SKJERM:
        display.set_pixel(y, 4 - x, ns)


sist_ut = None


def lys(m, b):
    """m er toninga av og på (0–1), b er blandinga (0 arbeid, 1 stemning)."""
    global sist_ut
    k = m * m                            # toninga ser jamnare ut for auget enn ei rett line
    a = k * (1 + cos(pi * b)) / 2        # cos² og sin²: a + s = k gjennom heile sveipet
    s = k - a
    ut = (int(1023 * a + 0.5), int(1023 * s + 0.5))
    if ut != sist_ut:
        pin0.write_analog(ut[0])
        pin1.write_analog(ut[1])
        vis(a, s)
        sist_ut = ut


pin0.write_analog(0)                       # lyset av før noko anna
pin1.write_analog(0)
pin0.set_analog_period_microseconds(PWM_US)
display.clear()

blanding, retning = les()
lagra_b = blanding                         # det som ligg på kortet
paa = True                                 # straum på er lys på
m = 0.0
mal = None                                 # blandinga glir mot denne etter vipping
t0 = None                                  # når den noverande berøringa tok til, eller None
handling = None                            # "trykk", "sveip" eller "ignorer"
sist_ror = 0                               # siste runde med kontakt
rekkje = 0                                 # runder på rad med kontakt
ror_t = 0                                  # når rekkja tok til
kopi = (paa, blanding, retning)            # slik lampa var då berøringa tok til
ro = [float(v) for v in accelerometer.get_values()]   # tyngdevektoren, jamna ut over ROLEG
g0 = ro[:]                                 # tyngdevektoren då berøringa tok til
snap = (kopi, g0)
ignorer = pin_logo.is_touched()            # ein finger som ligg på ved oppstart, blir sett bort frå
sist = ticks_ms()


def avslutt_sveip():
    """Neste hald går andre vegen, men frå ein ende går han vekk frå enden. Blandinga blir lagra."""
    global retning, lagra_b
    retning = -1 if blanding >= 1.0 - ENDE else (1 if blanding <= ENDE else -retning)
    if abs(blanding - lagra_b) > 0.02:     # eit kort trykk som rører blandinga litt, er ikkje verd ei skriving
        lagre(blanding, retning)
        lagra_b = blanding


try:
    while True:
        no = ticks_ms()
        dt = min(100, ticks_diff(no, sist))
        sist = no
        g = accelerometer.get_values()
        w = min(1.0, dt / ROLEG)
        for i in range(3):
            ro[i] += (g[i] - ro[i]) * w

        ror = pin_logo.is_touched()
        if ror:
            if rekkje == 0:
                ror_t = no
                snap = ((paa, blanding, retning), ro[:])
            rekkje += 1
            sist_ror = no
        else:
            rekkje = 0
            ignorer = False

        if t0 is None:
            if rekkje >= KLEM:                                 # ei ny berøring
                t0 = ror_t
                kopi, g0 = snap
                handling = "ignorer" if ignorer else "trykk"
                mal = None
        else:
            lengd = ticks_diff(sist_ror, t0)                   # kor lenge kontakten har vart
            if not ror and ticks_diff(no, sist_ror) > KLEM_UT:     # berøringa er over
                if handling == "trykk":
                    paa = not paa
                elif handling == "sveip":
                    avslutt_sveip()
                t0 = None
                handling = None
            elif handling == "trykk":
                if lengd >= KORT:
                    handling = "sveip" if paa else "ignorer"   # eit hald slår ikkje på ei lampe som er av
            if handling in ("trykk", "sveip"):
                d = (ro[0] - g0[0]) ** 2 + (ro[1] - g0[1]) ** 2 + (ro[2] - g0[2]) ** 2
                if d > FLYTTA * FLYTTA:                        # lampa blir vippa
                    paa, mal, retning = kopi[0], kopi[1], kopi[2]
                    handling = "ignorer"
            if handling == "sveip":
                if lengd > LANG:
                    avslutt_sveip()
                    handling = "ignorer"
                elif ror:
                    blanding = min(1.0, max(0.0, blanding + retning * dt / SVEIP))

        if mal is not None:                                    # gli attende etter vipping
            steg = dt / TONING
            if abs(mal - blanding) <= steg:
                blanding, mal = mal, None
            else:
                blanding += steg if mal > blanding else -steg

        m = min(1.0, m + dt / TONING) if paa else max(0.0, m - dt / TONING)
        lys(m, blanding)
        sleep_ms(RUNDE)
except Exception:
    reset()                                                    # ein feil skal ikkje la lampa stå på for alltid
finally:
    pin0.write_analog(0)                                       # Ctrl-C frå USB: lyset av
    pin1.write_analog(0)
