"""Motprov av PR2 (søyla i (c) i synsfeltet over skjermen).

Uavhengig av premiss.py: geometrien er henta direkte frå motorane (form04 motor.geometri(), form02 val.geometri_krok(),
form01 motor.geometri()), ikkje skriven av. Trekantane vert delte til kantar under 1,5 cm, projiserte til (asimut, elevasjon)
frå kvart auga og fylte (skimage polygon) i 0,05°-celler. Skjermen skjuler det som ligg bak plana y 0,45 innanfor rektangelet.
Sone per auga i 3D: retningar der strålen går over skjermkanten (z > 0,42 i y 0,45, x innanfor ±0,275) og el ≤ 15°.
Til samanlikning: sona i premiss.py (|az| ≤ 20,1°, el −2,8° til 15°, same for alle auge).
"""
import os, sys, math, json, time, importlib.util
import numpy as np
from skimage.draw import polygon as fill

ROOT = r'C:\Users\Iver\Documents\northern-lampe'
sys.path.insert(0, ROOT)
import felles as fe

t0 = time.time()
spec = importlib.util.spec_from_file_location('mo4', os.path.join(ROOT, 'form04', 'motor.py'))
mo = importlib.util.module_from_spec(spec); spec.loader.exec_module(mo)
sys.path.insert(0, os.path.join(ROOT, 'form01')); sys.path.insert(0, os.path.join(ROOT, 'form02'))
import val as V2
M1 = V2.M1

H = 0.05
EL0, EL1, AZ0, AZ1 = -10.0, 40.0, -50.0, 50.0
NE, NA = int((EL1 - EL0) / H), int((AZ1 - AZ0) / H)
els = EL0 + (np.arange(NE) + .5) * H
azs = AZ0 + (np.arange(NA) + .5) * H
EL, AZ = np.meshgrid(els, azs, indexing='ij')
S = fe.SCR


def dirs():
    ce, se = np.cos(np.radians(EL)), np.sin(np.radians(EL))
    return ce * np.sin(np.radians(AZ)), ce * np.cos(np.radians(AZ)), se


DX, DY, DZ = dirs()


def skjerm_og_sone(e):
    t = (S['y'] - e[1]) / DY
    X, Z = e[0] + t * DX, e[2] + t * DZ
    innx = (X > S['x0']) & (X < S['x1'])
    skj = innx & (Z > S['z0']) & (Z < S['z1'])
    sone = innx & (Z >= S['z1']) & (EL <= 15.0)
    return skj, sone


def deling(V, F, emax=0.015):
    T = V[np.asarray(F)]
    ut = []
    while len(T):
        e = np.max(np.linalg.norm(T[:, [1, 2, 0]] - T, axis=2), axis=1)
        ok = e <= emax
        ut.append(T[ok])
        T = T[~ok]
        if not len(T):
            break
        a, b, c = T[:, 0], T[:, 1], T[:, 2]
        ab, bc, ca = (a + b) / 2, (b + c) / 2, (c + a) / 2
        T = np.concatenate([np.stack(s, 1) for s in ((a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca))])
    return np.concatenate(ut)


def kart(T, e, skj):
    A = np.zeros((NE, NA), bool)
    v = T - e
    az = np.degrees(np.arctan2(v[..., 0], v[..., 1]))
    el = np.degrees(np.arctan2(v[..., 2], np.hypot(v[..., 0], v[..., 1])))
    bak = T[..., 1].mean(1) > S['y']
    r = (el - EL0) / H - .5
    c = (az - AZ0) / H - .5
    nær = (el.max(1) > -6) & (el.min(1) < 20) & (np.abs(az).min(1) < 45)
    for i in np.where(nær)[0]:
        rr, cc = fill(r[i], c[i], A.shape)
        if len(rr) == 0:                                   # tynn trekant: merk hjørna
            rr = np.clip(np.round(r[i]).astype(int), 0, NE - 1); cc = np.clip(np.round(c[i]).astype(int), 0, NA - 1)
        if bak[i]:
            m = ~skj[rr, cc]; rr, cc = rr[m], cc[m]
        A[rr, cc] = True
    return A


# ---------- geometri frå motorane ----------
geo = {}
# (c) prisme, FINAL, arbeid α = 0 (sok.json aw)
sj = json.load(open(os.path.join(ROOT, 'form04', 'sok.json'), encoding='utf-8'))
rad = [r for r in sj if abs(r['ys'] - mo.FINAL['ys']) < 1e-6 and abs(r['zs'] - mo.FINAL['zs']) < 1e-6]
a_c = math.radians(rad[0]['aw']) if rad else 0.0
Vc, Fc, emc = mo.geometri(mo.FINAL, a_c)
Tc = Vc[np.asarray(Fc)]
ber_c = np.all(np.abs(Tc[..., 0]) <= 0.052, axis=1) | np.all(Tc[..., 2] <= 0.02, axis=1)
Fc = np.asarray(Fc)
geo['c'] = dict(lys=deling(Vc, Fc[~ber_c]), bering=deling(Vc, Fc[ber_c]), info=dict(alfa_arb_deg=math.degrees(a_c)))
# del av beringa i (c): berre søyla (y ≥ 0,51)
geo['c']['soyle'] = deling(Vc, Fc[ber_c & np.all(Tc[..., 1] >= 0.51, axis=1)])

