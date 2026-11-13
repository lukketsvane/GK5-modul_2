"""Lysstudie av éin kropp: forma stor, lyset på bord og vegg, isolux, lysfordeling (polar) og nøkkeltal.
Bruk: python lysstudie.py gen01 1   ->  genNN/studie_kNN.png
Briefen: «prøv lys mot flater, skjerm og ansikt · undersøk lyset før forma vert låst».
"""
import os, sys, math, importlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates, gaussian_filter
from skimage.measure import find_contours

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import felles as fe

GEN, KID = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ('gen01', 1)
sys.path.insert(0, os.path.join(ROOT, GEN))
mo = importlib.import_module('motor')

RHO_DESK, RHO_WALL, RHO_MON = 0.45, 0.75, 0.08
TINT_DESK, TINT_WALL = np.array([1.0, 0.93, 0.84]), np.array([1.0, 0.99, 0.97])
CCT = {'arbeid': (2700, np.array([1.0, 0.90, 0.80])), 'stemning': (2200, np.array([1.0, 0.84, 0.70]))}  # halv kromatisk tilpassing
L_REF = 78.0                     # cd/m2 -> 0,6 i tonekurva (bord ved 500 lx), så fallet syner
SS = 2                           # supersampling
FONT = r'C:\Windows\Fonts\georgiai.ttf'


def tone(L):
    return (1 - np.exp(-np.maximum(L, 0) / L_REF)) ** (1 / 2.2)


def cam_rays(cam):
    S = cam.S
    ys, xs = np.mgrid[0:S, 0:S] + 0.5
    xc, yc = (xs - S / 2) / cam.k, -(ys - S / 2) / cam.k
    d = xc[..., None] * cam.M[0] + yc[..., None] * cam.M[1] + cam.M[2]      # camera-z = 1
    return d


