# -*- coding: utf-8 -*-
"""raup_geometri.py · Parametrisk Class-A B-rep geometrikjerne for RAUP (Northern).

Byggjer produksjonsklar, 100 % gyldig OCCT B-rep geometri (grad <= 3 på alle kurva flater,
utan voksling, utan høggradig loft-bloat og utan ustabil OCCT MakeThickSolid):
  - Hovudkropp som ope-botn skal (Class-A NURBS, jamn veggtjukkleik WALL_MM)
  - Avviklingsbar (sylinderforma) optisk diffusorplate med mjuke hjørneradier + 1:1 flatmønster
  - Avtakbart aluminiums botnchassis med diffusorfot, registreringskant, batterilomme og kabelkanal
  - Stålballastplate (6 mm S235) for høg veltetryggleik
  - Utskiftbar 21700-celle, drivar/dimmar-PCB, vertikal LED-kjølesøyle i aluminium og filmklips
  - Todelt støypeform for resirkulert papirmasse

Alle mål er i millimeter (1:1-skala der total lampehøgd til topp av diffusor = TOTAL_HEIGHT_MM).
"""
from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
import uuid
import zipfile
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.BRep import BRep_Tool
from OCP.BRepTools import BRepTools
from scipy.spatial import cKDTree
from OCP.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeSolid,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_Sewing,
)
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepLib import BRepLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.Geom import Geom_BSplineSurface, Geom_Line
from OCP.Geom2d import Geom2d_BSplineCurve
from OCP.GeomAPI import GeomAPI_IntCS, GeomAPI_PointsToBSplineSurface
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt, gp_Pnt2d
from OCP.ShapeFix import ShapeFix_Face, ShapeFix_Shape, ShapeFix_Solid
from OCP.TColgp import TColgp_Array1OfPnt2d, TColgp_Array2OfPnt
from OCP.TColStd import TColStd_Array1OfInteger, TColStd_Array1OfReal
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
from scipy.interpolate import RBFInterpolator, make_interp_spline, splprep, splev
from scipy.ndimage import gaussian_filter1d
from shapely.affinity import rotate as sh_rotate
from shapely.affinity import translate as sh_translate
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry import box as sh_box
from shapely.ops import nearest_points, unary_union

ROOT = Path(__file__).resolve().parents[1]
CAD_DIR = ROOT / "cad"
OUT_DIR = ROOT / "produksjon"
TEST_DIR = ROOT / "kontroll"
PRINT_DIR = ROOT / "print"


@dataclass(frozen=True)
class RaupParams:
    """Sentrale produksjonsparametrar for RAUP (alle lengder i mm)."""
    total_height_mm: float = 200.0       # Total lampehøgd (bordplate -> topp av diffusor, kompakt 1:1)
    wall_mm: float = 2.5                 # Jamn, slank veggtjukkleik i hovudskalet
    notch_z_mm: float = 51.0             # Referansehøgd ved 270 mm (skalerast med scale_ratio -> ~37.8 mm ved 200 mm)
    r_shoulder_out_mm: float = 4.5       # Mjuk skulderradius på toppen av ytterflata (skalert)
    r_shoulder_in_mm: float = 1.6        # Indre topp-overgangsradius (skalert)
    r_inner_tip_min_mm: float = 1.6      # Minste indre krummingsradius i spiralspissen
    n_u_pts: int = 96                    # Periodiske U-støttepunkt rundt omkrinsen
    dome_grid: int = 14                  # Rutenett for glatt bikubisk toppkuppel
    base_plate_h_mm: float = 3.0         # Tjukkleik på botnchassis-plata under hovudskalet
    chassis_lip_h_mm: float = 8.0        # Innvendig styrekant opp i hovudskalet
    chassis_clear_mm: float = 0.40       # Radiell glidpassning mellom chassis og indre skalvegg
    diffuser_thick_mm: float = 1.0       # Tjukkleik på bøybar monitor-diffusor/prismefilm
    diffuser_slot_w_mm: float = 1.40     # Sporbreidd i diffusorfoten (+0.20 mm klaring per side)
    diffuser_z_seat_mm: float = 6.0      # Nedre kant på diffusoren nede i fotsporet
    diffuser_plinth_h_mm: float = 10.5   # Høgd på diffusorfoten
    ballast_thick_mm: float = 5.0        # Stålplate S235 ballast (z = base_plate_h + 1.0 .. +6.0)
    p1s_bed_mm: float = 256.0            # Bambu Lab P1S byggjeplate
    fuzzy_skin_thickness_mm: float = 0.10     # Fin papirmasse-/steinstruktur på yttervegg (Bambu Fuzzy Skin)
    fuzzy_skin_point_dist_mm: float = 0.25    # Tett mikro-kornavstand på yttervegg (Bambu Fuzzy Skin)


# ---------------------------------------------------------------------------
# Kjeldedata frå FBX-målenettet (skalert eksakt til total_height_mm)
# ---------------------------------------------------------------------------

def load_fbx_scaled(total_height_mm: float = 270.0):
    npz = np.load(TEST_DIR / "fbx_malenett.npz")
    sc = float(total_height_mm) / float(npz["c006"][:, 2].max())
    zero = np.array([0.15, -0.25, 0.0])
    parts = {k: (npz[k] - zero) * sc for k in npz.files if not k.endswith("_tri")}
    tris = {k[:-4]: npz[k] for k in npz.files if k.endswith("_tri")}
    return parts, tris, sc


def section_mesh(verts: np.ndarray, tri_idx: np.ndarray, z: float) -> np.ndarray:
    t = verts[tri_idx]
    t = t[(t[:, :, 2].min(1) < z) & (t[:, :, 2].max(1) > z)]
    segs = []
    for face in t:
        ends = []
        for p, q in zip(face, np.roll(face, -1, axis=0)):
            if (p[2] < z) != (q[2] < z):
                ends.append(p[:2] + (z - p[2]) / (q[2] - p[2]) * (q[:2] - p[:2]))
        if len(ends) == 2:
            segs.append(ends)
    return np.array(segs) if segs else np.empty((0, 2, 2))


def trace_loops(seg: np.ndarray):
    adj = {}
    for a, b in seg:
        ka = tuple(np.round(a, 3))
        kb = tuple(np.round(b, 3))
        if ka == kb:
            continue
        adj.setdefault(ka, set()).add(kb)
        adj.setdefault(kb, set()).add(ka)
    lines = []
    while adj:
        start = next((a for a, v in adj.items() if len(v) == 1), next(iter(adj)))
        line = [start]
        q = start
        while q in adj:
            v = next(iter(adj[q]))
            adj[q].remove(v)
            adj[v].remove(q)
            if not adj[q]:
                del adj[q]
            if v in adj and not adj[v]:
                del adj[v]
            line.append(v)
            q = v
        lines.append(np.array(line))
    return sorted(lines, key=lambda p: -np.linalg.norm(np.diff(p, axis=0), axis=1).sum())


def clean_ccw(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    if len(p) > 1 and np.allclose(p[0], p[-1]):
        p = p[:-1]
    if not Polygon(p).exterior.is_ccw:
        p = p[::-1]
    return p


def fit_periodic_tck(pts: np.ndarray, s: float = 10.0, n_fit: int = 600):
    pts = clean_ccw(pts)
    cl = np.vstack([pts, pts[:1]])
    d = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(cl, axis=0), axis=1))]
    u = np.linspace(0.0, d[-1], n_fit, endpoint=False)
    q = np.column_stack([np.interp(u, d, cl[:, 0]), np.interp(u, d, cl[:, 1])])
    tck, _ = splprep([np.r_[q[:, 0], q[0, 0]], np.r_[q[:, 1], q[0, 1]]], s=s, per=True, k=3)
    return tck


# ---------------------------------------------------------------------------
# Class-A B-spline hjelparar (grad <= 3, eksakt periodisk U-kontinuitet)
# ---------------------------------------------------------------------------

def _solve_periodic_cubic_poles(vals: np.ndarray) -> np.ndarray:
    """Løys eksakte kontrollpunkt for uniform periodisk kubisk B-spline (OCCT-indeksering)."""
    n = vals.shape[0]
    a = np.zeros((n, n))
    for i in range(n):
        a[i, (i - 1) % n] = 1.0 / 6.0
        a[i, i] = 4.0 / 6.0
        a[i, (i + 1) % n] = 1.0 / 6.0
    poles = np.linalg.solve(a, vals.reshape(n, -1)).reshape(vals.shape)
    return np.roll(poles, 1, axis=0)


def _make_periodic_u_bspline_surface(grid_xyz: np.ndarray, v_deg: int = 3) -> Geom_BSplineSurface:
    n, m, _ = grid_xyz.shape
    q_u = _solve_periodic_cubic_poles(grid_xyz)
    v_deg = min(v_deg, m - 1)
    if v_deg == 1:
        p = q_u
        v_knots_uniq = np.linspace(0.0, 1.0, m)
        v_mults = [2] + [1] * (m - 2) + [2]
    else:
        v_par = np.linspace(0.0, 1.0, m)
        spl_v = make_interp_spline(v_par, q_u.transpose(1, 0, 2), k=3, axis=0)
        p = spl_v.c.transpose(1, 0, 2)
        v_knots_uniq, v_counts = np.unique(np.round(spl_v.t, 12), return_counts=True)
        v_mults = [int(c) for c in v_counts]

    nu, nv = p.shape[0], p.shape[1]
    poles = TColgp_Array2OfPnt(1, nu, 1, nv)
    for i in range(nu):
        for j in range(nv):
            poles.SetValue(i + 1, j + 1, gp_Pnt(float(p[i, j, 0]), float(p[i, j, 1]), float(p[i, j, 2])))

    u_knots = TColStd_Array1OfReal(1, nu + 1)
    u_mults = TColStd_Array1OfInteger(1, nu + 1)
    for i in range(nu + 1):
        u_knots.SetValue(i + 1, float(i) / nu)
        u_mults.SetValue(i + 1, 1)

    vk = TColStd_Array1OfReal(1, len(v_knots_uniq))
    vm = TColStd_Array1OfInteger(1, len(v_mults))
    for j, (kv, mv) in enumerate(zip(v_knots_uniq, v_mults)):
        vk.SetValue(j + 1, float(kv))
        vm.SetValue(j + 1, int(mv))

    return Geom_BSplineSurface(poles, u_knots, vk, u_mults, vm, 3, v_deg, True, False)


