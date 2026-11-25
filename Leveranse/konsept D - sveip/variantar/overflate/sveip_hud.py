# -*- coding: utf-8 -*-
"""sveip_hud.py: overflatestudiar på Sveip som ekte geometri.

Ytterhuda på Sveip er éi utbrettbar plate. Her er ho bretta ut til eit rutenett (s, z):
s er boglengda rundt stadionforma (0 i nasen, framsida først), z er høgda. Ein variant er
ein funksjon felt(G) som gjev høgda h(s, z) i mm ut frå plata, pluss tone og ruheit.
Kjernen byggjer nettet, legg det utanpå CAD-kroppen (D01) og rendrar med fast kamera og
lys på heilt svart bakgrunn (#000). Forma er altså den same i alle variantar.

Køyr frå overflate/:
  python sveip_hud.py v1_plate            (full kvalitet, 1536 x 1536)
  python sveip_hud.py v1_plate --prove    (rask prøve, 640 x 640, grovare nett)
Les   ../V0-basis/render/geometri.json og STL-ane (lag dei med sveip_produksjon.py --rask i V0-basis/cad)
Skriv bilete/<variant>.png  (eller bilete/<variant>_prove.png)

Ein variant er ei fil <namn>.py i denne mappa med:
  def felt(G): return dict(h=..., tone=..., rough=..., mat={...})
    h      høgd i mm ut frå plata, same form som G.S. Nullnivået for huda er H0 (0,3 mm).
    tone   (valfri) lysleik, om lag 0,8 til 1,1
    rough  (valfri) ruheit 0 til 1
    mat    (valfri) dict: farge (r, g, b) sRGB, metal 0..1, rough, sky (skydekt variasjon 0..1),
           vev (synleg vev i duk, 0..1), floyel (sheen for duk, 0..1)
"""
from __future__ import annotations

import importlib
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

HER = Path(__file__).resolve().parent
BASIS = HER.parent / "V0-basis"

# ---------------------------------------------------------------- mål frå CAD (mm), rev. B
S_, D_, R_ = 300.0, 105.0, 52.5
Z_SKJERM, X_STAMME, R_INN = 167.5, 178.0, 12.0
X_HAKK, Z_HAKK, R_HAKK = 45.5, 61.0, 7.0
PKT_X, PKT_Z = 165.0, 70.0
BUE = math.pi * R_ / 2          # kvartboge i nasen: 82,47
FLAT = S_ - 2 * R_              # flat side: 195
P_ = 2 * FLAT + 2 * math.pi * R_  # omkrins: 719,87
H0 = 0.3                        # nullnivå for huda over CAD-flata
S_FRAMME = (BUE, BUE + FLAT)                      # s-området til den flate framsida
S_VENSTRE = (BUE + FLAT, BUE + FLAT + math.pi * R_)  # venstre halvsylinder
S_BAK = (BUE + FLAT + math.pi * R_, P_ - BUE)     # flat bakside
S_KNAPP_F = BUE + (S_ - R_ - PKT_X)               # knappen framme: s = 164,97
S_KNAPP_B = S_BAK[0] + (PKT_X - R_)               # knappen bak
S_STAMME_F = BUE + (S_ - R_ - X_STAMME)           # høgre kant av stamma, framme: s = 151,97
S_STAMME_B = S_BAK[0] + (X_STAMME - R_)           # same, bak
S_NASE_BAK = P_ - BUE                             # der baksida går over i nasen


