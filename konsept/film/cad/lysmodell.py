# -*- coding: utf-8 -*-
"""
lysmodell.py  ·  lyset frå Ruta i fotometriske einingar: watt inn, lumen ut, candela per kvadratmeter på flatene, lux på bordet

Dette er fasiten studiosida (ruta/index.html) reknar etter i nettlesaren. Same antakingar som lys_sjekk.py:

  stripa         100 lm per watt
  inn i plata    60 % av lyset frå stripa
  ut av plata    60 % ned gjennom undersida, 30 % opp gjennom arket, 10 % ned ved den skrå kanten

Kvar flate er rekna som ein jamn, matt lysande firkant (Lambert). Då har lysstyrken på bordet ei eksakt løysing:
E = L/2 · Σ γ_i · (n · Γ_i), der γ_i er vinkelen kanten i spenner sett frå punktet og Γ_i er normalen til planet gjennom
punktet og kanten. Ingen strålesporing, ingen støy.

Det modellen ikkje tek med: arket samlar lyset (ein verkeleg prismefilm er ikkje matt), bjelken og foten skuggar ikkje, og
ingenting blir reflektert vidare. Tala er ikkje målte.

  python lysmodell.py     skriv ut-b/lysmodell.json og ein tabell
"""
import os, sys, json, math
import numpy as np

HER = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HER, 'ut-b', 'geometri.json'), encoding='utf-8'))
LM_PER_W, INN, NED, OPP, KANT = 100.0, 0.60, 0.60, 0.30, 0.10
UTE = 0.0285                       # så langt frå røyret kjem ruta ut av bjelken (m)
KANT_B = 0.004                     # breidda på stripa som lyser ned ved den frie kanten (m)
AKSE = np.array([0.0, G['YT'] / 1000.0, G['AKSE_H'] / 1000.0])
X0, X1 = G['XR0'] / 1000.0, G['XR1'] / 1000.0
U1 = (G['EKS'] + G['U_KANT'] + G['RUTE_D']) / 1000.0     # den frie kanten, målt frå røyret

def flater(vinkel):
    """Dei tre lysande firkantane ved ei helling: hjørne i rekkjefølgje, normal, areal. Rommet: x langs bjelken, y bakover, z opp."""
    t = math.radians(vinkel)
    u = np.array([0.0, -math.cos(t), -math.sin(t)])           # frå bjelken ut i ruta
    ned = np.array([0.0, math.sin(t), -math.cos(t)])          # ut av undersida
    def firkant(u0, u1, normal, loft):
        p = [AKSE + np.array([x, 0, 0]) + u * uu + normal * loft for x, uu in ((X0, u0), (X1, u0), (X1, u1), (X0, u1))]
        return dict(hjorne=np.array(p), normal=normal, areal=(X1 - X0) * (u1 - u0))
    return dict(ned=firkant(UTE, U1 - KANT_B, ned, 0.0015), kant=firkant(U1 - KANT_B, U1, ned, 0.0015), opp=firkant(UTE, U1, -ned, 0.0017))

def lysstyrkar(watt):
    """Lysfluks (lm) og luminans (cd/m²) for kvar flate, når flatene er matte."""
    F = flater(35.0); inn = watt * LM_PER_W * INN
    ut = dict(ned=inn * NED, opp=inn * OPP, kant=inn * KANT)
    return dict(kjelde_lm=watt * LM_PER_W, ut_lm=sum(ut.values()), fluks=ut, luminans={k: ut[k] / (math.pi * F[k]['areal']) for k in ut})

def lux(punkt, n, hjorne, L):
    """Lysstyrke (lux) i eit punkt med normal n frå ein matt firkant med luminans L. Eksakt. Firkanten må liggje over horisonten til punktet."""
    v = hjorne - punkt; v = v / np.linalg.norm(v, axis=1)[:, None]
    s = 0.0
    for i in range(len(v)):
        a, b = v[i], v[(i + 1) % len(v)]
        k = np.cross(a, b); l = np.linalg.norm(k)
        if l < 1e-12: continue
        s += math.acos(max(-1.0, min(1.0, float(a @ b)))) * float(n @ (k / l))
    return 0.5 * L * abs(s)

def bord(punkt, vinkel, watt):
    """Lux på bordet (z = 0, normal opp) i eit punkt. Undersida og kanten lyser berre ut frå undersida, arket berre ut frå oversida."""
    F = flater(vinkel); Ls = lysstyrkar(watt)['luminans']; n = np.array([0.0, 0.0, 1.0]); E = 0.0
    for k in ('ned', 'kant', 'opp'):
        f = F[k]
        if (punkt - f['hjorne'][0]) @ f['normal'] > 0: E += lux(punkt, n, f['hjorne'], Ls[k])
    return E

def felt(vinkel, watt, n=17):
    """Bordet under og framfor ruta: 40 x 40 cm om midten av ruta, slik lys_sjekk.py målte det."""
    F = flater(vinkel); c = F['opp']['hjorne'].mean(0)
    xs = np.linspace(c[0] - 0.2, c[0] + 0.2, n); ys = np.linspace(c[1] - 0.25, c[1] + 0.15, n)
    E = np.array([[bord(np.array([x, y, 0.0]), vinkel, watt) for x in xs] for y in ys])
    return dict(snitt=float(E.mean()), hogst=float(E.max()), under_midten=bord(np.array([c[0], c[1], 0.0]), vinkel, watt))

if __name__ == '__main__':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    rap = dict(antakingar=dict(lm_per_w=LM_PER_W, inn=INN, ned=NED, opp=OPP, kant=KANT, ute_m=UTE, kant_b_m=KANT_B),
               geometri=dict(akse=AKSE.tolist(), x0=X0, x1=X1, u1=U1), lysstyrkar={}, bord=[], punkt=[])
    for W in (0.5, 1.0, 2.0, 3.0):
        L = lysstyrkar(W); rap['lysstyrkar']['%g' % W] = L
        print('%.1f W: %3.0f lm frå stripa, %3.0f lm ut av ruta · undersida %4.0f cd/m², arket %4.0f cd/m², kanten %5.0f cd/m²' % (
            W, L['kjelde_lm'], L['ut_lm'], L['luminans']['ned'], L['luminans']['opp'], L['luminans']['kant']))
    print()
    for W in (0.5, 2.0):
        for v in (0, 20, 35, 60, 80):
            f = felt(v, W); rap['bord'].append(dict(watt=W, helling=v, **{k: round(x, 2) for k, x in f.items()}))
            print('%.1f W, helling %2d°: bordet under ruta snitt %4.0f lx, høgst %4.0f lx, rett under midten %4.0f lx' % (W, v, f['snitt'], f['hogst'], f['under_midten']))
    # punkt nettlesaren blir prøvd mot
    for (x, y) in ((-0.04, -0.10), (-0.04, -0.30), (0.20, -0.05), (-0.30, 0.10), (0.0, 0.25)):
        for v in (0, 35, 80):
            rap['punkt'].append(dict(x=x, y=y, helling=v, watt=2.0, lux=round(bord(np.array([x, y, 0.0]), v, 2.0), 3)))
    json.dump(rap, open(os.path.join(HER, 'ut-b', 'lysmodell.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print('\nskrive: ut-b/lysmodell.json (%d prøvepunkt)' % len(rap['punkt']))