def _make_periodic_2d_curve(uvs: np.ndarray) -> Geom2d_BSplineCurve:
    n = len(uvs)
    p_uv = _solve_periodic_cubic_poles(uvs)
    poles = TColgp_Array1OfPnt2d(1, n)
    for i in range(n):
        poles.SetValue(i + 1, gp_Pnt2d(float(p_uv[i, 0]), float(p_uv[i, 1])))
    u_knots = TColStd_Array1OfReal(1, n + 1)
    u_mults = TColStd_Array1OfInteger(1, n + 1)
    for i in range(n + 1):
        u_knots.SetValue(i + 1, float(i) / n)
        u_mults.SetValue(i + 1, 1)
    return Geom2d_BSplineCurve(poles, u_knots, u_mults, 3, True)


def _make_bspline_surf(x_grid: np.ndarray, y_grid: np.ndarray, z_grid: np.ndarray):
    ni, nj = x_grid.shape
    arr = TColgp_Array2OfPnt(1, ni, 1, nj)
    for i in range(ni):
        for j in range(nj):
            arr.SetValue(i + 1, j + 1, gp_Pnt(float(x_grid[i, j]), float(y_grid[i, j]), float(z_grid[i, j])))
    return GeomAPI_PointsToBSplineSurface(arr, 3, 3).Surface()


def _eval_surf_vertical(xy: np.ndarray, occt_surf):
    zs = np.empty(len(xy))
    uvs = np.empty((len(xy), 2))
    for i, (x, y) in enumerate(xy):
        lin = Geom_Line(gp_Lin(gp_Pnt(float(x), float(y), 0.0), gp_Dir(0, 0, 1)))
        inter = GeomAPI_IntCS(lin, occt_surf)
        if not (inter.IsDone() and inter.NbPoints() >= 1):
            raise RuntimeError(f"Ingen vertikal skjeringspunkt mot toppflata ved ({x:.2f}, {y:.2f})")
        p = inter.Point(1)
        u_p, v_p, _ = inter.Parameters(1)
        zs[i] = p.Z()
        uvs[i] = [u_p, v_p]
    return zs, uvs


def _make_extruded_poly_solid(poly_2d: Polygon, z0: float, z1: float, s: float = 0.8, n_pts: int = 64) -> cq.Solid:
    coords = clean_ccw(np.asarray(poly_2d.exterior.coords))
    tck = fit_periodic_tck(coords, s=s, n_fit=450)
    uu = np.linspace(0.0, 1.0, n_pts, endpoint=False)
    xs, ys = splev(uu, tck)
    w = cq.Wire.assembleEdges([
        cq.Edge.makeSpline([cq.Vector(float(x), float(y), float(z0)) for x, y in zip(xs, ys)], periodic=True)
    ])
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), cq.Vector(0, 0, float(z1 - z0)))


def _build_domed_solid_classA(
    poly_2d: Polygon,
    occt_surf,
    r_shoulder: float,
    z_bottom: float,
    n_pts: int = 96,
    s_outer: float = 10.0,
):
    """Bygg 4-flaters vanntett Class-A B-rep solid: plan botn, vertikal vegg, mjuk skulder og kuppel."""
    pts0 = clean_ccw(np.asarray(poly_2d.exterior.coords))
    tck0 = fit_periodic_tck(pts0, s=s_outer)
    uu = np.linspace(0.0, 1.0, n_pts, endpoint=False)
    xy0 = np.column_stack(splev(uu, tck0))
    if not Polygon(xy0).exterior.is_ccw:
        xy0 = xy0[::-1]
    uu_d = np.linspace(0.0, 1.0, 800, endpoint=False)
    dense0 = np.column_stack(splev(uu_d, tck0))
    if not Polygon(dense0).exterior.is_ccw:
        dense0 = dense0[::-1]
    poly_s = Polygon(dense0).buffer(0)

    def map_ortho_to_ring(prev_xy: np.ndarray, poly_ring: Polygon) -> np.ndarray:
        coords_r = clean_ccw(np.asarray(poly_ring.exterior.coords))
        ext = LineString(np.vstack([coords_r, coords_r[:1]]))
        length = ext.length
        s_vals = np.array([ext.project(Point(float(x), float(y))) for x, y in prev_xy])
        diffs = np.diff(np.r_[s_vals, s_vals[0]])
        diffs = (diffs + 0.5 * length) % length - 0.5 * length
        if np.median(diffs) <= 0:
            raise RuntimeError("Feil omløpsretning under ortogonal skuldermapping")
        min_step = 0.20 * (length / len(prev_xy))
        steps = np.maximum(diffs, min_step)
        steps *= length / steps.sum()
        s_mono = (s_vals[0] + np.r_[0.0, np.cumsum(steps[:-1])]) % length
        raw_xy = np.array([[ext.interpolate(float(sv)).x, ext.interpolate(float(sv)).y] for sv in s_mono])
        sm_xy = gaussian_filter1d(raw_xy, sigma=0.5, axis=0, mode="wrap")
        return np.array([
            [nearest_points(ext, Point(float(x), float(y)))[0].x,
             nearest_points(ext, Point(float(x), float(y)))[0].y]
            for x, y in sm_xy
        ])

    thetas = np.radians([0.0, 12.0, 30.0, 50.0, 70.0, 82.0, 90.0])
    ring_xys = [xy0]
    for th in thetas[1:]:
        d_in = r_shoulder * (1.0 - math.cos(float(th)))
        pr = poly_s.buffer(-d_in, join_style=1, quad_segs=32)
        if pr.geom_type == "MultiPolygon":
            pr = max(pr.geoms, key=lambda g: g.area)
        tck_pr = fit_periodic_tck(clean_ccw(np.asarray(pr.exterior.coords)), s=1.0, n_fit=500)
        pr_smooth = Polygon(np.column_stack(splev(uu_d, tck_pr))).buffer(0)
        ring_xys.append(map_ortho_to_ring(ring_xys[-1], pr_smooth))

    sh_grid = np.empty((n_pts, len(thetas), 3))
    cap_uvs = None
    for k, th in enumerate(thetas):
        z_surf, uvs = _eval_surf_vertical(ring_xys[k], occt_surf)
        h_drop = r_shoulder * (1.0 - math.sin(float(th)))
        sh_grid[:, k, :2] = ring_xys[k]
        sh_grid[:, k, 2] = z_surf - h_drop
        if k == len(thetas) - 1:
            cap_uvs = uvs

    if not Polygon(cap_uvs).exterior.is_ccw:
        cap_uvs = cap_uvs[::-1]
        sh_grid = sh_grid[::-1]

    c2d = _make_periodic_2d_curve(cap_uvs)

    wall_grid = np.empty((n_pts, 2, 3))
    wall_grid[:, 0, :2] = sh_grid[:, 0, :2]
    wall_grid[:, 0, 2] = z_bottom
    wall_grid[:, 1, :] = sh_grid[:, 0, :]
    wall_surf = _make_periodic_u_bspline_surface(wall_grid, v_deg=1)
    sh_surf = _make_periodic_u_bspline_surface(sh_grid, v_deg=3)

    gaps = [
        sh_surf.Value(float(t), 1.0).Distance(occt_surf.Value(c2d.Value(float(t)).X(), c2d.Value(float(t)).Y()))
        for t in np.linspace(0.0, 1.0, 300, endpoint=False)
    ]
    max_gap = float(max(gaps))

    wall_face = BRepBuilderAPI_MakeFace(wall_surf, 1e-4).Face()
    sh_face = BRepBuilderAPI_MakeFace(sh_surf, 1e-4).Face()

    edge_cap = BRepBuilderAPI_MakeEdge(c2d, occt_surf).Edge()
    BRepLib.BuildCurve3d_s(edge_cap)
    wire_cap = BRepBuilderAPI_MakeWire(edge_cap).Wire()
    mf_cap = BRepBuilderAPI_MakeFace(occt_surf, wire_cap, True)
    sff = ShapeFix_Face(mf_cap.Face())
    sff.FixOrientation()
    sff.Perform()
    cap_face = sff.Face()

    bot_iso = wall_surf.VIso(0.0)
    bot_edge = BRepBuilderAPI_MakeEdge(bot_iso).Edge()
    bot_wire = BRepBuilderAPI_MakeWire(bot_edge).Wire()
    bot_face = BRepBuilderAPI_MakeFace(bot_wire, True).Face()

    sew = BRepBuilderAPI_Sewing(max(0.05, max_gap * 2.5))
    sew.Add(bot_face)
    sew.Add(wall_face)
    sew.Add(sh_face)
    sew.Add(cap_face)
    sew.Perform()
    if sew.NbFreeEdges() != 0:
        raise RuntimeError(f"Sying etterlét {sew.NbFreeEdges()} opne kantar (max_gap={max_gap:.4f} mm)")

    shell_topo = TopoDS.Shell_s(sew.SewedShape())
    ms = BRepBuilderAPI_MakeSolid(shell_topo)
    sfs = ShapeFix_Solid(ms.Solid())
    sfs.Perform()
    solid = cq.Solid(TopoDS.Solid_s(sfs.Solid()))
    if solid.Volume() < 0:
        s_rev = solid.wrapped
        s_rev.Reverse()
        solid = cq.Solid(s_rev)
    shf = ShapeFix_Shape(solid.wrapped)
    shf.Perform()
    solid = cq.Solid(TopoDS.Solid_s(shf.Shape()))
    if not BRepCheck_Analyzer(solid.wrapped).IsValid():
        raise RuntimeError("Class-A solid bestod ikkje BRepCheck_Analyzer")
    return solid, poly_s, max_gap


# ---------------------------------------------------------------------------
# 1. HOVUDKROPP (OPE-BOTN SKAL + YTRE SOLID)
# ---------------------------------------------------------------------------