def plan(s):
    """Punkt (x, y), normal (nx, ny) og flatenummer for boglengda s rundt stadionforma.
    Flater: 0 nase framme, 1 framside, 2 venstre boge, 3 bakside, 4 nase bak."""
    s = np.asarray(s, dtype=np.float64) % P_
    x = np.empty_like(s)
    y = np.empty_like(s)
    nx = np.empty_like(s)
    ny = np.empty_like(s)
    fl = np.empty(s.shape, dtype=np.int8)
    a = s < BUE
    th = -s[a] / R_
    x[a], y[a], nx[a], ny[a], fl[a] = S_ - R_ + R_ * np.cos(th), R_ * np.sin(th), np.cos(th), np.sin(th), 0
    b = (s >= BUE) & (s < BUE + FLAT)
    x[b], y[b], nx[b], ny[b], fl[b] = S_ - R_ - (s[b] - BUE), -R_, 0.0, -1.0, 1
    c = (s >= S_VENSTRE[0]) & (s < S_VENSTRE[1])
    th = -math.pi / 2 - (s[c] - S_VENSTRE[0]) / R_
    x[c], y[c], nx[c], ny[c], fl[c] = R_ + R_ * np.cos(th), R_ * np.sin(th), np.cos(th), np.sin(th), 2
    d = (s >= S_BAK[0]) & (s < S_BAK[1])
    x[d], y[d], nx[d], ny[d], fl[d] = R_ + (s[d] - S_BAK[0]), R_, 0.0, 1.0, 3
    e = s >= S_BAK[1]
    th = math.pi / 2 - (s[e] - S_BAK[1]) / R_
    x[e], y[e], nx[e], ny[e], fl[e] = S_ - R_ + R_ * np.cos(th), R_ * np.sin(th), np.cos(th), np.sin(th), 4
    return x, y, nx, ny, fl


def glatt(x, a, b):
    """Mjukt steg frå 0 (x <= a) til 1 (x >= b). a > b gjev fallande steg."""
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def kuppel(d, r, h):
    """Kulekalott med radius r og høgd h, som funksjon av avstanden d frå sentrum."""
    return h * np.sqrt(np.clip(1 - (d / r) ** 2, 0.0, 1.0))


