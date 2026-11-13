"""Lysstudie av éin kropp: forma stor, lyset på bord og vegg, isolux, lysfordeling (polar) og nøkkeltal.
Bruk: python lysstudie.py gen01 1   eller   python lysstudie.py form01
Generisk grensesnitt (motor.py): BASE/FINAL, sok(B), opning(B, s, nt, n) -> (P,N,dA), eta(B), geometri(B, s) -> (V,F,emit,...)
Briefen: «prøv lys mot flater, skjerm og ansikt · undersøk lyset før forma vert låst».
(Førre versjon: lysstudie_gen01_v1.py)
"""
import os, sys, math, importlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import map_coordinates, gaussian_filter
from skimage.measure import find_contours

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import felles as fe

RHO_DESK, RHO_WALL, RHO_MON = 0.45, 0.75, 0.08
TINT_DESK, TINT_WALL = np.array([1.0, 0.93, 0.84]), np.array([1.0, 0.99, 0.97])
CCT = {'arbeid': (2700, np.array([1.0, 0.90, 0.80])), 'stemning': (2200, np.array([1.0, 0.84, 0.70]))}
L_REF = 78.0                     # cd/m2 -> 0,6 i tonekurva (bord ved 500 lx)
SS = 2
FONT = r'C:\Windows\Fonts\georgiai.ttf'


def tone(L):
    return (1 - np.exp(-np.maximum(L, 0) / L_REF)) ** (1 / 2.2)


def cam_rays(cam):
    S = cam.S
    ys, xs = np.mgrid[0:S, 0:S] + 0.5
    xc, yc = (xs - S / 2) / cam.k, -(ys - S / 2) / cam.k
    return xc[..., None] * cam.M[0] + yc[..., None] * cam.M[1] + cam.M[2]


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


def lamp_colors(V, F, cam):
    T = V[F]
    nn = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-15
    nn *= np.sign(((cam.eye - T.mean(1)) * nn).sum(1))[:, None]
    return np.clip(fe.ALB * (0.40 + 0.55 * np.clip(nn @ fe.KEY, 0, 1)[:, None] + 0.08 * np.clip(nn[:, 2], 0, 1)[:, None]), 0, 1)