def build_main_body_shell(params: RaupParams = RaupParams()):
    """Bygg den produksjonsklare hovudkroppen: ope botn, jamn veggtjukkleik, Class-A B-rep."""
    parts, tris, sc = load_fbx_scaled(params.total_height_mm)
    scale_ratio = params.total_height_mm / 270.0
    c1, c1_tri = parts["c001"], tris["c001"]

    p85 = clean_ccw(trace_loops(section_mesh(c1, c1_tri, 85.0 * scale_ratio + 0.0137))[0])
    p15 = clean_ccw(trace_loops(section_mesh(c1, c1_tri, 15.0 * scale_ratio + 0.0137))[0])
    poly85_raw = Polygon(p85).buffer(0)

    # Glatt bikubisk toppkuppel (TPS-RBF til indre topp-punkt av c001)
    tri_pts = c1[c1_tri]
    n_vec = np.cross(tri_pts[:, 1] - tri_pts[:, 0], tri_pts[:, 2] - tri_pts[:, 0])
    nz = n_vec[:, 2] / np.maximum(np.linalg.norm(n_vec, axis=1), 1e-12)
    top_idx = np.unique(c1_tri[nz > 0.30].ravel())
    tv = c1[top_idx]
    dists = np.array([poly85_raw.exterior.distance(Point(x, y)) for x, y in tv[:, :2]])
    m_int = dists > (3.5 * scale_ratio)
    rbf = RBFInterpolator(tv[m_int, :2], tv[m_int, 2], kernel="thin_plate_spline", smoothing=250.0 * (scale_ratio ** 2))

    margin = 20.0 * scale_ratio
    xmin, ymin, xmax, ymax = poly85_raw.bounds
    gx = np.linspace(xmin - margin, xmax + margin, params.dome_grid)
    gy = np.linspace(ymin - margin, ymax + margin, params.dome_grid)
    xx, yy = np.meshgrid(gx, gy, indexing="ij")
    zz = rbf(np.column_stack([xx.ravel(), yy.ravel()])).reshape(xx.shape)

    # Eksakt 3D parallell normalforskyving for indre kuppelflate
    dz_dx = np.gradient(zz, gx[1] - gx[0], axis=0)
    dz_dy = np.gradient(zz, gy[1] - gy[0], axis=1)
    nlen = np.sqrt(dz_dx ** 2 + dz_dy ** 2 + 1.0)
    xx_in = xx - params.wall_mm * (-dz_dx / nlen)
    yy_in = yy - params.wall_mm * (-dz_dy / nlen)
    zz_in = zz - params.wall_mm * (1.0 / nlen)

    surf_out = _make_bspline_surf(xx, yy, zz)
    surf_in = _make_bspline_surf(xx_in, yy_in, zz_in)

    # Ytre og indre kuppel-solid
    outer_domed, poly_up_out, gap_out = _build_domed_solid_classA(
        poly85_raw, surf_out,
        r_shoulder=params.r_shoulder_out_mm * scale_ratio,
        z_bottom=0.0,
        n_pts=params.n_u_pts,
        s_outer=10.0 * (scale_ratio ** 2),
    )

    r_tip = params.r_inner_tip_min_mm
    poly_up_in = (
        poly_up_out.buffer(-(params.wall_mm + r_tip), join_style=1, quad_segs=32)
        .buffer(r_tip, join_style=1, quad_segs=32)
    )
    if poly_up_in.geom_type != "Polygon":
        raise RuntimeError(f"Indre øvre snitt splitta ved vegg={params.wall_mm} mm: {poly_up_in.geom_type}")

    inner_domed, poly_up_in_s, gap_in = _build_domed_solid_classA(
        poly_up_in, surf_in,
        r_shoulder=params.r_shoulder_in_mm * scale_ratio,
        z_bottom=-10.0,
        n_pts=params.n_u_pts,
        s_outer=2.5 * (scale_ratio ** 2),
    )

    # Glatt arkitektonisk innsprang bak-høgre (z = 0 .. notch_z_mm) med vinkelrett (~85-90 grad) utgang
    # (hindrar tangentiell boolean-flising ved hjørna!)
    notch_z = params.notch_z_mm * scale_ratio
    notch_mask = np.array([poly85_raw.exterior.distance(Point(pt)) > (2.4 * scale_ratio) for pt in p15])
    start_non = int(np.where(~notch_mask)[0][0])
    p15r = np.roll(p15, -start_non, axis=0)
    nmr = np.roll(notch_mask, -start_non)
    ni = np.where(nmr)[0]
    seg_notch = p15r[ni[0] : ni[-1] + 1]

    dir_start_out = seg_notch[0] - seg_notch[4]
    dir_start_out /= np.linalg.norm(dir_start_out)
    dir_end_out = seg_notch[-1] - seg_notch[-5]
    dir_end_out /= np.linalg.norm(dir_end_out)

    ext_start = [seg_notch[0] + d * dir_start_out for d in (14.0 * scale_ratio, 9.0 * scale_ratio, 4.0 * scale_ratio)]
    ext_end = [seg_notch[-1] + d * dir_end_out for d in (4.0 * scale_ratio, 9.0 * scale_ratio, 14.0 * scale_ratio)]
    pts_full = np.vstack([ext_start, seg_notch, ext_end])
    d_n = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts_full, axis=0), axis=1))]
    u_n = np.linspace(0.0, d_n[-1], 140)
    qn = np.column_stack([np.interp(u_n, d_n, pts_full[:, 0]), np.interp(u_n, d_n, pts_full[:, 1])])
    tck_n, _ = splprep([qn[:, 0], qn[:, 1]], s=1.2 * (scale_ratio ** 2), k=3)
    xn, yn = splev(np.linspace(0.0, 1.0, 72), tck_n)

    x_far = xmax + 30.0 * scale_ratio
    notch_poly_pts = np.vstack([
        np.column_stack([xn, yn]),
        [x_far, yn[-1] + 15.0 * scale_ratio],
        [x_far, yn[0] - 15.0 * scale_ratio],
    ])
    poly_notch_out = Polygon(notch_poly_pts).buffer(0).buffer(-3.0 * scale_ratio, join_style=1).buffer(3.0 * scale_ratio, join_style=1)
    poly_notch_in = poly_notch_out.buffer(params.wall_mm, join_style=1, quad_segs=24)

    outer_body = outer_domed.cut(_make_extruded_poly_solid(poly_notch_out, -5.0, notch_z, s=0.3, n_pts=96))
    inner_cavity = inner_domed.cut(_make_extruded_poly_solid(poly_notch_in, -15.0, notch_z + params.wall_mm, s=0.3, n_pts=96))
    shell_base = outer_body.cut(inner_cavity)

    # Skarp horisontal debossed skuggelinje (0.72 mm djup x 1.45 mm høg med 45-graders sjølvberande fas)
    # i flukt med innsprangshøgda z = notch_z, som følgjer heile den konvekse ytterveggen frå innspranget
    # og tonar mjukt ut til eit spisst punkt rundt den avrunda front-spiralnasen!
    g_depth = 0.72
    g_h = 1.45
    z_g0 = notch_z
    z_g1 = z_g0 + g_h

    pts_ring = np.asarray(poly_up_out.exterior.coords[:-1], dtype=np.float64)
    n_ring = len(pts_ring)
    ch_ext = poly_up_out.convex_hull.exterior
    hull_not_notch = np.array([
        (ch_ext.distance(Point(xy)) < 1.2 * scale_ratio) and (not poly_notch_out.contains(Point(xy)))
        for xy in pts_ring
    ])
    starts_g = np.where((~np.roll(hull_not_notch, 1)) & hull_not_notch)[0]
    ends_g = np.where(hull_not_notch & (~np.roll(hull_not_notch, -1)))[0]
    i_nose = int(starts_g[0])
    i_step = int(ends_g[0])
    span_g = (i_step - i_nose) % n_ring
    seq_g = (np.arange(i_nose - 34, i_nose + span_g + 4)) % n_ring
    arc_xy = pts_ring[seq_g]
    ds_g = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(arc_xy, axis=0), axis=1))]
    total_g_len = float(ds_g[-1])

    tang_g = np.gradient(arc_xy, axis=0)
    tlen_g = np.maximum(np.linalg.norm(tang_g, axis=1, keepdims=True), 1e-12)
    tang_g /= tlen_g
    # pts_ring er CCW -> innover-normal mot veggen er (-ty, tx)
    n_in_g = np.column_stack([-tang_g[:, 1], tang_g[:, 0]])

    # Mjuk cosinus-utfasing rundt front-spiralnasen (s = 2..24 mm) og mjuk innfasing ved innsprangshjørnet
    t_nose = np.clip((ds_g - 2.0 * scale_ratio) / (22.0 * scale_ratio), 0.0, 1.0)
    w_nose = 0.5 * (1.0 - np.cos(np.pi * t_nose))
    t_step = np.clip((total_g_len - ds_g - 1.0 * scale_ratio) / (5.5 * scale_ratio), 0.0, 1.0)
    w_step = 0.5 * (1.0 - np.cos(np.pi * t_step))
    w_taper = w_nose * w_step

    # Når w_taper -> 0 går kutteprofilen -0.35 mm UT i fri luft slik at sporet spissar 100 % mjukt ut i overflata
    d_inward = (g_depth + 0.35) * w_taper - 0.35
    inner_g_pts = arc_xy + d_inward[:, None] * n_in_g
    outer_g_pts = arc_xy - 1.6 * n_in_g
    ring_floor_2d = Polygon(np.vstack([inner_g_pts, outer_g_pts[::-1]])).buffer(0)
    if ring_floor_2d.geom_type == "MultiPolygon":
        ring_floor_2d = max(ring_floor_2d.geoms, key=lambda g: g.area)

    groove_box = _make_extruded_poly_solid(ring_floor_2d, z_g0, z_g1, s=0.08, n_pts=160)
    try:
        groove_cutter = cq.Workplane(obj=groove_box).edges("#Z").chamfer(0.45).val()
    except Exception:
        groove_cutter = groove_box

    shell = shell_base.cut(groove_cutter)

    if not (shell.isValid() and BRepCheck_Analyzer(shell.wrapped).IsValid() and len(shell.Solids()) == 1):
        raise RuntimeError("Ferdig hovudskal med debossed skuggelinje feila BRepCheck_Analyzer")

    # Eksakte 2D-polygon for botnsnitt (ytre og indre) til chassis, ballast og verifisering
    poly_base_out = poly_up_out.difference(poly_notch_out).buffer(0)
    poly_base_in = poly_up_in_s.difference(poly_notch_in).buffer(0)

    meta = {
        "scale_mm_per_BU": sc,
        "scale_ratio": scale_ratio,
        "notch_z_mm": notch_z,
        "deboss_groove_z_mm": [round(z_g0, 2), round(z_g1, 2)],
        "deboss_groove_depth_mm": g_depth,
        "seam_gap_out_mm": round(gap_out, 5),
        "seam_gap_in_mm": round(gap_in, 5),
        "poly_up_out": poly_up_out,
        "poly_up_in": poly_up_in_s,
        "poly_base_out": poly_base_out,
        "poly_base_in": poly_base_in,
        "poly_notch_out": poly_notch_out,
        "rbf_dome": rbf,
    }
    return shell, outer_body, meta


