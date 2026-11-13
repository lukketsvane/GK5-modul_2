"""form04 «Prisme» — overhead-armen frå form03 + ei refraksjonsflate. Erstattar (c) flak.

Kropp: fot under skjermen, U-søyle bak han, arm fram over han (uendra, stødig). I enden: ei tverrstong med LED-line i ei renne,
og 5 cm under ho ei klar prismeplate (lineær Fresnel, PMMA 3 mm, 60 × 16 cm). Stong og plate er eitt hovud som vippar om LED-aksen.
Grep: kvar rille i plata har vinkelen sin frå lyslova: lambertsk vifte inn, jamn illuminans på arbeidsflata ut, og ingenting utanfor.
Gest: vipp hovudet (α). 0 = arbeid, bakover = same vifte på veggen (stemning), framover = mot andletet.
Rekna fridomsgrad: α. Rekna flate: rillevinkelen τ(s). Søkt: LED-aksen (ys, zs).
Lover: Snell + Fresnel-tap per stråle, fluksbevaring (lambertsk -> jamn E: G ∝ 1/cos²θ), synsfelt, tipp, fotplate frå gestkrafta.
"""
import os, sys, math, json
import numpy as np
HER = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HER)
sys.path.insert(0, ROOT)
import felles as fe

N_PMMA, RHO_PMMA = 1.49, 1190
E_ALU, RHO_ALU = 70e9, 2700
RISS = 0.95                    # PREMISS: tap i rilleveggane (riser) og spreidd lys
SIGMA = 4.0                    # grader: lett mattering av oversida («spreiing») mjukar kanten av vifta
STRO = 0.01                    # PREMISS: 1 % strølys utanfor vifta (for luminans mot auga)
SYN_MIN = 15.0
T_FRIK = 0.20                  # N·m friksjon i leddet, i tillegg til pendelmomentet frå plata
ALFA = list(np.radians(np.arange(-130, 101, 5)))
COL_W, COL_F, COL_T = 0.10, 0.03, 0.002
COL_Y = 0.512
FOT_XY = (0.24, 0.30)
M_SKJERM = 4.0
BASE = dict(id=1, rad=1, kol=1, namn='prisme', L=0.60, bp=0.16, d=0.05, tp=0.003, ys=0.25, zs=0.64, y1=0.02, y2=0.43)
FINAL = dict(BASE, ys=0.22, zs=0.70)                 # frå sok.json: robust punkt
GESTORD = 'vippa'


def fresnel_T(ti, tt, n1, n2):
    """Upolarisert transmisjon gjennom ei flate. ti innfall, tt brote."""
    ci, ct = np.cos(ti), np.cos(tt)
    rs = ((n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)) ** 2
    rp = ((n1 * ct - n2 * ci) / (n1 * ct + n2 * ci)) ** 2
    return 1 - 0.5 * (rs + rp)


_opt = {}


