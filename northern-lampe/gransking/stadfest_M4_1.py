# -*- coding: utf-8 -*-
"""stadfest_M4_1.py · motprøve av funn M4: kor mykje endrar lyset for (c) seg om LED-lina går på boge om tyngdepunktet?
Plata (rillene, optikk()) er fast: ho er rekna for (ys, zs). Berre kjelda og hovudpunkta flyttar seg.
Køyr: PYTHONIOENCODING=utf-8 python stadfest_M4_1.py   (om lag 10 s)
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, os.path.join(ROOT, 'form04'))
sys.path.insert(0, ROOT)
import felles as fe
import motor as M

B = dict(M.FINAL)
r = M.akse_under_led(B)
m_pl, m_st = M.hovud_masse(B)
print(f'akse under LED-lina {r * 1e3:.1f} mm (m_plate {m_pl:.3f}, m_stong {m_st:.3f})')
for al in (-105, -90):
    print(f'pendel om LED-lina ved {al}°: {m_pl * fe.G * (B["d"] + B["tp"] / 2) * abs(math.sin(math.radians(al))):.3f} N·m mot T_FRIK {M.T_FRIK}')

_I0, _L0, _H0 = M.I_mot, M.L_mot, M.hovudpunkt
MODE = {'ref': None}


def ned(a):
    return np.array([-math.sin(a), -math.cos(a)])


def senter(B, a):
    """LED-lina i (y, z). ref None: vipp om LED-lina (motoren). ref α0: akse i tyngdepunktet, LED-lina i (ys, zs) ved α0."""
    c0 = np.array([B['ys'], B['zs']])
    if MODE['ref'] is None:
        return c0
    akse = c0 + r * ned(MODE['ref'])
    return akse - r * ned(a)


def I_mot(B, a, Q):
    O = M.optikk(B)                      # plata er rekna for (ys, zs) og vert ikkje endra
    c = senter(B, a)
    S = M._src(dict(B, ys=c[0], zs=c[1]))
    d = Q[None] - S[:, None]
    rr = np.linalg.norm(d, axis=-1)
    xi = np.arcsin(np.clip(d[..., 0] / rr, -1, 1))
    th = np.arctan2(-d[..., 1], -d[..., 2])
    gam = (th - a + np.pi) % (2 * np.pi) - np.pi
    Gv = np.interp(gam, O['tg'], O['G'])
    return O['eta'] / len(S) * Gv * (2 / np.pi) * np.cos(xi), d, rr, S


def L_mot(B, a, Q):
    c = senter(B, a)
    return _L0(dict(B, ys=c[0], zs=c[1]), a, Q) if MODE['ref'] is None else _Lshift(B, a, Q, c)


def _Lshift(B, a, Q, c):
    I, d, rr, S = I_mot(B, a, Q)
    m = np.array([0.0, -math.sin(a), -math.cos(a)])
    C = np.array([0, c[0], c[1]])
    cc = ((Q - C) @ m) / np.linalg.norm(Q - C, axis=-1)
    A = B['L'] * B['bp']
    ok = ~fe.screen_block(S, Q)
    Lb = (I * ok).sum(0) / (A * np.clip(cc, 0.05, None))
    stro = M.STRO * M.optikk(B)['eta'] / (math.pi * A)
    return np.where(cc > 0, Lb + stro, 0.0)


def hovudpunkt(B, a):
    c = senter(B, a)
    return _H0(dict(B, ys=c[0], zs=c[1]), a)


M.I_mot, M.L_mot, M.hovudpunkt = I_mot, L_mot, hovudpunkt


def samandrag(S):
    W, Mo, Fa = S['work'], S['mood'], S['face']
    return dict(a_arb=math.degrees(W['s']), Phi=float(W['Phi']), U0=float(W['U0']), Lap=float(W['Lap']),
                a_stem=math.degrees(Mo['s']), R_stem=float(Mo['R_stem']), Ev_stem=float(Mo['Ev_stem']), L_stem=float(Mo['L_stem']),
                a_ansikt=math.degrees(Fa['s']), Phi150=float(S['Phi150']), L150=float(S['L150']), sveip=S['sveip'], ok=S['ok'])


ut = {}
S0 = M.sok(B); ut['LED-akse (motor)'] = samandrag(S0)
a_w, a_m = S0['work']['s'], S0['mood']['s']
for lab, ref in (('TP-akse, LED fast i arbeid', a_w), ('TP-akse, LED fast i stemning', a_m), ('TP-akse, LED fast midt', (a_w + a_m) / 2)):
    MODE['ref'] = ref
    ut[lab] = samandrag(M.sok(B))
    # same vinklar som motoren, utan nytt val: rein verknad av flyttinga
    rows = {round(math.degrees(rw['s'])): rw for rw in M.sok(B)['rows']}
    w, mo = rows[round(math.degrees(a_w))], rows[round(math.degrees(a_m))]
    Phi_w = fe.E_TASK / max(w['Em'], 1e-12)
    ut[lab]['same_vinklar'] = dict(Phi=float(Phi_w), U0=float(w['U0']), Lap=float(max(w['Le'], w['Lr']) * Phi_w), kolli_arb=bool(M.kollisjon(B, a_w, True)),
                                   R_stem=float(mo['R_stem']), Ev_stem_motorPhi=float(mo['Ew'] * S0['work']['Phi'] * fe.DIM_STEM), kolli_stem=bool(mo['kolli']),
                                   flytt_stem_mm=float(np.linalg.norm(senter(B, a_m) - np.array([B['ys'], B['zs']])) * 1e3),
                                   flytt_arb_mm=float(np.linalg.norm(senter(B, a_w) - np.array([B['ys'], B['zs']])) * 1e3))
MODE['ref'] = None
for k, v in ut.items():
    print(k)
    print('  ', {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v.items() if kk != 'same_vinklar'})
    if 'same_vinklar' in v:
        print('   same vinklar:', {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in v['same_vinklar'].items()})