# ---------------------------------------------------------------------------
# 2. AVVIKLINGSBAR DIFFUSORPLATE + 1:1 FLATMØNSTER (MJUKE HJØRNE)
# ---------------------------------------------------------------------------

def build_diffuser_and_flat(body_meta: dict, params: RaupParams = RaupParams()):
    """Bygg 100 % avviklingsbar sylinderforma diffusor (ingen kollisjon mot hovudskalet) + 1:1 flatmønster."""
    parts, tris, _ = load_fbx_scaled(params.total_height_mm)
    scale_ratio = body_meta["scale_ratio"]
    c6, c6_tri = parts["c006"], tris["c006"]
    poly_body = body_meta["poly_up_out"]

    p6_100 = Polygon(trace_loops(section_mesh(c6, c6_tri, 100.0 * scale_ratio + 0.0137))[0]).buffer(0)

    # Trekk ut glatt senterkurve i XY
    center = np.array([25.0, -70.0]) * scale_ratio
    thetas = np.linspace(math.radians(170.0), math.radians(10.0), 140)
    mid_pts = []
    for th in thetas:
        ray = LineString([center, center + 240.0 * scale_ratio * np.array([math.cos(th), math.sin(th)])])
        inter = p6_100.intersection(ray)
        if inter.geom_type == "LineString" and inter.length > 0.4:
            mid_pts.append(np.array(inter.coords).mean(axis=0))
    mid_pts = np.array(mid_pts)

    # Kutt venstre startkant slik at diffusoren ligg pent i spiralmunningen med >= 1.5 mm fysisk klaring!
    min_center_dist = 0.5 * params.diffuser_thick_mm + 1.5
    dists = np.array([poly_body.distance(Point(x, y)) for x, y in mid_pts])
    keep = np.where(dists >= min_center_dist)[0]
    cl_raw = mid_pts[keep[0] : keep[-1] + 1]

    tck_cl, _ = splprep([cl_raw[:, 0], cl_raw[:, 1]], s=2.5 * (scale_ratio ** 2), k=3)
    uu = np.linspace(0.0, 1.0, 400)
    x_cl, y_cl = splev(uu, tck_cl)
    dx_cl, dy_cl = splev(uu, tck_cl, der=1)
    ddx_cl, ddy_cl = splev(uu, tck_cl, der=2)
    kappa = np.abs(dx_cl * ddy_cl - dy_cl * ddx_cl) / np.maximum((dx_cl ** 2 + dy_cl ** 2) ** 1.5, 1e-12)
    min_bend_r = float(1.0 / np.max(kappa))

    cl_dense = np.column_stack([x_cl, y_cl])
    u_arc = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(cl_dense, axis=0), axis=1))]
    total_arc = float(u_arc[-1])

    # Pakk ut alle c006-punkt til (u, z) for eksakt mjuke-hjørne silhuett (jf. cad_visning_1/2 og 01_hero)
    dmat = np.linalg.norm(c6[:, None, :2] - cl_dense[None, :, :], axis=2)
    nearest_i = np.argmin(dmat, axis=1)
    u_v = u_arc[nearest_i]
    z_v = c6[:, 2]

    # Bygg reint, avrunda 2D flatmønster i (u, z)
    # Nedre kant setjast nede i diffusorfotsporet (z_seat = 7.5 mm) midt på, og rundar mjuke hjørne opp mot endane
    n_bins = 28
    u_edges = np.linspace(0.0, total_arc, n_bins + 1)
    u_mid, z_top_raw, z_bot_raw = [], [], []
    for i in range(n_bins):
        m = (u_v >= u_edges[i]) & (u_v <= u_edges[i + 1])
        if np.sum(m) >= 5:
            u_mid.append(0.5 * (u_edges[i] + u_edges[i + 1]))
            z_top_raw.append(float(np.percentile(z_v[m], 99)))
            z_bot_raw.append(float(np.percentile(z_v[m], 1)))

    # Tilpass skulpturell silhuett med runde hjørne (som cad_visning_1 og 01_hero!)
    # Lag ei glatt overkant- og underkantkurve med runde overgangar ved u=0 og u=total_arc
    u_mid = np.asarray(u_mid)
    z_top_raw = np.asarray(z_top_raw)
    z_bot_raw = np.asarray(z_bot_raw)

    # Skaler topp-kurva så maks høgd blir eksakt total_height_mm (270.0 mm)
    z_shift_top = params.total_height_mm - float(np.max(z_top_raw))
    z_top_raw = z_top_raw + z_shift_top

    # Flatmønster-polygon med avrunda hjørne via glatt polynom/spline + buffer-avrunding!
    # Ekstrapoler litt ut til u=0 og u=total_arc, bygg lukka polygon og rund av hjørna med R = 24 mm!
    u_dense_flat = np.linspace(0.0, total_arc, 120)
    top_coef = np.polyfit(u_mid[1:-1], z_top_raw[1:-1], deg=3)
    bot_coef = np.polyfit(u_mid[2:-2], z_bot_raw[2:-2], deg=2)
    z_top_curve = np.polyval(top_coef, u_dense_flat)
    z_bot_curve = np.polyval(bot_coef, u_dense_flat)
    # Fest toppen eksakt på total_height_mm og senk nedre midtparti til diffusor-setehøgd (7.5 mm)
    z_top_curve += params.total_height_mm - float(z_top_curve.max())
    z_bot_curve = np.maximum(z_bot_curve - (float(z_bot_curve.min()) - params.diffuser_z_seat_mm), params.diffuser_z_seat_mm)

    raw_flat_poly = Polygon(
        np.vstack([
            np.column_stack([u_dense_flat, z_top_curve]),
            np.column_stack([u_dense_flat[::-1], z_bot_curve[::-1]]),
        ])
    ).buffer(0)
    # Rund av alle 4 hjørne skulpturelt (R = 22 mm på ytterkantane) — akkurat som i 01_hero.png & cad_visning_1!
    r_corner = 22.0 * scale_ratio
    flat_poly = raw_flat_poly.buffer(-r_corner, join_style=1, quad_segs=24).buffer(r_corner, join_style=1, quad_segs=24)
    # Følg toppen eksakt til total_height_mm og botn til diffuser_z_seat_mm etter avrunding
    fu_min, fz_min, fu_max, fz_max = flat_poly.bounds
    flat_coords = clean_ccw(np.asarray(flat_poly.exterior.coords))
    # Strekk Z ørlite (<0.5 mm) så maks Z = total_height_mm og min Z = diffuser_z_seat_mm
    flat_coords[:, 1] = params.diffuser_z_seat_mm + (flat_coords[:, 1] - fz_min) * (
        (params.total_height_mm - params.diffuser_z_seat_mm) / (fz_max - fz_min)
    )
    # Klem u til [0, total_arc]
    flat_coords[:, 0] = np.clip((flat_coords[:, 0] - fu_min) * (total_arc / (fu_max - fu_min)), 0.0, total_arc)
    flat_poly_final = Polygon(flat_coords).buffer(0)

    # Konstruer 3D B-rep diffusorplate eksakt frå flat_poly_final vikla rundt cl_dense!
    # Metode: bygg rein sylinder-ekstrudering (thickness = 1.0 mm) med høgd [0..280],
    # og klipp ut profilen ved å byggje ein presis loft av rette tverrsnitt langs u (med avrunda ender)!
    # Endå reinare og 100 % nøyaktig: lag 3D-skalet av for- og bakflate som to eksakte NURBS-flater
    # eller tett tverrsnitt-loft frå u = u_min + eps til u_max - eps med 45 seksjonar som følgjer flat_poly_final!
    u_samples = np.concatenate([
        np.linspace(0.4, 18.0, 12),
        np.linspace(22.0, total_arc - 22.0, 24),
        np.linspace(total_arc - 18.0, total_arc - 0.4, 12),
    ])

    def cl_point_normal(u_val: float):
        x = float(np.interp(u_val, u_arc, x_cl))
        y = float(np.interp(u_val, u_arc, y_cl))
        tx = float(np.interp(u_val, u_arc, dx_cl))
        ty = float(np.interp(u_val, u_arc, dy_cl))
        tl = math.hypot(tx, ty)
        # Normal som peikar bakover (+Y ved toppen av bogen)
        nx, ny = -ty / tl, tx / tl
        return np.array([x, y]), np.array([nx, ny])

    half_t = 0.5 * params.diffuser_thick_mm
    wires = []
    for u_val in u_samples:
        vline = LineString([(u_val, -10.0), (u_val, params.total_height_mm + 20.0)])
        inter = flat_poly_final.intersection(vline)
        if inter.is_empty:
            continue
        zb, zt = inter.bounds[1], inter.bounds[3]
        if zt - zb < 2.0:
            continue
        p0, n0 = cl_point_normal(u_val)
        p_lo = p0 - half_t * n0
        p_hi = p0 + half_t * n0
        verts = [
            cq.Vector(float(p_lo[0]), float(p_lo[1]), float(zb)),
            cq.Vector(float(p_hi[0]), float(p_hi[1]), float(zb)),
            cq.Vector(float(p_hi[0]), float(p_hi[1]), float(zt)),
            cq.Vector(float(p_lo[0]), float(p_lo[1]), float(zt)),
        ]
        wires.append(cq.Wire.makePolygon(verts, close=True))

    diffuser_solid = cq.Solid.makeLoft(wires, ruled=False)
    if not BRepCheck_Analyzer(diffuser_solid.wrapped).IsValid():
        shf = ShapeFix_Shape(diffuser_solid.wrapped)
        shf.Perform()
        diffuser_solid = cq.Solid(TopoDS.Solid_s(shf.Shape()))
    if not (diffuser_solid.isValid() and BRepCheck_Analyzer(diffuser_solid.wrapped).IsValid()):
        raise RuntimeError("Diffusor-solid feila BRepCheck_Analyzer")

    diff_meta = {
        "centerline_xy": cl_dense,
        "u_arc": u_arc,
        "total_arc_mm": round(total_arc, 2),
        "min_bend_radius_mm": round(min_bend_r, 1),
        "min_clearance_to_body_mm": round(float(min(poly_body.distance(Point(x, y)) for x, y in cl_dense) - half_t), 2),
        "flat_coords": clean_ccw(np.asarray(flat_poly_final.exterior.coords)),
        "flat_area_cm2": round(float(flat_poly_final.area / 100.0), 1),
        "cl_point_normal": cl_point_normal,
    }
    return diffuser_solid, diff_meta


