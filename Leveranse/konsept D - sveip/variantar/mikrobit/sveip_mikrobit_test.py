# -*- coding: utf-8 -*-
"""Testar sveip_mikrobit.py mot eit simulert micro:bit V2-kort, utan kort.

Simulatoren gjer det same som MicroPython 2.1.2 der det har noko å seie:
  ticks_ms går rundt ved 2**30, slik som på kortet, og ticks_diff tek omsyn til det.
  write_analog godtek berre heiltal 0–1023, set_pixel berre 0–9.
  Kvar runde tek 2 ms i tillegg til sleep_ms.
Kva berøring og akselerometer gjer, er gjeve som tidslinjer i kvart scenario.

Køyr frå mikrobit/:  python3 sveip_mikrobit_test.py
"""
import math
import sys
from pathlib import Path

PROGRAM = (Path(__file__).resolve().parent / "sveip_mikrobit.py").read_text(encoding="utf-8")
PERIODE = 2 ** 30
RO = (1000, 0, 0)          # tyngda i kortkoordinatar når lampa står (høgrekanten på kortet ned)
FIL = "sveip.txt"


class Ferdig(Exception):
    pass


class Pinne:
    def __init__(self, kort, namn):
        self.kort, self.namn, self.verdi, self.periode = kort, namn, None, None
        self.logg = []

    def write_analog(self, v):
        assert isinstance(v, int) and 0 <= v <= 1023, (self.namn, v)
        self.verdi = v
        self.logg.append((self.kort.t, v))

    def set_analog_period_microseconds(self, p):
        assert p >= 256
        self.periode = p
        self.kort.hendingar.append(("periode", self.namn, self.kort.t))


