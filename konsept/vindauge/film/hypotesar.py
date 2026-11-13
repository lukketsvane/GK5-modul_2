# -*- coding: utf-8 -*-
"""
hypotesar.py -- eksakt todimensjonal geometrisk-optisk sporar for tynne
mikrostrukturfilmar (prismefilm, lentikulaer, einvegsdiffusor), og
hypoteseproving mot fotoa av arket fraa skjermen.

Kva sporaren gjer (alt er rekna, ingenting er maalt paa arket):
  - periodisk overflateprofil gitt som polylinje (prisme med kva toppvinkel
    som helst, runda toppar, sirkelbogar, sinus, tilfeldig ruglete profil)
  - flat motsett side, valfritt baerelag (PET) under strukturlaget
  - Fresnel for s og p kvar for seg i kvar flate (upolarisert lys = snittet),
    totalrefleksjon, straalar som gaar inn att i naboryggen
  - bolgjelengdavhengig brytingsindeks (Sellmeier, sjaa n_pc / n_harpiks)
  - begge orienteringar av arket (struktur mot kamera eller mot vindauget)
    og helling
  - skeive straalar (komponent langs ryggane) med effektiv indeks; daa er
    Fresnel-vektene eit upolarisert snitt i kvar flate (tilnaerming)

Vinklar: alt i grader. u = "opp" langs arket (tvers paa ryggane),
normalen peikar mot kamera. Ein kamerastraale som gaar bort fraa kamera
med vinkel a over normalen (positiv = stig), kjem ut paa andre sida med
vinkel b. Med arket loddrett og ryggane vassrett er a og b elevasjonar.

Koeyr:
  python hypotesar.py test      kontrollar (energi, plate, handrekna prisme, dispersjon)
  python hypotesar.py kart      avbildingskart sann -> tilsynelatande elevasjon
  python hypotesar.py bilete    syntetiske gjennomsyn
  python hypotesar.py foto      maal i fotoa (skriv berre til context/delar-foto/analyse/)
  python hypotesar.py alt       alt over
"""
import os
os.environ.setdefault("NUMBA_NUM_THREADS", "4")
import sys
import math
import json
import time
import numpy as np
from numba import njit, prange

HER = os.path.dirname(os.path.abspath(__file__))
UT = os.path.join(HER, "hypotesar")
CACHE = os.path.join(UT, "_cache")
ROT = os.path.abspath(os.path.join(HER, "..", "..", ".."))
FOTO = os.path.join(ROT, "context", "delar-foto")
ANALYSE = os.path.join(FOTO, "analyse")

# --------------------------------------------------------------------------
# Brytingsindeks
# --------------------------------------------------------------------------
# kjent fraa kjelde: Sultanova, Kasarova, Nikolov (2009), "Dispersion
# properties of optical polymers", Acta Physica Polonica A 116, 585.
# Sellmeier med eitt ledd, lambda i mikrometer (slik refractiveindex.info
# gjev dei att). Formlane er skrivne av etter minnet og kontrollerte mot
# n_d: PC 1,585, PMMA 1,491, PS 1,592.

def n_pc(lam_nm):
    l2 = (np.asarray(lam_nm, dtype=float) * 1e-3) ** 2
    return np.sqrt(1.0 + 1.4182 * l2 / (l2 - 0.021304))


def n_pmma(lam_nm):
    l2 = (np.asarray(lam_nm, dtype=float) * 1e-3) ** 2
    return np.sqrt(1.0 + 1.1819 * l2 / (l2 - 0.011313))


def n_ps(lam_nm):
    l2 = (np.asarray(lam_nm, dtype=float) * 1e-3) ** 2
    return np.sqrt(1.0 + 1.4435 * l2 / (l2 - 0.020216))


ND_HARPIKS = 1.59   # ANTAKING: UV-herda akrylat i prismelaget (typisk for lysforsterkingsfilm)
ND_PET = 1.65       # ANTAKING: PET-baerelag i planet


def n_harpiks(lam_nm, nd=ND_HARPIKS):
    """ANTAKING: prismeharpiksen har same dispersjonsform som polykarbonat
    (Abbe-tal kring 28-30), flytta slik at n(587,6 nm) = nd."""
    return n_pc(lam_nm) + (nd - float(n_pc(587.6)))


def n_pet(lam_nm, nd=ND_PET):
    """ANTAKING: PET = nd ved 587,6 nm med 1,15 x dispersjonen til PC.
    Baerelaget er planparallelt og endrar ikkje retningar, berre Fresnel-tap."""
    return nd + 1.15 * (n_pc(lam_nm) - float(n_pc(587.6)))


LAM = np.linspace(400.0, 700.0, 16)     # 16 bolgjelengder, 20 nm steg

# --------------------------------------------------------------------------
# Profilar (polylinjer over ein periode, x fraa 0 til 1, z >= 0)
# --------------------------------------------------------------------------

def profil_flat():
    return np.array([0.0, 1.0]), np.array([0.0, 0.0])