# ---------------------------------------------------------------------------
# 3. KOMPLETT PRODUKSJONS-SAMANSTILLING (BOTNCHASSIS, BALLAST, BATTERI, PCB, LED, KLIPS)
# ---------------------------------------------------------------------------

def build_assembly_components(body_meta: dict, diff_meta: dict, params: RaupParams = RaupParams()):
    """Bygg alle funksjonelle komponentar i produksjonssamanstillinga med garantert klaring (0 kollisjon)."""
    scale_ratio = body_meta["scale_ratio"]
    poly_base_out: Polygon = body_meta["poly_base_out"]
    poly_base_in: Polygon = body_meta["poly_base_in"]
    cl_xy = diff_meta["centerline_xy"]
    u_arc = diff_meta["u_arc"]
    total_arc = float(u_arc[-1])

    z_plate = params.base_plate_h_mm  # 3.5 mm: hovudskalet kviler på z = 3.5 mm i samanstillinga!

    # --- A. Botnchassis (02_raup_botn_chassis) ---
    # 1) Nedre botnplate (z = 0..3.5 mm): følgjer hovudkroppen sin fot + glatt bro fram til diffusorfoten
    #    (med 0.8 mm skuggefuge-innsprang langs ytterkanten så hovudskalet får skarpt svev mot bordet!)
    poly_under_body = poly_base_out.buffer(-0.8, join_style=1, quad_segs=24)

    # Diffusorfot-segmentet i XY: følgjer midtre 68 % av diffusorkurva der nedre kant går ned i sporet
    m_foot = (u_arc >= 0.14 * total_arc) & (u_arc <= 0.84 * total_arc)
    cl_foot = LineString(cl_xy[m_foot])
    poly_diff_foot = cl_foot.buffer(4.2, cap_style=1, join_style=1)

    # Bru mellom botnplata og diffusorfoten (skjult under bogen mellom kropp og diffusor)
    bridge_pts = np.array([
        [-30.0, 26.0], [50.0, 28.0], [45.0, -4.0], [-20.0, -8.0]
    ]) * scale_ratio
    poly_bridge = Polygon(bridge_pts).buffer(6.0, join_style=1)

    poly_chassis_plate = unary_union([poly_under_body, poly_bridge, poly_diff_foot]).buffer(2.0, join_style=1).buffer(-2.0, join_style=1)
    chassis_plate = _make_extruded_poly_solid(poly_chassis_plate, 0.0, z_plate, s=1.0, n_pts=80)

    # 2) Innvendig styrekant / register-flens som glir opp inne i hovudskalet (z = base .. base + lip_h)
    #    Radiell klaring = chassis_clear_mm (0.40 mm) -> 0 kollisjon!
    poly_lip_out = poly_base_in.buffer(-params.chassis_clear_mm, join_style=1, quad_segs=24)
    lip_wall = 2.4 if scale_ratio < 0.85 else 3.0
    poly_lip_in = poly_lip_out.buffer(-lip_wall, join_style=1, quad_segs=24)
    if poly_lip_in.geom_type == "MultiPolygon":
        poly_lip_in = max(poly_lip_in.geoms, key=lambda g: g.area)
    lip_outer = _make_extruded_poly_solid(poly_lip_out, z_plate - 0.5, z_plate + params.chassis_lip_h_mm, s=1.0 * (scale_ratio ** 2), n_pts=72)
    lip_inner = _make_extruded_poly_solid(poly_lip_in, z_plate + 0.5, z_plate + params.chassis_lip_h_mm + 2.0, s=1.0 * (scale_ratio ** 2), n_pts=72)
    chassis_lip = lip_outer.cut(lip_inner)

    # 3) Diffusorfot (plinth) som løftar seg rundt diffusorens nedre kant, med 1.40 mm boga spor!
    #    NB: pass på at diffusorfoten ikkje rører hovudskalet (klipp bort alt innanfor poly_base_out + 0.8 mm!)
    poly_plinth_xy = poly_diff_foot.difference(poly_base_out.buffer(0.8, join_style=1)).buffer(0)
    if poly_plinth_xy.geom_type == "MultiPolygon":
        poly_plinth_xy = max(poly_plinth_xy.geoms, key=lambda g: g.area)
    plinth_solid = _make_extruded_poly_solid(poly_plinth_xy, z_plate - 0.5, params.diffuser_plinth_h_mm, s=0.5 * (scale_ratio ** 2), n_pts=64)

    # Skjer presist boga 1.40 mm diffusorspor i foten -> +0.20 mm klaring per side til 1.0 mm film!
    cl_slot = LineString(cl_xy[(u_arc >= 0.10 * total_arc) & (u_arc <= 0.88 * total_arc)])
    poly_slot = cl_slot.buffer(0.5 * params.diffuser_slot_w_mm, cap_style=2, join_style=1)
    slot_cutter = _make_extruded_poly_solid(poly_slot, params.diffuser_z_seat_mm - 0.6, params.diffuser_plinth_h_mm + 3.0, s=0.15, n_pts=72)
    plinth_slotted = plinth_solid.cut(slot_cutter)

    # Slå saman botnplate + innvendig styrekant + diffusorfot til eitt komplett aluminiums botnchassis!
    chassis = chassis_plate.fuse(chassis_lip).fuse(plinth_slotted)

    # Kabelutgang / USB-C-utsparing bak-høgre i botnplata (z = 0.0 .. base_plate_h)
    cable_notch = (
        cq.Workplane("XY")
        .box(14.0 * scale_ratio + 2.0, 22.0 * scale_ratio + 2.0, z_plate + 2.0)
        .rotate((0, 0, 0), (0, 0, 1), -32)
        .translate((46.0 * scale_ratio, 64.0 * scale_ratio, 0.5 * z_plate))
        .val()
    )
    chassis = chassis.cut(cable_notch)

    # 3x M3 skruehol gjennom botnplata (til festebossar / service)
    screw_pts = [(-58.0 * scale_ratio, -54.0 * scale_ratio), (-42.0 * scale_ratio, 42.0 * scale_ratio), (24.0 * scale_ratio, 66.0 * scale_ratio)]
    for sx, sy in screw_pts:
        chassis = chassis.cut(cq.Solid.makeCylinder(1.7, z_plate + 4.0, cq.Vector(sx, sy, -1.0)))

    # --- B. Stålballastplate S235 (03_raup_ballast) ---
    poly_ballast = poly_lip_in.buffer(-1.5, join_style=1, quad_segs=24)
    if poly_ballast.geom_type == "MultiPolygon":
        poly_ballast = max(poly_ballast.geoms, key=lambda g: g.area)
    z_bal0 = z_plate + 1.0
    z_bal1 = z_bal0 + params.ballast_thick_mm
    ballast = _make_extruded_poly_solid(poly_ballast, z_bal0, z_bal1, s=0.8 * (scale_ratio ** 2), n_pts=64)
    for sx, sy in screw_pts:
        if poly_ballast.contains(Point(sx, sy)):
            ballast = ballast.cut(cq.Solid.makeCylinder(1.7, params.ballast_thick_mm + 2.0, cq.Vector(sx, sy, z_bal0 - 1.0)))

    # --- C. Utskiftbar Li-ion celle (04_raup_batteri_21700) ---
    # 18650 (Ø18.4 x 65.2 mm) i kompakt 200 mm skala, eller 21700 (Ø21.2 x 70.5 mm) ved >= 240 mm
    bat_r, bat_len = (9.2, 65.2) if params.total_height_mm < 240.0 else (10.6, 70.5)
    bat_cx, bat_cy, bat_ang = -8.0 * scale_ratio, 54.0 * scale_ratio, 22.0
    bat_z = z_plate + params.chassis_lip_h_mm + 1.5 + bat_r
    battery = (
        cq.Workplane("YZ")
        .circle(bat_r)
        .extrude(bat_len, both=False)
        .translate((-0.5 * bat_len, 0, 0))
        .rotate((0, 0, 0), (0, 0, 1), bat_ang)
        .translate((bat_cx, bat_cy, bat_z))
        .val()
    )

    # --- D. Drivar / Dimmar / USB-C PCB (05_raup_drivar_pcb) ---
    pcb_l, pcb_w, pcb_h = (32.0, 14.0, 5.0) if params.total_height_mm < 240.0 else (38.0, 18.0, 6.0)
    pcb_cx, pcb_cy, pcb_ang = -68.0 * scale_ratio, -12.0 * scale_ratio, 76.0
    pcb_z = z_plate + params.chassis_lip_h_mm + 1.8
    pcb = (
        cq.Workplane("XY")
        .box(pcb_l, pcb_w, pcb_h, centered=(True, True, False))
        .rotate((0, 0, 0), (0, 0, 1), pcb_ang)
        .translate((pcb_cx, pcb_cy, pcb_z))
        .val()
    )

    # --- E. Vertikal LED-kjølesøyle i eloksert aluminium (06_raup_led_berar) ---
    led_x, led_y = 20.0 * scale_ratio, 14.2 * scale_ratio
    led_w = 12.0 if params.total_height_mm < 240.0 else 16.0
    led_d = 5.5 if params.total_height_mm < 240.0 else 7.0
    led_h = 145.0 * scale_ratio
    led_z0 = z_plate + 0.5
    led_bar = (
        cq.Workplane("XY")
        .box(led_w, led_d, led_h, centered=(True, True, False))
        .edges("|Z")
        .fillet(1.0)
        .translate((led_x, led_y, led_z0))
        .val()
    )
    for dx in (-3.5, 3.5):
        led_bar = led_bar.cut(cq.Solid.makeCylinder(1.25, 8.0, cq.Vector(led_x + dx, led_y, led_z0 - 0.5)))

    # --- F. Skånsam boga styreklips ved spiralmunningen (08_raup_filmklips) ---
    t_left = cl_xy[1] - cl_xy[0]
    t_left = t_left / np.linalg.norm(t_left)
    p_back = cl_xy[0] - 4.0 * t_left
    cl_clip_ext = LineString(np.vstack([p_back, cl_xy[u_arc <= 0.10 * total_arc]]))
    poly_clip_ext = cl_clip_ext.buffer(2.8, cap_style=1, join_style=1).difference(poly_base_out.buffer(0.6, join_style=1)).buffer(0)
    if poly_clip_ext.geom_type == "MultiPolygon":
        poly_clip_ext = max(poly_clip_ext.geoms, key=lambda g: g.area)
    cl_slot_clip = LineString(cl_xy[u_arc <= 0.14 * total_arc])
    poly_slot_clip = cl_slot_clip.buffer(0.80, cap_style=2, join_style=1)
    clip_z0, clip_z1 = 15.0 * scale_ratio, 32.0 * scale_ratio
    clip = _make_extruded_poly_solid(poly_clip_ext, clip_z0, clip_z1, s=0.25, n_pts=48).cut(
        _make_extruded_poly_solid(poly_slot_clip, clip_z0 - 1.0, clip_z1 + 1.0, s=0.15, n_pts=48)
    )

    return {
        "raup_botn_chassis": chassis,
        "raup_ballast": ballast,
        "raup_batteri_21700": battery,
        "raup_drivar_pcb": pcb,
        "raup_led_berar": led_bar,
        "raup_filmklips": clip,
    }