class Kort:
    """Eitt simulert kort. beroring: liste med (frå, til) i ms. rorsle: funksjon t -> (x, y, z)."""

    def __init__(self, slutt, beroring=(), rorsle=None, filer=None, start=0, runde_ekstra=2):
        self.t = start
        self.start = start
        self.slutt = start + slutt
        self.beroring = [(start + a, start + b) for a, b in beroring]
        self.rorsle = rorsle
        self.filer = dict(filer or {})
        self.skrivingar = 0
        self.runde_ekstra = runde_ekstra
        self.pin0, self.pin1 = Pinne(self, "pin0"), Pinne(self, "pin1")
        self.matrise = [[0] * 5 for _ in range(5)]     # [rad][kolonne] slik kortet ser det
        self.hendingar = []
        self.prov = []                                  # (t, pin0, pin1, lampebilete)

    # --- microbit
    def is_touched(self):
        return any(a <= self.t < b for a, b in self.beroring)

    def get_values(self):
        return self.rorsle(self.t - self.start) if self.rorsle else RO

    def set_pixel(self, x, y, v):
        assert isinstance(v, int) and 0 <= v <= 9 and 0 <= x <= 4 and 0 <= y <= 4
        self.matrise[y][x] = v

    def clear(self):
        self.matrise = [[0] * 5 for _ in range(5)]

    # --- time
    def ticks_ms(self):
        return self.t % PERIODE

    @staticmethod
    def ticks_diff(a, b):
        return ((a - b + PERIODE // 2) % PERIODE) - PERIODE // 2

    def sleep_ms(self, n):
        self.prov.append((self.t - self.start, self.pin0.verdi, self.pin1.verdi, lampebilete(self.matrise)))
        self.t += n + self.runde_ekstra
        if self.t >= self.slutt:
            raise Ferdig

    # --- filsystemet
    def open(self, namn, modus="r"):
        kort = self

        class Fil:
            def __init__(self):
                if modus == "r" and namn not in kort.filer:
                    raise OSError(2)
                self.buf = ""

            def read(self):
                return kort.filer[namn]

            def write(self, s):
                self.buf += s

            def __enter__(self):
                return self

            def __exit__(self, *a):
                if modus == "w":
                    kort.filer[namn] = self.buf
                    kort.skrivingar += 1

        return Fil()

    def kjor(self):
        import types
        mb = types.SimpleNamespace(
            accelerometer=types.SimpleNamespace(get_values=self.get_values),
            display=types.SimpleNamespace(set_pixel=self.set_pixel, clear=self.clear),
            pin0=self.pin0, pin1=self.pin1,
            pin_logo=types.SimpleNamespace(is_touched=self.is_touched))
        tid = types.SimpleNamespace(ticks_ms=self.ticks_ms, ticks_diff=self.ticks_diff, sleep_ms=self.sleep_ms)
        modular = {"microbit": mb, "time": tid, "math": math}
        ekte = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def imp(namn, *a, **k):
            return modular[namn] if namn in modular else ekte(namn, *a, **k)

        innebygd = dict(vars(__builtins__) if hasattr(__builtins__, "__dict__") else __builtins__)
        innebygd.update(__import__=imp, open=self.open)
        try:
            exec(compile(PROGRAM, "sveip_mikrobit.py", "exec"), {"__builtins__": innebygd, "__name__": "__main__"})
        except Ferdig:
            pass
        return self

    def ved(self, t):
        """Siste prøve før eller ved t (ms etter start)."""
        siste = None
        for p in self.prov:
            if p[0] <= t:
                siste = p
        return siste


# Matrisa slik ho syner på lampa, rekna frå CAD-en og ikkje frå programmet:
# LED (kolonne k, rad r) sit på kortet i u = (k-2)*4, v = (2-r)*4 (d15_lysrist.LED).
# mini_passform.til_lampa roterer -90° om z og +90° om x: (u, v, w) -> x = MX + v, z = MZ - u.
def til_lampa(u, v, w=0.0):
    def rot(p, akse, grader):
        c, s = math.cos(math.radians(grader)), math.sin(math.radians(grader))
        x, y, z = p
        if akse == "z":
            return (c * x - s * y, s * x + c * y, z)
        return (x, c * y - s * z, s * y + c * z)
    return rot(rot((u, v, w), "z", -90), "x", 90)


def lampebilete(matrise):
    """[rad ovanfrå][kolonne frå venstre] sett framanfrå lampa (frå -y, x mot høgre, z opp)."""
    bilete = [[None] * 5 for _ in range(5)]
    for r in range(5):
        for k in range(5):
            x, _, z = til_lampa((k - 2) * 4.0, (2 - r) * 4.0)
            kol, rad = round(x / 4) + 2, round(-z / 4) + 2
            bilete[rad][kol] = matrise[r][k]
    return bilete


ARBEID = [(x, y) for y in (2, 3, 4) for x in (0, 1, 2)]
STEMNING = [(x, y) for y in (0, 1) for x in range(5)]
HOL = [(x, y) for y in (2, 3, 4) for x in (3, 4)]


def delar(bilete):
    """Nivået i stamma, i skjermen og det høgaste i hjørnet under skjermen."""
    a = {bilete[y][x] for x, y in ARBEID}
    s = {bilete[y][x] for x, y in STEMNING}
    assert len(a) == 1 and len(s) == 1, ("ujamt", bilete)
    return a.pop(), s.pop(), max(bilete[y][x] for x, y in HOL)


def naer(a, b, tol, tekst):
    assert abs(a - b) <= tol, "%s: %s, venta %s ± %s" % (tekst, a, b, tol)


# ---------------------------------------------------------------- scenario

def test_oppstart():
    k = Kort(1000).kjor()
    assert k.pin0.logg[0] == (0, 0) and k.pin1.logg[0] == (0, 0), "lyset skal vere av først"
    assert ("periode", "pin0", 0) in k.hendingar and k.pin0.periode == 256
    _, p0, p1, b = k.ved(150)
    assert 0 < p0 < 1023 and p1 == 0, "toninga er i gang etter 150 ms"
    _, p0, p1, b = k.ved(400)
    assert (p0, p1) == (1023, 0), "fullt arbeidslys utan lagra blanding"
    assert delar(b) == (9, 0, 0), "stamma lyser, skjermen og hjørnet er mørke"
    assert k.skrivingar == 0


def test_lampebiletet_er_ikonet():
    """Ved halvvegs sveip er heile Γ-forma lyst, og hjørnet under skjermen er mørkt."""
    k = Kort(5500, beroring=[(500, 5500)]).kjor()
    b = k.prov[-1][3]
    for y in range(5):
        for x in range(5):
            assert (b[y][x] > 0) == ((x, y) not in HOL), (x, y, b)


def test_kort_trykk_av_og_paa():
    k = Kort(3000, beroring=[(1000, 1150), (2000, 2120)]).kjor()
    assert k.ved(1100)[1] == 1023, "lyset endrar seg ikkje før fingeren går"
    t_av = next(t for t, p0, p1, _ in k.prov if t > 1150 and p0 == 0 and p1 == 0)
    naer(t_av - 1150, 300, 40, "toninga av")
    assert delar(k.ved(1600)[3]) == (0, 0, 0)
    assert k.ved(2600)[1:3] == (1023, 0), "andre trykket slår på att"
    assert k.skrivingar == 0, "trykk skal ikkje skrive til flash"


def test_hald_sveiper_paa_8_s():
    k = Kort(11000, beroring=[(1000, 10500)]).kjor()
    assert k.ved(1390)[1:3] == (1023, 0), "sveipet byrjar først etter 400 ms"
    t_ferdig = next(t for t, p0, p1, _ in k.prov if p1 == 1023)
    naer(t_ferdig - 1400, 8000, 120, "tida for heile sveipet")
    _, p0, p1, b = k.ved(1400 + 4000)
    naer(p0, 512, 15, "arbeid halvvegs")
    naer(p1, 512, 15, "stemning halvvegs")
    for t, p0, p1, _ in k.prov:
        if t > 400:
            naer(p0 + p1, 1023, 1, "summen ved t = %d" % t)
    assert delar(k.prov[-1][3]) == (0, 9, 0)
    assert k.filer[FIL].split() == ["1.000", "-1"], k.filer[FIL]
    assert k.skrivingar == 1


def test_neste_hald_gaar_andre_vegen():
    k = Kort(9000, beroring=[(1000, 4400), (5000, 7400)]).kjor()
    b1 = k.ved(4500)[2] / 1023
    b2 = k.ved(7500)[2] / 1023
    assert b1 > 0.2, b1
    assert b2 < b1, "andre haldet skal gå attende mot arbeid"
    assert k.filer[FIL].split()[1] == "1", "etter to hald peikar retninga mot stemning att"


def test_hald_naar_lampa_er_av():
    k = Kort(5000, beroring=[(500, 600), (1500, 4000)]).kjor()
    assert k.ved(1400)[1:3] == (0, 0), "av etter trykket"
    assert k.ved(1890)[1:3] == (0, 0), "ingenting før haldet har vart 400 ms"
    _, p0, p1, _ = k.ved(2400)
    assert p0 + p1 > 1000 and p1 > 0, "haldet slår på og sveiper"


def test_flytta_lampe_gaar_attende():
    def lyft(t):
        if t < 2000:
            return RO
        a = math.radians(40)                    # vippa 40° og haldt der
        return (int(1000 * math.cos(a)), int(1000 * math.sin(a)), 0)
    k = Kort(5000, beroring=[(1000, 4000)], rorsle=lyft).kjor()
    assert k.ved(1990)[2] > 0, "sveipet var i gang før lyftet"
    assert k.ved(2600)[1:3] == (1023, 0), "attende til arbeidslys"
    assert k.ved(4900)[1:3] == (1023, 0), "slepp etter lyftet slår ikkje av"
    assert k.skrivingar == 0


def test_flytta_under_trykk_slaar_ikkje_av():
    def lyft(t):
        return (600, 800, 0) if 1050 <= t else RO      # tippa om lag 53° rett etter at fingeren kom
    k = Kort(3000, beroring=[(1000, 1300)], rorsle=lyft).kjor()
    assert k.ved(2900)[1:3] == (1023, 0)


def test_stot_fraa_trykket_tel_ikkje_som_flytting():
    def stot(t):
        return (1000, 900, 0) if 1000 <= t < 1060 else RO   # 0,9 g sidelengs i 60 ms når fingeren trykkjer
    k = Kort(2500, beroring=[(1000, 1200)], rorsle=stot).kjor()
    assert k.ved(2400)[1:3] == (0, 0), "trykket skal slå av sjølv om lampa fekk eit støyt"


def test_startar_med_lagra_blanding():
    k = Kort(1000, filer={FIL: "0.750 -1"}).kjor()
    _, p0, p1, _ = k.ved(900)
    naer(p1 / 1023, (1 - math.cos(math.pi * 0.75)) / 2, 0.002, "stemning ved 0,75")
    naer(p0 + p1, 1023, 1, "summen")


def test_oydelagd_fil_gjev_arbeidslys():
    for innhald in ("", "hei", "0.5", "x 1", "2.5 1"):
        k = Kort(600, filer={FIL: innhald}).kjor()
        venta = (0, 1023) if innhald == "2.5 1" else (1023, 0)
        assert k.ved(500)[1:3] == venta, (innhald, k.ved(500))


def test_ticks_gaar_rundt_under_sveipet():
    k = Kort(10500, beroring=[(1000, 10000)], start=PERIODE - 4000).kjor()
    t_ferdig = next(t for t, p0, p1, _ in k.prov if p1 == 1023)
    naer(t_ferdig - 1400, 8000, 120, "sveipet over omslaget i ticks_ms")


def test_treg_runde():
    """Ein runde på 100 ms (til dømes når flash blir skriven) skal ikkje gjere sveipet raskare."""
    k = Kort(11000, beroring=[(1000, 10500)], runde_ekstra=60).kjor()
    t_ferdig = next(t for t, p0, p1, _ in k.prov if p1 == 1023)
    naer(t_ferdig - 1400, 8000, 200, "sveipet med treg runde")


def test_matrisa_foelgjer_kanalane():
    k = Kort(11000, beroring=[(1000, 10500)]).kjor()
    for t, p0, p1, b in k.prov[30:]:
        a, s, hol = delar(b)
        assert hol == 0
        for p, n in ((p0, a), (p1, s)):
            v = p / 1023 * 255                         # nivå n har lysstyrke 2**(n-1)/255
            if v < 0.625:                              # rundt grensa for det lågaste nivået (0,5)
                assert n == 0 or (n == 1 and v >= 0.375), (t, p0, p1, a, s)
            else:
                feil_pwm = math.log2(1 + 0.125 / v)     # PWM er runda til 1/1023, matrisa er ikkje
                naer(math.log2(v) + 1, n, 0.5 + feil_pwm + 1e-3, "nivå ved t = %d" % t)


TESTAR = [v for k, v in sorted(globals().items()) if k.startswith("test_")]

if __name__ == "__main__":
    feil = 0
    for test in TESTAR:
        try:
            test()
            print("ok   ", test.__name__)
        except AssertionError as e:
            feil += 1
            print("FEIL ", test.__name__, e)
    print("%d av %d testar gjekk" % (len(TESTAR) - feil, len(TESTAR)))
    sys.exit(1 if feil else 0)
