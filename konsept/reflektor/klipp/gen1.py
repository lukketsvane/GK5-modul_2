# -*- coding: utf-8 -*-
"""Generasjon 1: identiteten til klippet. Same oppstilling («fram»), same skive Ø 25 cm i satin, same watt.
Berre klippet skil kroppane. Overgangen er rein dimming, så likskapen skal bli 1 for alle."""
from familie import *

def g(klipp=None, **kw): return lambda t: lampe(t, klipp=klipp, **kw)

tunge = [dict(u=0.0, v=-0.02, b=0.08, l=0.085, mal=b(-0.25, 0.30, 0))]
lam = [dict(u=0.0, v=v0, b=1.7 * math.sqrt(R0 ** 2 - (v0 + 0.018) ** 2), l=0.036, vinkel=25, akse=0, rund=False) for v0 in (-0.085, -0.04, 0.005, 0.05)]
grad = lambda u, v: 0.35 + 0.75 * (R0 - v) / (2 * R0)

G1 = [
    ('heil',      g(),                                  dict(lag=[None])),
    ('ring',      g(ring(0.055)),                       dict(lag=[ring(0.055)])),
    ('maane',     g(maane(0.09, dv=-0.085)),            dict(lag=[maane(0.09, dv=-0.085)])),
    ('halv',      g(halv(-0.02)),                       dict(lag=[halv(-0.02)])),
    ('blad',      g(blad(0.11)),                        dict(lag=[blad(0.11)])),
    ('stripe',    g(stripe(0.09)),                      dict(lag=[stripe(0.09)])),
    ('sektor',    g(sektor(100, -90)),                  dict(lag=[sektor(100, -90)])),
    ('hol',       g(hol(0.05, 0.014)),                  dict(lag=[hol(0.05, 0.014)])),
    ('hol-grad',  g(hol(0.05, 0.019, grad)),            dict(lag=[hol(0.05, 0.019, grad)])),
    ('slissar',   g(slissar(0.05, 0.4)),                dict(lag=[slissar(0.05, 0.4)])),
    ('bogar',     g(bogar(0.04, 0.45)),                 dict(lag=[bogar(0.04, 0.45)])),
    ('spiral',    g(spiral(2.5, 0.016)),                dict(lag=[spiral(2.5, 0.016)])),
    ('frynser',   g(frynser(12, 0.055)),                dict(lag=[frynser(12, 0.055)])),
    ('tunge',     g(flikar=tunge),                      dict(lag=[None])),
    ('lamellar',  g(flikar=lam),                        dict(lag=[None])),
    ('VELT-auge', g(hol(0.05, 0.014), kp=b(0.47, 0.52, 0.33), c=b(0.40, 0.39, 0.36), mot=b(0.3, YV, 0.6)), dict(lag=[hol(0.05, 0.014)])),
    ('UMOGL-ringar', g(bogar(0.04, 0.45, bruer=0)),     dict(lag=[bogar(0.04, 0.45, bruer=0)])),
]
if __name__ == '__main__':
    GREP = [(n, f) for n, f, _ in G1]; INFO = {n: i for n, _, i in G1}
    kjor(GREP, INFO, os.path.join(HER, 'gen1'), px=0)