def optikk(B):
    """Rillevinkel τ(s) og utstrålt fordeling G(θ). θ og φ: frå loddrett ned, positiv mot brukaren."""
    key = (B['bp'], B['d'], B['ys'], B['zs'], B['y1'], B['y2'])
    if key in _opt:
        return _opt[key]
    n = N_PMMA
    phm = math.atan(B['bp'] / 2 / B['d'])
    ph = np.linspace(-phm, phm, 2001)
    th1 = math.atan((B['ys'] - B['y2']) / B['zs'])            # bakre kant av sona
    th2 = math.atan((B['ys'] - B['y1']) / B['zs'])            # fremre kant
    Fs = (np.sin(ph) + math.sin(phm)) / (2 * math.sin(phm))   # lambertsk i snittet
    th = np.arctan(math.tan(th1) + Fs * (math.tan(th2) - math.tan(th1)))   # jamn E: kumulativ ∝ tan θ
    phi_i = np.arcsin(np.sin(ph) / n)                         # etter flat overside
    tau = np.arctan2(n * np.sin(phi_i) - np.sin(th), n * np.cos(phi_i) - np.cos(th))   # normalen til rilleflata
    ti2 = phi_i - tau
    T1 = fresnel_T(np.abs(ph), np.abs(phi_i), 1.0, n)
    T2 = fresnel_T(np.abs(ti2), np.abs(th - tau), n, 1.0)
    tir = np.abs(n * np.sin(ti2)) >= 1
    w = np.cos(ph) * T1 * T2 * (~tir)
    samla = math.sin(phm)                                     # del av LED-fluksen som treffer plata (renna klipper resten)
    eta = samla * np.trapezoid(w, ph) / np.trapezoid(np.cos(ph), ph) * RISS
    # fordeling per radian av θ, så mattering (gauss) på jamt gitter
    tg = np.radians(np.arange(-180, 180.01, 0.25))
    Fc = np.cumsum(w); Fc = Fc / Fc[-1]
    Fi = np.interp(tg, th, Fc, left=0, right=1)
    G = np.gradient(Fi, tg)
    k = np.exp(-0.5 * (np.degrees(tg - tg[len(tg) // 2]) / SIGMA) ** 2); k /= k.sum()
    G = np.convolve(G, k, mode='same')
    G /= np.trapezoid(G, tg)
    _opt[key] = dict(ph=ph, th=th, tau=tau, s=B['d'] * np.tan(ph), eta=float(eta), tg=tg, G=G, th1=th1, th2=th2, phm=phm,
                     ti2_maks=float(np.degrees(np.abs(ti2).max())), tir=bool(tir.any()), T_snitt=float(np.trapezoid(w, ph) / np.trapezoid(np.cos(ph), ph)), samla=samla)
    return _opt[key]


def eta(B):
    return optikk(B)['eta']


def _src(B, nx=24):
    xs = (np.arange(nx) + .5) / nx * B['L'] - B['L'] / 2
    return np.c_[xs, np.full(nx, B['ys']), np.full(nx, B['zs'])]


def I_mot(B, a, Q):
    """Lysstyrke per LED-lumen [cd/lm] frå kvart lineelement mot punkta Q. Returnerer (I (ns,nq), d, r)."""
    O = optikk(B)
    S = _src(B)
    d = Q[None] - S[:, None]
    r = np.linalg.norm(d, axis=-1)
    xi = np.arcsin(np.clip(d[..., 0] / r, -1, 1))
    th = np.arctan2(-d[..., 1], -d[..., 2])
    gam = (th - a + np.pi) % (2 * np.pi) - np.pi
    Gv = np.interp(gam, O['tg'], O['G'])
    return O['eta'] / len(S) * Gv * (2 / np.pi) * np.cos(xi), d, r, S


def E_punkt(B, a, Q, qn):
    """Illuminans [lx per LED-lumen] på punkta Q med normal qn."""
    I, d, r, S = I_mot(B, a, Q)
    ci = -(d @ qn) / r
    ok = (ci > 0) & ~fe.screen_block(S, Q)
    return (np.where(ok, I * ci / r ** 2, 0.0)).sum(0)


def L_mot(B, a, Q):
    """Snittluminans av plata sett frå Q [cd/m2 per LED-lumen]: I/(A·cos), pluss strølys. 0 om ein ser oversida."""
    I, d, r, S = I_mot(B, a, Q)
    m = np.array([0.0, -math.sin(a), -math.cos(a)])              # lyssida si normal
    c = ((Q - np.array([0, B['ys'], B['zs']])) @ m) / np.linalg.norm(Q - np.array([0, B['ys'], B['zs']]), axis=-1)
    A = B['L'] * B['bp']
    ok = ~fe.screen_block(S, Q)
    Lb = (I * ok).sum(0) / (A * np.clip(c, 0.05, None))
    stro = STRO * optikk(B)['eta'] / (math.pi * A)
    return np.where(c > 0, Lb + stro, 0.0)


def hovudpunkt(B, a):
    """Punkt på hovudet i y–z (plateunderside og tverrstong) for kollisjon og synsfelt."""
    ned = np.array([-math.sin(a), -math.cos(a)]); fram = np.array([-math.cos(a), math.sin(a)])
    c = np.array([B['ys'], B['zs']])
    loc = [(v, B['d'] + B['tp']) for v in np.linspace(-B['bp'] / 2, B['bp'] / 2, 7)] + [(-0.01, -0.02), (0.01, -0.02)]
    return np.array([c + v * fram + w * ned for v, w in loc])


def kollisjon(B, a, arbeid):
    p = hovudpunkt(B, a)
    if (p[:, 0] > 0.73).any() or ((p[:, 0] < 0.50) & (p[:, 1] < 0.50)).any():
        return True
    if ((p[:, 0] > 0.43) & (p[:, 0] < 0.49) & (p[:, 1] < 0.44)).any():
        return True
    if (p[:, 0] > COL_Y - 0.01).any():
        return True
    if arbeid:
        e = fe.EYES[0]
        if (np.degrees(np.arctan2(p[:, 1] - e[2], p[:, 0] - e[1])) < SYN_MIN).any():
            return True
    return False


def speglepunkt(B):
    """Punkt på skjermen der auga ser plata spegla (om nokon)."""
    c = np.array([0, B['ys'], B['zs'] - B['d']])
    out = []
    for e in fe.EYES:
        em = e.copy(); em[1] = 2 * fe.SCR['y'] - e[1]
        t = (fe.SCR['y'] - em[1]) / (c[1] - em[1])
        q = em + t * (c - em)
        if fe.SCR['x0'] < q[0] < fe.SCR['x1'] and fe.SCR['z0'] < q[2] < fe.SCR['z1'] and c[1] < fe.SCR['y']:
            out.append(q)
    return np.array(out)


def sok(B):
    rows = []
    sp = speglepunkt(B)
    for a in ALFA:
        Et = E_punkt(B, a, fe.TASK, np.array([0, 0, 1.0]))
        Ew = E_punkt(B, a, fe.WALLG, np.array([0, -1.0, 0])).mean()
        Ed = E_punkt(B, a, fe.DESKG, np.array([0, 0, 1.0])).mean()
        Em = Et.mean()
        r = dict(s=a, Em=Em, U0=Et.min() / max(Em, 1e-12), Phi=fe.E_TASK / max(Em, 1e-12), Ew=Ew, Ed=Ed,
                 R_stem=Ew / max(Ew + Ed, 1e-12), face=E_punkt(B, a, fe.EYES[:1], np.array([0, 1.0, 0]))[0],
                 Le=float(L_mot(B, a, fe.EYES).max()), Lr=float(L_mot(B, a, sp).max()) if len(sp) else 0.0,
                 kolli=kollisjon(B, a, False), A=B['L'] * B['bp'])
        rows.append(r)
    for r in rows:
        r['Lap'] = max(r['Le'], r['Lr']) * r['Phi']                 # luminans mot auga (direkte eller spegla) ved 500 lx
        r['vis'] = r['Le'] * r['Phi'] > 300
        r['refl'] = r['Lr'] * r['Phi'] > 300
        r['glare_ok'] = r['Lap'] <= fe.L_MAX
    fw = [r for r in rows if r['glare_ok'] and r['U0'] >= fe.U0_MIN and not kollisjon(B, r['s'], True)]
    W = min(fw or rows, key=lambda r: r['Phi'])
    for r in rows:
        r['L_stem'] = max(r['Le'], r['Lr']) * W['Phi'] * fe.DIM_STEM
        r['stem_ok'] = r['L_stem'] <= fe.L_STEM_MAX
        r['Ev_stem'] = r['Ew'] * W['Phi'] * fe.DIM_STEM
    fm = [r for r in rows if not r['kolli'] and r['stem_ok']]
    Mo = max(fm or rows, key=lambda r: (r['R_stem'] >= fe.R_STEM_MIN, r['Ev_stem']))
    Fa = max([r for r in rows if not r['kolli']] or rows, key=lambda r: r['face'])
    i0, i1 = sorted((rows.index(W), rows.index(Mo)))
    veg = list(range(i0, i1 + 1))
    if rows.index(W) > rows.index(Mo):
        veg = veg[::-1]
    fri = all((not rows[i]['kolli']) and max(rows[i]['Le'], rows[i]['Lr']) * W['Phi'] * (1 - 0.75 * j / max(len(veg) - 1, 1)) <= fe.L_MAX
              for j, i in enumerate(veg))
    Phi150 = fe.E_FACE / max(Fa['face'], 1e-12)
    return dict(rows=rows, work=W, mood=Mo, face=Fa, veg=veg if fri else None, sveip='fri' if fri else 'stengd', steg=len(veg) - 1,
                L150=Fa['Le'] * Phi150, Phi150=Phi150,
                ok=bool(bool(fw) and fri and Mo['R_stem'] >= fe.R_STEM_MIN and Mo['stem_ok']))


# ---------------- grensesnitt mot lysstudie.py ----------------
def E_flate(B, a, Phi, pts, qn):
    out = np.zeros(len(pts))
    for i in range(0, len(pts), 3000):
        out[i:i + 3000] = E_punkt(B, a, pts[i:i + 3000], qn) * Phi
    return out


def I_kurve(B, a):
    """cd/klm i snittet (x = 0), vinkel gm: 0 = ned, + mot veggen."""
    O = optikk(B)
    gm = np.radians(np.arange(0, 361, 1))
    th = -gm
    gam = (th - a + np.pi) % (2 * np.pi) - np.pi
    return O['eta'] * np.interp(gam, O['tg'], O['G']) * (2 / np.pi) * 1000


# ---------------- geometri ----------------
def rekt(x0, x1, y0, y1, z0, z1):
    return fe.prism(np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]]), z0, z1)


FOT_BAK = 0.04                 # foten stikk 4 cm bak søyla: første versjon tippa bakover (næraste kant var bakkanten)


def fot_y():
    y1 = COL_Y + COL_F + FOT_BAK
    return y1 - FOT_XY[1], y1


def fot_t(B, F_g, deler):
    """Fottjukn frå lova: F_tipp (utan skjerm, næraste kant) >= 2·F_gest. Heile mm."""
    y0, y1 = fot_y()
    kont = np.array([[-FOT_XY[0] / 2, y0], [FOT_XY[0] / 2, y0], [FOT_XY[0] / 2, y1], [-FOT_XY[0] / 2, y1]])
    for t_mm in range(3, 13):
        t = t_mm / 1000
        parts = deler + [(RHO_ALU * FOT_XY[0] * FOT_XY[1] * t + 0.15, np.array([0, (y0 + y1) / 2, t / 2]))]
        st = fe.stabilitet(parts, [kont], B['zs'], F_g)
        if st['F_tipp_N'] >= 2 * F_g and st['tipp_deg'] >= fe.TIP_MIN:
            return t
    return 0.012


def hovud_masse(B):
    m_plate = RHO_PMMA * B['L'] * B['bp'] * (B['tp'] + 0.001)
    m_stong = RHO_ALU * (0.016 + 2 * 0.020) * 0.0015 * B['L']
    return m_plate, m_stong + 0.10


def gestkraft(B):
    """Vippeaksen ligg i tyngdepunktet til hovudet (mellom LED-line og plate), så pendelmomentet er null.
    Første versjon vippa om LED-lina: plata hang som pendel (0,22 N·m), gestkrafta vart 5,3 N og foten 12 mm utan å halde.
    Forenkling: lyset er framleis rekna som om hovudet vippar om LED-lina (feil <= avstanden til tyngdepunktet)."""
    m_plate, m_stong = hovud_masse(B)
    return T_FRIK / (B['bp'] / 2), 0.0


def akse_under_led(B):
    m_plate, m_stong = hovud_masse(B)
    return m_plate * B['d'] / (m_plate + m_stong)


def geometri(B, a, pitch=0.005):
    O = optikk(B)
    c0 = np.array([0.0, B['ys'], B['zs']])
    ned = np.array([0.0, -math.sin(a), -math.cos(a)])
    fram = np.array([0.0, -math.cos(a), math.sin(a)])
    ex = np.array([1.0, 0, 0])
    meshes, emit = [], []

    def quad(p0, p1, p2, p3, em=False):
        meshes.append((np.array([p0, p1, p2, p3]), [(0, 1, 2), (0, 2, 3)])); emit.append(np.full(2, em))
    hx = B['L'] / 2
    top = c0 + B['d'] * ned
    # oversida av plata (flat) og rillene på undersida (teikna med 5 mm deling; reelt 0,5–1 mm)
    quad(top - hx * ex - B['bp'] / 2 * fram, top + hx * ex - B['bp'] / 2 * fram, top + hx * ex + B['bp'] / 2 * fram, top - hx * ex + B['bp'] / 2 * fram)
    nb = int(round(B['bp'] / pitch))
    for i in range(nb):
        s0, s1 = -B['bp'] / 2 + i * pitch, -B['bp'] / 2 + (i + 1) * pitch
        tau = float(np.interp((s0 + s1) / 2, O['s'], O['tau']))
        h = min(abs(math.tan(tau)) * pitch, 0.004)
        z0, z1 = (B['tp'] + h, B['tp']) if tau > 0 else (B['tp'], B['tp'] + h)
        p0, p1 = top + s0 * fram + z0 * ned, top + s1 * fram + z1 * ned
        quad(p0 - hx * ex, p0 + hx * ex, p1 + hx * ex, p1 - hx * ex, True)
        if i + 1 < nb:                                                  # rillevegg
            tau2 = float(np.interp(s1 + pitch / 2, O['s'], O['tau']))
            h2 = min(abs(math.tan(tau2)) * pitch, 0.004)
            zn = B['tp'] + h2 if tau2 > 0 else B['tp']
            p2 = top + s1 * fram + zn * ned
            quad(p1 - hx * ex, p1 + hx * ex, p2 + hx * ex, p2 - hx * ex)
    for sx in (-1, 1):                                                  # kinn i endane: frå tverrstong til plate
        o = c0 + sx * hx * ex
        quad(o - 0.010 * fram - 0.020 * ned, o + 0.010 * fram - 0.020 * ned, o + B['bp'] / 2 * fram + (B['d'] + B['tp']) * ned, o - B['bp'] / 2 * fram + (B['d'] + B['tp']) * ned)

    def add(m):
        meshes.append(m); emit.append(np.zeros(len(m[1]), bool))
    # tverrstong: U-renne 16 × 20, opning ned i hovudet
    for off in (-0.008, 0.008):
        quad(c0 - hx * ex + off * fram + 0.005 * ned, c0 + hx * ex + off * fram + 0.005 * ned, c0 + hx * ex + off * fram - 0.015 * ned, c0 - hx * ex + off * fram - 0.015 * ned)
    quad(c0 - hx * ex - 0.008 * fram - 0.015 * ned, c0 + hx * ex - 0.008 * fram - 0.015 * ned, c0 + hx * ex + 0.008 * fram - 0.015 * ned, c0 - hx * ex + 0.008 * fram - 0.015 * ned)
    za = B['zs'] + 0.03                                                 # underkant arm; LED-aksen heng 3 cm under
    yb = COL_Y
    for sx in (-1, 1):
        add(rekt(sx * COL_W / 2 - 0.001, sx * COL_W / 2 + 0.001, B['ys'] - 0.012, B['ys'] + 0.012, B['zs'] - 0.012, za + COL_F))
        add(rekt(sx * COL_W / 2 - 0.001, sx * COL_W / 2 + 0.001, B['ys'] - 0.012, yb + COL_F, za, za + COL_F))
        add(rekt(sx * COL_W / 2 - 0.001, sx * COL_W / 2 + 0.001, yb, yb + COL_F, 0.004, za))
    add(rekt(-COL_W / 2, COL_W / 2, B['ys'] - 0.012, yb + COL_F, za + COL_F - COL_T, za + COL_F))
    add(rekt(-COL_W / 2, COL_W / 2, yb + COL_F - COL_T, yb + COL_F, 0.004, za + COL_F))
    t_f = tal_mek(B)['t_fot']
    add(rekt(-FOT_XY[0] / 2, FOT_XY[0] / 2, fot_y()[0], fot_y()[1], 0.0, t_f))
    V, F = fe.merge(meshes)
    return V, F, np.concatenate(emit)


_mek = {}


def tal_mek(B):
    key = (B['L'], B['bp'], B['d'], B['tp'], B['ys'], B['zs'])
    if key in _mek:
        return _mek[key]
    za = B['zs'] + 0.03
    m_plate, m_stong = hovud_masse(B)
    A_col = (COL_W + 2 * COL_F) * COL_T
    L_arm = COL_Y + COL_F - B['ys']
    m_col, m_arm = RHO_ALU * A_col * za, RHO_ALU * A_col * L_arm
    yb = COL_Y
    F_g, T_pend = gestkraft(B)
    deler = [(m_plate, np.array([0, B['ys'], B['zs'] - B['d']])), (m_stong, np.array([0, B['ys'], B['zs']])),
             (m_arm, np.array([0, B['ys'] + L_arm / 2, za])), (m_col, np.array([0, yb + COL_F / 2, za / 2]))]
    t_f = fot_t(B, F_g, deler)
    fy0, fy1 = fot_y()
    m_f = RHO_ALU * FOT_XY[0] * FOT_XY[1] * t_f + 0.15
    parts = deler + [(m_f, np.array([0, (fy0 + fy1) / 2, t_f / 2]))]
    kont = np.array([[-FOT_XY[0] / 2, fy0], [FOT_XY[0] / 2, fy0], [FOT_XY[0] / 2, fy1], [-FOT_XY[0] / 2, fy1]])
    st_a = fe.stabilitet(parts, [kont], B['zs'], F_g)
    st_m = fe.stabilitet(parts + [(M_SKJERM, np.array([0, 0.50, 0.20]))], [kont], B['zs'], F_g)
    c = (2 * COL_F * COL_T * COL_F / 2 + COL_W * COL_T * COL_T / 2) / A_col
    I_col = 2 * (COL_T * COL_F ** 3 / 12 + COL_T * COL_F * (COL_F / 2 - c) ** 2) + COL_W * COL_T ** 3 / 12 + COL_W * COL_T * (c - COL_T / 2) ** 2
    a_ = L_arm + B['bp'] / 2
    sv = (F_g * L_arm ** 3 / 3 + (F_g * a_) * za * a_) / (E_ALU * I_col) * 1000
    ned = (m_plate + m_stong) * fe.G * (L_arm ** 3 / 3 + L_arm ** 2 * za) / (E_ALU * I_col) * 1000
    _mek[key] = dict(st_a=st_a, st_m=st_m, t_fot=t_f, F_g=F_g, T_pend=T_pend, svikt=sv, ned=ned, L_arm=L_arm, m_plate=m_plate)
    return _mek[key]


def tal(B, S=None):
    S = S or sok(B)
    W, Mo = S['work'], S['mood']
    O = optikk(B)
    mk = tal_mek(B)
    V = geometri(B, W['s'])[0]
    A_kj = (0.016 + 2 * 0.020) * 2 * B['L']                            # tverrstonga, begge sider
    t = fe.tal_felles(B, S, mk['st_m'], V[V[:, 2] > 0.02], mk['svikt'], A_kj)
    t.update(L_mot_auga=W['Lap'], alfa_arb=math.degrees(W['s']), alfa_stem=math.degrees(Mo['s']), alfa_ansikt=math.degrees(S['face']['s']),
             sving=abs(math.degrees(Mo['s'] - W['s'])), Phi_ansikt=S['Phi150'], eta=O['eta'], samla=O['samla'], T_fresnel=O['T_snitt'],
             rille_min_deg=float(np.degrees(O['tau'].min())), rille_maks_deg=float(np.degrees(O['tau'].max())), innfall_maks_deg=O['ti2_maks'], tir=O['tir'],
             vifte_fra_deg=math.degrees(O['th1']), vifte_til_deg=math.degrees(O['th2']), tipp_aleine=mk['st_a']['tipp_deg'], F_tipp_aleine=mk['st_a']['F_tipp_N'],
             masse_kg=mk['st_a']['masse_kg'], fot_cm2=mk['st_a']['fot_cm2'], t_fot_mm=mk['t_fot'] * 1000, nedboying_mm=mk['ned'], T_pendel=mk['T_pend'],
             m_plate_kg=mk['m_plate'], akse_under_led_mm=akse_under_led(B) * 1000, ys=B['ys'], zs=B['zs'], L=B['L'], bp=B['bp'], d=B['d'])
    if mk['st_a']['F_tipp_N'] < 2 * mk['F_g'] or mk['st_a']['tipp_deg'] < fe.TIP_MIN:
        pass
    fl = fe.standard_flagg(t)
    if O['tir']: fl.append('totalrefleksjon i rillene')
    if mk['st_a']['F_tipp_N'] < 2 * mk['F_g'] or mk['st_a']['tipp_deg'] < fe.TIP_MIN: fl.append('veltar utan skjerm på foten')
    t['flagg'] = '; '.join(fl) or '-'
    return t, S


def search():
    res = []
    for ys in (0.18, 0.22, 0.26, 0.30, 0.34):
        for zs in (0.60, 0.63, 0.66, 0.70):
            B = dict(BASE, ys=ys, zs=zs)
            S = sok(B); W, Mo = S['work'], S['mood']
            res.append(dict(ys=ys, zs=zs, ok=S['ok'], Phi=float(W['Phi']), U0=float(W['U0']), Lauga=float(W['Lap']), eta=eta(B), Rst=float(Mo['R_stem']),
                            Ev=float(Mo['Ev_stem']), L150=float(S['L150']), Phi150=float(S['Phi150']), aw=math.degrees(W['s']), am=math.degrees(Mo['s']),
                            af=math.degrees(S['face']['s']), sveip=S['sveip'], kolli_arb=bool(kollisjon(B, W['s'], True))))
    json.dump(res, open(os.path.join(HER, 'sok.json'), 'w'), indent=1)
    return res


if __name__ == '__main__':
    res = search()
    ok = [r for r in res if r['ok']]
    print(len(res), 'køyrt', len(ok), 'ok')
    for r in sorted(ok or res, key=lambda r: r['Phi'])[:10]:
        print({k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()})


def LINJER(B, S, lw, lm):
    """Tekst til lysstudien: kjelda er retta, ikkje skjerma."""
    W, M = S['work'], S['mood']
    nn_ = lambda v, d=0: f'{v:,.{d}f}'.replace(',', ' ').replace('.', ',')
    lw[2] = f'ingenting utanfor vifta: {nn_(W["Lap"])} cd/m² mot auga'
    lm[2] = 'same vifte, lagd på veggen'
    return lw, lm


def render_kropp(B, path):
    from PIL import Image
    S = sok(B)
    ims = []
    for st in (S['work']['s'], S['mood']['s'], S['face']['s']):
        V, F, emit = geometri(B, st)
        V = V.copy(); V[:, 1] -= 0.45
        im, _ = fe.render(V, F, fe.Cam(S=2048, el=17, az=240, fov=19, D=4.6, target=(0, 0, 0.36)), emit=emit)
        ims.append(im)
    out = Image.new('RGB', (ims[0].width * 3, ims[0].height), 'black')
    for j, im in enumerate(ims):
        out.paste(im, (j * im.width, 0))
    out.save(path)
    return S


def kontroll_fluks(B):
    """Fluksbevaring: integrer lysstyrken over heile kula. Skal gje η."""
    n = 400
    u = (np.arange(n) + .5) / n * 2 - 1
    az = (np.arange(2 * n) + .5) / (2 * n) * 2 * np.pi
    U, A = np.meshgrid(u, az)
    r_ = np.sqrt(1 - U ** 2)
    D = np.c_[(r_ * np.cos(A)).ravel(), (r_ * np.sin(A)).ravel(), U.ravel()] * 50.0 + np.array([0, B['ys'], B['zs']])
    I, d, r, S_ = I_mot(B, 0.0, D)
    return float(I.sum(0).mean() * 4 * np.pi)
