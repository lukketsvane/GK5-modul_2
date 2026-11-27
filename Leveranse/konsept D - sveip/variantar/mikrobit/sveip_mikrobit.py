# Sveip mini · fastvare for micro:bit V2 (MicroPython 2.1.2, python.microbit.org)
#
# Messingpunktet framme er kopla til touch-logoen med ei fjør.
#   Kort trykk  lampa av og på, med ei kort toning.
#   Hald        lyset sveiper mellom arbeid (stamma, ned) og stemning (skjermen, opp) på 8 s.
#               Neste hald går andre vegen. Er lampa av, slår haldet henne på først.
#   Flytting    blir lampa flytta medan fingeren ligg på, går lyset attende til der det var.
#
# Matrisa er lampa sett framanfrå: dei to øvste radene er skjermen, dei tre nedste radene til
# venstre er stamma, og kvar del lyser like sterkt som kanalen sin. Kortet står rotert 90° med
# klokka i lampa, så biletet blir snudd her.
# P0 (arbeid) og P1 (stemning) er PWM på 3,9 kHz til ein LED-drivar, med 10 kΩ til GND på kvar.
# Summen av dei to er alltid den same, som i rev. B: lyset blir flytta, ikkje dempa.
# Blandinga blir lagra på kortet etter kvart sveip, og lampa startar med henne når straumen kjem.
# Kortet kalibrerer berøringa når det startar: ikkje rør messingen når kabelen går i.
from microbit import accelerometer, display, pin0, pin1, pin_logo
from math import cos, pi
from time import sleep_ms, ticks_diff, ticks_ms

SVEIP = 8000       # ms for heile sveipet (F2: under 10 s)
KORT = 400         # ms: kortare berøring er av og på, lengre er sveip
TONING = 300       # ms for å slå av eller på
RUNDE = 20         # ms per runde
ROLEG = 200        # ms: tidskonstanten for tyngdevektoren, så eit trykk på messingen ikkje tel
FLYTTA = 400       # milli-g: så mykje må tyngdevektoren endre seg (om lag 23° eller ei varig rørsle)
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
    with open(FIL, "w") as f:
        f.write("%.3f %d" % (b, r))


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
pin0.set_analog_period_microseconds(256)   # 3,9 kHz, felles for alle PWM-utgangane
display.clear()

blanding, retning = les()
paa = True                                 # straum på er lys på
m = 0.0
t0 = None                                  # når fingeren kom, eller None
handling = None                            # "trykk", "sveip" eller "forkasta"
kopi = (paa, blanding, retning)            # slik lampa var då fingeren kom
ro = [float(v) for v in accelerometer.get_values()]   # tyngdevektoren, jamna ut over ROLEG
g0 = ro[:]                                 # tyngdevektoren då fingeren kom
sist = ticks_ms()

while True:
    no = ticks_ms()
    dt = min(100, ticks_diff(no, sist))
    sist = no
    g = accelerometer.get_values()
    w = min(1.0, dt / ROLEG)
    for i in range(3):
        ro[i] += (g[i] - ro[i]) * w

    if pin_logo.is_touched():
        if t0 is None:                                         # fingeren kom no
            t0, handling = no, "trykk"
            kopi, g0 = (paa, blanding, retning), ro[:]
        elif handling != "forkasta":
            d = (ro[0] - g0[0]) ** 2 + (ro[1] - g0[1]) ** 2 + (ro[2] - g0[2]) ** 2
            if d > FLYTTA * FLYTTA:                            # lampa blir flytta eller lyfta
                paa, blanding, retning = kopi
                handling = "forkasta"
            elif ticks_diff(no, t0) >= KORT:
                if handling == "trykk":
                    paa, handling = True, "sveip"
                blanding = min(1.0, max(0.0, blanding + retning * dt / SVEIP))
    elif t0 is not None:                                       # fingeren gjekk no
        if handling == "trykk":
            paa = not paa
        elif handling == "sveip":
            retning = -1 if blanding >= 1.0 else (1 if blanding <= 0.0 else -retning)
            lagre(blanding, retning)
        t0 = None

    m = min(1.0, m + dt / TONING) if paa else max(0.0, m - dt / TONING)
    lys(m, blanding)
    sleep_ms(RUNDE)