# ---------------------------------------------------------------------------
# 4. TODELT STØYPEFORM FOR RESIRKULERT PAPIRMASSE
# ---------------------------------------------------------------------------

def build_pulp_molds(outer_body: cq.Solid, body_meta: dict):
    """Bygg todelt støypeform (-Y og +Y) med styringspinnar frå den reine Class-A ytterkroppen."""
    bb = outer_body.BoundingBox()
    pad_xy = 18.0
    pad_z = 12.0
    y_split = 24.0 * body_meta["scale_ratio"]

    x0, x1 = bb.xmin - pad_xy, bb.xmax + pad_xy
    y0, y1 = bb.ymin - pad_xy, bb.ymax + pad_xy
    z0, z1 = -pad_z, bb.zmax + pad_z

    molds = {}
    for side, ylo, yhi in [("minus_Y", y0, y_split), ("pluss_Y", y_split, y1)]:
        blk = cq.Solid.makeBox(x1 - x0, yhi - ylo, z1 - z0, cq.Vector(x0, ylo, z0))
        mold = blk.cut(outer_body)
        # 4x Ø5.2 mm styringspinne-hol på delingsplanet y = y_split
        for px in (x0 + 8.0, x1 - 8.0):
            for pz in (z0 + 25.0, z1 - 25.0):
                p_start = cq.Vector(px, y_split - 8.0 if side == "minus_Y" else y_split, pz)
                mold = mold.cut(cq.Solid.makeCylinder(2.6, 8.0, p_start, cq.Vector(0, 1, 0)))
        # Open drenerings-/fyllingskanal nedanfrå (z < 0)
        molds["raup_stoypform_" + side] = mold
    return molds


# ---------------------------------------------------------------------------
# 5. EKSAKT BAMBU LAB P1S 3MF-EKSPORT (1:1 mm, sentrert på 256x256 mm plate)
# ---------------------------------------------------------------------------

def _make_dense_curve_table(poly_2d: Polygon, s_fit: float = 1.5, n_eval: int = 12000):
    coords = clean_ccw(np.asarray(poly_2d.exterior.coords))
    tck = fit_periodic_tck(coords, s=s_fit, n_fit=600)
    uu = np.linspace(0.0, 1.0, n_eval, endpoint=False)
    xs, ys = splev(uu, tck)
    dx, dy = splev(uu, tck, der=1)
    dl = np.hypot(dx, dy)
    nx, ny = dy / dl, -dx / dl  # Ytre einingsnormal for moturs (CCW) ytterkontur
    pts = np.column_stack([xs, ys])
    norms = np.column_stack([nx, ny])
    return cKDTree(pts), pts, norms


