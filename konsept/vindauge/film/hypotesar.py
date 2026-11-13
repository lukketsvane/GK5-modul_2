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
    x = np.linspace(0.0, 1.0, nseg + 1)
    A = math.tan(math.radians(maks_helling)) / math.pi
    z = A * (1.0 - np.cos(2 * math.pi * x)) / 2.0 * 2.0 / 2.0
    # z = A/2 (1 - cos): helling = A*pi*sin -> maks = A*pi
    z = A * (1.0 - np.cos(2 * math.pi * x)) / 2.0
    z = z * 2.0  # maks helling = 2*pi*A/2*... -> rett opp under
    # rett skalering: z = a(1-cos(2 pi x)), dz/dx = 2 pi a sin -> a = tan/(2 pi)
    a = math.tan(math.radians(maks_helling)) / (2 * math.pi)
    z = a * (1.0 - np.cos(2 * math.pi * x))
    return x, z


def profil_ru(sigma_helling=12.0, nmodar=24, nseg=768, froe=7):
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
          wmin, st, ut):
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
            if nhend > 200000:
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
                                  fra_topp, sin_a, wmin, st, ut)
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
               skeiv=0.0, wmin=1e-14, land=0.05):
    """Ein straale: liste av (side, vinkel, ws, wp) og tapt vekt. For kontroll."""
    px, pz = profil
    pz = np.ascontiguousarray(pz + land)
    px = np.ascontiguousarray(px)
    st = np.empty((400, 7)); ut = np.empty((4000, 4))
    nut, tapt, nh = _spor(px, pz, float(pz.max()), t_sub, n_res, n_sub, skeiv,
                          x0, fra_topp, math.sin(math.radians(alfa_grad)), wmin, st, ut)
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
# namn: (forklaring, profil, tilleggsspreiing i grader (isotrop gauss), 2D-flagg)
# 2D-flagg: "1d" = kjernen verkar berre loddrett. "2d" = same kjerne i baae
# retningar (separabel tilnaerming for isotrope strukturar). "kryss" = to
# prismefilmar i kryss.

def kandidatar():
    K = {}
    K["a_prisme90"] = dict(tekst="(a) prisme 90 grader, skarp", profil=profil_prisme(90.0), modus="1d")
    K["b_prisme90_r08"] = dict(tekst="(b) prisme 90 grader, runda topp r = 0,08 p", profil=profil_prisme(90.0, r_topp=0.08), modus="1d")
    K["b_prisme90_r20"] = dict(tekst="(b) prisme 90 grader, runda topp r = 0,20 p", profil=profil_prisme(90.0, r_topp=0.20), modus="1d")
    K["b_prisme80"] = dict(tekst="(b) prisme 80 grader", profil=profil_prisme(80.0), modus="1d")
    K["b_prisme100"] = dict(tekst="(b) prisme 100 grader", profil=profil_prisme(100.0), modus="1d")
    K["b_prisme110"] = dict(tekst="(b) prisme 110 grader", profil=profil_prisme(110.0), modus="1d")
    K["b_prisme90_ujamn"] = dict(tekst="(b) prisme 90 grader, ujamn hoegd", profil=profil_prisme_ujamn(90.0), modus="1d")
    K["c_linse_R06"] = dict(tekst="(c) lentikulaer, R = 0,6 p", profil=profil_linse(0.6), modus="1d")
    K["c_linse_R10"] = dict(tekst="(c) lentikulaer, R = 1,0 p", profil=profil_linse(1.0), modus="1d")
    K["d_einveg_ru12"] = dict(tekst="(d) einvegsdiffusor, sigma helling 12 grader", profil=profil_ru(12.0), modus="1d")
    K["e_diffusor_ru12"] = dict(tekst="(e) vanleg diffusor (2D), sigma helling 12 grader", profil=profil_ru(12.0), modus="2d")
    K["f_polarisator"] = dict(tekst="(f) reflekterande polarisator (plan film, 50 %)", profil=profil_flat(), modus="1d", faktor=0.5)
    K["f_polarisator_matt"] = dict(tekst="(f) reflekterande polarisator + matt lag", profil=profil_ru(6.0), modus="2d", faktor=0.5)
    K["g_mikrolinse"] = dict(tekst="(g) mikrolinsefilm (2D), R = 0,6 p", profil=profil_linse(0.6), modus="2d")
    K["h_prisme90_matt"] = dict(tekst="(h) prisme 90 grader + matt bakside (sigma 3 grader)", profil=profil_prisme(90.0), modus="1d", gauss2d=3.0)
    K["h_prisme_kryss"] = dict(tekst="(h) to prismefilmar i kryss", profil=profil_prisme(90.0), modus="kryss")
    return K