class Gitter:
    """Utbretta hud. Alle felt har form (ns, nz + 1): akse 0 er s (lukka, går rundt), akse 1 er z."""

    def __init__(self, steg=0.25):
        self.steg = steg
        self.ns = int(round(P_ / steg))
        self.nz = int(round(S_ / steg))
        self.ds = P_ / self.ns
        self.dz = S_ / self.nz
        self.s = np.arange(self.ns) * self.ds
        self.z = np.arange(self.nz + 1) * self.dz
        self.S, self.Z = np.meshgrid(self.s, self.z, indexing="ij")
        x, y, nx, ny, fl = plan(self.s)
        self.x1, self.y1, self.nx1, self.ny1 = x, y, nx, ny
        self.X = np.repeat(x[:, None], self.nz + 1, axis=1)       # verdskoordinat x for kvart punkt
        self.flate = np.repeat(fl[:, None], self.nz + 1, axis=1)
        self.krum = (self.flate != 1) & (self.flate != 3)          # sant på dei krumme partia
        self.fast = self._fast(self.X, self.Z)                     # sant der det er plate
        # avstand (mm) frå kvart punkt til næraste kant av plata (toppkant, underkant, utskjeringar)
        pad = int(60 / steg)
        m = np.concatenate([self.fast[-pad:], self.fast, self.fast[:pad]], axis=0)
        m = np.pad(m, ((0, 0), (1, 1)), constant_values=False)
        self.kant = (ndimage.distance_transform_edt(m) * steg)[pad:-pad, 1:-1]
        # kva veg næraste kant går: sant der kanten er vassrett (gradienten peikar i z)
        gs = np.abs(np.roll(self.kant, -1, 0) - np.roll(self.kant, 1, 0))
        gz = np.abs(np.gradient(self.kant, axis=1)) * 2
        self.kant_vassrett = gz >= gs
        self.d_knapp = np.minimum(np.hypot(self.avst_s(S_KNAPP_F), self.Z - PKT_Z),
                                  np.hypot(self.avst_s(S_KNAPP_B), self.Z - PKT_Z))

    @staticmethod
    def _fast(X, Z):
        ut = (X > X_STAMME) & (Z < Z_SKJERM)
        hj = (X < X_STAMME + R_INN) & (Z > Z_SKJERM - R_INN) & \
             (np.hypot(X - (X_STAMME + R_INN), Z - (Z_SKJERM - R_INN)) > R_INN)
        ut &= ~hj
        hk = (X < X_HAKK) & (Z < Z_HAKK)
        hh = (X > X_HAKK - R_HAKK) & (Z > Z_HAKK - R_HAKK) & \
             (np.hypot(X - (X_HAKK - R_HAKK), Z - (Z_HAKK - R_HAKK)) > R_HAKK)
        hk &= ~hh
        return ~(ut | hk)

    # ------------------------------------------------------------ avstandar og mønster
    def avst_s(self, s0):
        """Avstand langs s til s0, rekna rundt (mm)."""
        return np.abs(((self.S - s0 + P_ / 2) % P_) - P_ / 2)

    def saum_s(self, *s0):
        """Avstand til næraste loddrette saum i lista."""
        return np.minimum.reduce([self.avst_s(v) for v in s0])

    def saum_z(self, *z0):
        """Avstand til næraste vassrette saum i lista."""
        return np.minimum.reduce([np.abs(self.Z - v) for v in z0])

    def naglar_z(self, z0, deling=12.0, r=1.1, h=0.45, fase=0.0, s_fra=None, s_til=None):
        """Ei vassrett naglerekkje i høgda z0, jamn deling rundt heile forma (delinga blir retta
        så ho går opp i omkrinsen). s_fra/s_til avgrensar rekkja til eit s-område."""
        n = max(1, round(P_ / deling))
        d = P_ / n
        u = ((self.S - fase + d / 2) % d) - d / 2
        ut = kuppel(np.hypot(u, self.Z - z0), r, h)
        if s_fra is not None:
            ut = ut * ((self.S >= s_fra) & (self.S <= s_til))
        return ut

    def naglar_s(self, s0, deling=12.0, r=1.1, h=0.45, fase=0.0, z_fra=0.0, z_til=S_):
        """Ei loddrett naglerekkje ved s0, frå z_fra til z_til."""
        n = max(1, round((z_til - z_fra) / deling))
        d = (z_til - z_fra) / n
        v = ((self.Z - z_fra - fase + d / 2) % d) - d / 2
        ut = kuppel(np.hypot(self.avst_s(s0), v), r, h)
        return ut * ((self.Z >= z_fra) & (self.Z <= z_til))

    def naglar_langs_kant(self, a=5.0, deling=12.0, r=1.1, h=0.45):
        """Naglar i avstanden a innanfor alle kantane på plata (toppkant, underkant, utskjeringar)."""
        ns_ = max(1, round(P_ / deling))
        dsd = P_ / ns_
        u = np.where(self.kant_vassrett, ((self.S + dsd / 2) % dsd) - dsd / 2,
                     ((self.Z + deling / 2) % deling) - deling / 2)
        return kuppel(np.hypot(u, self.kant - a), r, h)

    def panel_id(self, s_saumar, z_saumar):
        """Heiltal per panel i eit rutenett av saumar (s rundt, z opp)."""
        ss = np.sort(np.asarray(s_saumar, dtype=float) % P_)
        zs = np.sort(np.asarray(z_saumar, dtype=float))
        i = np.searchsorted(ss, self.S, side="right") % max(1, len(ss))
        j = np.searchsorted(zs, self.Z, side="right")
        return i * (len(zs) + 1) + j

    def tone_per_panel(self, ids, spreiing=0.06, fro=1):
        """Ein tilfeldig lysleik per panel-id, 1 +- spreiing."""
        rng = np.random.default_rng(fro)
        tab = 1 + spreiing * rng.uniform(-1, 1, int(ids.max()) + 1)
        return tab[ids]

    def stoy(self, skala=30.0, fro=1):
        """Mjuk støy med storleik om lag `skala` mm, verdiar om lag -1 til 1, saumlaus rundt s."""
        rng = np.random.default_rng(fro)
        f = max(1, int(round(skala / self.steg / 6)))
        a = rng.standard_normal((self.ns // f + 1, self.nz // f + 2))
        a = ndimage.gaussian_filter(a, 1.6, mode=("wrap", "nearest"))
        a = ndimage.zoom(a, (self.ns / a.shape[0], (self.nz + 1) / a.shape[1]), order=1, mode="grid-wrap")
        a = a[:self.ns, :self.nz + 1]
        return a / (np.abs(a).max() + 1e-9)


# ---------------------------------------------------------------- nett


def lag_nett(G, h):
    """Punkt, firkantar og uv for huda. Returnerer (verts, quads, uv_per_vert, er_kantstripe)."""
    ns, nz = G.ns, G.nz
    h = np.where(G.fast, h, 0.0)
    px = G.x1[:, None] + G.nx1[:, None] * h
    py = G.y1[:, None] + G.ny1[:, None] * h
    pz = G.Z
    # firkant (i, j) dekkjer s_i..s_i+1, z_j..z_j+1; fast om alle fire hjørna er plate og ikkje i knappeholet
    hol = G.d_knapp < 6.6
    ok = G.fast & ~hol
    i1 = (np.arange(ns) + 1) % ns
    q = ok[:, :-1] & ok[i1][:, :-1] & ok[:, 1:] & ok[i1][:, 1:]
    idx = np.arange(ns * (nz + 1)).reshape(ns, nz + 1)
    a = idx[:, :-1][q]
    b = idx[i1][:, :-1][q]
    c = idx[i1][:, 1:][q]
    d = idx[:, 1:][q]
    quads = np.stack([a, d, c, b], axis=1)        # normalen peikar ut
    # kantstriper: mellom huda og CAD-flata (h = 0) langs alle frie kantar, så ein ikkje ser inn bak huda
    kanter = []
    qq = np.pad(q, ((0, 0), (1, 1)), constant_values=False)
    # vassrette kantar: firkanten over/under manglar
    opp = q & ~qq[:, 2:]          # fri kant på toppen av firkanten (z_j+1)
    ned = q & ~qq[:, :-2]         # fri kant i botnen (z_j)
    kanter.append((idx[:, 1:][opp], idx[i1][:, 1:][opp]))
    kanter.append((idx[i1][:, :-1][ned], idx[:, :-1][ned]))
    # loddrette kantar: naboen i s manglar
    hog = q & ~np.roll(q, -1, axis=0)   # fri kant ved s_i+1
    ven = q & ~np.roll(q, 1, axis=0)    # fri kant ved s_i
    kanter.append((idx[i1][:, 1:][hog], idx[i1][:, :-1][hog]))
    kanter.append((idx[:, :-1][ven], idx[:, 1:][ven]))
    ka = np.concatenate([k[0] for k in kanter])
    kb = np.concatenate([k[1] for k in kanter])
    V = np.stack([px.ravel(), py.ravel(), pz.ravel()], axis=1)
    bx = np.repeat(G.x1[:, None], nz + 1, axis=1).ravel()
    by = np.repeat(G.y1[:, None], nz + 1, axis=1).ravel()
    inn = 0.05                                    # stripa går 0,05 mm inn i CAD-flata
    nxf = np.repeat(G.nx1[:, None], nz + 1, axis=1).ravel()
    nyf = np.repeat(G.ny1[:, None], nz + 1, axis=1).ravel()
    B = np.stack([bx - inn * nxf, by - inn * nyf, pz.ravel()], axis=1)
    brukt = np.unique(np.concatenate([quads.ravel(), ka, kb]))
    kart = -np.ones(V.shape[0], dtype=np.int64)
    kart[brukt] = np.arange(brukt.size)
    kb_ids = np.unique(np.concatenate([ka, kb]))
    kart_b = -np.ones(V.shape[0], dtype=np.int64)
    kart_b[kb_ids] = brukt.size + np.arange(kb_ids.size)
    verts = np.concatenate([V[brukt], B[kb_ids]])
    quads2 = kart[quads]
    striper = np.stack([kart[ka], kart[kb], kart_b[kb], kart_b[ka]], axis=1)
    uv = np.stack([G.S.ravel(), G.Z.ravel()], axis=1) / 1000.0
    uvv = np.concatenate([uv[brukt], uv[kb_ids]])
    return verts, quads2, striper, uvv, brukt, kb_ids


# ---------------------------------------------------------------- Blender


def render(namn, prove=False, ut=None):
    import bpy
    from mathutils import Vector

    mod = importlib.import_module(namn)
    G = Gitter(0.5 if prove else 0.25)
    res = mod.felt(G)
    h = np.asarray(res["h"], dtype=np.float64)
    assert h.shape == G.S.shape, f"h har form {h.shape}, skal vere {G.S.shape}"
    assert np.isfinite(h).all(), "h har NaN eller inf"
    # kring knappen er huda flat på nullnivået
    k = glatt(G.d_knapp, 7.0, 10.0)
    h = H0 + (h - H0) * k
    h = np.clip(h, 0.03, 8.0)
    tone = np.asarray(res.get("tone", np.ones_like(h)), dtype=np.float64) * np.ones_like(h)
    rough = res.get("rough")
    m = dict(farge=(0.83, 0.83, 0.84), metal=1.0, rough=0.42, sky=0.35, vev=0.0, floyel=0.0)
    m.update(res.get("mat", {}))
    rough = (np.full_like(h, m["rough"]) if rough is None else np.asarray(rough, dtype=np.float64) * np.ones_like(h))
    verts, quads, striper, uv, brukt, kb_ids = lag_nett(G, h)
    tone_v = np.concatenate([tone.ravel()[brukt], tone.ravel()[kb_ids]])
    rough_v = np.concatenate([rough.ravel()[brukt], rough.ravel()[kb_ids]])
    print(f"nett: {verts.shape[0]} punkt, {quads.shape[0]} + {striper.shape[0]} flater, "
          f"h {h[G.fast].min():.2f} til {h[G.fast].max():.2f} mm")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.threads_mode = "FIXED"
    sc.render.threads = 4
    sc.cycles.use_denoising = True
    sc.cycles.adaptive_threshold = 0.012
    sc.cycles.samples = 64 if prove else 400
    sc.cycles.max_bounces = 8
    sc.render.resolution_x = sc.render.resolution_y = 1536
    sc.render.resolution_percentage = 42 if prove else 100
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    def lin(c):
        return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

    def enkel(nm, farge, rough_=0.5, metal=0.0):
        mt = bpy.data.materials.new(nm)
        mt.use_nodes = True
        bs = mt.node_tree.nodes.get("Principled BSDF")
        bs.inputs["Base Color"].default_value = (*lin(farge), 1.0)
        bs.inputs["Roughness"].default_value = rough_
        bs.inputs["Metallic"].default_value = metal
        return mt

    # ---- huda
    me = bpy.data.meshes.new("hud")
    alle = np.concatenate([quads, striper]).astype(np.int32)
    nf = alle.shape[0]
    me.vertices.add(verts.shape[0])
    me.vertices.foreach_set("co", (verts / 1000.0).astype(np.float32).ravel())
    me.loops.add(nf * 4)
    me.loops.foreach_set("vertex_index", alle.ravel())
    me.polygons.add(nf)
    me.polygons.foreach_set("loop_start", np.arange(0, nf * 4, 4, dtype=np.int32))
    me.polygons.foreach_set("loop_total", np.full(nf, 4, dtype=np.int32))
    me.polygons.foreach_set("use_smooth", np.ones(nf, dtype=bool))
    me.update(calc_edges=True)
    uvl = me.uv_layers.new(name="UVMap")
    uvl.data.foreach_set("uv", uv[alle.ravel()].astype(np.float32).ravel())
    at = me.attributes.new("tone", "FLOAT", "POINT")
    at.data.foreach_set("value", tone_v.astype(np.float32))
    ar = me.attributes.new("ruheit", "FLOAT", "POINT")
    ar.data.foreach_set("value", rough_v.astype(np.float32))
    ob = bpy.data.objects.new("hud", me)
    sc.collection.objects.link(ob)

    mt = bpy.data.materials.new("hud")
    mt.use_nodes = True
    nt = mt.node_tree
    bs = nt.nodes.get("Principled BSDF")
    bs.inputs["Metallic"].default_value = m["metal"]
    try:
        bs.inputs["Sheen Weight"].default_value = m["floyel"]
        bs.inputs["Sheen Roughness"].default_value = 0.5
    except Exception:
        pass
    a_t = nt.nodes.new("ShaderNodeAttribute")
    a_t.attribute_name = "tone"
    a_r = nt.nodes.new("ShaderNodeAttribute")
    a_r.attribute_name = "ruheit"
    uvn = nt.nodes.new("ShaderNodeUVMap")
    # skydekt variasjon, som handpussa aluminium eller ujamn dope
    sky = nt.nodes.new("ShaderNodeTexNoise")
    sky.inputs["Scale"].default_value = 22.0
    sky.inputs["Detail"].default_value = 6.0
    sky.inputs["Roughness"].default_value = 0.6
    nt.links.new(uvn.outputs["UV"], sky.inputs["Vector"])
    kart = nt.nodes.new("ShaderNodeMapRange")
    kart.inputs["From Min"].default_value = 0.3
    kart.inputs["From Max"].default_value = 0.7
    kart.inputs["To Min"].default_value = 1.0 - 0.16 * m["sky"]
    kart.inputs["To Max"].default_value = 1.0 + 0.10 * m["sky"]
    nt.links.new(sky.outputs["Fac"], kart.inputs["Value"])
    gange = nt.nodes.new("ShaderNodeMath")
    gange.operation = "MULTIPLY"
    nt.links.new(a_t.outputs["Fac"], gange.inputs[0])
    nt.links.new(kart.outputs["Result"], gange.inputs[1])
    farge = nt.nodes.new("ShaderNodeMixRGB")
    farge.blend_type = "MULTIPLY"
    farge.inputs["Fac"].default_value = 1.0
    farge.inputs["Color1"].default_value = (*lin(m["farge"]), 1.0)
    nt.links.new(gange.outputs["Value"], farge.inputs["Color2"])
    nt.links.new(farge.outputs["Color"], bs.inputs["Base Color"])
    rk = nt.nodes.new("ShaderNodeMapRange")
    rk.inputs["From Min"].default_value = 0.3
    rk.inputs["From Max"].default_value = 0.7
    rk.inputs["To Min"].default_value = -0.07 * m["sky"]
    rk.inputs["To Max"].default_value = 0.07 * m["sky"]
    nt.links.new(sky.outputs["Fac"], rk.inputs["Value"])
    rsum = nt.nodes.new("ShaderNodeMath")
    rsum.operation = "ADD"
    rsum.use_clamp = True
    nt.links.new(a_r.outputs["Fac"], rsum.inputs[0])
    nt.links.new(rk.outputs["Result"], rsum.inputs[1])
    nt.links.new(rsum.outputs["Value"], bs.inputs["Roughness"])
    if m["vev"] > 0:   # lerretsvev: to bølgjemønster i kryss, 0,7 mm trådavstand, som bump
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.35 * m["vev"]
        bump.inputs["Distance"].default_value = 0.0002
        w = []
        for retn in ("X", "Y"):
            wv = nt.nodes.new("ShaderNodeTexWave")
            wv.wave_type = "BANDS"
            wv.bands_direction = retn
            wv.inputs["Scale"].default_value = 0.31416 / 0.0007   # éin tråd per 0,7 mm (uv i meter)
            wv.inputs["Distortion"].default_value = 0.6
            wv.inputs["Detail"].default_value = 1.0
            nt.links.new(uvn.outputs["UV"], wv.inputs["Vector"])
            w.append(wv)
        mx = nt.nodes.new("ShaderNodeMath")
        mx.operation = "MAXIMUM"
        nt.links.new(w[0].outputs["Fac"], mx.inputs[0])
        nt.links.new(w[1].outputs["Fac"], mx.inputs[1])
        nt.links.new(mx.outputs["Value"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bs.inputs["Normal"])
    me.materials.append(mt)

    # ---- resten av lampa frå CAD
    geo = json.loads((BASIS / "render" / "geometri.json").read_text(encoding="utf-8"))
    mats = {
        "D01": enkel("inn", (0.86, 0.86, 0.85), 0.6, 0.0),
        "D02": enkel("chassis", (0.30, 0.30, 0.30), 0.6, 0.6),
        "D10": enkel("luke", (0.30, 0.30, 0.30), 0.6, 0.6),
        "D12F": enkel("messing", (0.86, 0.68, 0.38), 0.3, 1.0),
        "D12B": enkel("messing2", (0.86, 0.68, 0.38), 0.3, 1.0),
        "D13F": enkel("svart", (0.05, 0.05, 0.05), 0.5),
        "D13B": enkel("svart2", (0.05, 0.05, 0.05), 0.5),
        "K08": enkel("fot", (0.10, 0.10, 0.10), 0.5),
        "E01": enkel("leidning", (0.035, 0.035, 0.035), 0.75),
        "D08": enkel("opal", (0.93, 0.93, 0.92), 0.5),
    }
    for d in geo["delar"]:
        if d["id"] not in mats:
            continue
        bpy.ops.wm.stl_import(filepath=str(BASIS / d["stl"]), global_scale=0.001)
        o = bpy.context.selected_objects[0]
        o.name = d["id"]
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(28))
        except Exception:
            pass
        o.data.materials.append(mats[d["id"]])
        if d["id"] in ("D12F", "D12B"):   # knappen står litt lenger ut, sidan huda ligg utanpå plata
            o.location.y += (-1 if d["id"] == "D12F" else 1) * (H0 / 1000.0)

    # ---- kamera og lys (fast for alle variantar)
    M = Vector((0.150, 0.0, 0.146))
    cam = bpy.data.cameras.new("kam")
    cam.lens = 165
    co = bpy.data.objects.new("kam", cam)
    sc.collection.objects.link(co)
    co.location = Vector((-0.27, -1.90, 0.64))
    co.rotation_euler = (M - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co

    def flate(nm, pos, storleik, energi, farge=(1, 1, 1), form=None):
        l = bpy.data.lights.new(nm, "AREA")
        if form:
            l.shape = "RECTANGLE"
            l.size, l.size_y = form
        else:
            l.size = storleik
        l.energy = energi
        l.color = farge
        o = bpy.data.objects.new(nm, l)
        sc.collection.objects.link(o)
        o.location = Vector(pos)
        o.rotation_euler = (M - o.location).to_track_quat("-Z", "Y").to_euler()

    flate("nokkel", (-1.25, -1.35, 1.15), 1.5, 95)                       # stor, mjuk, oppe til venstre
    flate("stripe", (-1.9, -0.25, 0.35), 0, 26, form=(0.35, 1.6))         # streiflys frå venstre: løftar relieff
    flate("front", (0.55, -2.4, 0.55), 2.2, 22)                          # brei flate framfor: noko å spegle
    flate("kant", (1.25, 0.75, 0.95), 0, 34, (0.88, 0.93, 1.0), form=(0.4, 1.4))  # kjølig kantlys bak til høgre
    flate("topp", (0.15, -0.2, 1.7), 1.2, 12)
    w = bpy.data.worlds.new("verd")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes.get("Background").inputs["Color"].default_value = (0, 0, 0, 1)
    w.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.0

    utmappe = HER / "bilete"
    utmappe.mkdir(exist_ok=True)
    fil = Path(ut) if ut else utmappe / f"{namn}{'_prove' if prove else ''}.png"
    sc.render.filepath = str(fil)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(write_still=True)
    # legg på heilt svart bakgrunn (#000)
    from PIL import Image
    im = Image.open(fil).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(fil)
    print("SKREIV", fil)
    return fil


if __name__ == "__main__":
    arg = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not arg:
        sys.exit("bruk: python sveip_hud.py <variant> [--prove]")
    sys.path.insert(0, str(HER))
    render(arg[0], prove="--prove" in sys.argv)
