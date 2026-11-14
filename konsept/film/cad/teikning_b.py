# -*- coding: utf-8 -*-
"""
teikning_b.py  ·  målteikning av revisjon B: framanfrå og frå sida, som kvit strek til svart side

Kantane kjem frå same CAD som alt anna (northern.py), med skjulte liner fjerna. Fila ut-b/teikning/maal.svg er eit
SVG-fragment i pikslar som presentasjonen les rett inn.

  python teikning_b.py
"""
import os, math
import northern as N
from teikning import Vising

HER = os.path.dirname(os.path.abspath(__file__))
K = 1.2                                    # pikslar per mm
FRAMME = ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0))            # auget framfor lampa, x mot høgre
SIDE = ((-1.0, 0.0, 0.0), (0.0, -1.0, 0.0))             # auget til venstre for lampa, framsida mot høgre
SYNLEG = ('01', '04', '05', '06', '07', '08', '11')

def f(x): return ('%.1f' % x).rstrip('0').rstrip('.')
def t(x): return ('%g' % round(x)).replace('.', ',')

class Ark:
    def __init__(s): s.ut = []
    def strek(s, pk, klasse):
        d = []; forrige = None
        for p in pk:
            q = (round(p[0], 1), round(p[1], 1))
            if q != forrige: d.append(q); forrige = q
        if len(d) > 1: s.ut.append('<polyline class="%s" points="%s"/>' % (klasse, ' '.join('%s,%s' % (f(a), f(b)) for a, b in d)))
    def line(s, a, b, klasse='m'):
        s.ut.append('<line class="%s" x1="%s" y1="%s" x2="%s" y2="%s"/>' % (klasse, f(a[0]), f(a[1]), f(b[0]), f(b[1])))
    def tekst(s, p, tekst, anker='middle', klasse='mt', roter=None):
        r = ' transform="rotate(%s %s %s)"' % (f(roter), f(p[0]), f(p[1])) if roter else ''
        s.ut.append('<text class="%s" x="%s" y="%s" text-anchor="%s"%s>%s</text>' % (klasse, f(p[0]), f(p[1]), anker, r, tekst))
    def maal(s, a, b, tekst, ut=18.0, side=1):
        """Mållinje mellom a og b (pikslar), flytta ut vinkelrett. Hjelpeliner frå punkta, korte skråstrekar i endane."""
        v = (b[0] - a[0], b[1] - a[1]); l = math.hypot(*v); v = (v[0] / l, v[1] / l); n = (v[1] * side, -v[0] * side)
        a2 = (a[0] + n[0] * ut, a[1] + n[1] * ut); b2 = (b[0] + n[0] * ut, b[1] + n[1] * ut)
        for p, q in ((a, a2), (b, b2)):
            s.line((p[0] + n[0] * 4, p[1] + n[1] * 4), (q[0] + n[0] * 4, q[1] + n[1] * 4), 'h')
        s.line(a2, b2)
        for p in (a2, b2):
            s.line((p[0] - (v[0] + n[0]) * 3, p[1] - (v[1] + n[1]) * 3), (p[0] + (v[0] + n[0]) * 3, p[1] + (v[1] + n[1]) * 3))
        m = ((a2[0] + b2[0]) / 2 + n[0] * 5, (a2[1] + b2[1]) / 2 + n[1] * 5)
        vink = math.degrees(math.atan2(v[1], v[0]))
        if abs(vink) < 1 or abs(abs(vink) - 180) < 1: s.tekst((m[0], m[1] + (-1 if n[1] < 0 else 8)), tekst)
        elif abs(abs(vink) - 90) < 1: s.tekst((m[0] + (3 if n[0] > 0 else -3), m[1] + 3), tekst, 'start' if n[0] > 0 else 'end')
        else: s.tekst(m, tekst, roter=vink if abs(vink) < 90 else vink + 180)
    def peikar(s, p, q, tekst, anker='start'):
        s.line(p, q); s.ut.append('<circle class="p" cx="%s" cy="%s" r="1.6"/>' % (f(p[0]), f(p[1])))
        s.tekst((q[0] + (4 if anker == 'start' else -4), q[1] + 3), tekst, anker)