ALFA = np.arange(-89.0, 89.01, 0.5)     # innfallsvinklar for kjernane
NB = 720                                 # utvinkelboksar (0,25 grader)
BETA = (np.arange(NB) + 0.5) * 180.0 / NB - 90.0


def kjerne_spektral(namn, side, npos=500, tving=False, skeiv=0.0, nd=ND_HARPIKS):
    """Kjernar for alle 16 bolgjelengder. side = "kamera" (strukturen vender
    mot kamera) eller "vindauge" (strukturen vender mot vindauget).
    Kamerastraalen blir spora bakover (fraa kamera ut i scena).
    Returnerer T, R med form (16, na, NB)."""
    os.makedirs(CACHE, exist_ok=True)
    tag = "%s_%s_%d_s%03d_n%03d" % (namn, side, npos, int(round(skeiv * 100)), int(round(nd * 100)))
    f = os.path.join(CACHE, tag + ".npz")
    if os.path.exists(f) and not tving:
        d = np.load(f)
        return d["T"], d["R"]
    kand = kandidatar()[namn]
    T = np.zeros((len(LAM), len(ALFA), NB), dtype=np.float32)
    R = np.zeros_like(T)
    for il, lam in enumerate(LAM):
        t, r, l = kjerne(kand["profil"], float(n_harpiks(lam, nd)), float(n_pet(lam)),
                         ALFA, fra_topp=(side == "kamera"), npos=npos, nb=NB, skeiv=skeiv)
        T[il] = t; R[il] = r
    np.savez_compressed(f, T=T, R=R)
    return T, R


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
    # mjuk avrulling mot kvitt i staden for hard klipping
    rgb = np.clip(rgb, 0.0, None)
    rgb = rgb / (1.0 + 0.18 * rgb ** 2) ** 0.5 * (1.0 + 0.18) ** 0.5 * 0.999
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
                    L[i, j] = 2.6 * felt * sol * refl / np.sum(sol * refl * _Y) * np.sum(refl * _Y * dag) * 1.4
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

def _gauss_kjerne(sigma_grad, steg):
    n = int(math.ceil(4 * sigma_grad / steg))
    x = np.arange(-n, n + 1) * steg
    k = np.exp(-0.5 * (x / sigma_grad) ** 2)
    return k / k.sum()


def _flytt_kjerne(Tl, helling):
    """Kjerne i verdsvinklar for eit ark som hallar. helling > 0: toppen
    lener seg bort fraa kamera (mot vindauget), dvs. normalen mot scena
    peikar `helling` grader nedover. Verdsvinkel = lokal vinkel - helling.
    Returnerer K[a_verd, e_verd] paa netta (APP, EL)."""
    # lokal innfallsvinkel for kvar verdsvinkel
    a_lok = APP + helling
    ia = np.clip(np.round((a_lok - ALFA[0]) / 0.5).astype(int), 0, len(ALFA) - 1)
    gyldig = (a_lok >= ALFA[0]) & (a_lok <= ALFA[-1])
    K = Tl[ia] * gyldig[:, None]
    # flytt utvinkelen: e_verd = b_lok - helling
    sk = int(round(helling / (180.0 / NB)))
    if sk != 0:
        K2 = np.zeros_like(K)
        if sk > 0:
            K2[:, :-sk] = K[:, sk:]
        else:
            K2[:, -sk:] = K[:, :sk]
        K = K2
    return K


APP = np.arange(-70.0, 70.01, 0.25)      # tilsynelatande elevasjon (kamerastraalen)