def build_clean_textured_shell_mesh(
    shell: cq.Shape,
    body_meta: dict,
    params: RaupParams = RaupParams(),
    max_edge_mm: float = 1.10,
    tex_amp_mm: float = 0.095,
    out_stl: Path | None = None,
) -> tuple[np.ndarray, np.ndarray, dict]:
    """Bygg 100 % vanntett, C2-projisert høyoppløysingsnett (alle kantar <= max_edge_mm, 0 flate-fasettar)
    med ekte 3D mikro-papirmassestruktur på ytterveggen og sylskarp debossed skuggelinje.
    """
    BRepTools.Clean_s(shell.wrapped)
    BRepMesh_IncrementalMesh(shell.wrapped, 0.03, False, 0.08, True)

    verts, tris, v_off = [], [], 0
    for face in shell.Faces():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face.wrapped, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        rev = face.wrapped.Orientation().name == "TopAbs_REVERSED"
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            verts.append((p.X(), p.Y(), p.Z()))
        for i in range(1, tri.NbTriangles() + 1):
            n1, n2, n3 = tri.Triangle(i).Get()
            tris.append(
                (v_off + n1 - 1, v_off + n3 - 1, v_off + n2 - 1)
                if rev
                else (v_off + n1 - 1, v_off + n2 - 1, v_off + n3 - 1)
            )
        v_off += tri.NbNodes()

    v_arr = np.asarray(verts, dtype=np.float64)
    t_arr = np.asarray(tris, dtype=np.int32)
    keys = np.round(v_arr * 1e4).astype(np.int64)
    _, u_idx, inv_idx = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    v = v_arr[u_idx]
    t = inv_idx[t_arr]
    t = t[(t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 2] != t[:, 0])]

    sc_r = float(body_meta["scale_ratio"])
    notch_z = float(body_meta["notch_z_mm"])
    z_g0, z_g1 = body_meta.get("deboss_groove_z_mm", [notch_z, notch_z + 1.45])
    rbf_dome = body_meta["rbf_dome"]

    tree_up_out, pts_up_out, norms_up_out = _make_dense_curve_table(body_meta["poly_up_out"], s_fit=2.0 * (sc_r ** 2))
    tree_up_in, pts_up_in, _ = _make_dense_curve_table(body_meta["poly_up_in"], s_fit=1.0 * (sc_r ** 2))
    tree_base_out, pts_base_out, norms_base_out = _make_dense_curve_table(body_meta["poly_base_out"], s_fit=0.5 * (sc_r ** 2))
    tree_base_in, pts_base_in, _ = _make_dense_curve_table(body_meta["poly_base_in"], s_fit=0.5 * (sc_r ** 2))

    # Vektorisert vanntett kant-deling + eksakt C2-projeksjon på krumme veggar (eliminerer alle 600 mm2 fasettar!)
    for _ in range(12):
        p0, p1, p2 = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
        l01 = np.linalg.norm(p1 - p0, axis=1)
        l12 = np.linalg.norm(p2 - p1, axis=1)
        l20 = np.linalg.norm(p0 - p2, axis=1)
        cur_max = float(max(l01.max(), l12.max(), l20.max()))
        if cur_max <= max_edge_mm:
            break
        thresh = max(max_edge_mm, 0.48 * cur_max)
        e01 = np.sort(t[:, [0, 1]], axis=1)
        e12 = np.sort(t[:, [1, 2]], axis=1)
        e20 = np.sort(t[:, [2, 0]], axis=1)
        hot_edges = np.vstack([e01[l01 > thresh], e12[l12 > thresh], e20[l20 > thresh]])
        if len(hot_edges) == 0:
            break
        uniq_hot = np.unique(hot_edges, axis=0)
        mids = 0.5 * (v[uniq_hot[:, 0]] + v[uniq_hot[:, 1]])

        z_m = mids[:, 2]
        z_dome_m = rbf_dome(mids[:, :2])
        z_sh_out = z_dome_m - params.r_shoulder_out_mm * sc_r - 0.6
        z_sh_in = z_dome_m - params.wall_mm - params.r_shoulder_in_mm * sc_r - 0.6

        d_out, idx_out = tree_up_out.query(mids[:, :2])
        d_in, idx_in = tree_up_in.query(mids[:, :2])
        d_b_out, idx_b_out = tree_base_out.query(mids[:, :2])
        d_b_in, idx_b_in = tree_base_in.query(mids[:, :2])

        in_groove_z = (z_m >= z_g0 - 0.15) & (z_m <= z_g1 + 0.15)
        on_up_out = (d_out < 0.35) & (z_m > notch_z + 0.15) & (z_m < z_sh_out) & (~in_groove_z)
        mids[on_up_out, :2] = pts_up_out[idx_out[on_up_out]]

        on_base_out = (d_b_out < 0.35) & (z_m > 0.05) & (z_m < notch_z - 0.15)
        mids[on_base_out, :2] = pts_base_out[idx_b_out[on_base_out]]

        on_up_in = (d_in < 0.35) & (z_m > notch_z + params.wall_mm + 0.15) & (z_m < z_sh_in)
        mids[on_up_in, :2] = pts_up_in[idx_in[on_up_in]]

        on_base_in = (d_b_in < 0.35) & (z_m > 0.05) & (z_m < notch_z - 0.15)
        mids[on_base_in, :2] = pts_base_in[idx_b_in[on_base_in]]

        base_idx = len(v)
        v = np.vstack([v, mids])

        hot_keys = (uniq_hot[:, 0].astype(np.int64) << 32) | uniq_hot[:, 1].astype(np.int64)
        order = np.argsort(hot_keys)
        hot_keys_s = hot_keys[order]
        hot_vals_s = (base_idx + np.arange(len(uniq_hot), dtype=np.int32))[order]

        def _lookup_edge(ea):
            k = (ea[:, 0].astype(np.int64) << 32) | ea[:, 1].astype(np.int64)
            pos = np.searchsorted(hot_keys_s, k)
            pos_c = np.clip(pos, 0, len(hot_keys_s) - 1)
            hit = hot_keys_s[pos_c] == k
            out = np.full(len(ea), -1, dtype=np.int32)
            out[hit] = hot_vals_s[pos_c[hit]]
            return out

        id01, id12, id20 = _lookup_edge(e01), _lookup_edge(e12), _lookup_edge(e20)
        s01, s12, s20 = id01 >= 0, id12 >= 0, id20 >= 0
        cnt = s01.astype(int) + s12.astype(int) + s20.astype(int)

        new_tris = [t[cnt == 0]]
        for rot, (sa, sb, sc, ida) in enumerate([(s01, s12, s20, id01), (s12, s20, s01, id12), (s20, s01, s12, id20)]):
            m1 = (cnt == 1) & sa
            if np.any(m1):
                tr = np.roll(t[m1], -rot, axis=1)
                ma = ida[m1]
                new_tris.append(np.column_stack([tr[:, 0], ma, tr[:, 2]]))
                new_tris.append(np.column_stack([ma, tr[:, 1], tr[:, 2]]))

        for rot, (sa, sb, sc, ida, idb) in enumerate([(s01, s12, s20, id01, id12), (s12, s20, s01, id12, id20), (s20, s01, s12, id20, id01)]):
            m2 = (cnt == 2) & sa & sb
            if np.any(m2):
                tr = np.roll(t[m2], -rot, axis=1)
                ma, mb = ida[m2], idb[m2]
                new_tris.append(np.column_stack([ma, tr[:, 1], mb]))
                d1 = np.linalg.norm(v[ma] - v[tr[:, 2]], axis=1)
                d2 = np.linalg.norm(v[mb] - v[tr[:, 0]], axis=1)
                c1 = d1 <= d2
                if np.any(c1):
                    new_tris.append(np.column_stack([tr[c1, 0], ma[c1], tr[c1, 2]]))
                    new_tris.append(np.column_stack([ma[c1], mb[c1], tr[c1, 2]]))
                if np.any(~c1):
                    new_tris.append(np.column_stack([tr[~c1, 0], ma[~c1], mb[~c1]]))
                    new_tris.append(np.column_stack([tr[~c1, 0], mb[~c1], tr[~c1, 2]]))

        m3 = cnt == 3
        if np.any(m3):
            tr = t[m3]
            ma, mb, mc = id01[m3], id12[m3], id20[m3]
            new_tris.append(np.column_stack([tr[:, 0], ma, mc]))
            new_tris.append(np.column_stack([ma, tr[:, 1], mb]))
            new_tris.append(np.column_stack([mc, mb, tr[:, 2]]))
            new_tris.append(np.column_stack([ma, mb, mc]))

        t = np.vstack([x for x in new_tris if len(x) > 0])

    # Legg på fin taktil 3D mikro-papirmassestruktur (±tex_amp_mm) direkte på heile ytterveggen
    # heilt fram til kanten av den debossed skuggelinja, innspranget og botnen (0.0 mm glatte felt!)
    if tex_amp_mm > 0:
        zv = v[:, 2]
        d_up, idx_up = tree_up_out.query(v[:, :2])
        d_ba, idx_ba = tree_base_out.query(v[:, :2])
        is_below = zv < notch_z
        d_ext = np.where(is_below, d_ba, d_up)
        n_ext = np.where(is_below[:, None], norms_base_out[idx_ba], norms_up_out[idx_up])

        # Berekn glatte toppunkt-normalar før forskyving for å låse sporkantar og horisontale flater (|n_z| > 0.22)
        vt0 = v[t]
        fn0 = np.cross(vt0[:, 1] - vt0[:, 0], vt0[:, 2] - vt0[:, 0])
        vn0 = np.zeros_like(v)
        np.add.at(vn0, t[:, 0], fn0)
        np.add.at(vn0, t[:, 1], fn0)
        np.add.at(vn0, t[:, 2], fn0)
        vn_len = np.maximum(np.linalg.norm(vn0, axis=1, keepdims=True), 1e-12)
        v_norm = vn0 / vn_len

        z_dome_v = rbf_dome(v[:, :2])
        z_sh_v = z_dome_v - params.r_shoulder_out_mm * sc_r - 0.5

        m_bot = np.clip((zv - 0.12) / 0.25, 0.0, 1.0)
        m_top = np.clip((z_sh_v + 1.0 - zv) / 1.8, 0.0, 1.0)
        m_ext = np.clip((0.08 - d_ext) / 0.05, 0.0, 1.0)
        m_vert = np.clip((0.22 - np.abs(v_norm[:, 2])) / 0.14, 0.0, 1.0)
        mask = m_bot * m_top * m_ext * m_vert

        active = mask > 1e-3
        if np.any(active):
            pts_a = v[active]
            rng = np.random.default_rng(20261119)
            n_waves = 32
            angles_xy = rng.uniform(0, 2 * math.pi, n_waves)
            k_xy = rng.uniform(2 * math.pi / 3.0, 2 * math.pi / 1.5, n_waves)
            k_z = rng.uniform(2 * math.pi / 2.6, 2 * math.pi / 1.3, n_waves) * rng.choice([-1.0, 1.0], n_waves)
            phases = rng.uniform(0, 2 * math.pi, n_waves)
            kx = k_xy * np.cos(angles_xy)
            ky = k_xy * np.sin(angles_xy)
            arg = pts_a[:, 0:1] * kx[None, :] + pts_a[:, 1:2] * ky[None, :] + pts_a[:, 2:3] * k_z[None, :] + phases[None, :]
            grain = np.sum(np.sin(arg), axis=1) / math.sqrt(0.5 * n_waves)
            strata = 0.35 * np.sin(2.0 * math.pi * pts_a[:, 2] / 0.44)
            raw_field = np.zeros(len(v), dtype=np.float64)
            raw_field[active] = grain + strata

            # 1-pass vektorisert kant-glatting på skalarfeltet + RMS-bevaring:
            # fjernar enkelttopp-sagtakkar medan full ±tex_amp_mm taktil strukturdjupn blir bevart!
            edges_u = np.r_[t[:, 0], t[:, 1], t[:, 2], t[:, 1], t[:, 2], t[:, 0]]
            edges_v = np.r_[t[:, 1], t[:, 2], t[:, 0], t[:, 0], t[:, 1], t[:, 2]]
            deg = np.maximum(np.bincount(edges_u, minlength=len(v)).astype(np.float64), 1.0)
            nei_sum = np.bincount(edges_u, weights=raw_field[edges_v], minlength=len(v))
            sm_field = 0.58 * raw_field + 0.42 * (nei_sum / deg)
            disp_full = tex_amp_mm * mask * np.tanh(1.15 * sm_field)

            v[active, 0] += disp_full[active] * n_ext[active, 0]
            v[active, 1] += disp_full[active] * n_ext[active, 1]

    # Skriv binær STL dersom out_stl er oppgitt
    vt = v[t]
    fn = np.cross(vt[:, 1] - vt[:, 0], vt[:, 2] - vt[:, 0])
    fl = np.linalg.norm(fn, axis=1)
    un = (fn / np.maximum(fl[:, None], 1e-12)).astype(np.float32)

    if out_stl is not None:
        out_stl.parent.mkdir(parents=True, exist_ok=True)
        dtype = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")])
        rec = np.zeros(len(t), dtype=dtype)
        rec["n"] = un
        rec["v"] = vt.astype(np.float32)
        hdr = b"RAUP Class-A C2-Subdivided & Micro-Textured Shell".ljust(80, b" ")
        with open(out_stl, "wb") as fh:
            fh.write(hdr)
            fh.write(np.uint32(len(t)).tobytes())
            rec.tofile(fh)

    # Sjekk maks trekantareal ved innsprangshjørnet
    c = vt.mean(axis=1)
    m_box = (c[:, 0] > 5) & (c[:, 0] < 50) & (c[:, 1] > 10) & (c[:, 1] < 40) & (c[:, 2] > 20) & (c[:, 2] < 80)
    max_step_area = float(0.5 * fl[m_box].max()) if np.any(m_box) else 0.0
    e_max = float(max(
        np.linalg.norm(vt[:, 1] - vt[:, 0], axis=1).max(),
        np.linalg.norm(vt[:, 2] - vt[:, 1], axis=1).max(),
        np.linalg.norm(vt[:, 0] - vt[:, 2], axis=1).max(),
    ))
    stats = {
        "vertices": int(len(v)),
        "triangles": int(len(t)),
        "max_edge_mm": round(e_max, 3),
        "max_step_corner_tri_area_mm2": round(max_step_area, 3),
        "texture_amplitude_mm": tex_amp_mm,
        "deboss_groove_z_mm": [round(z_g0, 2), round(z_g1, 2)],
    }
    return stats


def _load_bambu_profile_flattened(sys_dir: Path, kind: str, name: str) -> dict:
    """Slå saman heile inherits-kjeda for ein offisiell Bambu Studio systemprofil."""
    folder = sys_dir / kind
    chain = []
    cur = name
    while cur:
        p = folder / f"{cur}.json"
        if not p.exists():
            hits = list(folder.rglob(f"{cur}.json"))
            if not hits:
                raise FileNotFoundError(f"Manglar Bambu Studio profil: {kind}/{cur}.json")
            p = hits[0]
        d = json.loads(p.read_text(encoding="utf-8"))
        chain.append(d)
        cur = d.get("inherits")
    merged = {}
    for d in reversed(chain):
        merged.update(d)
    merged.pop("inherits", None)
    return merged