def profil_prisme(topp=90.0, r_topp=0.0, r_dal=0.0, nbue=24):
    """Symmetrisk prisme med toppvinkel `topp` (grader). r_topp og r_dal er
    avrundingsradius i einingar av perioden. Dalen ligg i x = 0 og x = 1."""
    h = math.radians(topp / 2.0)            # halv toppvinkel
    H = 0.5 / math.tan(h)                   # hoegd for skarp topp
    fi_max = math.pi / 2.0 - h              # flatenormalen sin vinkel fraa loddrett
    xs, zs = [], []
    if r_dal > 0:
        zc = r_dal / math.sin(h)
        for f in np.linspace(0.0, fi_max, nbue // 2 + 1):
            xs.append(r_dal * math.sin(f)); zs.append(zc - r_dal * math.cos(f))
    else:
        xs.append(0.0); zs.append(0.0)
    if r_topp > 0:
        zc = H - r_topp / math.sin(h)
        for f in np.linspace(-fi_max, fi_max, nbue + 1):
            xs.append(0.5 + r_topp * math.sin(f)); zs.append(zc + r_topp * math.cos(f))
    else:
        xs.append(0.5); zs.append(H)
    if r_dal > 0:
        zc = r_dal / math.sin(h)
        for f in np.linspace(fi_max, 0.0, nbue // 2 + 1):
            xs.append(1.0 - r_dal * math.sin(f)); zs.append(zc - r_dal * math.cos(f))
    else:
        xs.append(1.0); zs.append(0.0)
    x = np.array(xs); z = np.array(zs)
    z = z - z.min()
    return x, z


def profil_prisme_ujamn(topp=90.0, hogder=(1.0, 0.8, 0.92, 0.7)):
    """Fleire prisme med ulik hoegd i ein superperiode (same flatevinklar).
    Tverrsnittsbiletet av "randomisert prismehoegd"."""
    h = math.radians(topp / 2.0)
    w = np.array(hogder, dtype=float)
    w = w / w.sum()
    xs, zs = [0.0], [0.0]
    x0 = 0.0
    for wi in w:
        xs.append(x0 + wi / 2.0); zs.append((wi / 2.0) / math.tan(h))
        xs.append(x0 + wi); zs.append(0.0)
        x0 += wi
    xs[-1] = 1.0
    return np.array(xs), np.array(zs)


def profil_linse(R=0.6, nseg=96):
    """Sylinderlinser (lentikulaer): sirkelboge med radius R (einingar av
    perioden, R >= 0,5) over kvar periode, spiss dal mellom linsene."""
    x = np.linspace(0.0, 1.0, nseg + 1)
    z = np.sqrt(R * R - (x - 0.5) ** 2) - math.sqrt(R * R - 0.25)
    z[0] = 0.0; z[-1] = 0.0
    return x, z


def profil_sinus(maks_helling=25.0, nseg=96):
    """Sinusprofil med gitt stoerste helling (grader)."""
    x = np.linspace(0.0, 1.0, nseg + 1)
    a = math.tan(math.radians(maks_helling)) / (2 * math.pi)
    z = a * (1.0 - np.cos(2 * math.pi * x))
    return x, z


def profil_ru(sigma_helling=12.0, nmodar=12, nseg=256, froe=7):
    """Tilfeldig glatt 1D-profil (einvegsdiffusor / matt flate i tverrsnitt).
    Gaussisk hellingsfordeling med standardavvik sigma_helling (grader)."""
    rng = np.random.default_rng(froe)
    x = np.linspace(0.0, 1.0, nseg + 1)
    z = np.zeros_like(x)
    for k in range(3, 3 + nmodar):
        z += rng.normal() / k * np.cos(2 * math.pi * k * x + rng.uniform(0, 2 * math.pi))
    dz = np.diff(z) / np.diff(x)
    z *= math.tan(math.radians(sigma_helling)) / dz.std()
    z -= z.min()
    z[-1] = z[0]
    return x, z


# --------------------------------------------------------------------------
# Kjernen: sporing av ein straale med forgreining
# --------------------------------------------------------------------------

@njit(cache=True)
def _treff_poly(px, pz, x, z, ux, uz, tlim, tmin):
    """Naeraste treff mellom straalen og den periodiske polylinja (periode 1).
    Returnerer (t, segment). segment = -1: ingen treff foer tlim. -2: gav opp."""
    N = px.shape[0] - 1
    k = math.floor(x)
    ncelle = 0
    while ncelle < 20000:
        tbest = 1e300
        ibest = -1
        for i in range(N):
            ex = px[i + 1] - px[i]
            ez = pz[i + 1] - pz[i]
            den = ux * ez - uz * ex
            if den == 0.0:
                continue
            rx = px[i] + k - x
            rz = pz[i] - z
            t = (rx * ez - rz * ex) / den
            if t <= tmin or t >= tbest:
                continue
            s = (rx * uz - rz * ux) / den
            if s >= -1e-12 and s <= 1.0 + 1e-12:
                tbest = t
                ibest = i
        if ibest >= 0:
            if tbest <= tlim:
                return tbest, ibest
            return -1.0, -1
        if ux > 0.0:
            k += 1
            tc = (k - x) / ux
        elif ux < 0.0:
            tc = (k - x) / ux
            k -= 1
        else:
            return -1.0, -1
        if tc > tlim:
            return -1.0, -1
        ncelle += 1
    return -2.0, -2


@njit(cache=True)
def _spor(px, pz, zmax, t_sub, n_res, n_sub, skeiv, x0, fra_topp, sin_a,
          wmin, st, ut, maxhend):
    """Spor ein straale gjennom arket med alle greiner.
    Geometri: z = 0 er botnen av strukturlaget. Strukturflata z = pz(x) > 0,
    luft over. Baerelag mellom z = -t_sub og 0, luft under.
    fra_topp: straalen kjem inn fraa struktursida (retning (sin a, -cos a)),
    elles fraa den flate sida (retning (sin a, +cos a)).
    ut[k] = (side, vinkel_grad, ws, wp): side 0 = ut paa flat side, 1 = ut paa
    struktursida. Vinkelen er rekna fraa normalen paa den sida, mot +x.
    Returnerer (tal utstraalar, tapt vekt, tal hendingar)."""
    m_luft = math.sqrt(1.0 - skeiv * skeiv)
    m_res = math.sqrt(n_res * n_res - skeiv * skeiv)
    m_sub = math.sqrt(n_sub * n_sub - skeiv * skeiv)
    cos_a = math.sqrt(1.0 - sin_a * sin_a)
    M = st.shape[0]
    maxut = ut.shape[0]
    tmin = 1e-10
    if fra_topp:
        st[0, 0] = x0; st[0, 1] = zmax * (1.0 + 1e-9) + 1e-9
        st[0, 2] = sin_a; st[0, 3] = -cos_a; st[0, 4] = 3.0
    else:
        st[0, 0] = x0; st[0, 1] = -t_sub - 1e-9
        st[0, 2] = sin_a; st[0, 3] = cos_a; st[0, 4] = 0.0
    st[0, 5] = 1.0; st[0, 6] = 1.0
    sp = 1
    nut = 0
    tapt = 0.0
    nhend = 0
    while sp > 0:
        sp -= 1
        x = st[sp, 0]; z = st[sp, 1]; ux = st[sp, 2]; uz = st[sp, 3]
        med = int(st[sp, 4]); ws = st[sp, 5]; wp = st[sp, 6]
        while True:
            nhend += 1
            if nhend > maxhend:
                tapt += 0.5 * (ws + wp)
                break
            slag = -1
            t = 0.0
            iseg = -1
            if med == 0:
                if uz <= 0.0:
                    if nut < maxut:
                        ut[nut, 0] = 0.0
                        ut[nut, 1] = math.degrees(math.atan2(ux, -uz))
                        ut[nut, 2] = ws; ut[nut, 3] = wp
                        nut += 1
                    else:
                        tapt += 0.5 * (ws + wp)
                    break
                t = (-t_sub - z) / uz
                slag = 0
            elif med == 1:
                if uz > 0.0:
                    t = (0.0 - z) / uz
                    slag = 1
                else:
                    t = (-t_sub - z) / uz
                    slag = 0
            elif med == 2:
                tlim = 1e300
                if uz < 0.0:
                    tlim = (0.0 - z) / uz
                t, iseg = _treff_poly(px, pz, x, z, ux, uz, tlim, tmin)
                if iseg >= 0:
                    slag = 2
                elif uz < 0.0 and iseg == -1:
                    t = tlim
                    slag = 1
                else:
                    tapt += 0.5 * (ws + wp)
                    break
            else:
                tlim = 1e300
                if uz > 0.0:
                    if z >= zmax:
                        tlim = 0.0
                    else:
                        tlim = (zmax - z) / uz
                if tlim > 0.0:
                    t, iseg = _treff_poly(px, pz, x, z, ux, uz, tlim, tmin)
                else:
                    iseg = -1
                if iseg >= 0:
                    slag = 2
                elif uz > 0.0 and iseg == -1:
                    if nut < maxut:
                        ut[nut, 0] = 1.0
                        ut[nut, 1] = math.degrees(math.atan2(ux, uz))
                        ut[nut, 2] = ws; ut[nut, 3] = wp
                        nut += 1
                    else:
                        tapt += 0.5 * (ws + wp)
                    break
                else:
                    tapt += 0.5 * (ws + wp)
                    break
            # flytt til treffpunktet
            x = x + ux * t
            z = z + uz * t
            x = x - math.floor(x)
            # normal (peikar opp) og media over/under flata
            if slag == 0:
                Nx = 0.0; Nz = 1.0
                z = -t_sub
                n_o = n_sub; m_o = m_sub; med_o = 1
                n_u = 1.0; m_u = m_luft; med_u = 0
            elif slag == 1:
                Nx = 0.0; Nz = 1.0
                z = 0.0
                n_o = n_res; m_o = m_res; med_o = 2
                n_u = n_sub; m_u = m_sub; med_u = 1
            else:
                ex = px[iseg + 1] - px[iseg]
                ez = pz[iseg + 1] - pz[iseg]
                ln = math.sqrt(ex * ex + ez * ez)
                Nx = -ez / ln; Nz = ex / ln
                n_o = 1.0; m_o = m_luft; med_o = 3
                n_u = n_res; m_u = m_res; med_u = 2
            udn = ux * Nx + uz * Nz
            if udn < 0.0:       # kjem ovanfraa
                n1 = n_o; m1 = m_o; n2 = n_u; m2 = m_u
                med1 = med_o; med2 = med_u
                Nix = Nx; Niz = Nz
            else:               # kjem nedanfraa
                n1 = n_u; m1 = m_u; n2 = n_o; m2 = m_o
                med1 = med_u; med2 = med_o
                Nix = -Nx; Niz = -Nz
            ci = abs(udn)
            if ci > 1.0:
                ci = 1.0
            eta = m1 / m2
            st2 = eta * eta * (1.0 - ci * ci)
            rx = ux - 2.0 * udn * Nx
            rz = uz - 2.0 * udn * Nz
            if st2 >= 1.0:      # totalrefleksjon
                ux = rx; uz = rz
                med = med1
                continue
            ct = math.sqrt(1.0 - st2)
            c1 = m1 * ci / n1       # sann cos(innfallsvinkel)
            c2 = m2 * ct / n2       # sann cos(brytingsvinkel)
            rs = (n1 * c1 - n2 * c2) / (n1 * c1 + n2 * c2)
            rp = (n2 * c1 - n1 * c2) / (n2 * c1 + n1 * c2)
            Rs = rs * rs
            Rp = rp * rp
            if skeiv != 0.0:
                Rs = 0.5 * (Rs + Rp)
                Rp = Rs
            tx = eta * ux + (eta * ci - ct) * Nix
            tz = eta * uz + (eta * ci - ct) * Niz
            tn = math.sqrt(tx * tx + tz * tz)
            tx /= tn; tz /= tn
            wrs = ws * Rs
            wrp = wp * Rp
            if 0.5 * (wrs + wrp) > wmin and sp < M:
                st[sp, 0] = x; st[sp, 1] = z; st[sp, 2] = rx; st[sp, 3] = rz
                st[sp, 4] = float(med1); st[sp, 5] = wrs; st[sp, 6] = wrp
                sp += 1
            else:
                tapt += 0.5 * (wrs + wrp)
            ws = ws * (1.0 - Rs)
            wp = wp * (1.0 - Rp)
            ux = tx; uz = tz
            med = med2
            if 0.5 * (ws + wp) <= wmin:
                tapt += 0.5 * (ws + wp)
                break
    return nut, tapt, nhend


@njit(parallel=True, cache=True)
def _kjerne(px, pz, zmax, t_sub, t_jit, n_res, n_sub, skeiv, fra_topp,
            alfa, npos, wmin, nb):
    """Vinkelkjerne. T[ia, ib]: del av ein jamn straalebunt med innfallsvinkel
    alfa[ia] som kjem ut paa andre sida i vinkelboks ib (boksar paa 180/nb grader
    fraa -90 til 90). R: det same for det som kjem attende paa innfallssida.
    L: tapt (avkorta) del."""
    na = alfa.shape[0]
    T = np.zeros((na, nb))
    R = np.zeros((na, nb))
    L = np.zeros(na)
    for ia in prange(na):
        st = np.empty((400, 7))
        ut = np.empty((4000, 4))
        sin_a = math.sin(math.radians(alfa[ia]))
        for ip in range(npos):
            x0 = (ip + 0.5) / npos
            ts = t_sub + t_jit * ((ip * 0.6180339887498949) % 1.0)
            nut, tapt, nh = _spor(px, pz, zmax, ts, n_res, n_sub, skeiv, x0,
                                  fra_topp, sin_a, wmin, st, ut, 200000)
            L[ia] += tapt
            for k in range(nut):
                w = 0.5 * (ut[k, 2] + ut[k, 3])
                ib = int((ut[k, 1] + 90.0) / 180.0 * nb)
                if ib < 0:
                    ib = 0
                if ib >= nb:
                    ib = nb - 1
                gjennom = (ut[k, 0] == 0.0) == fra_topp
                if gjennom:
                    T[ia, ib] += w
                else:
                    R[ia, ib] += w
        for ib in range(nb):
            T[ia, ib] /= npos
            R[ia, ib] /= npos
        L[ia] /= npos
    return T, R, L


def spor_liste(profil, n_res, n_sub, alfa_grad, x0, fra_topp=True, t_sub=3.0,
               skeiv=0.0, wmin=1e-14, land=0.05, maxut=4000, maxhend=200000):
    """Ein straale: liste av (side, vinkel, ws, wp) og tapt vekt. For kontroll."""
    px, pz = profil
    pz = np.ascontiguousarray(pz + land)
    px = np.ascontiguousarray(px)
    st = np.empty((400, 7)); ut = np.empty((maxut, 4))
    nut, tapt, nh = _spor(px, pz, float(pz.max()), t_sub, n_res, n_sub, skeiv,
                          x0, fra_topp, math.sin(math.radians(alfa_grad)), wmin, st, ut, maxhend)
    return ut[:nut].copy(), tapt


def kjerne(profil, n_res, n_sub, alfa, fra_topp, npos=600, nb=720, skeiv=0.0,
           wmin=1e-5, t_sub=3.0, t_jit=2.0, land=0.05):
    """Sjaa _kjerne. profil = (x, z) over ein periode. t_sub: tjukn paa
    baerelaget i periodar; t_jit: straale for straale varierer tjukna over
    t_jit periodar (verkelege ark har ikkje fast fase mellom side og side)."""
    px, pz = profil
    pz = np.ascontiguousarray(pz + land, dtype=np.float64)
    px = np.ascontiguousarray(px, dtype=np.float64)
    return _kjerne(px, pz, float(pz.max()), float(t_sub), float(t_jit),
                   float(n_res), float(n_sub), float(skeiv), bool(fra_topp),
                   np.ascontiguousarray(alfa, dtype=np.float64), int(npos),
                   float(wmin), int(nb))


# --------------------------------------------------------------------------
# Kandidatar
# --------------------------------------------------------------------------
# PROFILAR: det som faktisk blir spora. KANDIDATAR: kva profil kvar hypotese
# bruker og korleis kjernen blir brukt i biletet.
# modus "1d": kjernen verkar berre loddrett (lineaer struktur, vassrette ryggar).
# modus "2d": same kjerne i baae retningar (separabel tilnaerming for
#   isotrope strukturar, ANTAKING). modus "kryss": to prismefilmar i kryss.
# gauss2d: isotrop tilleggsspreiing (sigma i grader). faktor: transmisjonsfaktor.

def profilar():
    P = {}
    P["prisme90"] = profil_prisme(90.0)
    P["prisme90_r08"] = profil_prisme(90.0, r_topp=0.08, nbue=64)
    P["prisme90_r20"] = profil_prisme(90.0, r_topp=0.20, nbue=64)
    P["prisme80"] = profil_prisme(80.0)
    P["prisme100"] = profil_prisme(100.0)
    P["prisme110"] = profil_prisme(110.0)
    P["prisme90_ujamn"] = profil_prisme_ujamn(90.0)
    P["linse_R06"] = profil_linse(0.6)
    P["linse_R10"] = profil_linse(1.0)
    P["ru12"] = profil_ru(12.0)
    P["flat"] = profil_flat()
    return P


def kandidatar():
    K = {}
    K["a_prisme90"] = dict(tekst="(a) prisme 90, skarp", profil="prisme90", modus="1d")
    K["b_prisme90_r08"] = dict(tekst="(b) prisme 90, runda topp r=0,08p", profil="prisme90_r08", modus="1d")
    K["b_prisme90_r20"] = dict(tekst="(b) prisme 90, runda topp r=0,20p", profil="prisme90_r20", modus="1d")
    K["b_prisme80"] = dict(tekst="(b) prisme 80", profil="prisme80", modus="1d")
    K["b_prisme100"] = dict(tekst="(b) prisme 100", profil="prisme100", modus="1d")
    K["b_prisme110"] = dict(tekst="(b) prisme 110", profil="prisme110", modus="1d")
    K["b_prisme90_ujamn"] = dict(tekst="(b) prisme 90, ujamn hoegd", profil="prisme90_ujamn", modus="1d")
    K["c_linse_R06"] = dict(tekst="(c) lentikulaer R=0,6p", profil="linse_R06", modus="1d")
    K["c_linse_R10"] = dict(tekst="(c) lentikulaer R=1,0p", profil="linse_R10", modus="1d")
    K["d_einveg"] = dict(tekst="(d) einvegsdiffusor, sigma 12", profil="ru12", modus="1d")
    K["e_diffusor"] = dict(tekst="(e) vanleg diffusor (2D), sigma 12", profil="ru12", modus="2d")
    K["f_polarisator"] = dict(tekst="(f) refl. polarisator (plan, 50 %)", profil="flat", modus="1d", faktor=0.5)
    K["f_polarisator_matt"] = dict(tekst="(f) refl. polarisator + matt lag sigma 4", profil="flat", modus="1d", faktor=0.5, gauss2d=4.0)
    K["g_mikrolinse"] = dict(tekst="(g) mikrolinsefilm (2D) R=0,6p", profil="linse_R06", modus="2d")
    K["h_prisme90_matt"] = dict(tekst="(h) prisme 90 + matt bakside sigma 3", profil="prisme90", modus="1d", gauss2d=3.0)
    K["h_prisme_kryss"] = dict(tekst="(h) to prismefilmar i kryss", profil="prisme90", modus="kryss")
    return K


ALFA = np.arange(-89.0, 89.01, 0.25)    # innfallsvinklar for kjernane
DALFA = 0.25
NB = 720                                 # utvinkelboksar (0,25 grader)
BETA = (np.arange(NB) + 0.5) * 180.0 / NB - 90.0


def _npos_for(profilnamn):
    return 250 if profilnamn.startswith("ru") else 400


def kjerne_spektral(profilnamn, side, npos=None, tving=False, skeiv=0.0, nd=ND_HARPIKS, stille=True):
    """Kjernar for alle 16 bolgjelengder. side = "kamera" (strukturen vender
    mot kamera) eller "vindauge" (strukturen vender mot vindauget).
    Kamerastraalen blir spora bakover (fraa kamera ut i scena).
    Returnerer T, R med form (16, na, NB), float32. Mellomlagra i _cache."""
    os.makedirs(CACHE, exist_ok=True)
    if npos is None:
        npos = _npos_for(profilnamn)
    tag = "%s_%s_%d_s%03d_n%03d" % (profilnamn, side, npos, int(round(skeiv * 100)), int(round(nd * 100)))
    f = os.path.join(CACHE, tag + ".npz")
    if os.path.exists(f) and not tving:
        d = np.load(f)
        return d["T"], d["R"]
    prof = profilar()[profilnamn]
    T = np.zeros((len(LAM), len(ALFA), NB), dtype=np.float32)
    R = np.zeros_like(T)
    t0 = time.time()
    for il, lam in enumerate(LAM):
        t, r, l = kjerne(prof, float(n_harpiks(lam, nd)), float(n_pet(lam)),
                         ALFA, fra_topp=(side == "kamera"), npos=npos, nb=NB, skeiv=skeiv)
        T[il] = t; R[il] = r
    if not stille:
        print("  kjerne %s %s: %.0f s" % (profilnamn, side, time.time() - t0), flush=True)
    np.savez_compressed(f, T=T, R=R)
    return T, R


def alle_kjernar():
    for namn in profilar():
        for side in ("kamera", "vindauge"):
            if namn == "flat" and side == "vindauge":
                continue
            kjerne_spektral(namn, side, stille=False)


# --------------------------------------------------------------------------
# Farge: spektrum -> sRGB
# --------------------------------------------------------------------------
# kjent fraa kjelde: Wyman, Sloan, Shirley (2013), "Simple Analytic
# Approximations to the CIE XYZ Color Matching Functions", JCGT 2(2).
# Stykkevis gaussisk tilpassing til CIE 1931 2-graders observator.

def cie_xyz(lam):
    lam = np.asarray(lam, dtype=float)
    def g(mu, s1, s2):
        t = (lam - mu) * np.where(lam < mu, s1, s2)
        return np.exp(-0.5 * t * t)
    x = 0.362 * g(442.0, 0.0624, 0.0374) + 1.056 * g(599.8, 0.0264, 0.0323) - 0.065 * g(501.1, 0.0490, 0.0382)
    y = 0.821 * g(568.8, 0.0213, 0.0247) + 0.286 * g(530.9, 0.0613, 0.0322)
    z = 1.217 * g(437.0, 0.0845, 0.0278) + 0.681 * g(459.0, 0.0385, 0.0725)
    return x, y, z


# kjent fraa kjelde: IEC 61966-2-1 (sRGB), XYZ (D65) -> lineaer sRGB
M_XYZ_RGB = np.array([[3.2406, -1.5372, -0.4986],
                      [-0.9689, 1.8758, 0.0415],
                      [0.0557, -0.2040, 1.0570]])


def planck(lam_nm, T):
    l = np.asarray(lam_nm, dtype=float) * 1e-9
    return 1.0 / (l ** 5 * (np.exp(1.4388e-2 / (l * T)) - 1.0))


_X, _Y, _Z = cie_xyz(LAM)
_D65 = planck(LAM, 6500.0)                  # ANTAKING: dagslys = svart lekam 6500 K
_D65 = _D65 / np.sum(_D65 * _Y)
# kvitpunkt: 6500 K-spekteret skal gje R = G = B (liten korreksjon fordi Planck 6500 K ikkje er D65)
_KVIT = M_XYZ_RGB @ np.array([np.sum(_D65 * _X), np.sum(_D65 * _Y), np.sum(_D65 * _Z)])


def spektrum_til_srgb(S, eksponering=1.0):
    """S[..., 16] spektral radians (same nett som LAM) -> sRGB 0..1."""
    X = np.tensordot(S, _X, axes=([-1], [0]))
    Y = np.tensordot(S, _Y, axes=([-1], [0]))
    Z = np.tensordot(S, _Z, axes=([-1], [0]))
    xyz = np.stack([X, Y, Z], axis=-1)
    rgb = xyz @ M_XYZ_RGB.T / _KVIT
    rgb = rgb * eksponering
    # mjuk skulder over 0,7 i staden for hard klipping
    rgb = np.clip(rgb, 0.0, None)
    hog = rgb > 0.7
    rgb = np.where(hog, 0.7 + 0.3 * (1.0 - np.exp(-(rgb - 0.7) / 0.3)), rgb)
    rgb = np.clip(rgb, 0.0, 1.0)
    return np.where(rgb <= 0.0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - 0.055)


def norm_y(S):
    """Skaler eit spektrum til luminans 1."""
    return S / np.sum(S * _Y)


# --------------------------------------------------------------------------
# Prosedyrescene (ANTAKING, laga for aa likne utsynet i fotoa)
# --------------------------------------------------------------------------
EL = BETA.copy()                         # sann elevasjon, -90..90 i 0,25 grader
AZ = np.arange(-30.0, 30.01, 0.2)        # asimut


def scene(snokant=False, froe=3):
    """Spektral radians L[el, az, lam]. Luminansar relativt til himmelen ved
    horisonten (= 1). Alle tal ANTAKING.
    - himmel: bleikblaa hoegt oppe, lysare og kvitare mot horisonten
    - solbelyste bygningstoppar (varme) ned til skuggelinja
    - skuggelagde fasadar, lagt bygg, snoe i skugge med moerke flekker
    - snokant=True: lys snoekant like under vindauget (-66 til -76 grader)
      og moerk karm under."""
    rng = np.random.default_rng(froe)
    nel, naz = len(EL), len(AZ)
    L = np.zeros((nel, naz, len(LAM)))
    dag = norm_y(planck(LAM, 6500.0))
    sol = norm_y(planck(LAM, 2900.0))                    # laag sol
    blaa = norm_y(planck(LAM, 6500.0) * (550.0 / LAM) ** 3.0)
    snoskugge = norm_y(planck(LAM, 6500.0) * (550.0 / LAM) ** 1.6)
    gul = np.clip(0.35 + 0.55 / (1 + np.exp(-(LAM - 520.0) / 25.0)), 0, 1)   # gul puss
    teglraud = np.clip(0.12 + 0.5 / (1 + np.exp(-(LAM - 590.0) / 20.0)), 0, 1)
    graa = np.ones_like(LAM) * 0.5
    # silhuett: blokker med ulik hoegd
    topp = np.zeros(naz)
    farge = np.zeros(naz, dtype=int)
    a = -30.0
    while a < 30.0:
        w = rng.uniform(2.0, 7.0)
        h = rng.choice([6.0, 8.5, 11.0, 13.0, 14.5, 16.0], p=[0.15, 0.2, 0.2, 0.2, 0.15, 0.1])
        c = rng.integers(0, 3)
        m = (AZ >= a) & (AZ < a + w)
        topp[m] = h; farge[m] = c
        a += w
        if rng.uniform() < 0.3:
            a += rng.uniform(0.5, 2.0)                  # glipe: laagare bygg bak
    topp[topp == 0] = 4.5
    # pipe og mast
    m = (AZ > -21.0) & (AZ < -20.2); topp[m] = 18.0; farge[m] = 2
    skugge = 10.0 + 0.04 * AZ                           # skuggelinja (sola kjem laagt fraa sida)
    for j in range(naz):
        az = AZ[j]
        for i in range(nel):
            el = EL[i]
            if el > topp[j]:
                wk = 1.0 - math.exp(-max(el, 0.0) / 22.0)       # 0 ved horisonten, 1 hoegt oppe
                lum = 0.72 + 0.28 * math.exp(-max(el, 0.0) / 14.0)
                L[i, j] = lum * ((1 - wk) * (0.55 * dag + 0.45 * blaa) + wk * blaa)
            elif el > 2.0:
                refl = (gul, teglraud, graa)[farge[j]]
                # vindaugsband: moerkare loddrette felt
                felt = 0.75 + 0.25 * math.cos(2 * math.pi * az / 0.9)
                if el > skugge[j]:
                    L[i, j] = 2.0 * felt * sol * refl / np.sum(sol * refl * _Y) * np.sum(refl * _Y * dag)
                else:
                    L[i, j] = 0.16 * felt * snoskugge * refl / 0.5
            elif el > -1.0:
                L[i, j] = 0.30 * dag                     # lys betongkant paa laagbygget
            elif el > -4.0:
                L[i, j] = 0.05 * dag                     # moerk sokkel
            else:
                L[i, j] = 0.42 * snoskugge               # snoe i skugge
    # moerke flekker i snoeen (asfalt, spor), skalert med perspektiv
    for k in range(260):
        e0 = -4.0 - 60.0 * rng.uniform() ** 1.3
        a0 = rng.uniform(-32, 32)
        se = 0.25 + 0.035 * abs(e0) * rng.uniform(0.5, 1.5)
        sa = se * rng.uniform(1.5, 5.0)
        d = np.exp(-0.5 * ((EL[:, None] - e0) / se) ** 2 - 0.5 * ((AZ[None, :] - a0) / sa) ** 2)
        m = EL < -4.0
        L[m] *= (1.0 - 0.75 * d[m])[..., None]
    if snokant:
        m = (EL <= -66.0) & (EL > -76.0)
        L[m] = 1.1 * dag
        L[EL <= -76.0] = 0.02 * dag
    return L


ROM = 0.035        # ANTAKING: radians i rommet bak kamera (det som blir spegla), relativt til himmelen


# --------------------------------------------------------------------------
# Syntetisk gjennomsyn
# --------------------------------------------------------------------------

APP = np.arange(-70.0, 70.01, 0.25)      # tilsynelatande elevasjon (kamerastraalen)


def _flytt_kjerne(Tl, helling):
    """Kjerne i verdsvinklar for eit ark som hallar. helling > 0: toppen
    lener seg bort fraa kamera (mot vindauget), dvs. normalen mot scena
    peikar `helling` grader nedover. Lokal vinkel = verdsvinkel + helling.
    Returnerer K[APP, EL] og indeksane inn i ALFA."""
    a_lok = APP + helling
    ia = np.round((a_lok - ALFA[0]) / DALFA).astype(int)
    gyldig = (ia >= 0) & (ia < len(ALFA))
    ia = np.clip(ia, 0, len(ALFA) - 1)
    K = Tl[ia] * gyldig[:, None]
    sk = int(round(helling / (180.0 / NB)))     # e_verd = b_lok - helling
    if sk != 0:
        K2 = np.zeros_like(K)
        if sk > 0:
            K2[:, :-sk] = K[:, sk:]
        else:
            K2[:, -sk:] = K[:, :sk]
        K = K2
    return K, ia, gyldig


def gjennomsyn(namn, side, L, helling=0.0, nd=ND_HARPIKS):
    """Spektralt bilete [APP, AZ, 16] av scena L sett gjennom kandidaten.
    Ryggane ligg vassrett. Kjernen verkar loddrett i kvar kolonne (straalar
    i loddrett plan, skeiv = 0), pluss tilleggsledd etter kandidaten sin modus."""
    from scipy.ndimage import convolve1d, gaussian_filter1d
    kand = kandidatar()[namn]
    T, R = kjerne_spektral(kand["profil"], side, nd=nd)
    faktor = kand.get("faktor", 1.0)
    modus = kand["modus"]
    nel, naz, nl = L.shape
    ut = np.zeros((len(APP), naz, nl))
    romspekter = norm_y(planck(LAM, 4500.0))
    steg_az = AZ[1] - AZ[0]
    i0 = int(np.argmin(np.abs(ALFA)))
    for il in range(nl):
        K, ia, gyldig = _flytt_kjerne(T[il].astype(np.float64), helling)
        bilete = K @ L[:, :, il]
        refl = R[il][ia].sum(axis=1) * gyldig
        if modus == "2d":
            # isotrop struktur: bruk kjernen ved normalt innfall som vassrett
            # spreiefunksjon (separabel tilnaerming, ANTAKING)
            k0 = T[il][i0].astype(np.float64)
            xs = np.arange(-45.0, 45.01, steg_az)
            ks = np.interp(xs, BETA, k0)
            ks = ks / ks.sum()
            bilete = convolve1d(bilete, ks, axis=1, mode="nearest")
        elif modus == "kryss":
            # film nummer to har loddrette ryggar: kopiar forskyvde vassrett.
            # Tilnaerming: kjernen ved normalt innfall brukt vassrett, scena
            # spegla utanfor biletkanten.
            k0 = T[il][i0].astype(np.float64)
            xs = np.arange(-58.0, 58.01, steg_az)
            ks = np.interp(xs, BETA, k0) * (steg_az / 0.25)
            bilete = convolve1d(bilete, ks, axis=1, mode="reflect")
        g = kand.get("gauss2d", 0.0)
        if g > 0:
            bilete = gaussian_filter1d(bilete, g / 0.25, axis=0, mode="nearest")
            bilete = gaussian_filter1d(bilete, g / steg_az, axis=1, mode="nearest")
        ut[:, :, il] = faktor * bilete + (faktor * refl[:, None] + (1.0 - faktor)) * ROM * romspekter[il]
    return ut


def direkte(L):
    """Scena utan ark, paa same nett som gjennomsynet."""
    ie = np.floor((APP + 90.0) / 0.25 + 1e-9).astype(int)
    return L[np.clip(ie, 0, len(EL) - 1)]


def til_bilete(S, eksponering=1.15, skala=1, tekst=None, merke=None):
    """Spektralt bilete -> PIL-bilete. merke: liste av (elevasjon, farge) som
    blir teikna som korte strekar i venstre kant."""
    from PIL import Image, ImageDraw
    rgb = spektrum_til_srgb(S, eksponering)[::-1]          # elevasjon opp
    im = Image.fromarray((rgb * 255 + 0.5).astype(np.uint8))
    if skala != 1:
        im = im.resize((int(im.width * skala), int(im.height * skala)), Image.BILINEAR)
    d = ImageDraw.Draw(im)
    if merke:
        for el, farge in merke:
            y = (APP[-1] - el) / (APP[-1] - APP[0]) * (im.height - 1)
            d.line([0, y, 14 * skala, y], fill=farge, width=max(1, int(skala)))
    if tekst:
        d.rectangle([0, 0, im.width, 13], fill=(0, 0, 0))
        d.text((3, 1), tekst, fill=(255, 255, 255))
    return im


def _skala_stripe(hogd, breidd=34):
    """Smal stripe med elevasjonsskala (kvar 10. grad)."""
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (breidd, hogd), (20, 20, 20))
    d = ImageDraw.Draw(im)
    for el in range(-70, 71, 10):
        y = (APP[-1] - el) / (APP[-1] - APP[0]) * (hogd - 1)
        d.line([breidd - 6, y, breidd, y], fill=(230, 230, 230))
        d.text((1, y - 5), "%+d" % el, fill=(230, 230, 230))
    return im


def bilete(helling=0.0):
    """Syntetiske gjennomsyn for alle kandidatar og begge orienteringar."""
    from PIL import Image
    os.makedirs(UT, exist_ok=True)
    L = scene(snokant=False)
    dir_im = til_bilete(direkte(L), tekst="scena utan ark")
    dir_im.save(os.path.join(UT, "scene_direkte.png"))
    K = kandidatar()
    for side in ("kamera", "vindauge"):
        panel = [dir_im]
        for namn, kand in K.items():
            if kand["profil"] == "flat" and side == "vindauge":
                S = gjennomsyn(namn, "kamera", L, helling)
            else:
                S = gjennomsyn(namn, side, L, helling)
            im = til_bilete(S, tekst=kand["tekst"])
            im.save(os.path.join(UT, "syn_%s_%s.png" % (namn, side)))
            panel.append(im)
        # oversynsark: 2 rader, elevasjonsskala til venstre i kvar rad
        n = len(panel)
        per_rad = (n + 1) // 2
        stripe = _skala_stripe(dir_im.height)
        w = dir_im.width + 4
        h = dir_im.height + 4
        ark = Image.new("RGB", (stripe.width + per_rad * w, 2 * h), (0, 0, 0))
        ark.paste(stripe, (0, 0)); ark.paste(stripe, (0, h))
        for i, pm in enumerate(panel):
            ark.paste(pm, (stripe.width + (i % per_rad) * w, (i // per_rad) * h))
        ark.save(os.path.join(UT, "oversyn_struktur_mot_%s.png" % side))
        print("lagra oversyn for struktur mot", side, flush=True)
    # dei beste kandidatane i stoerre format, med snoekant og helling
    Ls = scene(snokant=True)
    rad = [_skala_stripe(dir_im.height * 2), til_bilete(direkte(Ls), skala=2, tekst="scena utan ark (med snoekant under vindauget)")]
    for namn, side, hell, tekst in (
            ("a_prisme90", "kamera", 0.0, "(a) prisme 90, struktur mot kamera, loddrett"),
            ("a_prisme90", "kamera", 8.0, "(a) same, arket lener 8 grader mot vindauget"),
            ("b_prisme90_r08", "kamera", 0.0, "(b) runda topp r=0,08p, struktur mot kamera"),
            ("a_prisme90", "vindauge", 0.0, "(a) prisme 90, struktur mot vindauget")):
        S = gjennomsyn(namn, side, Ls, hell)
        n_g = float(n_harpiks(550.0))
        merke = None
        if side == "kamera":
            merke = [(prisme_tir_grense(n_g) - hell, (255, 0, 255)), (-45.0 - hell, (0, 255, 255))]
        rad.append(til_bilete(S, skala=2, tekst=tekst, merke=merke))
    w = sum(r.width + 6 for r in rad)
    ark = Image.new("RGB", (w, rad[1].height), (0, 0, 0))
    x = 0
    for r in rad:
        ark.paste(r, (x, 0)); x += r.width + 6
    ark.save(os.path.join(UT, "beste_kandidatar.png"))
    print("lagra beste_kandidatar.png", flush=True)


# --------------------------------------------------------------------------
# Avbildingskart: sann elevasjon -> tilsynelatande elevasjon
# --------------------------------------------------------------------------

def _klynger(vinklar, vekt, gap=1.0, minvekt=0.01):
    """Samanhengande grupper i eit histogram -> (tyngdepunkt, fraa, til, vekt)."""
    idx = np.nonzero(vekt > 1e-5)[0]
    ut = []
    if len(idx) == 0:
        return ut
    steg = vinklar[1] - vinklar[0]
    grupper = np.split(idx, np.nonzero(np.diff(idx) > gap / steg)[0] + 1)
    for g in grupper:
        w = float(vekt[g].sum())
        if w >= minvekt:
            ut.append((float((vinklar[g] * vekt[g]).sum() / w), float(vinklar[g].min() - steg / 2),
                       float(vinklar[g].max() + steg / 2), w))
    return ut


def kart():
    """1. Figurar: for kvar profil og orientering eit kart med sann elevasjon
       vassrett og tilsynelatande elevasjon loddrett (loddrett ark). Fargen er
       summen over dei 16 bolgjelengdene, saa dispersjon syner som fargekantar.
       2. kart.csv: lys fraa sann elevasjon t (kvar 5. grad, -70..70) spora
       framover gjennom arket; kvar grein med tilsynelatande elevasjon og del
       av innfallande fluks, for kvar av dei 16 bolgjelengdene."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(UT, exist_ok=True)
    P = profilar()
    grupper = (("kart_prisme.png", ["prisme90", "prisme90_r08", "prisme90_r20", "prisme80", "prisme100", "prisme110", "prisme90_ujamn"]),
               ("kart_andre.png", ["linse_R06", "linse_R10", "ru12", "flat"]))
    ja = np.nonzero((ALFA >= -70.0) & (ALFA <= 70.0))[0]
    jb = np.nonzero((BETA >= -70.0) & (BETA <= 70.0))[0]
    for fil, namn in grupper:
        fig, axs = plt.subplots(len(namn), 2, figsize=(9.0, 4.3 * len(namn)), squeeze=False)
        for i, pn in enumerate(namn):
            for j, side in enumerate(("kamera", "vindauge")):
                T, R = kjerne_spektral(pn, "kamera" if pn == "flat" else side)
                S = np.moveaxis(T[:, ja][:, :, jb].astype(np.float64), 0, -1)     # [app, sann, lam]
                S = S * _D65[None, None, :]          # kvitt lys: T = 1 gjev luminans 1
                rgb = spektrum_til_srgb(S, eksponering=3.0)
                ax = axs[i, j]
                ax.imshow(rgb, origin="lower", extent=[-70, 70, -70, 70], aspect="equal", interpolation="nearest")
                ax.plot([-70, 70], [-70, 70], color=(0.4, 0.4, 0.4), lw=0.5, ls=":")
                ax.set_title("%s, struktur mot %s" % (pn, side), fontsize=9)
                ax.set_xlabel("sann elevasjon (grader)", fontsize=8)
                ax.set_ylabel("tilsynelatande elevasjon (grader)", fontsize=8)
                ax.set_xticks(range(-60, 61, 20)); ax.set_yticks(range(-60, 61, 20))
                ax.tick_params(labelsize=7)
                ax.set_facecolor("black")
        fig.tight_layout()
        fig.savefig(os.path.join(UT, fil), dpi=110)
        plt.close(fig)
        print("lagra", fil, flush=True)
    # tabell, framover-sporing
    sann = np.arange(-70.0, 70.01, 5.0)
    linjer = ["profil;struktur_mot;bolgjelengd_nm;sann_elevasjon;tilsynelatande_elevasjon;fraa;til;del_av_fluks;sum_gjennom;sum_attende"]
    for pn in P:
        for side in ("kamera", "vindauge"):
            if pn == "flat" and side == "vindauge":
                continue
            npos = 600 if pn.startswith("ru") else 2000
            for lam in LAM:
                # lys fraa elevasjon t reiser nedover: innfallsvinkel -t paa
                # vindaugssida. Kjem ut mot kamera med vinkel b; kamera ser
                # det i elevasjon -b.
                t, r, l = kjerne(P[pn], float(n_harpiks(lam)), float(n_pet(lam)), -sann,
                                 fra_topp=(side != "kamera"), npos=npos, nb=NB, wmin=1e-5)
                for k, tv in enumerate(sann):
                    kl = _klynger(-BETA[::-1], t[k][::-1])
                    for c, a0, a1, w in kl:
                        linjer.append("%s;%s;%.0f;%+.0f;%+.2f;%+.2f;%+.2f;%.4f;%.4f;%.4f" % (
                            pn, side, lam, tv, c, a0, a1, w, t[k].sum(), r[k].sum()))
        print("  tabell:", pn, flush=True)
    with open(os.path.join(UT, "kart.csv"), "w", encoding="utf-8") as f:
        f.write("\n".join(linjer) + "\n")
    print("lagra kart.csv (%d linjer)" % len(linjer), flush=True)


# --------------------------------------------------------------------------
# Analytiske hjelpefunksjonar for prisme (handrekning)
# --------------------------------------------------------------------------

def prisme_fjern_flate(a_grad, n, topp=90.0):
    """Struktur mot kamera. Kamerastraale med vinkel a (grader, negativ =
    ned). Gjennom flata som vender bort fraa straalen (den oevre flata sett
    ovanfraa): sceneelevasjon b. NaN om flata ikkje er synleg."""
    fi = math.radians(90.0 - topp / 2.0)
    a = math.radians(a_grad)
    inn = fi - a
    if inn >= math.pi / 2 or inn <= -math.pi / 2:
        return float("nan")
    r = math.asin(math.sin(inn) / n)
    indre = fi - r
    s = n * math.sin(indre)
    if abs(s) >= 1:
        return float("nan")
    return math.degrees(math.asin(s))


def prisme_naer_flate(a_grad, n, topp=90.0):
    """Struktur mot kamera, flata som vender mot straalen. Returnerer
    sceneelevasjon (negativ = ned) eller NaN ved totalrefleksjon i baksida."""
    fi = math.radians(90.0 - topp / 2.0)
    a = math.radians(a_grad)
    inn = fi + a            # for a < 0: innfallsvinkel fi - |a|
    r = math.asin(math.sin(inn) / n)
    indre = fi - r          # vinkel nedover fraa normalen
    s = n * math.sin(indre)
    if abs(s) >= 1:
        return float("nan")
    return -math.degrees(math.asin(s))


def prisme_tir_grense(n, topp=90.0):
    """Struktur mot kamera: kameravinkelen (negativ) der den naere flata sitt
    bilete sluttar fordi straalen blir totalreflektert i den flate baksida."""
    fi = math.radians(90.0 - topp / 2.0)
    tc = math.asin(1.0 / n)
    r = fi - tc
    inn = math.asin(n * math.sin(r))
    return -(math.degrees(fi) - math.degrees(inn))


def prisme_mot_vindauge(a_grad, n, topp=90.0):
    """Flat side mot kamera. Kamerastraale med vinkel a < 0 (ned). Gjennom
    flata som hallar nedover: sceneelevasjon b, eller NaN ved totalrefleksjon."""
    fi = math.radians(90.0 - topp / 2.0)
    g = math.asin(math.sin(math.radians(abs(a_grad))) / n)
    inn = fi - g
    s = n * math.sin(inn)
    if abs(s) >= 1:
        return float("nan")
    return math.degrees(math.asin(s)) - math.degrees(fi)


# --------------------------------------------------------------------------
# Kontrollar
# --------------------------------------------------------------------------

def test():
    ok = True
    print("== KONTROLLAR ==")
    # 0. indeksar
    print("n_d  PC %.4f  PMMA %.4f  PS %.4f   harpiks(450/550/650) %.4f %.4f %.4f" % (
        n_pc(587.6), n_pmma(587.6), n_ps(587.6), n_harpiks(450), n_harpiks(550), n_harpiks(650)))
    nF, nd, nC = n_harpiks(486.1), n_harpiks(587.6), n_harpiks(656.3)
    print("Abbe-tal harpiks: %.1f" % ((nd - 1) / (nF - nC)))

    # 1. Fresnel: R + T = 1 med T rekna uavhengig fraa amplitudekoeffisientane
    verst = 0.0
    for n1, n2 in ((1.0, 1.59), (1.59, 1.0), (1.59, 1.65), (1.65, 1.0)):
        for vi in np.linspace(0.0, 89.9, 400):
            ci = math.cos(math.radians(vi)); si = math.sin(math.radians(vi))
            stt = n1 / n2 * si
            if stt >= 1:
                continue
            ct = math.sqrt(1 - stt * stt)
            rs = (n1 * ci - n2 * ct) / (n1 * ci + n2 * ct)
            rp = (n2 * ci - n1 * ct) / (n2 * ci + n1 * ct)
            ts = 2 * n1 * ci / (n1 * ci + n2 * ct)
            tp = 2 * n1 * ci / (n2 * ci + n1 * ct)
            Ts = n2 * ct / (n1 * ci) * ts * ts
            Tp = n2 * ct / (n1 * ci) * tp * tp
            verst = max(verst, abs(rs * rs + Ts - 1), abs(rp * rp + Tp - 1))
    print("1. Fresnel R + T - 1, stoerste avvik: %.2e" % verst); ok &= verst < 1e-12

    # 2. energi: sum ut + avkorta = 1 for mange straalar og profilar
    verst = 0.0; storst_tap = 0.0
    rng = np.random.default_rng(1)
    tap = []
    for namn in ("prisme90", "prisme90_r08", "prisme110", "linse_R06", "ru12"):
        prof = profilar()[namn]
        for fra_topp in (True, False):
            for _ in range(100):
                a = rng.uniform(-85, 85); x0 = rng.uniform(0, 1)
                lam = rng.uniform(400, 700)
                ut, tapt = spor_liste(prof, float(n_harpiks(lam)), float(n_pet(lam)), a, x0, fra_topp,
                                      wmin=1e-7, maxut=400000, maxhend=20000000)
                s = 0.5 * (ut[:, 2] + ut[:, 3]).sum()
                verst = max(verst, abs(s + tapt - 1.0)); tap.append(tapt)
    tap = np.array(tap)
    print("2. energi, 1000 straalar: |reflektert + transmittert + avkorta - 1| stoerst %.2e" % verst)
    print("   avkorta del (greiner under 1e-7): median %.1e, snitt %.1e, stoerst %.1e" % (np.median(tap), tap.mean(), tap.max()))
    ok &= verst < 1e-12 and tap.mean() < 1e-4

    # 3. planparallell plate: ingen avbøying
    verst = 0.0
    for a in np.linspace(-85, 85, 35):
        ut, tapt = spor_liste(profil_flat(), 1.59, 1.65, a, 0.37, True, wmin=1e-13)
        for side, v, ws, wp in ut:
            if side == 0.0:
                verst = max(verst, abs(v - a))
            else:
                verst = max(verst, abs(v - a))      # spegla: same vinkel maalt fraa sin normal
    print("3. plate: stoerste retningsavvik %.2e grader" % verst); ok &= verst < 1e-9
    # plate: transmisjon mot Airy-sum (inkoherent) for s og p
    a = 40.0; n = 1.59
    ut, tapt = spor_liste(profil_flat(), n, n, a, 0.2, True, wmin=1e-15)
    ci = math.cos(math.radians(a)); ct = math.sqrt(1 - (math.sin(math.radians(a)) / n) ** 2)
    Rs = ((ci - n * ct) / (ci + n * ct)) ** 2; Rp = ((n * ci - ct) / (n * ci + ct)) ** 2
    Tfas = 0.5 * ((1 - Rs) / (1 + Rs) + (1 - Rp) / (1 + Rp))
    Tsp = 0.5 * (ut[ut[:, 0] == 0.0][:, 2] + ut[ut[:, 0] == 0.0][:, 3]).sum()
    print("   plate 40 grader: T spora %.12f, fasit (1-R)/(1+R) %.12f" % (Tsp, Tfas)); ok &= abs(Tsp - Tfas) < 1e-10

    # 4. handrekna prisme: struktur mot kamera, normalt innfall, n = 1,59, n_sub = n
    n = 1.59
    r = math.asin(math.sin(math.radians(45)) / n)
    indre = math.radians(45) - r
    b_fasit = math.degrees(math.asin(n * math.sin(indre)))
    ci = math.cos(math.radians(45)); ct = math.cos(r)
    Rs1 = ((ci - n * ct) / (ci + n * ct)) ** 2; Rp1 = ((n * ci - ct) / (n * ci + ct)) ** 2
    ci2 = math.cos(indre); ct2 = math.cos(math.radians(b_fasit))
    Rs2 = ((n * ci2 - ct2) / (n * ci2 + ct2)) ** 2; Rp2 = ((ci2 - n * ct2) / (ci2 + n * ct2)) ** 2
    w_fasit = 0.5 * ((1 - Rs1) * (1 - Rs2) + (1 - Rp1) * (1 - Rp2))
    ut, tapt = spor_liste(profil_prisme(90.0), n, n, 0.0, 0.3, True, wmin=1e-14)
    # x0 = 0,3 treff venstre flate (normal mot -x, opp): straalen blir boeygd mot +x? finn hovudgreina
    hoved = ut[np.argmax(0.5 * (ut[:, 2] + ut[:, 3]))]
    print("4. prisme 90, n 1,59, normalt innfall: vinkel spora %.10f, handrekna %.10f (avvik %.1e)" % (
        abs(hoved[1]), b_fasit, abs(abs(hoved[1]) - b_fasit)))
    print("   vekt spora %.12f, handrekna %.12f" % (0.5 * (hoved[2] + hoved[3]), w_fasit))
    ok &= abs(abs(hoved[1]) - b_fasit) < 1e-9 and abs(0.5 * (hoved[2] + hoved[3]) - w_fasit) < 1e-9
    # forteikn: kva flate gjev kva retning
    ut_v, _ = spor_liste(profil_prisme(90.0), n, n, 0.0, 0.3, True, wmin=1e-3)
    ut_h, _ = spor_liste(profil_prisme(90.0), n, n, 0.0, 0.7, True, wmin=1e-3)
    hv = ut_v[np.argmax(ut_v[:, 2])][1]; hh = ut_h[np.argmax(ut_h[:, 2])][1]
    print("   flata med normal mot -x gjev b = %+.3f, flata med normal mot +x gjev b = %+.3f" % (hv, hh))
    # 4b. flat side mot kamera, a = -25: handrekna
    b2 = prisme_mot_vindauge(-25.0, n)
    ut, _ = spor_liste(profil_prisme(90.0), n, n, -25.0, 0.3, False, wmin=1e-14)
    gj = ut[ut[:, 0] == 1.0]
    hoved = gj[np.argmax(0.5 * (gj[:, 2] + gj[:, 3]))]
    print("4b. flat side inn, a = -25: spora %+.10f, handrekna %+.10f" % (hoved[1], b2))
    ok &= abs(hoved[1] - b2) < 1e-9
    # 4c. flat side inn, normalt innfall: alt kjem attende (retrorefleksjon)
    t, rr, l = kjerne(profil_prisme(90.0), n, n, np.array([0.0]), False, npos=400, wmin=1e-9)
    print("4c. flat side inn, normalt innfall: T = %.2e, R = %.9f (ventar T = 0)" % (t.sum(), rr.sum()))
    ok &= t.sum() < 1e-9
    # 4d. fjern flate ved skraatt innfall mot analytisk formel
    for a in (-20.0, -30.0, -40.0):
        bf = prisme_fjern_flate(a, n)
        ut, _ = spor_liste(profil_prisme(90.0), n, n, a, 0.45, True, wmin=1e-14)
        gj = ut[(ut[:, 0] == 0.0) & (ut[:, 1] > 0)]
        hoved = gj[np.argmax(0.5 * (gj[:, 2] + gj[:, 3]))]
        print("4d. struktur inn, a = %+.0f: fjern flate spora %+.10f, handrekna %+.10f" % (a, hoved[1], bf))
        ok &= abs(hoved[1] - bf) < 1e-9

    # 5. blaatt blir avboeygd meir enn raudt
    res = []
    for lam in (450.0, 550.0, 650.0):
        nn = float(n_harpiks(lam))
        ut, _ = spor_liste(profil_prisme(90.0), nn, float(n_pet(lam)), 0.0, 0.3, True, wmin=1e-6)
        hoved = ut[np.argmax(0.5 * (ut[:, 2] + ut[:, 3]))]
        res.append(abs(hoved[1]))
    print("5. avboeying ved normalt innfall: 450 nm %.4f, 550 nm %.4f, 650 nm %.4f grader" % tuple(res))
    ok &= res[0] > res[1] > res[2]

    # 6. etendue: integral T(a) cos a da er likt i begge retningar (resiprositet)
    al = np.arange(-89.75, 90, 0.5)
    t1, _, _ = kjerne(profil_prisme(90.0, r_topp=0.08), 1.59, 1.65, al, True, npos=400, wmin=1e-7)
    t2, _, _ = kjerne(profil_prisme(90.0, r_topp=0.08), 1.59, 1.65, al, False, npos=400, wmin=1e-7)
    c = np.cos(np.radians(al))
    i1 = (t1.sum(axis=1) * c).sum(); i2 = (t2.sum(axis=1) * c).sum()
    print("6. resiprositet: sum T cos(a) struktur inn %.5f, flat side inn %.5f (avvik %.2e relativt)" % (i1, i2, abs(i1 - i2) / i1))
    ok &= abs(i1 - i2) / i1 < 3e-3
    print("ALLE KONTROLLAR OK" if ok else "FEIL I KONTROLLANE")
    return ok


# --------------------------------------------------------------------------
# Rekna tal til dokumentet
# --------------------------------------------------------------------------

def _a_for_e(e, n, topp):
    """Kameravinkelen der den fjerne flata syner sceneelevasjon e (struktur mot kamera)."""
    a = np.arange(-(topp / 2.0) + 0.01, 40.0, 0.01)
    ee = np.array([prisme_fjern_flate(x, n, topp) for x in a])
    m = np.isfinite(ee)
    if m.sum() < 2 or e < ee[m].min() or e > ee[m].max():
        return float("nan")
    return float(np.interp(e, ee[m], a[m]))


def _kantar(I, minsprang=0.04):
    """Finn kopiar av ein kant i eit bileteprofil I(APP): toppar i |dI/da|.
    Returnerer liste (elevasjon, sprang, breidd 10-90 i grader)."""
    d = np.diff(I)
    a = 0.5 * (APP[1:] + APP[:-1])
    ut = []
    aktiv = np.abs(d) > 0.002
    i = 0
    while i < len(d):
        if aktiv[i]:
            j = i
            while j + 1 < len(d) and aktiv[j + 1] and np.sign(d[j + 1]) == np.sign(d[i]):
                j += 1
            sprang = d[i:j + 1].sum()
            if abs(sprang) >= minsprang:
                c = np.cumsum(d[i:j + 1]) / sprang
                a10 = a[i:j + 1][np.searchsorted(c, 0.1)]
                a90 = a[i:j + 1][min(np.searchsorted(c, 0.9), j - i)]
                a50 = a[i:j + 1][min(np.searchsorted(c, 0.5), j - i)]
                ut.append((float(a50), float(sprang), float(abs(a90 - a10) + 0.25)))
            i = j + 1
        else:
            i += 1
    return ut


def tal():
    os.makedirs(UT, exist_ok=True)
    res = {}
    # ---- 1. prismefamilien analytisk (struktur mot kamera)
    rader = []
    print("\n== PRISME, STRUKTUR MOT KAMERA (rekna, analytisk) ==")
    print("topp  n_d   a_TIR  b ved lina  avboeying D  strekk ved lina  strekk 10 over  fargekant R-B  linetjukn B-R")
    for topp in (80, 85, 90, 95, 100, 110):
        for nd in (1.50, 1.59, 1.65):
            ng = float(n_harpiks(550.0, nd)); nb = float(n_harpiks(460.0, nd)); nr = float(n_harpiks(600.0, nd))
            at = prisme_tir_grense(ng, topp)
            a1 = at + 0.6
            e1 = prisme_fjern_flate(a1, ng, topp)
            D = e1 - a1
            def strekk(a):
                return 1.0 / (prisme_fjern_flate(a + 0.25, ng, topp) - prisme_fjern_flate(a - 0.25, ng, topp)) * 0.5
            fr = _a_for_e(e1, nr, topp) - _a_for_e(e1, nb, topp)
            tl = prisme_tir_grense(nb, topp) - prisme_tir_grense(nr, topp)
            rader.append(dict(toppvinkel=topp, n_d=nd, a_tir=at, b_ved_lina=e1, avboeying=D,
                              strekk_ved_lina=strekk(a1), strekk_10_over=strekk(a1 + 10.0),
                              fargekant_R_minus_B=fr, linetjukn_B_minus_R=tl))
            print("%4d  %.2f  %6.2f   %6.2f      %6.2f        %5.2f           %5.2f         %5.2f          %5.2f" % (
                topp, nd, at, e1, D, strekk(a1), strekk(a1 + 10.0), fr, tl))
    res["prisme_struktur_mot_kamera"] = rader
    # ---- 2. greiner fraa kjernane (550 nm)
    il = int(np.argmin(np.abs(LAM - 550.0)))
    il_b = int(np.argmin(np.abs(LAM - 460.0)))
    il_r = int(np.argmin(np.abs(LAM - 640.0)))
    grein = {}
    print("\n== GREINER VED %.0f nm: kameravinkel a -> (sceneelevasjon, vekt) ==" % LAM[il])
    for pn in profilar():
        for side in ("kamera", "vindauge"):
            if pn == "flat" and side == "vindauge":
                continue
            T, R = kjerne_spektral(pn, side)
            d = {}
            linje = "%-15s %-8s" % (pn, side)
            for a in (10.0, 0.0, -10.0, -20.0, -30.0, -40.0, -50.0):
                ia = int(round((a - ALFA[0]) / DALFA))
                kl = _klynger(BETA, T[il, ia].astype(np.float64), gap=1.5, minvekt=0.02)
                d["%+.0f" % a] = dict(gjennom=float(T[il, ia].sum()), attende=float(R[il, ia].sum()),
                                      greiner=[dict(elevasjon=round(c, 2), fraa=round(a0, 2), til=round(a1, 2), vekt=round(w, 3)) for c, a0, a1, w in kl])
                linje += "  a=%+.0f T=%.2f:" % (a, T[il, ia].sum()) + ",".join("%+.0f(%.2f)" % (c, w) for c, a0, a1, w in kl)
            grein[pn + "_" + side] = d
            print(linje)
    res["greiner_%.0fnm" % LAM[il]] = grein
    # ---- 3. dei fire observasjonane, rekna for kvar profil og side
    # Proevescene: himmel (1) over E0 = 12 grader, moerkt under. Loddrett ark.
    E0 = 12.0
    over = (BETA > E0).astype(np.float64)
    ia_app = np.round((APP - ALFA[0]) / DALFA).astype(int)
    fakta = {}
    print("\n== DEI FIRE OBSERVASJONANE (rekna; himmel over %.0f grader, loddrett ark) ==" % E0)
    print("profil          side      himmel synleg ned til   kantkopiar (elevasjon: sprang, breidd)            fargekant a(640)-a(460)")
    for pn in profilar():
        for side in ("kamera", "vindauge"):
            if pn == "flat" and side == "vindauge":
                continue
            T, R = kjerne_spektral(pn, side)
            I = T[il][ia_app].astype(np.float64) @ over
            Ib = T[il_b][ia_app].astype(np.float64) @ over
            Ir = T[il_r][ia_app].astype(np.float64) @ over
            under = APP < E0
            syn = APP[under & (I >= 0.10)]
            ned_til = float(syn.min()) if len(syn) else float("nan")
            # samanhengande himmelsone rett under den sanne horisonten?
            k = _kantar(I)
            kb = _kantar(Ib); kr = _kantar(Ir)
            # fargekant for den sterkaste kanten under horisonten
            frynse = float("nan")
            under_k = [x for x in k if x[0] < E0 - 1.0 and x[1] > 0]
            if under_k:
                hoved = max(under_k, key=lambda x: x[1])
                fb = [x for x in kb if abs(x[0] - hoved[0]) < 8 and x[1] > 0]
                fr_ = [x for x in kr if abs(x[0] - hoved[0]) < 8 and x[1] > 0]
                if fb and fr_:
                    frynse = max(fr_, key=lambda x: x[1])[0] - max(fb, key=lambda x: x[1])[0]
            fakta[pn + "_" + side] = dict(himmel_synleg_ned_til=ned_til,
                                          kantkopiar=[dict(elevasjon=x[0], sprang=round(x[1], 3), breidd=x[2]) for x in k],
                                          fargekant_640_minus_460=frynse,
                                          himmeldel_ved_minus10=float(I[int(round((-10.0 - APP[0]) / 0.25))]),
                                          himmeldel_ved_minus25=float(I[int(round((-25.0 - APP[0]) / 0.25))]))
            print("%-15s %-8s  %+6.1f                 %-50s %+.2f" % (
                pn, side, ned_til, " ".join("%+.1f:%+.2f,%.1f" % x for x in k)[:50], frynse))
    res["fire_observasjonar"] = fakta
    # ---- 4. naerfelt: kor mykje flyttar ein ting som ligg d mm bak arket seg
    ng = float(n_harpiks(550.0))
    b0 = prisme_fjern_flate(0.0, ng)
    res["naerfelt_prisme90"] = dict(avboeying_normalt=b0,
                                    forskyving_mm_ved_1mm=math.tan(math.radians(b0)) * 1.0,
                                    forskyving_mm_ved_10mm=math.tan(math.radians(b0)) * 10.0,
                                    forskyving_mm_ved_100mm=math.tan(math.radians(b0)) * 100.0)
    print("\nnaerfelt, prisme 90: avboeying %.1f grader -> forskyving %.1f mm ved 1 mm, %.1f mm ved 10 mm, %.0f mm ved 100 mm avstand" % (
        b0, math.tan(math.radians(b0)), math.tan(math.radians(b0)) * 10, math.tan(math.radians(b0)) * 100))
    with open(os.path.join(UT, "tal.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print("lagra tal.json")
    return res


# --------------------------------------------------------------------------
# Maal i fotoa (alt som kjem fraa fotoa blir skrive til context/delar-foto/analyse/)
# --------------------------------------------------------------------------
F35 = 26.0      # ANTAKING: hovudkamera paa telefon, 26 mm ekvivalent, ingen zoom, ingen linsekorreksjon


def _foto(navn):
    from PIL import Image
    im = np.asarray(Image.open(os.path.join(FOTO, navn)).convert("RGB")).astype(np.float64) / 255.0
    return np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)


def _glatt(v, n=9):
    k = np.ones(n) / n
    return np.convolve(np.pad(v, n // 2, mode="edge"), k, mode="valid")


def foto():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    if not os.path.exists(os.path.join(FOTO, "07-prismefilm-heil-mot-vindauge.jpg")):
        print("fotoa finst ikkje her; hoppar over")
        return None
    os.makedirs(ANALYSE, exist_ok=True)
    res = {"f35_mm_ANTAKING": F35}
    ng = float(n_harpiks(550.0))
    a_tir = prisme_tir_grense(ng)

    def oppsett(arr):
        H, W = arr.shape[:2]
        fpx = F35 / 43.27 * math.hypot(W, H)
        cy = (H - 1) / 2.0
        return fpx, cy

    def vinkel(y, fpx, cy):
        return math.degrees(math.atan((cy - y) / fpx))

    def kantrad(v, y0, y1, forteikn):
        """Rad for sterkaste glatta gradient med gitt forteikn i [y0, y1]."""
        g = np.diff(_glatt(v, 15))
        seg = g[y0:y1] * forteikn
        return y0 + int(np.argmax(seg)) + 0.5

    def tyngdepunkt_fall(v, y0, y1, forteikn=-1):
        g = np.diff(_glatt(v, 15))[y0:y1] * forteikn
        g = np.clip(g, 0, None)
        return y0 + float((np.arange(len(g)) * g).sum() / g.sum()) + 0.5

    def topp_rad(v, y0, y1):
        seg = _glatt(v, 5)[y0:y1]
        grunn = np.linspace(seg[0], seg[-1], len(seg))
        return y0 + int(np.argmax(seg - grunn))

    # ---------------- foto 07
    A = _foto("07-prismefilm-heil-mot-vindauge.jpg")
    fpx, cy = oppsett(A)
    lum = lambda P: 0.2126 * P[:, 0] + 0.7152 * P[:, 1] + 0.0722 * P[:, 2]
    pA = A[:, 950:1080].mean(axis=1)       # kolonne gjennom den gule blokka
    pB = A[:, 420:520].mean(axis=1)        # kolonne der himmelen rekk laagast
    m = {}
    m["arktopp"] = kantrad(lum(pA), 120, 260, +1)
    m["karm"] = kantrad(lum(pA), 1950, 2100, -1)
    m["linje_R"] = topp_rad(pA[:, 0], 1760, 1870)
    m["linje_G"] = topp_rad(pA[:, 1], 1760, 1870)
    m["linje_B"] = topp_rad(pA[:, 2], 1760, 1870)
    m["gul_topp_R_stig"] = tyngdepunkt_fall(pA[:, 0], 1300, 1500, +1)
    m["gul_topp_B_fell"] = tyngdepunkt_fall(pA[:, 2], 1300, 1500, -1)
    m["himmelkant_R"] = tyngdepunkt_fall(pB[:, 0], 1600, 1990)
    m["himmelkant_G"] = tyngdepunkt_fall(pB[:, 1], 1600, 1990)
    m["himmelkant_B"] = tyngdepunkt_fall(pB[:, 2], 1600, 1990)
    m["linje_G_venstre"] = topp_rad(pB[:, 1], 1780, 1850)
    m["direkte_silhuett_venstre"] = kantrad(lum(A[:, 430:520].mean(axis=1)), 40, 150, -1)
    v = {k: vinkel(y, fpx, cy) for k, y in m.items()}
    r07 = dict(rader=m, vinklar_fraa_biletaksen=v)
    r07["himmelsone_arktopp_til_gul_topp"] = v["arktopp"] - v["gul_topp_R_stig"]
    r07["himmelsone_arktopp_til_himmelkant_venstre"] = v["arktopp"] - v["himmelkant_G"]
    r07["gul_topp_til_linje"] = v["gul_topp_R_stig"] - v["linje_G"]
    r07["linje_til_karm"] = v["linje_G"] - v["karm"]
    r07["fargekant_himmelkant_R_minus_B"] = v["himmelkant_R"] - v["himmelkant_B"]
    r07["linje_B_minus_R"] = v["linje_B"] - v["linje_R"]
    # invariant: avboeying ved lina. Silhuetten til venstre sett direkte (over arket) og gjennom arket.
    D_obs = v["direkte_silhuett_venstre"] - v["himmelkant_G"]
    a_bilete = a_tir + (v["himmelkant_G"] - v["linje_G"])
    D_mod = prisme_fjern_flate(a_bilete, ng) - a_bilete
    r07["avboeying_silhuett_observert"] = D_obs
    r07["avboeying_silhuett_modell_prisme90"] = D_mod
    r07["lokal_vinkel_for_silhuettbiletet"] = a_bilete
    # kva toppvinkel gjev den observerte avboeyinga (n_d 1,59)?
    tv = np.arange(70.0, 120.01, 0.25)
    Dm = []
    for t in tv:
        at = prisme_tir_grense(ng, t)
        ab = at + (v["himmelkant_G"] - v["linje_G"])
        Dm.append(prisme_fjern_flate(ab, ng, t) - ab)
    Dm = np.array(Dm)
    ok = np.isfinite(Dm)
    r07["toppvinkel_som_gjev_observert_avboeying"] = float(np.interp(-D_obs, -Dm[ok], tv[ok]))
    r07["toppvinkel_ved_24mm_linse"] = None
    # same med 24 mm: alle vinklar blir stoerre
    f24 = 24.0 / 43.27 * math.hypot(A.shape[1], A.shape[0])
    v24 = {k: vinkel(y, f24, cy) for k, y in m.items()}
    D24 = v24["direkte_silhuett_venstre"] - v24["himmelkant_G"]
    Dm24 = []
    for t in tv:
        at = prisme_tir_grense(ng, t)
        ab = at + (v24["himmelkant_G"] - v24["linje_G"])
        Dm24.append(prisme_fjern_flate(ab, ng, t) - ab)
    Dm24 = np.array(Dm24); ok = np.isfinite(Dm24)
    r07["avboeying_silhuett_observert_24mm"] = D24
    r07["toppvinkel_ved_24mm_linse"] = float(np.interp(-D24, -Dm24[ok], tv[ok]))
    # toppen av den gule blokka: kvar skal han liggje i direkte syn etter modellen?
    a_gul = a_tir + (v["gul_topp_R_stig"] - v["linje_G"])
    D_gul = prisme_fjern_flate(a_gul, float(n_harpiks(600.0))) - a_gul
    y_dir = cy - fpx * math.tan(math.radians(v["gul_topp_R_stig"] + D_gul))
    r07["gul_topp_modell_rad_i_direkte_syn"] = y_dir
    res["foto07"] = r07

    # ---------------- foto 01
    B = _foto("01-prismefilm-mot-vindauge.jpg")
    fpx1, cy1 = oppsett(B)
    qA = B[:, 1000:1100].mean(axis=1)
    m1 = {}
    m1["arktopp"] = kantrad(lum(qA), 420, 520, +1)
    m1["linje_R"] = topp_rad(qA[:, 0], 1620, 1720)
    m1["linje_G"] = topp_rad(qA[:, 1], 1620, 1720)
    m1["linje_B"] = topp_rad(qA[:, 2], 1620, 1720)
    m1["gul_topp_R_stig"] = tyngdepunkt_fall(qA[:, 0], 1230, 1400, +1)
    m1["karm"] = kantrad(lum(qA), 1800, 1960, -1)
    v1 = {k: vinkel(y, fpx1, cy1) for k, y in m1.items()}
    r01 = dict(rader=m1, vinklar_fraa_biletaksen=v1)
    r01["himmelsone_arktopp_til_gul_topp"] = v1["arktopp"] - v1["gul_topp_R_stig"]
    r01["gul_topp_til_linje"] = v1["gul_topp_R_stig"] - v1["linje_G"]
    r01["linje_til_karm"] = v1["linje_G"] - v1["karm"]
    r01["linje_B_minus_R"] = v1["linje_B"] - v1["linje_R"]
    a_gul1 = a_tir + (v1["gul_topp_R_stig"] - v1["linje_G"])
    D_gul1 = prisme_fjern_flate(a_gul1, float(n_harpiks(600.0))) - a_gul1
    r01["gul_topp_modell_rad_i_direkte_syn"] = cy1 - fpx1 * math.tan(math.radians(v1["gul_topp_R_stig"] + D_gul1))
    res["foto01"] = r01

    # ---------------- fin tekstur i naerbilete 05: retning og periode
    try:
        from scipy.ndimage import gaussian_filter
        C = _foto("05-prismefilm-naerbilete-a.jpg")
        tek = []
        for (x0, y0) in ((300, 2050), (900, 2060), (1300, 1900), (600, 900)):
            pt = C[y0:y0 + 256, x0:x0 + 256, 1].copy()
            pt = pt - gaussian_filter(pt, 6.0)
            win = np.hanning(256)[:, None] * np.hanning(256)[None, :]
            F = np.abs(np.fft.fftshift(np.fft.fft2(pt * win))) ** 2
            fy, fx = np.indices(F.shape); fy = fy - 128; fx = fx - 128
            rr = np.hypot(fx, fy)
            F[(rr < 8) | (rr > 110)] = 0.0
            F[fy < 0] = 0.0                      # halve planet (symmetrisk spektrum)
            iy, ix = np.unravel_index(np.argmax(F), F.shape)
            ky, kx = iy - 128, ix - 128
            # styrke: toppen mot medianen i ringen
            ring = F[(rr > 8) & (rr < 110) & (fy >= 0)]
            tek.append(dict(x0=x0, y0=y0, periode_px=256.0 / math.hypot(kx, ky),
                            bolgjevektor_vinkel_fraa_vassrett=math.degrees(math.atan2(ky, kx)),
                            topp_over_median=float(F[iy, ix] / np.median(ring))))
        res["tekstur_foto05"] = tek
    except Exception as ex:
        res["tekstur_foto05"] = "feil: %s" % ex

    # ---------------- modellprofil mot fotoprofil (himmelkanten til venstre i 07)
    T, R = kjerne_spektral("prisme90", "kamera")
    ia_app = np.round((APP - ALFA[0]) / DALFA).astype(int)
    E_s = prisme_fjern_flate(a_bilete, ng)                 # silhuetten sin lokale elevasjon
    dag = norm_y(planck(LAM, 6500.0)); blaa = norm_y(planck(LAM, 6500.0) * (550.0 / LAM) ** 3.0)
    sno = norm_y(planck(LAM, 6500.0) * (550.0 / LAM) ** 1.6)
    Lk = np.zeros((len(EL), len(LAM)))
    Lk[EL > E_s] = 0.6 * dag + 0.4 * blaa
    Lk[(EL <= E_s) & (EL > 0)] = 0.12 * dag
    Lk[EL <= 0] = 0.40 * sno
    Lk[EL <= -75] = 0.03 * dag
    rom = norm_y(planck(LAM, 4500.0))
    Smod = np.zeros((len(APP), len(LAM)))
    for il in range(len(LAM)):
        Smod[:, il] = T[il][ia_app].astype(np.float64) @ Lk[:, il] + R[il][ia_app].sum(axis=1) * 0.10 * rom[il]
    X = Smod @ _X; Y = Smod @ _Y; Z = Smod @ _Z
    rgbm = np.stack([X, Y, Z], axis=-1) @ M_XYZ_RGB.T / _KVIT
    fig, axs = plt.subplots(1, 2, figsize=(15, 5.5))
    yy = np.arange(len(pB))
    th = np.degrees(np.arctan((cy - yy) / fpx)) - v["linje_G"]
    for c, col in enumerate("rgb"):
        axs[0].plot(th, pB[:, c], col, lw=1.0)
        axs[0].plot(th, pA[:, c], col, lw=0.6, ls="--")
    axs[0].set_xlim(12, -8); axs[0].set_xlabel("vinkel over den lyse lina (grader, 26 mm ANTAKING)")
    axs[0].set_title("foto 07: heil = x 420-520 (himmelkant), stipla = x 950-1080 (gul blokk)")
    axs[0].grid(alpha=0.3)
    for c, col in enumerate("rgb"):
        axs[1].plot(APP - a_tir, rgbm[:, c], col, lw=1.0)
    axs[1].set_xlim(12, -8); axs[1].set_xlabel("vinkel over totalrefleksjonsgrensa (grader)")
    axs[1].set_title("modell: prisme 90, struktur mot kamera, himmelkant ved %.1f grader" % E_s)
    axs[1].grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(ANALYSE, "fysikk-maal-profil.png"), dpi=90); plt.close(fig)
    # modellen sin fargekant med same definisjon som i fotoet
    def tp(vv, a0, a1):
        rel = APP - a_tir
        g = np.clip(np.diff(vv), 0, None)
        am = 0.5 * (rel[1:] + rel[:-1])
        mm = (am >= a0) & (am <= a1)
        return float((am[mm] * g[mm]).sum() / g[mm].sum())
    lo = vinkel(1990, fpx, cy) - v["linje_G"]; hi = vinkel(1600, fpx, cy) - v["linje_G"]
    res["modell_fargekant_R_minus_B_same_definisjon"] = tp(rgbm[:, 0], lo, hi) - tp(rgbm[:, 2], lo, hi)

    # ---------------- side om side: foto 07 og modell (berre til analyse-mappa)
    Ls = scene(snokant=True)
    S = gjennomsyn("a_prisme90", "kamera", Ls, 0.0)
    y0, y1 = int(m["arktopp"]), int(m["karm"]) + 60
    utsnitt = Image.open(os.path.join(FOTO, "07-prismefilm-heil-mot-vindauge.jpg")).crop((300, y0, 1560, y1))
    # modellen: same vinkelomraade, lokal vinkel = a_tir + (vinkel - vinkel_linje)
    a_topp = a_tir + (v["arktopp"] - v["linje_G"]); a_botn = a_tir + (vinkel(y1, fpx, cy) - v["linje_G"])
    i_t = int(round((a_topp - APP[0]) / 0.25)); i_b = int(round((a_botn - APP[0]) / 0.25))
    rgb = spektrum_til_srgb(S[i_b:i_t + 1][::-1], 1.15)
    mod = Image.fromarray((rgb * 255 + 0.5).astype(np.uint8))
    # tangensprojeksjon: radene i fotoet er ikkje jamne i vinkel; resample modellen
    rad_v = np.array([vinkel(y, fpx, cy) for y in range(y0, y1)])
    a_rad = a_tir + (rad_v - v["linje_G"])
    idx = np.clip(np.round((a_topp - a_rad) / 0.25).astype(int), 0, rgb.shape[0] - 1)
    mod2 = Image.fromarray((rgb[idx] * 255 + 0.5).astype(np.uint8)).resize((utsnitt.width * 2 // 3, utsnitt.height), Image.BILINEAR)
    ark = Image.new("RGB", (utsnitt.width + mod2.width + 10, utsnitt.height), (0, 0, 0))
    ark.paste(utsnitt, (0, 0)); ark.paste(mod2, (utsnitt.width + 10, 0))
    ark.save(os.path.join(ANALYSE, "fysikk-side-om-side-07.png"))
    with open(os.path.join(ANALYSE, "fysikk-maal.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))
    return res



if __name__ == "__main__":
    kva = sys.argv[1] if len(sys.argv) > 1 else "test"
    if kva in ("test", "alt"):
        if not test():
            sys.exit(1)
    if kva in ("kjernar", "alt"):
        alle_kjernar()
    if kva in ("kart", "alt"):
        kart()
    if kva in ("bilete", "alt"):
        bilete()
    if kva in ("tal", "alt"):
        tal()
    if kva in ("foto", "alt"):
        foto()