def main():
    D = {d[0]: d[2] for d in N.delar()}
    former = [D[i] for i in SYNLEG]
    A = Ark()
    bakke = 404.0
    # ---------------- framanfrå
    V = Vising(former, FRAMME)
    x0 = 44.0 - V.min[0] * K
    P = lambda x, z: (x0 + x * K, bakke - z * K)
    for vekt, pk in V.liner:
        A.strek([P(*p) for p in pk], 'k' if vekt >= 1.6 else 's' if vekt >= 1.0 else 't')
    r = N.FOT_D / 2; topp = N.AKSE_H + N.R
    hogre = V.max[0]
    A.line(P(V.min[0] - 14, 0), P(hogre + 14, 0), 'g')
    A.maal(P(N.X0, topp), P(N.X1, topp), t(N.X1 - N.X0), ut=16)
    A.maal(P(-r, 0), P(r, 0), 'Ø ' + t(N.FOT_D), ut=16, side=-1)
    A.maal(P(V.min[0], 0), P(hogre, 0), t(hogre - V.min[0]), ut=38, side=-1)
    A.maal(P(hogre, 0), P(hogre, N.AKSE_H), t(N.AKSE_H), ut=22, side=-1)
    A.line(P(N.X1 + 2, N.AKSE_H), P(hogre + 4, N.AKSE_H), 'h')
    # peikarar: bjelke, røyr, boge, rute, messingpunkt
    xm = 0.5 * (N.XR0 + N.XR1)
    A.peikar(P(N.X0 + 70, topp - 4), P(N.X0 + 86, topp + 40), 'bjelke Ø ' + t(N.BJELKE_D))
    A.peikar(P(N.X0, N.AKSE_H), P(N.X0 - 10, topp + 40), 'messing Ø ' + t(N.DIMMER_D), 'start')
    zr = 95.0; xr = N.ROYR_FOT[0] + (zr - N.FOT_H) * math.tan(math.radians(N.ROYR_HELL))
    A.peikar(P(xr, zr), P(xr + 34, zr - 14), 'røyr Ø %s, hallar %s°' % (t(N.ROYR_D), t(N.ROYR_HELL)))
    A.peikar(P(N.T2[0] + 30, N.AKSE_H - 12), P(N.T2[0] + 40, topp + 40), 'éin boge, R ' + t(N.ROYR_BOGE), 'start')
    A.peikar(P(xm - 40, 200), P(xm - 40, 118), 'rute %s × %s, hjørne R %s' % (t(N.RUTE_B), t(N.RUTE_D), t(N.RUTE_HJORNE)), 'middle')
    A.tekst((P(xm, 0)[0], bakke + 66), 'FRAMANFRÅ', klasse='et')
    # ---------------- frå sida
    W = Vising(former, SIDE)
    x1 = P(hogre, 0)[0] + 205.0 - W.min[0] * K
    Q = lambda y, z: (x1 + y * K, bakke - z * K)                 # y er teikneplanet sin x: framover mot høgre
    for vekt, pk in W.liner:
        A.strek([Q(*p) for p in pk], 'k' if vekt >= 1.6 else 's' if vekt >= 1.0 else 't')
    A.line(Q(W.min[0] - 14, 0), Q(W.max[0] + 40, 0), 'g')
    akse = (-N.YT, N.AKSE_H)
    def paa(v, d): return (akse[0] + d * math.cos(math.radians(v)), akse[1] - d * math.sin(math.radians(v)))
    d0, d1 = N.EKS + N.U_KANT, N.EKS + N.U_KANT + N.RUTE_D
    for v in N.VINKEL_OMRAADE:
        A.line(Q(*paa(v, d0 + 12)), Q(*paa(v, d1)), 'st')
        A.tekst(Q(*paa(v, d1 + 12)), t(v) + '°')
    A.maal(Q(*paa(N.VINKEL, d0)), Q(*paa(N.VINKEL, d1)), t(N.RUTE_D), ut=20, side=1)
    # vinkelbogen frå vassrett til ruta
    rb = 74.0; pk = [Q(*paa(v, rb)) for v in [N.VINKEL * i / 12 for i in range(13)]]
    A.strek(pk, 'm')
    A.tekst(Q(*paa(N.VINKEL / 2, rb + 14)), t(N.VINKEL) + '°')
    A.maal(Q(-r, 0), Q(r, 0), 'Ø ' + t(N.FOT_D), ut=16, side=-1)
    A.maal(Q(W.min[0], 0), Q(W.max[0], 0), t(W.max[0] - W.min[0]), ut=38, side=-1)
    A.maal(Q(W.min[0], 0), Q(W.min[0], topp), t(topp), ut=22, side=1)
    A.tekst((Q(0.5 * (W.min[0] + W.max[0]), 0)[0], bakke + 66), 'FRÅ SIDA', klasse='et')
    breidd = Q(W.max[0] + 44, 0)[0]
    os.makedirs(os.path.join(N.UT, 'teikning'), exist_ok=True)
    svg = '<svg class="maal" width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">\n%s\n</svg>\n' % (
        breidd, bakke + 72, breidd, bakke + 72, '\n'.join(A.ut))
    open(os.path.join(N.UT, 'teikning', 'maal.svg'), 'w', encoding='utf-8').write(svg)
    print('maal.svg %d x %d px · framanfrå %.0f mm brei · frå sida %.0f mm djup, %.0f mm høg' % (breidd, bakke + 72, hogre - V.min[0], W.max[0] - W.min[0], topp))

