# -*- coding: utf-8 -*-
"""stadfest_M2_1.py · motprøve av M2: kolliderer hovudet i (c) med armen på veg til stemning?
Brukar motor.geometri() sjølv (same mesh som konsept.png), ikkje mekanikk_kontroll.py.
1) stemningsvinkelen sok() vel, 2) hovudmesh mot armboksen over vippebana (om LED-lina, som teikna),
3) same med akse i tyngdepunktet, 4) sok() med armsjekk lagd til: kva stemning er mogleg innan fri bane.
"""
import os, sys, math
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'form04'))
import felles as fe
import motor as m4

B = dict(m4.FINAL)
ys, zs = B['ys'], B['zs']
za = zs + 0.03
COLF, COLW, COLY = m4.COL_F, m4.COL_W, m4.COL_Y
# armen slik geometri() teiknar han: flensar x ±0,05 (2 mm), y ys−0,012 .. COL_Y+COL_F, z za .. za+COL_F; steg øvst
ARM = [(-COLW / 2 - 0.001, -COLW / 2 + 0.001), (COLW / 2 - 0.001, COLW / 2 + 0.001)]
y_a0, y_a1 = ys - 0.012, COLY + COLF

S = m4.sok(B)
print(f"sok(): arbeid α {math.degrees(S['work']['s']):+.0f}°, stemning α {math.degrees(S['mood']['s']):+.0f}°, Ev_stem {S['mood']['Ev_stem']:.1f} lx, R {S['mood']['R_stem']:.2f}, sveip {S['sveip']}")

# hovudmesh: plukk ut berre hovudet (alt som roterer). Samanlikn mesh ved α og ved 0: punkt som flyttar seg = hovud.
V0, F0, _ = m4.geometri(B, 0.0)
def hovud_V(a, akse_z=zs):
    V, F, _ = m4.geometri(B, a)
    flytt = np.linalg.norm(V - V0, axis=1) > 1e-9 if a != 0 else None
    # rotasjon om LED-lina er det geometri() gjer; for anna akse: roter hovud-punkta vidare
    return V, flytt

# finn hovudpunkta (dei som flyttar seg ved ein liten vinkel)
Vt, _, _ = m4.geometri(B, math.radians(-1))
HOV = np.linalg.norm(Vt - V0, axis=1) > 1e-9
print(f"mesh: {len(V0)} punkt, {HOV.sum()} på hovudet (roterer)")

def i_arm(P):
    """punkt P (n,3) inne i ein flens eller under/gjennom steget (z ≥ za i y-rekkja til armen og |x| ≤ 0,051)."""
    iy = (P[:, 1] >= y_a0) & (P[:, 1] <= y_a1)
    iz = (P[:, 2] >= za) & (P[:, 2] <= za + COLF)
    return iy & iz

def plate_kryss(P):
    """Plata er kontinuerleg i x (±0,30), så eit (y,z)-punkt på plata inne i armprofilet kryssar flensane ved x ±0,05."""
    return i_arm(P)

def roter_om(P, a, akse):
    """roter (y,z) om (ys, akse) med same konvensjon som geometri(): ned = (−sin a, −cos a)."""
    c, s = math.cos(a), math.sin(a)
    q = P.copy()
    dy, dz = P[:, 1] - ys, P[:, 2] - akse
    q[:, 1] = ys + c * dy + s * dz
    q[:, 2] = akse - s * dy + c * dz
    return q

# kontroll av rotasjonskonvensjonen mot geometri(): rotera hovud ved 0 om LED-lina = geometri(a)
a_t = math.radians(-73)
Va, _, _ = m4.geometri(B, a_t)
err = np.abs(roter_om(V0[HOV], a_t, zs) - Va[HOV]).max()
print(f"kontroll rotasjon mot geometri(): maks avvik {err * 1e3:.4f} mm")

m_plate, m_stong = m4.hovud_masse(B)
z_cg = zs - m4.akse_under_led(B)
print(f"akse i tyngdepunktet (motor): {m4.akse_under_led(B) * 1e3:.1f} mm under LED-lina, z {z_cg:.4f}")

for lab, akse in (('LED-lina (som teikna/rekna)', zs), ('tyngdepunktet (som logg.md seier)', z_cg)):
    first, zmax, pen = None, -1, 0
    for ad in np.arange(0, -105.01, -0.5):
        P = roter_om(V0[HOV], math.radians(ad), akse)
        k = plate_kryss(P)
        inny = P[(P[:, 1] >= y_a0) & (P[:, 1] <= y_a1)]
        if len(inny):
            zmax = max(zmax, inny[:, 2].max())
        if k.any() and first is None:
            first = ad
    P105 = roter_om(V0[HOV], math.radians(-105), akse)
    sel = P105[(P105[:, 1] >= y_a0)]
    top = sel[np.argmax(sel[:, 2])]
    print(f"  {lab}: første kontakt med armen ved α {first}°, høgaste hovudpunkt innanfor armen z {zmax:.4f} = {(zmax - za) * 1e3:.1f} mm over underkanten; "
          f"ved −105°: høgaste punkt y {top[1]:.3f} z {top[2]:.3f} (x {top[0]:+.3f})")

# hengjarane mot renna ved α = 0
Vh = V0[~HOV]
hj = (np.abs(np.abs(Vh[:, 0]) - COLW / 2) < 0.0015) & (Vh[:, 2] < zs + 0.001)
print(f"hengjar-punkt under LED-lina: {hj.sum()}, lågaste z {Vh[hj][:, 2].min() if hj.any() else float('nan'):.3f} (renna: z {zs - 0.005:.3f}–{zs + 0.015:.3f}, y {ys - 0.008:.3f}–{ys + 0.008:.3f})")

# kva stemning er mogleg innan fri bane (om LED-lina, som lyset er rekna)?
def kolli_arm(a, akse=zs):
    P = roter_om(V0[HOV], a, akse)
    return bool(plate_kryss(P).any())

rows = S['rows']
W = S['work']
for lab, akse in (('LED-lina', zs), ('tyngdepunktet', z_cg)):
    # fri bane frå arbeid: dei samanhengande vinklane frå arbeid mot veggen utan armkontakt
    fri = [r for r in rows if r['s'] <= W['s'] + 1e-9]
    fri.sort(key=lambda r: -r['s'])
    ok = []
    for r in fri:
        if kolli_arm(r['s'], akse) or r['kolli']:
            break
        ok.append(r)
    best = max(ok, key=lambda r: (r['R_stem'] >= fe.R_STEM_MIN and r['stem_ok'], r['Ev_stem']))
    print(f"  akse {lab}: fri bane til α {math.degrees(ok[-1]['s']):+.0f}°; beste stemning der α {math.degrees(best['s']):+.0f}°: "
          f"Ev {best['Ev_stem']:.1f} lx, R {best['R_stem']:.2f}, stem_ok {best['stem_ok']} (mot {S['mood']['Ev_stem']:.1f} lx, R {S['mood']['R_stem']:.2f} ved {math.degrees(S['mood']['s']):+.0f}°)")
for ad in (-40, -45, -50, -55, -60, -65, -75, -90, -105):
    r = min(rows, key=lambda r: abs(math.degrees(r['s']) - ad))
    print(f"    α {ad:+d}: Ev_stem {r['Ev_stem']:5.1f} lx, R_stem {r['R_stem']:.2f}, L_stem {r['L_stem']:.0f}, arm LED {kolli_arm(r['s'], zs)}, arm tp {kolli_arm(r['s'], z_cg)}")