def study(Efun, V, F, emit, cam, label):
    """Éin gesttilstand. Efun(pts, qn) -> lux på punkta. V,F,emit lampegeometri."""
    gx, gy = np.linspace(-0.70, 0.70, 281), np.linspace(0.0, 0.75, 151)
    DX, DY = np.meshgrid(gx, gy)
    Ed = Efun(np.c_[DX.ravel(), DY.ravel(), np.zeros(DX.size)], np.array([0, 0, 1.0])).reshape(DX.shape)
    wx, wz = np.linspace(-0.70, 0.70, 281), np.linspace(0.0, 1.20, 241)
    WX, WZ = np.meshgrid(wx, wz)
    Ew = Efun(np.c_[WX.ravel(), np.full(WX.size, fe.WALL_Y - 1e-3), WZ.ravel()], np.array([0, -1.0, 0])).reshape(WX.shape)
    lc = CCT[label][1]
    col = lamp_colors(V, F, cam)
    col[emit] = np.minimum(lc + 0.1, 1)
    Vm, Fm = box(fe.SCR['x0'], fe.SCR['x1'], fe.SCR['y'], fe.SCR['y'] + 0.02, fe.SCR['z0'], fe.SCR['z1'], 36)
    Vs, Fs = box(-0.03, 0.03, 0.47, 0.50, 0.001, fe.SCR['z0'], 2)
    Vf, Ff = box(-0.11, 0.11, 0.42, 0.60, 0.001, 0.008, 2)
    mon = fe.merge([(Vm, Fm), (Vs, Fs), (Vf, Ff)])
    Tm = mon[0][mon[1]]
    nm = np.cross(Tm[:, 1] - Tm[:, 0], Tm[:, 2] - Tm[:, 0]); nm /= np.linalg.norm(nm, axis=1, keepdims=True) + 1e-15
    Emon = np.zeros(len(nm)); cm_ = Tm.mean(1)
    for q in np.unique(np.round(nm, 3), axis=0):
        mk = np.all(np.abs(nm - q) < 2e-3, axis=1)
        Emon[mk] = Efun(cm_[mk] + q * 1e-3, q)
    colm = np.clip(tone(RHO_MON * Emon / math.pi)[:, None] * lc * 0.9 + 0.025, 0, 1)
    colm[len(Fm):] = 0.045
    Vall, Fall = fe.merge([(V, F), mon])
    img, zb = raster(cam, Vall, Fall, np.r_[col, colm])
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
    front = (1 / tpl) > zb
    out = img.copy()
    cd = np.stack([(Hd[..., 1] - gy[0]) / (gy[1] - gy[0]), (Hd[..., 0] - gx[0]) / (gx[1] - gx[0])])
    cw = np.stack([(Hw[..., 2] - wz[0]) / (wz[1] - wz[0]), (Hw[..., 0] - wx[0]) / (wx[1] - wx[0])])
    Ed_px = map_coordinates(Ed, cd.reshape(2, -1), order=1, mode='nearest').reshape(zb.shape)
    Ew_px = map_coordinates(Ew, cw.reshape(2, -1), order=1, mode='nearest').reshape(zb.shape)
    md, mw = use_d & front, use_w & front
    E_amb = 0.02 * max(Ed.mean(), Ew.mean())                 # grovt sprett (kosmetisk, ikkje i tal)
    out[md] = tone(RHO_DESK * (Ed_px[md] + E_amb) / math.pi)[:, None] * lc * TINT_DESK
    out[mw] = tone(RHO_WALL * (Ew_px[mw] + E_amb) / math.pi)[:, None] * lc * TINT_WALL
    if emit.any():
        _, zba = raster(cam, V, F[emit], np.ones((int(emit.sum()), 3)))
        em = ((zba > 0) & (zba >= zb - 1e-9)).astype(float)
        glow = gaussian_filter(em, 6 * SS) * 0.6 + gaussian_filter(em, 25 * SS) * 0.35
        out = 1 - (1 - out) * (1 - np.clip(glow, 0, 1)[..., None] * lc)
    return dict(img=np.clip(out, 0, 1), zb=zb, Ed=Ed, Ew=Ew, gx=gx, gy=gy, wx=wx, wz=wz)


def draw_isolux(im, cam, R, levels, plane, col=(235, 215, 190)):
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
            ok = [(0 <= int(x) < S and 0 <= int(y) < S and (R['zb'][int(y), int(x)] == 0 or 1 / z > R['zb'][int(y), int(x)] - 1e-9)) for x, y, z in p]
            seg = []
            for (x, y, _), v in zip(p, ok):
                if v:
                    seg.append((x, y))
                else:
                    if len(seg) > 1:
                        dr.line(seg, fill=col + (110,), width=SS)
                    seg = []
            if len(seg) > 1:
                dr.line(seg, fill=col + (110,), width=SS)
            vis = [q for q, v in zip(p, ok) if v]
            if len(vis) > 20:
                x, y, _ = min(vis, key=lambda q: q[0])
                dr.text((x + 6 * SS, y - 22 * SS), f'{lv:g} lx', font=f, fill=col + (190,))