# (b) krok, arbeidsvinkel frå sok_krok
t1 = time.time()
Bb = dict(V2.B_KROK)
Sb = V2.sok_krok(Bb)
psi_b = Sb['work']['s']
Vb, Fb, emb, Ab = V2.geometri_krok(Bb, psi_b)
Fb = np.asarray(Fb)
n_lys = int(np.where(emb)[0].max()) + 1
geo['b'] = dict(lys=deling(Vb, Fb[:n_lys]), bering=deling(Vb, Fb[n_lys:]),
                info=dict(psi_arb_deg=math.degrees(psi_b), arm_D_mm=Ab['D'] * 1000, sok_s=time.time() - t1))
geo['b']['arm'] = deling(Vb, Fb[n_lys:][np.all(Vb[Fb[n_lys:]][..., 1] > Bb['yp'] + 0.02, axis=1)])

# (a) bru: parametrane premiss.py og tal.json gjev (yp 0,18, hp 0,62); a frå FINAL. Arbeidsvinkel: grov, påverkar ikkje silhuetten
Ba = dict(M1.FINAL, yp=0.18, hp=0.62)
Va, Fa, ema = M1.geometri(Ba, 0.0)[:3]
Fa = np.asarray(Fa); Ta = Va[Fa]
lys_a = np.all(np.abs(Ta[..., 0]) <= Ba['L'] / 2 + 0.003, axis=1) & np.all(Ta[..., 2] > Ba['hp'] - 0.03, axis=1)
geo['a'] = dict(lys=deling(Va, Fa[lys_a]), bering=deling(Va, Fa[~lys_a]), info=dict(L=Ba['L'], a=Ba.get('a')))

# ---------- kartlegging ----------
UT = {'metode': 'trekantar frå motorane, delte til ≤ 1,5 cm, fylte i 0,05°-celler; sone i 3D per auga', 'H_deg': H}
az_skj = math.degrees(math.atan(0.275 / 0.75)); el_topp = math.degrees(math.atan(-0.03 / 0.75))
sone_p = (np.abs(AZ) <= az_skj) & (EL <= 15.0) & (EL >= el_topp - 0.5)
for e_lab, e in (('midt', fe.EYES[0]), ('venstre', fe.EYES[1]), ('hogre', fe.EYES[2])):
    skj, sone = skjerm_og_sone(e)
    UT.setdefault('skjerm_deg2', {})[e_lab] = float(skj.sum() * H * H)
    UT.setdefault('sone_deg2', {})[e_lab] = float(sone.sum() * H * H)
    for k in 'abc':
        r = UT.setdefault(k, {}).setdefault(e_lab, {})
        for d in [q for q in geo[k] if q != 'info']:
            A = kart(geo[k][d], e, skj)
            r[d + '_sone3d'] = round(float((A & sone).sum() * H * H), 2)
            r[d + '_sone_premiss'] = round(float((A & sone_p).sum() * H * H), 2)
            if d == 'bering' or d == 'soyle':
                m = A & (np.abs(AZ) <= 40)
                if m.any():
                    over = m & ~skj
                    r[d + '_el_min_synleg'] = round(float(EL[over & (EL > -5)].min()), 2) if (over & (EL > -5)).any() else None
                    r[d + '_el_max'] = round(float(EL[m].max()), 2)
        if k in 'abc':
            r['info'] = geo[k]['info']
# (b) røyret i 2D mot 3D: lågaste elevasjon av røyrsilhuetten innanfor skjermbreidda frå midtauga
e = fe.EYES[0]
for k, B in (('b', Bb),):
    xs = np.linspace(-0.275, 0.275, 111)
    yc, zc, R = B['yp'], B['hp'], B['R']
    ell = []
    for x in xs:
        dh = math.hypot(x, yc - e[1]); dz = zc - e[2]; dist = math.hypot(dh, dz)
        ell.append(math.degrees(math.atan2(dz, dh) - math.asin(R / dist)))
    UT['b_roeyr_el_min_3d'] = dict(x0=round(ell[55], 2), skjermkant=round(ell[0], 2),
                                   az20=round(min(v for x, v in zip(xs, ell) if abs(math.degrees(math.atan2(x, yc - e[1]))) <= az_skj), 2),
                                   el_2d_motor=round(math.degrees(math.atan2(zc - R - e[2], yc - e[1])), 2))
# handrekning for søyla (c): breidd og høgd i vinkel frå midtauga
dy = mo.COL_Y - e[1]
UT['handrekning_soyle'] = dict(breidd_deg=round(2 * math.degrees(math.atan(mo.COL_W / 2 / dy)), 2),
                               el_skjermkant=round(math.degrees(math.atan((S['z1'] - e[2]) / (S['y'] - e[1]))), 2),
                               el_topp=round(math.degrees(math.atan((mo.FINAL['zs'] + 0.06 - e[2]) / dy)), 2),
                               areal_til_15_deg2=round(2 * math.degrees(math.atan(mo.COL_W / 2 / dy)) * (15 - math.degrees(math.atan((S['z1'] - e[2]) / (S['y'] - e[1])))), 1))
UT['tid_s'] = round(time.time() - t0, 1)
print(json.dumps(UT, ensure_ascii=False, indent=1))