def raster(cam, V, F, col):
    S = cam.S
    p = cam.proj(V)
    img = np.zeros((S, S, 3)); zb = np.zeros((S, S))
    for i, (a, b, c) in enumerate(F):
        P = p[[a, b, c]]
        if (P[:, 2] <= 0).any():
            continue
        x0, x1 = max(int(P[:, 0].min()), 0), min(int(P[:, 0].max()) + 1, S - 1)
        y0, y1 = max(int(P[:, 1].min()), 0), min(int(P[:, 1].max()) + 1, S - 1)
        if x1 < x0 or y1 < y0:
            continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (xa, ya), (xb, yb), (xc, yc) = P[:, :2]
        den = (yb - yc) * (xa - xc) + (xc - xb) * (ya - yc)
        if abs(den) < 1e-9:
            continue
        l1 = ((yb - yc) * (xs - xc) + (xc - xb) * (ys - yc)) / den
        l2 = ((yc - ya) * (xs - xc) + (xa - xc) * (ys - yc)) / den
        l3 = 1 - l1 - l2
        iz = l1 / P[0, 2] + l2 / P[1, 2] + l3 / P[2, 2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m = (l1 >= 0) & (l2 >= 0) & (l3 >= 0) & (iz > sub)
        sub[m] = iz[m]
        img[y0:y1 + 1, x0:x1 + 1][m] = col[i]
    return img, zb


def box(x0, x1, y0, y1, z0, z1, n=8):
    """Boks med oppdelte sider (for lys per flatebit)."""
    V, F = [], []
    def quad(o, ea, eb):
        base = len(V)
        for i in range(n + 1):
            for j in range(n + 1):
                V.append(o + ea * i / n + eb * j / n)
        for i in range(n):
            for j in range(n):
                a = base + i * (n + 1) + j
                F.extend([(a, a + n + 1, a + n + 2), (a, a + n + 2, a + 1)])
    O = np.array([x0, y0, z0]); X = np.array([x1 - x0, 0, 0]); Y = np.array([0, y1 - y0, 0]); Z = np.array([0, 0, z1 - z0])
    quad(O, X, Z); quad(O + Y, X, Z); quad(O, Y, Z); quad(O + X, Y, Z); quad(O + Z, X, Y)
    return np.array(V), F


def plane_E(P, N, dA, L, pts, qn):
    out = np.zeros(len(pts))
    for i in range(0, len(pts), 4000):
        out[i:i + 4000] = fe.illum(P, N, dA, pts[i:i + 4000], qn) * L
    return out


def study(B, phi, Phi_led, eta, cam, label):
    """Returnerer RGB (S×S) for éin gesttilstand + desk-E-kart for isolux."""
    P, n, dA = mo.aperture(B, phi, ns=24, nt=4)
    N = np.tile(n, (len(P), 1))
    A = dA.sum()
    L = eta * Phi_led / (math.pi * A)                       # cd/m2 i opninga
    # E-kart i verdsrommet
    gx, gy = np.linspace(-0.70, 0.70, 281), np.linspace(0.0, 0.75, 151)
    DX, DY = np.meshgrid(gx, gy)
    Ed = plane_E(P, N, dA, L, np.c_[DX.ravel(), DY.ravel(), np.zeros(DX.size)], np.array([0, 0, 1.0])).reshape(DX.shape)
    wx, wz = np.linspace(-0.70, 0.70, 281), np.linspace(0.0, 1.20, 241)
    WX, WZ = np.meshgrid(wx, wz)
    Ew = plane_E(P, N, dA, L, np.c_[WX.ravel(), np.full(WX.size, fe.WALL_Y - 1e-3), WZ.ravel()], np.array([0, -1.0, 0])).reshape(WX.shape)
    # mesh: lampe (husstil-lambert) + skjerm (lyst av lampa) + lysande opning
    geo = mo.build(B, phi)
    V, F = geo['V'], geo['F']
    T = V[F]
    nn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-15
    nn *= np.sign(((cam.eye - T.mean(1)) * nn).sum(1))[:, None]
    col = np.clip(fe.ALB * (0.40 + 0.55 * np.clip(nn @ fe.KEY, 0, 1)[:, None] + 0.08 * np.clip(nn[:, 2], 0, 1)[:, None]), 0, 1)
    Vm, Fm = box(fe.SCR['x0'], fe.SCR['x1'], fe.SCR['y'], fe.SCR['y'] + 0.02, fe.SCR['z0'], fe.SCR['z1'], 36)
    Vs, Fs = box(-0.03, 0.03, 0.47, 0.50, 0.001, fe.SCR['z0'], 2)
    Vf, Ff = box(-0.11, 0.11, 0.42, 0.60, 0.001, 0.008, 2)
    mon = fe.merge([(Vm, Fm), (Vs, Fs), (Vf, Ff)])
    Tm = mon[0][mon[1]]
    nm = np.cross(Tm[:, 1] - Tm[:, 0], Tm[:, 2] - Tm[:, 0]); nm /= np.linalg.norm(nm, axis=1, keepdims=True) + 1e-15
    cm = Tm.mean(1)
    Emon = np.array([fe.illum(P, N, dA, (c + q * 1e-3)[None], q)[0] * L for c, q in zip(cm, nm)])
    lc = CCT[label][1]
    colm = np.clip(tone(RHO_MON * Emon / math.pi)[:, None] * lc * 0.9 + 0.025, 0, 1)
    colm[len(Fm):] = 0.045                                  # fot og hals: flat mørk
    # opninga som lysande kordeflate
    td = np.cross(B['u'], n)
    quads = []
    for s0, Ls in B['seg']:
        a0, a1 = Ls * (1 - B['k']) / 2, Ls * (1 + B['k']) / 2
        for x0_, x1_ in zip(np.linspace(a0, a1, 25)[:-1], np.linspace(a0, a1, 25)[1:]):
            for x in (x0_, x1_):
                pass
            b0_, b1_ = mo.beta_at(B, x0_ + 1e-6, Ls), mo.beta_at(B, x1_ - 1e-6, Ls)
            p = [B['c0'] + (s0 + x0_) * B['u'] + B['R'] * math.cos(b0_) * n * 0.98 - B['R'] * math.sin(b0_) * td,
                 B['c0'] + (s0 + x1_) * B['u'] + B['R'] * math.cos(b1_) * n * 0.98 - B['R'] * math.sin(b1_) * td,
                 B['c0'] + (s0 + x1_) * B['u'] + B['R'] * math.cos(b1_) * n * 0.98 + B['R'] * math.sin(b1_) * td,
                 B['c0'] + (s0 + x0_) * B['u'] + B['R'] * math.cos(b0_) * n * 0.98 + B['R'] * math.sin(b0_) * td]
            quads.append(p)
    Va = np.array([q for p in quads for q in p]); Fa = [(4 * i, 4 * i + 1, 4 * i + 2) for i in range(len(quads))] + [(4 * i, 4 * i + 2, 4 * i + 3) for i in range(len(quads))]
    Vall, Fall = fe.merge([(V, F), mon, (Va, Fa)])
    emis = np.r_[np.zeros(len(F)), np.zeros(len(mon[1])), np.ones(len(Fa))].astype(bool)
    colall = np.r_[col, colm, np.tile(np.minimum(lc * 1.0 + 0.1, 1), (len(Fa), 1))]
    # (opning berre lysande om ho vender mot kamera; elles ser ein ryggen av hylsa)
    face_cam = ((cam.eye - Va[0::4]) @ n) > 0
    img, zb = raster(cam, Vall, Fall, colall)
    if not face_cam.any():
        pass
    # planer per piksel
    d = cam_rays(cam); e = cam.eye
    with np.errstate(divide='ignore', invalid='ignore'):
        td_ = np.where(d[..., 2] < 0, -e[2] / d[..., 2], np.inf)
        tw_ = np.where(d[..., 1] > 0, (fe.WALL_Y - e[1]) / d[..., 1], np.inf)
    Hd = e + td_[..., None] * d
    Hw = e + tw_[..., None] * d
    ind = (Hd[..., 0] > -0.70) & (Hd[..., 0] < 0.70) & (Hd[..., 1] > 0) & (Hd[..., 1] < 0.75) & np.isfinite(td_)
    inw = (Hw[..., 0] > -0.70) & (Hw[..., 0] < 0.70) & (Hw[..., 2] > 0) & (Hw[..., 2] < 1.20) & np.isfinite(tw_)
    use_d = ind & (~inw | (td_ < tw_))
    use_w = inw & ~use_d
    tpl = np.where(use_d, td_, np.where(use_w, tw_, np.inf))
    plane_front = (1 / tpl) > zb
    out = img.copy()
    Ei = np.zeros(zb.shape)
    cd = np.stack([(Hd[..., 1] - gy[0]) / (gy[1] - gy[0]), (Hd[..., 0] - gx[0]) / (gx[1] - gx[0])])
    cw = np.stack([(Hw[..., 2] - wz[0]) / (wz[1] - wz[0]), (Hw[..., 0] - wx[0]) / (wx[1] - wx[0])])
    Ed_px = map_coordinates(Ed, cd.reshape(2, -1), order=1, mode='nearest').reshape(zb.shape)
    Ew_px = map_coordinates(Ew, cw.reshape(2, -1), order=1, mode='nearest').reshape(zb.shape)
    md = use_d & plane_front
    mw = use_w & plane_front
    E_amb = 0.02 * max(Ed.mean(), Ew.mean())                # grovt sprett i rommet (kosmetisk, ikkje i tal)
    out[md] = tone(RHO_DESK * (Ed_px[md] + E_amb) / math.pi)[:, None] * lc * TINT_DESK
    out[mw] = tone(RHO_WALL * (Ew_px[mw] + E_amb) / math.pi)[:, None] * lc * TINT_WALL
    # mjuk glød rundt lysande opning når ho er synleg
    em_mask = np.zeros(zb.shape)
    if face_cam.any():
        _, zba = raster(cam, Va, np.array(Fa), np.ones((len(Fa), 3)))
        em_mask = ((zba > 0) & (zba >= zb - 1e-9)).astype(float)
        glow = gaussian_filter(em_mask, 6 * SS) * 0.6 + gaussian_filter(em_mask, 25 * SS) * 0.35
        out = 1 - (1 - out) * (1 - np.clip(glow, 0, 1)[..., None] * lc)
    return dict(img=np.clip(out, 0, 1), zb=zb, Ed=Ed, Ew=Ew, gx=gx, gy=gy, wx=wx, wz=wz, L=L, A=A, n=n, P=P, dA=dA)


def draw_isolux(im, cam, R, levels, plane, col=(235, 215, 190)):
    """Teikn isoluxkurver (verdsrom -> bilete), med enkle tal ved kurva."""
    dr = ImageDraw.Draw(im, 'RGBA')
    S = cam.S
    f = ImageFont.truetype(FONT, int(15 * SS))
    E = R['Ed'] if plane == 'bord' else R['Ew']
    for lv in levels:
        for c in find_contours(E, lv):
            if plane == 'bord':
                W = np.c_[np.interp(c[:, 1], np.arange(len(R['gx'])), R['gx']), np.interp(c[:, 0], np.arange(len(R['gy'])), R['gy']), np.zeros(len(c))]
            else:
                W = np.c_[np.interp(c[:, 1], np.arange(len(R['wx'])), R['wx']), np.full(len(c), fe.WALL_Y - 1e-3), np.interp(c[:, 0], np.arange(len(R['wz'])), R['wz'])]
            p = cam.proj(W)
            ok = []
            for (x, y, z) in p:
                xi, yi = int(x), int(y)
                vis = 0 <= xi < S and 0 <= yi < S and (R['zb'][yi, xi] == 0 or 1 / z > R['zb'][yi, xi] - 1e-9)
                ok.append(vis)
            seg = []
            for (x, y, _), v in zip(p, ok):
                if v:
                    seg.append((x, y))
                elif len(seg) > 1:
                    dr.line(seg, fill=col + (110,), width=SS); seg = []
                else:
                    seg = []
            if len(seg) > 1:
                dr.line(seg, fill=col + (110,), width=SS)
            vis_pts = [q for q, v in zip(p, ok) if v]
            if len(vis_pts) > 20:
                x, y, _ = min(vis_pts, key=lambda q: q[0])
                dr.text((x + 6 * SS, y - 22 * SS), f'{lv:g} lx', font=f, fill=col + (190,))


def polar(dr, cx, cy, r, B, states, col_main, f):
    """Lysfordeling i planet vinkelrett på ryggraden: cd per 1000 lm, 0° = ned. Ringar 100/200/300 cd/klm."""
    for rr in (100, 200, 300):
        rad = r * rr / 300
        dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(90, 85, 78), width=1)
    dr.line([cx, cy - r - 8, cx, cy + r + 8], fill=(70, 66, 60), width=1)
    dr.line([cx - r - 8, cy, cx + r + 8, cy], fill=(70, 66, 60), width=1)
    # aksane i planet: w0 = ned (0°), v-retning = +y (mot veggen) teikna til høgre
    for st in states:
        n, eta, A, col, wdt = st[:5]
        gam = np.radians(np.arange(0, 361, 1))
        pts = []
        for gm in gam:
            dvec = math.cos(gm) * B['w'] + math.sin(gm) * B['v']
            c = float(dvec @ n)
            I = max(c, 0) * eta * 1000 / math.pi              # cd/klm, lambertsk opning
            rad = r * I / 300
            pts.append((cx + rad * math.sin(gm), cy + rad * math.cos(gm)))
        dr.line(pts, fill=col, width=wdt, joint='curve')
        tip = max(pts, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
        if len(st) > 5:
            dr.text((tip[0] + 10, tip[1] - 14), st[5], font=f, fill=col)
    dr.text((cx + r * 0.71 + 6, cy + r * 0.71 + 2), '300 cd/klm', font=f, fill=(150, 142, 130))


def main():
    B = next(b for b in mo.BODIES + mo.CONTROLS if b['id'] == KID)
    t, geo = mo.tal(B)
    eta, _ = mo.cavity_eta(B)
    op = lambda B_, ph: (lambda P, n, dA: (P, np.tile(n, (len(P), 1)), dA))(*mo.aperture(B_, ph))
    S_ = fe.sok(B, list(np.radians(np.arange(-180, 180, 5))), op, eta)
    W, M = S_['work'], S_['mood']
    PhiW = W['Phi']
    el = float(os.environ.get('EL', 26))
    cam = fe.Cam(S=1200 * SS, el=el, az=240, fov=19, D=float(os.environ.get('D', 3.1)), target=(0.0, 0.34, 0.30))
    Rw = study(B, W['s'], PhiW, eta, cam, 'arbeid')
    Rm = study(B, M['s'], PhiW * fe.DIM_STEM, eta, cam, 'stemning')
    ims = []
    for R, lv, pl in ((Rw, (100, 300, 500, 700), 'bord'), (Rm, (25, 50, 100), 'vegg')):
        im = Image.fromarray((R['img'] * 255).astype(np.uint8))
        draw_isolux(im, cam, R, lv, pl)
        ims.append(im.resize((1200, 1200), Image.LANCZOS))
    # ark
    Wd, Hd = 2*1200 + 3*80, 1200 + 2*80 + 560
    sheet = Image.new('RGB', (Wd, Hd), 'black')
    for j, im in enumerate(ims):
        sheet.paste(im, (80 + j * (1200 + 80), 80))
    dr = ImageDraw.Draw(sheet)
    fh = ImageFont.truetype(FONT, 46); fb = ImageFont.truetype(FONT, 33); fs = ImageFont.truetype(FONT, 24)
    white, grey = (240, 236, 228), (170, 163, 152)
    def head(x, y, s, w):
        dr.text((x, y), s, font=fh, fill=white)
        dr.line([x, y + 64, x + w, y + 62], fill=white, width=2)
    y0 = 80 + 1200 + 70
    dphi = abs((math.degrees(M['s'] - W['s']) + 180) % 360 - 180)
    Ev = M['Ev_stem']
    out_lm = eta * PhiW
    head(80, y0, 'arbeid', 210)
    nn_ = lambda v, d=0: f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')
    lines_w = [f'{nn_(PhiW)} lm frå LED · {nn_(PhiW / fe.LM_W, 1)} W · 2700 K',
               f'{nn_(W["Em"] * PhiW)} lx snitt på arbeidsflata · U0 {nn_(W["U0"], 2)}',
               'kjelda er skjerma frå auga og frå skjermen',
               f'kurvene: 100 · 300 · 500 · 700 lx']
    for i, s in enumerate(lines_w):
        dr.text((80, y0 + 100 + i * 50), s, font=fb, fill=white if i < 2 else grey)
    x2 = 80 + 1200 + 80
    head(x2, y0, 'stemning', 270)
    lines_m = [f'{nn_(PhiW * fe.DIM_STEM)} lm (25 %) · 2200 K · hylsa vridd {dphi:.0f}°',
               f'{Ev:.0f} lx snitt på veggen · {M["R_stem"] * 100:.0f} % av lyset på veggen',
               'kjelda er skjerma frå auga',
               'kurvene: 25 · 50 · 100 lx på veggen']
    for i, s in enumerate(lines_m):
        dr.text((x2, y0 + 100 + i * 50), s, font=fb, fill=white if i < 2 else grey)
    # polar
    cx, cy, r = x2 + 1200 - 200, y0 + 230, 170
    polar(dr, cx, cy, r, B, [((math.cos(W['s']) * B['w'] + math.sin(W['s']) * B['v']), eta, 0, (245, 225, 200), 3, 'arbeid'),
                             ((math.cos(M['s']) * B['w'] + math.sin(M['s']) * B['v']), eta * fe.DIM_STEM, 0, (205, 165, 125), 2, 'stemning')], None, fs)
    dr.text((cx - r - 10, cy - r - 60), 'lysfordeling, snitt', font=fs, fill=grey)
    path = os.path.join(ROOT, GEN, f'studie_k{KID:02d}.png')
    sheet.save(path)
    print(path, f"PhiW={PhiW:.0f} Em={W['Em']*PhiW:.0f} U0={W['U0']:.2f} Ev={Ev:.0f} R={M['R_stem']:.2f} dphi={dphi:.0f} out_lm={out_lm:.0f} L_ap={Rw['L']:.0f}")


if __name__ == '__main__':
    main()