def polar(dr, cx, cy, r, curves, f):
    """curves: [(I(γ) i cd/klm, farge, breidd, etikett)], γ i planet y–z, 0° = ned, + mot veggen (til høgre)."""
    top = max(float(np.max(c[0])) for c in curves)
    sc = 300 if top <= 330 else (900 if top <= 990 else 1500)
    for rr in (sc / 3, 2 * sc / 3, sc):
        rad = r * rr / sc
        dr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(90, 85, 78), width=1)
    dr.line([cx, cy - r - 8, cx, cy + r + 8], fill=(70, 66, 60), width=1)
    dr.line([cx - r - 8, cy, cx + r + 8, cy], fill=(70, 66, 60), width=1)
    for I, col, wdt, lab in curves:
        g = np.radians(np.arange(0, 361, 1))
        pts = [(cx + r * min(i, 1.1 * sc) / sc * math.sin(gm), cy + r * min(i, 1.1 * sc) / sc * math.cos(gm)) for i, gm in zip(I, g)]
        dr.line(pts, fill=col, width=wdt, joint='curve')
        tip = max(pts, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
        dr.text((tip[0] + 10, tip[1] - 14), lab, font=f, fill=col)
    dr.text((cx + r * 0.71 + 6, cy + r * 0.71 + 2), f'{sc} cd/klm', font=f, fill=(150, 142, 130))


def intensity_curve(P, N, dA, L_per_lm):
    g = np.radians(np.arange(0, 361, 1))
    D = np.c_[np.zeros_like(g), np.sin(g), -np.cos(g)]
    return (np.clip(N @ D.T, 0, None) * dA[:, None]).sum(0) * L_per_lm * 1000


def sheet(Rw, Rm, cam, lines_w, lines_m, curves, path):
    ims = []
    for R, lv, pl in ((Rw, (100, 300, 500, 700), 'bord'), (Rm, (25, 50, 100), 'vegg')):
        im = Image.fromarray((R['img'] * 255).astype(np.uint8))
        draw_isolux(im, cam, R, lv, pl)
        ims.append(im.resize((1200, 1200), Image.LANCZOS))
    Wd, Hd = 2 * 1200 + 3 * 80, 1200 + 2 * 80 + 560
    sh = Image.new('RGB', (Wd, Hd), 'black')
    for j, im in enumerate(ims):
        sh.paste(im, (80 + j * (1200 + 80), 80))
    dr = ImageDraw.Draw(sh)
    fh, fb, fs = (ImageFont.truetype(FONT, s) for s in (46, 33, 24))
    white, grey = (240, 236, 228), (170, 163, 152)
    y0 = 80 + 1200 + 70
    for x, head, w, lines in ((80, 'arbeid', 210, lines_w), (80 + 1280, 'stemning', 270, lines_m)):
        dr.text((x, y0), head, font=fh, fill=white)
        dr.line([x, y0 + 64, x + w, y0 + 62], fill=white, width=2)
        for i, s in enumerate(lines):
            dr.text((x, y0 + 100 + i * 50), s, font=fb, fill=white if i < 2 else grey)
    cx, cy, r = 80 + 1280 + 1200 - 200, y0 + 230, 170
    polar(dr, cx, cy, r, curves, fs)
    dr.text((cx - r - 10, cy - r - 60), 'lysfordeling, snitt', font=fs, fill=grey)
    sh.save(path)


nn_ = lambda v, d=0: f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')


def lines(PhiW, W, M, sving, verb):
    lw = [f'{nn_(PhiW)} lm frå LED · {nn_(PhiW / fe.LM_W, 1)} W · 2700 K',
          f'{nn_(W["Em"] * PhiW)} lx snitt på arbeidsflata · U0 {nn_(W["U0"], 2)}',
          ('lysflata er synleg, under 3 000 cd/m²' if W.get('vis') else 'kjelda er skjerma frå auga og frå skjermen') if W['glare_ok'] else 'kjelda er synleg: blendar',
          'kurvene: 100 · 300 · 500 · 700 lx']
    lm = [f'{nn_(PhiW * fe.DIM_STEM)} lm (25 %) · 2200 K · {verb} {sving:.0f}°',
          f'{nn_(M["Ev_stem"])} lx snitt på veggen · {M["R_stem"] * 100:.0f} % av lyset på veggen',
          ('lysflata er synleg, under 1 000 cd/m²' if (M.get('vis') or M.get('refl')) else 'kjelda er skjerma frå auga') if M['stem_ok'] else 'kjelda er synleg',
          'kurvene: 25 · 50 · 100 lx på veggen']
    return lw, lm


def make_cam():
    return fe.Cam(S=1200 * SS, el=float(os.environ.get('EL', 26)), az=240, fov=19, D=float(os.environ.get('D', 3.1)),
                  target=(0.0, 0.34, 0.30))


def run_generic(mo, gen):
    B = dict(mo.FINAL) if hasattr(mo, 'FINAL') else dict(mo.BASE)
    S = mo.sok(B)
    W, M = S['work'], S['mood']
    eta = mo.eta(B)
    PhiW = W['Phi']
    cam = make_cam()
    Rs = {}
    for lab, st, Phi in (('arbeid', W['s'], PhiW), ('stemning', M['s'], PhiW * fe.DIM_STEM)):
        V, F, emit = mo.geometri(B, st)[:3]
        if hasattr(mo, 'E_flate'):                                   # retta kjelde (linse/prisme)
            Rs[lab] = study(lambda pts, qn, st=st, Phi=Phi: mo.E_flate(B, st, Phi, pts, qn), V, F, np.asarray(emit, bool), cam, lab)
            Rs[lab]['I'] = mo.I_kurve(B, st)
        else:
            P, N, dA = mo.opning(B, st, nt=4, n=97)
            L = eta * Phi / (math.pi * dA.sum())
            Rs[lab] = study(lambda pts, qn, P=P, N=N, dA=dA, L=L: plane_E(P, N, dA, L, pts, qn), V, F, np.asarray(emit, bool), cam, lab)
            Rs[lab]['I'] = intensity_curve(P, N, dA, eta / (math.pi * dA.sum()))
    sving = (len(S['veg']) - 1) * 5 if S.get('veg') else abs((math.degrees(M['s'] - W['s']) + 180) % 360 - 180)
    lw, lm = lines(PhiW, W, M, sving, getattr(mo, 'GESTORD', 'vridd'))
    if hasattr(mo, 'LINJER'):
        lw, lm = mo.LINJER(B, S, lw, lm)
    curves = [(Rs['arbeid']['I'], (245, 225, 200), 3, 'arbeid'), (Rs['stemning']['I'] * fe.DIM_STEM, (205, 165, 125), 2, 'stemning')]
    path = os.path.join(ROOT, gen, 'studie.png')
    sheet(Rs['arbeid'], Rs['stemning'], cam, lw, lm, curves, path)
    print(path, f"Phi={PhiW:.0f} Em={W['Em']*PhiW:.0f} U0={W['U0']:.2f} Ev={M['Ev_stem']:.0f} R={M['R_stem']:.2f} sving={sving:.0f}")


def run_gen01(mo, kid, gen):
    B = next(b for b in mo.BODIES + mo.CONTROLS if b['id'] == kid)
    mo.tal(B)
    eta, _ = mo.cavity_eta(B)
    op = lambda B_, ph: (lambda P, n, dA: (P, np.tile(n, (len(P), 1)), dA))(*mo.aperture(B_, ph))
    S = fe.sok(B, list(np.radians(np.arange(-180, 180, 5))), op, eta)
    W, M = S['work'], S['mood']
    PhiW = W['Phi']
    cam = make_cam()
    Rs = {}
    for lab, st, Phi in (('arbeid', W['s'], PhiW), ('stemning', M['s'], PhiW * fe.DIM_STEM)):
        P, n, dA = mo.aperture(B, st, ns=24, nt=4)
        N = np.tile(n, (len(P), 1))
        L = eta * Phi / (math.pi * dA.sum())
        geo = mo.build(B, st)
        Rs[lab] = study(lambda pts, qn, P=P, N=N, dA=dA, L=L: plane_E(P, N, dA, L, pts, qn), geo['V'], geo['F'], np.zeros(len(geo['F']), bool), cam, lab)
        Rs[lab]['I'] = intensity_curve(P, N, dA, eta / (math.pi * dA.sum()))
    dphi = abs((math.degrees(M['s'] - W['s']) + 180) % 360 - 180)
    lw, lm = lines(PhiW, W, M, dphi, 'hylsa vridd')
    curves = [(Rs['arbeid']['I'], (245, 225, 200), 3, 'arbeid'), (Rs['stemning']['I'] * fe.DIM_STEM, (205, 165, 125), 2, 'stemning')]
    sheet(Rs['arbeid'], Rs['stemning'], cam, lw, lm, curves, os.path.join(ROOT, gen, f'studie_k{kid:02d}.png'))


if __name__ == '__main__':
    gen = sys.argv[1] if len(sys.argv) > 1 else 'gen01'
    sys.path.insert(0, os.path.join(ROOT, gen))
    mo = importlib.import_module('motor')
    if hasattr(mo, 'geometri'):
        run_generic(mo, gen)
    else:
        run_gen01(mo, int(sys.argv[2]) if len(sys.argv) > 2 else 1, gen)