def export_bambu_p1s_3mf(
    shape: cq.Shape,
    out_3mf: Path,
    wall_mm: float = 2.5,
    total_height_mm: float = 200.0,
    object_name: str | None = None,
    lin_deflection: float = 0.05,
    ang_deflection: float = 0.10,
    bed_mm: float = 256.0,
    layer_height_mm: float = 0.16,
    fuzzy_skin: str = "external",
    fuzzy_thickness_mm: float = 0.08,
    fuzzy_point_dist_mm: float = 0.25,
    stl_source: Path | None = None,
):
    """Skriv ein 100 % offisiell, ferdig-slica Bambu Studio P1S .3mf i eksakt 1:1 mm-skala.

    Dersom Bambu Studio er installert lokalt, blir modellen sentrert eksakt på P1S-plata (128, 128, 0)
    utan rotasjon og slica direkte gjennom Bambu Studio CLI (`--slice 0 --export-3mf`) med verifisert
    G-kode, C2-subdividert mikro-teksturert nett + Fuzzy Skin (`external` = Contour), 6 veggliner,
    0 % fylling og tre-støtte frå plata.
    """
    bb = shape.BoundingBox()
    size = np.array([float(bb.xlen), float(bb.ylen), float(bb.zlen)], dtype=np.float64)
    bed_cx = 0.5 * bed_mm
    bed_cy = 0.5 * bed_mm
    lo_b = np.array([bed_cx - 0.5 * size[0], bed_cy - 0.5 * size[1], 0.0])
    hi_b = np.array([bed_cx + 0.5 * size[0], bed_cy + 0.5 * size[1], float(size[2])])
    if lo_b[0] < 0 or hi_b[0] > bed_mm or lo_b[1] < 0 or hi_b[1] > bed_mm or hi_b[2] > bed_mm:
        raise ValueError(f"Modellen overstig P1S {bed_mm}mm byggjevolum: min={lo_b.round(2)}, max={hi_b.round(2)}")

    wall_loops = max(2, int(math.ceil(wall_mm / 0.42)))
    top_layers = max(6, int(math.ceil(wall_mm / layer_height_mm)))

    bambu_exe = Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")
    bambu_sys = Path(os.environ.get("APPDATA", "")) / "BambuStudio" / "system" / "BBL"

    if bambu_exe.exists() and bambu_sys.exists():
        tmp_dir = Path(tempfile.mkdtemp(prefix="raup_bambu_"))
        try:
            stl_name = f"RAUP_H{total_height_mm:g}_{wall_mm:g}mm_1to1.stl"
            stl_tmp = tmp_dir / stl_name
            if stl_source is not None and stl_source.exists():
                dtype = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")])
                hdr = stl_source.read_bytes()[:84]
                raw = np.fromfile(stl_source, dtype=dtype, offset=84).copy()
                v_stl = raw["v"]
                lo_s = v_stl.reshape(-1, 3).min(axis=0)
                hi_s = v_stl.reshape(-1, 3).max(axis=0)
                shift = np.array([bed_cx - 0.5 * (lo_s[0] + hi_s[0]), bed_cy - 0.5 * (lo_s[1] + hi_s[1]), -lo_s[2]], dtype=np.float32)
                raw["v"] = v_stl + shift
                with open(stl_tmp, "wb") as f:
                    f.write(hdr)
                    raw.tofile(f)
            else:
                cx_s = 0.5 * (bb.xmin + bb.xmax)
                cy_s = 0.5 * (bb.ymin + bb.ymax)
                shape_bed = shape.translate(cq.Vector(bed_cx - cx_s, bed_cy - cy_s, -bb.zmin))
                cq.exporters.export(shape_bed, str(stl_tmp), tolerance=lin_deflection, angularTolerance=ang_deflection)

            mach = _load_bambu_profile_flattened(bambu_sys, "machine", "Bambu Lab P1S 0.4 nozzle")
            proc = _load_bambu_profile_flattened(bambu_sys, "process", "0.16mm Optimal @BBL X1C")
            fil = _load_bambu_profile_flattened(bambu_sys, "filament", "Bambu PLA Matte @BBL P1S 0.4 nozzle")
            fil["default_filament_colour"] = ["#F1EDE6"]
            fil["filament_colour"] = ["#F1EDE6"]

            proc.update({
                "layer_height": f"{layer_height_mm:g}",
                "initial_layer_print_height": "0.2",
                "wall_generator": "arachne",
                "wall_loops": str(wall_loops),
                "sparse_infill_density": "0%",
                "top_shell_layers": str(top_layers),
                "top_shell_thickness": f"{wall_mm:g}",
                "bottom_shell_layers": "0",
                "bottom_shell_thickness": "0",
                "fuzzy_skin": fuzzy_skin,
                "fuzzy_skin_first_layer": "0",
                "fuzzy_skin_mode": "displacement",
                "fuzzy_skin_noise_type": "classic",
                "fuzzy_skin_thickness": f"{fuzzy_thickness_mm:g}",
                "fuzzy_skin_point_distance": f"{fuzzy_point_dist_mm:g}",
                "precise_outer_wall": "1",
                "seam_position": "back",
                "enable_support": "1",
                "support_type": "tree(auto)",
                "support_style": "tree_hybrid",
                "support_on_build_plate_only": "1",
                "support_critical_regions_only": "1",
                "support_threshold_angle": "30",
                "brim_type": "outer_only",
                "brim_width": "5",
                "brim_object_gap": "0.1",
                "curr_bed_type": "Textured PEI Plate",
            })

            m_json = tmp_dir / "machine.json"
            p_json = tmp_dir / "process.json"
            f_json = tmp_dir / "filament.json"
            m_json.write_text(json.dumps(mach, indent=2), encoding="utf-8")
            p_json.write_text(json.dumps(proc, indent=2), encoding="utf-8")
            f_json.write_text(json.dumps(fil, indent=2), encoding="utf-8")

            cmd = [
                str(bambu_exe),
                "--orient", "0",
                "--arrange", "0",
                "--load-settings", f"{m_json};{p_json}",
                "--load-filaments", str(f_json),
                "--slice", "0",
                "--outputdir", str(tmp_dir),
                "--export-3mf", out_3mf.name,
                str(stl_tmp),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            rjson_path = tmp_dir / "result.json"
            rinfo = json.loads(rjson_path.read_text(encoding="utf-8")) if rjson_path.exists() else {}
            gen_3mf = tmp_dir / out_3mf.name
            if res.returncode != 0 or not gen_3mf.exists():
                raise RuntimeError(f"Bambu Studio CLI-slicing feila (rc={res.returncode}): {rinfo}")

            out_3mf.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(gen_3mf, out_3mf)

            plate = (rinfo.get("sliced_plates") or [{}])[0]
            fil_used = (plate.get("filaments") or [{}])[0]
            return {
                "fil": str(out_3mf.relative_to(ROOT)).replace("\\", "/"),
                "pre_sliced_by_bambu_cli": True,
                "unit": "millimeter",
                "scale_transform": "1 0 0 0 1 0 0 0 1 0 0 0",
                "triangles": int(plate.get("triangle_count", 0)),
                "size_mm": [round(float(s), 3) for s in size],
                "bed_min_mm": [round(float(v), 3) for v in lo_b],
                "bed_max_mm": [round(float(v), 3) for v in hi_b],
                "wall_mm": wall_mm,
                "wall_loops": wall_loops,
                "layer_height_mm": layer_height_mm,
                "sparse_infill": "0%",
                "fuzzy_skin": fuzzy_skin,
                "fuzzy_skin_thickness_mm": fuzzy_thickness_mm,
                "fuzzy_skin_point_distance_mm": fuzzy_point_dist_mm,
                "sliced_print_time_s": round(float(plate.get("total_predication", 0.0)), 1),
                "sliced_filament_object_g": round(float(fil_used.get("main_used_g", 0.0)), 1),
                "sliced_filament_total_g": round(float(fil_used.get("total_used_g", 0.0)), 1),
                "slicer_warning": plate.get("warning_message", ""),
            }
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # Reserve-eksport dersom Bambu Studio ikkje er installert på maskina
    BRepMesh_IncrementalMesh(shape.wrapped, lin_deflection, False, ang_deflection, True)
    verts, tris, v_offset = [], [], 0
    for face in shape.Faces():
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face.wrapped, loc)
        if tri is None:
            continue
        trsf = loc.Transformation()
        is_rev = face.wrapped.Orientation().name == "TopAbs_REVERSED"
        for i in range(1, tri.NbNodes() + 1):
            p = tri.Node(i).Transformed(trsf)
            verts.append((p.X(), p.Y(), p.Z()))
        for i in range(1, tri.NbTriangles() + 1):
            n1, n2, n3 = tri.Triangle(i).Get()
            tris.append((v_offset + n1 - 1, v_offset + n3 - 1, v_offset + n2 - 1) if is_rev else (v_offset + n1 - 1, v_offset + n2 - 1, v_offset + n3 - 1))
        v_offset += tri.NbNodes()
    v_arr = np.asarray(verts, dtype=np.float64)
    t_arr = np.asarray(tris, dtype=np.int32)
    keys = np.round(v_arr * 1e4).astype(np.int64)
    _, uniq_idx, inv_idx = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    v_uniq = v_arr[uniq_idx]
    t_mapped = inv_idx[t_arr]
    t_mapped = t_mapped[(t_mapped[:, 0] != t_mapped[:, 1]) & (t_mapped[:, 1] != t_mapped[:, 2]) & (t_mapped[:, 2] != t_mapped[:, 0])]
    lo, hi = v_uniq.min(axis=0), v_uniq.max(axis=0)
    v_bed = v_uniq + np.array([bed_cx - 0.5 * (lo[0] + hi[0]), bed_cy - 0.5 * (lo[1] + hi[1]), -lo[2]])
    v_lines = "".join(f'<vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in v_bed)
    t_lines = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t_mapped)
    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        f' <resources><object id="1" type="model"><mesh><vertices>{v_lines}</vertices><triangles>{t_lines}</triangles></mesh></object></resources>\n'
        ' <build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></build>\n</model>\n'
    )
    out_3mf.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_3mf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        zf.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        zf.writestr("3D/3dmodel.model", model_xml)
    return {
        "fil": str(out_3mf.relative_to(ROOT)).replace("\\", "/"),
        "pre_sliced_by_bambu_cli": False,
        "unit": "millimeter",
        "scale_transform": "1 0 0 0 1 0 0 0 1 0 0 0",
        "triangles": int(len(t_mapped)),
        "size_mm": [round(float(s), 3) for s in size],
        "bed_min_mm": [round(float(v), 3) for v in lo_b],
        "bed_max_mm": [round(float(v), 3) for v in hi_b],
        "wall_mm": wall_mm,
        "wall_loops": wall_loops,
        "layer_height_mm": layer_height_mm,
        "sparse_infill": "0%",
        "fuzzy_skin": fuzzy_skin,
        "fuzzy_skin_thickness_mm": fuzzy_thickness_mm,
        "fuzzy_skin_point_distance_mm": fuzzy_point_dist_mm,
    }