def gjennomsyn(namn, side, L, helling=0.0, npos=500, skeiv_korr=False):
    """Bilete [APP, AZ, 3] (sRGB) av scena L sett gjennom kandidaten.
    Ryggane ligg vassrett. Kjernen verkar loddrett i kvar kolonne (skeiv = 0),
    pluss tilleggsledd etter kandidaten sin modus."""
    kand = kandidatar()[namn]
    T, R = kjerne_spektral(namn, side, npos=npos)
    faktor = kand.get("faktor", 1.0)
    modus = kand["modus"]
    nel, naz, nl = L.shape
    ut = np.zeros((len(APP), naz, nl))
    dag = norm_y(planck(LAM, 4500.0))
    for il in range(nl):
        K = _flytt_kjerne(T[il].astype(np.float64), helling)      # [APP, EL]
        bilete = K @ L[:, :, il]                                  # [APP, AZ]
        # spegla del: rommet bak kamera, jamt moerkt
        ia = np.clip(np.round((APP + helling - ALFA[0]) / 0.5).astype(int), 0, len(ALFA) - 1)
        refl = R[il][ia].sum(axis=1)
        if modus == "2d":
            # same kjerne vassrett: bruk kjernen ved normalt innfall som
            # vassrett spreiefunksjon (separabel tilnaerming, ANTAKING)
            k0 = T[il][len(ALFA) // 2].astype(np.float64)
            k0 = k0 / max(k0.sum(), 1e-12)
            steg_az = AZ[1] - AZ[0]
            # resample k0 (0,25 grader) til asimutsteget
            xk = BETA
            xs = np.arange(-45.0, 45.01, steg_az)
            ks = np.interp(xs, xk, k0)
            ks = ks / ks.sum()
            bilete = np.apply_along_axis(lambda v: np.convolve(np.pad(v, len(ks) // 2, mode="edge"), ks, mode="valid"), 1, bilete)
        elif modus == "kryss":
            # film 2 med loddrette ryggar: to kopiar forskyvde vassrett.
            # Tilnaerming: kjernen ved normalt innfall brukt vassrett.
            k0 = T[il][len(ALFA) // 2].astype(np.float64)
            steg_az = AZ[1] - AZ[0]
            xs = np.arange(-60.0, 60.01, steg_az)
            ks = np.interp(xs, BETA, k0)
            ks = ks / max(k0.sum() * (steg_az / 0.25), 1e-12)
            bilete = np.apply_along_axis(lambda v: np.convolve(np.pad(v, len(ks) // 2, mode="reflect"), ks, mode="valid"), 1, bilete)
        g = kand.get("gauss2d", 0.0)
        if g > 0:
            kv = _gauss_kjerne(g, 0.25)
            kh = _gauss_kjerne(g, AZ[1] - AZ[0])
            bilete = np.apply_along_axis(lambda v: np.convolve(np.pad(v, len(kv) // 2, mode="edge"), kv, mode="valid"), 0, bilete)
            bilete = np.apply_along_axis(lambda v: np.convolve(np.pad(v, len(kh) // 2, mode="edge"), kh, mode="valid"), 1, bilete)
        ut[:, :, il] = faktor * bilete + (refl[:, None] + (1 - faktor) * 0.5) * ROM * dag[il]
    return ut


def direkte(L):
    """Scena utan ark, paa same nett som gjennomsynet."""
    ie = np.round((APP + 90.0) / 0.25 - 0.5).astype(int)
    return L[np.clip(ie, 0, len(EL) - 1)]


def lagre_bilete(S, fil, eksponering=0.9, skala=2, tekst=None):
    from PIL import Image, ImageDraw
    rgb = spektrum_til_srgb(S, eksponering)
    rgb = rgb[::-1]                                   # elevasjon opp
    im = Image.fromarray((rgb * 255 + 0.5).astype(np.uint8))
    if skala != 1:
        im = im.resize((im.width * skala, im.height * skala), Image.BILINEAR)
    if tekst:
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, im.width, 15], fill=(0, 0, 0))
        d.text((4, 2), tekst, fill=(255, 255, 255))
    im.save(fil)
    return im


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
    for namn in ("a_prisme90", "b_prisme90_r08", "b_prisme110", "c_linse_R06", "d_einveg_ru12"):
        prof = kandidatar()[namn]["profil"]
        for fra_topp in (True, False):
            for _ in range(300):
                a = rng.uniform(-85, 85); x0 = rng.uniform(0, 1)
                lam = rng.uniform(400, 700)
                ut, tapt = spor_liste(prof, float(n_harpiks(lam)), float(n_pet(lam)), a, x0, fra_topp, wmin=1e-13)
                s = 0.5 * (ut[:, 2] + ut[:, 3]).sum()
                verst = max(verst, abs(s + tapt - 1.0)); storst_tap = max(storst_tap, tapt)
    print("2. energi: |reflektert + transmittert + avkorta - 1| stoerst %.2e, stoerste avkorta del %.2e" % (verst, storst_tap))
    ok &= verst < 1e-10 and storst_tap < 1e-6

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


if __name__ == "__main__":
    kva = sys.argv[1] if len(sys.argv) > 1 else "test"
    if kva in ("test", "alt"):
        if not test():
            sys.exit(1)