# ------------------------------------------------------------------ sprengt vising som strek

SPRENGT = {'11': (-55, 0, 0), '08': (0, 0, 275), '07': (0, -235, 0), '10': (0, 0, -30), '09': (0, 0, -55), '06': (0, 0, -90),
           '13': (0, 0, -178), 'E': (0, 0, -125), '04': (190, 0, 0), '12': (190, 0, -34), '01': (190, 0, -55), '03': (190, 0, -140),
           '02': (190, 0, -225)}
AUGE = ((0.452, -0.646, 0.615), (0.819, 0.573, 0.0))      # sett framanfrå til høgre og ovanfrå, utan perspektiv

def sprengt(k=1.02):
    """Delane trekte frå kvarandre langs aksane, med ruta vassrett. Skriv ut-b/teikning/sprengt.svg og ankerpunkta til nummera."""
    import json
    D = {d[0]: d[2] for d in N.delar(0.0)}
    former = [D[i].translate(SPRENGT.get(i, (0, 0, 0))) for i in D]
    V = Vising(former, AUGE)
    A = Ark(); m = 30.0
    P = lambda p: (m + (p[0] - V.min[0]) * k, m + (V.max[1] - p[1]) * k)
    R = lambda q: P(V.punkt(q))
    for vekt, pk in V.liner:
        if vekt < 1.0: continue                                  # ikkje saumane på sylindrar og avrundingar
        A.strek([P(p) for p in pk], 'k' if vekt >= 1.6 else 's')
    # aksane delane er trekte langs
    ym = N.YT - N.EKS; z0 = N.AKSE_H; xm = 0.5 * (N.XR0 + N.XR1)
    akser = [((xm, ym, z0 - N.R - 4), (xm, ym, z0 - 150)),                                        # det som sit under bjelken
             ((N.X0 - 6, ym, z0), (N.X0 - 50, ym, z0)),                                           # messingpunktet
             ((N.X1 + 6, N.YT, z0), (N.X0 + 32 + 190 - 6, N.YT, z0)),                             # røyret ut av bjelken
             ((190, 0, -55 - 6), (190, 0, -225 + 6))]                                             # foten
    for a, b in akser: A.line(R(a), R(b), 'st')
    # ankerpunkt til nummera: eit punkt på kvar del, i teikninga sine pikslar
    def paa(i, q): o = SPRENGT.get(i, (0, 0, 0)); return R((q[0] + o[0], q[1] + o[1], q[2] + o[2]))
    r = N.FOT_D / 2
    anker = {'01': paa('01', (-r * 0.55, -r * 0.55, N.FOT_H)), '02': paa('02', (-r * 0.5, -r * 0.5, 2.0)), '03': paa('03', (N.BALLAST_X - 40, -30, N.FOT_H - N.TOPP_T)),
             '04': paa('04', (N.X0 + 60, N.YT, z0 + 6)), '05': paa('05', (N.X0 + 70, ym, z0 + N.R)), '06': paa('06', (N.X0 + 6, ym - 8, z0 - 12)),
             '07': paa('07', (N.XR0 + 6, ym - 100, z0)), '08': paa('08', (N.XR0 + 6, ym - 100, z0)), '09': paa('09', (N.XR0 + 2, ym + 0.2, z0)),
             '10': paa('10', (N.XR0 + 2, ym - 1.8, z0)), '11': paa('11', (N.X0 - 1, ym, z0 + 10)), '12': paa('12', (N.STOPP_X, N.YT, z0 - 8)),
             '13': paa('13', (N.BREMS_X, N.YT, z0 - 12)), 'E': paa('E', (N.SKRUAR_X[0], ym - N.U_SKRUE, z0 - 14))}
    b, h = m * 2 + (V.max[0] - V.min[0]) * k, m * 2 + (V.max[1] - V.min[1]) * k
    svg = '<svg class="strek" width="%d" height="%d" viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">\n%s\n</svg>\n' % (b, h, b, h, '\n'.join(A.ut))
    open(os.path.join(N.UT, 'teikning', 'sprengt.svg'), 'w', encoding='utf-8').write(svg)
    json.dump(dict(breidd=b, hogd=h, anker={i: [round(p[0], 1), round(p[1], 1)] for i, p in anker.items()}),
              open(os.path.join(N.UT, 'teikning', 'sprengt.json'), 'w'), indent=1)
    print('sprengt.svg %d x %d px' % (b, h))

if __name__ == '__main__':
    import sys
    os.makedirs(os.path.join(N.UT, 'teikning'), exist_ok=True)
    if sys.argv[1:2] != ['sprengt']: main()
    if sys.argv[1:2] != ['maal']: sprengt()
