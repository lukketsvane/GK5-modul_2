# -*- coding: utf-8 -*-
"""sveip_produksjon.py: byggjer alle delar, eksporterer og kontrollerer Sveip rev. B.

Køyr frå cad/:  python sveip_produksjon.py [--rask]
Skriv:
  cad/step/*.step, cad/sveip_samanstilling.step, cad/sveip_samanstilling.glb
  produksjon/dxf/*.dxf (flatmønster 1:1), produksjon/stl/*.stl, produksjon/sveip_stykkliste.csv
  kontroll/sveip_kontroll.json, render/geometri.json
--rask hoppar over rørslekontrollane (innsetjing, batteri, plugg).
"""
from __future__ import annotations

import csv
import itertools
import json
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
from lagprio import lag_prioritet  # noqa: E402

lag_prioritet()

import cadquery as cq  # noqa: E402
from OCP.BRepCheck import BRepCheck_Analyzer  # noqa: E402
from OCP.BRepExtrema import BRepExtrema_DistShapeShape  # noqa: E402
from shapely.geometry import MultiPoint, Point  # noqa: E402

import sveip_flat as F  # noqa: E402
import sveip_innmat as I  # noqa: E402
import sveip_kropp as K  # noqa: E402
import sveip_lys as L  # noqa: E402
import sveip_samanstilling as SA  # noqa: E402
from sveip_geometri import P0  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

CAD = Path(__file__).resolve().parent
ROT = CAD.parent
STEP = CAD / "step"
DXF = ROT / "produksjon" / "dxf"
STL = ROT / "produksjon" / "stl"
KONTROLL = ROT / "kontroll"
RENDER = ROT / "render"
for d in (STEP, DXF, STL, KONTROLL, RENDER):
    d.mkdir(parents=True, exist_ok=True)


def rydd():
    """Fjern gamle eksportar, så mappene berre har delane i gjeldande register."""
    for d, ending in ((STEP, "*.step"), (STL, "*.stl"), (DXF, "*.dxf")):
        for f in d.glob("sveip_" + ending):
            f.unlink()

ASCII = str.maketrans({"æ": "ae", "ø": "o", "å": "aa", "Æ": "AE", "Ø": "O", "Å": "AA", " ": "_",
                       "×": "x", ",": "_", "/": "_", "(": "", ")": "", "-": "_"})

# delar som høyrer til innmatsmodulen (blir senka ned gjennom toppen)
MODUL = {"D02", "D03", "D04", "D04L", "D05", "D05L", "D06", "D07", "D08", "D09", "D09K", "D11",
         "D11K", "D11J", "D14", "K01", "K02", "K03", "K05", "K06", "K07", "K10", "K11", "K12",
         "K13", "K15", "K18", "K19", "K20", "K21", "K22", "K23"}
PAA_KROPPEN = {"D01"}                    # punkta (D12/D13) og føtene (K08) kjem etter modulen
UNDER = {"D10", "K14", "K09"}            # luke og skruar nedanfrå, etter innsetjing
LAKK_G_PER_CM2 = 0.007 * 1.5             # 70 µm pulverlakk, 1,5 g/cm3
# innkjøpspostar som ikkje er modellerte
TILLEGG_BOM = [
    ["W1", "Kabelsett USB-kort til hovudkort", 1, "4-leiar 28 AWG, JST PH 4-pol (PHR-4 + SPH-002T), 120 mm", "kjop", 2, 2, "-", "-"],
    ["W2", "Kabelsett hovudkort til lysmodul", 1, "4-leiar 26 AWG, JST PH 4-pol, 230 mm", "kjop", 3, 3, "-", "-"],
    ["W3", "Kabelsett berøringskort", 1, "3-leiar 28 AWG (S1, S2, GND), JST PH 3-pol, 150 mm", "kjop", 2, 2, "-", "-"],
    ["W4", "Kabelsett nedkort til opp-kort", 1, "2-leiar 26 AWG, JST PH 2-pol, 60 mm", "kjop", 1, 1, "-", "-"],
    ["W5", "Jordleidning chassis", 1, "kabelsko M3 + 50 mm 24 AWG til GND på D09, tannskive under éin K09", "kjop", 1, 1, "-", "-"],
    ["T1", "Termopute nedkort", 1, "silikon 0,25 mm, 3 W/mK, D-form som D05", "kjop", 1, 1, "-", "-"],
    ["T2", "Termopute opp-kort", 1, "silikon 0,25 mm, 3 W/mK, 240 x 36", "kjop", 1, 1, "-", "-"],
    ["T3", "Trekkband celle", 1, "polyimid 10 x 90 mm under cella", "kjop", 0.5, 0.5, "-", "-"],
    ["T4", "Isolerfilm under hovudkortet", 1, "polyimid 0,1 mm, 75 x 25 over cella", "kjop", 0.3, 0.3, "-", "-"],
    ["S1", "Skruar berøringskort M3 x 5", 2, "A2, ISO 7380", "kjop", 0.4, 0.8, "-", "-"],
    ["L1", "Typeskilt", 1, "lasermerkt på luka: klasse III, 5 V 1,5 A, Li-ion 21700 3,6 V, + mot hakket, CE, WEEE, batterisymbol", "lag", 0, 0, "-", "-"],
]


def namn(d):
    return f"sveip_{d[0]}_{d[1]}".translate(ASCII).lower()


def form_av(w):
    v = w.vals()
    return v[0] if len(v) == 1 else cq.Compound.makeCompound(v)


def snitt(a, b):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or bb.ymax < ba.ymin
            or ba.zmax < bb.zmin or bb.zmax < ba.zmin):
        return 0.0
    return a.intersect(b).Volume()


def avstand(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value() if d.IsDone() else float("nan")


def _slicestatus():
    sti = ROT / "print" / "print_rapport.json"
    if not sti.exists():
        return "ikkje gjort"
    r = json.loads(sti.read_text(encoding="utf-8"))
    ok = [p_["plate"] for p_ in r if p_.get("slica")]
    return f"{len(ok)} av {len(r)} plater slica i Bambu Studio CLI (print/print_rapport.json); verktøybanene ikkje sette over i GUI"


def main(rask=False):
    t0 = time.time()
    rap = {"lampe": "Sveip", "revisjon": "B", "eining": "mm", "dato": "2026-11-24",
           "koordinatar": "x mot utkraginga, y djupn (framside negativ), z opp; bordet i z = -%.1f" % P0.fot_h}
    rydd()
    print("byggjer delar ...")
    former, meta = {}, {}
    for d in SA.DELAR:
        w = d[2]()
        s = form_av(w)
        former[d[0]] = s
        meta[d[0]] = d
    # ------------------------------------------------ gyldigheit og eksport
    delrap = []
    assy = cq.Assembly(name="Sveip_revA")
    for d in SA.DELAR:
        s = former[d[0]]
        ok = BRepCheck_Analyzer(s.wrapped).IsValid()
        n = namn(d)
        sti = STEP / f"{n}.step"
        cq.exporters.export(cq.Workplane().add(s), str(sti))
        att = cq.importers.importStep(str(sti)).val()
        ok2 = BRepCheck_Analyzer(att.wrapped).IsValid() and abs(att.Volume() - s.Volume()) < 1e-3 * max(1, s.Volume())
        tol = (0.02, 0.08) if d[0] in ("D01", "D12F", "D12B") else (0.05, 0.15)
        cq.exporters.export(cq.Workplane().add(s), str(STL / f"{n}.stl"),
                            tolerance=tol[0], angularTolerance=tol[1])
        bb = s.BoundingBox()
        delrap.append(dict(id=d[0], namn=d[1], materiale=d[3], type=d[6], tal=d[7],
                           gyldig=ok, step_attlest=ok2, volum_cm3=round(s.Volume() / 1e3, 3),
                           masse_g=round(s.Volume() / 1e3 * d[4], 1),
                           maal_mm=[round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
                           step=f"cad/step/{n}.step", stl=f"produksjon/stl/{n}.stl"))
        if d[6] != "ekstern":
            assy.add(cq.Workplane().add(s), name=n, color=cq.Color(*d[5]))
        if not (ok and ok2):
            raise RuntimeError(f"ugyldig del {d[0]}")
    assy.save(str(CAD / "sveip_samanstilling.step"))
    try:
        assy.save(str(CAD / "sveip_samanstilling.glb"), tolerance=0.05, angularTolerance=0.2)
    except Exception as e:
        print("GLB vart ikkje skriven:", e)
    rap["delar"] = delrap
    print(f"eksportert {len(delrap)} delar, {time.time() - t0:.0f} s")

    # ------------------------------------------------ kollisjon (alle par)
    kol, par = [], 0
    ids = list(former)
    for a, b in itertools.combinations(ids, 2):
        if "E01" in (a, b) and False:
            continue
        par += 1
        v = snitt(former[a], former[b])
        if v > 0.05:
            kol.append(dict(a=a, b=b, mm3=round(v, 3)))
    rap["kollisjon"] = dict(testa_par=par, grense_mm3=0.05, kollisjonar=kol, bestatt=not kol)
    print(f"kollisjon: {len(kol)} av {par} par, {time.time() - t0:.0f} s")

    # ------------------------------------------------ klaringar som er kravde
    krav = [("D01*", "D02", 2.0), ("D01", "D03", 2.5), ("D01", "D06", 1.5), ("D01", "D08", 2.0),
            ("D01", "K22", 0.3), ("D01", "K20", 1.0), ("D01", "D09", 10.0), ("D01", "D05", 10.0),
            ("D01", "D04", 10.0), ("D01", "D14", 3.0), ("D02", "D13F", 0.4),
            ("D02", "D13B", 0.4), ("D14", "D13F", 1.0), ("D14", "D13B", 1.0), ("D02", "D06", 0.3),
            ("D02", "D11K", 0.2), ("D09", "K01", 1.0), ("D02", "K01", 1.5), ("D03", "D05L", 0.5),
            ("D07", "D05L", 10.0), ("D08", "D04L", 25.0), ("D01", "E01", 0.5)]
    klar = []
    # D01* = kroppen utan botnflensane (chassiset skal liggje på flensane)
    former["D01*"] = former["D01"].cut(cq.Solid.makeBox(400, 200, P0.fl_ri + P0.t + 0.5,
                                                         cq.Vector(-50, -100, -1)))
    for a, b, k in krav:
        d_ = avstand(former[a], former[b])
        klar.append(dict(a=a, b=b, min_mm=round(d_, 3), krav_mm=k, ok=d_ >= k - 1e-6))
    rap["klaring"] = dict(par=klar, bestatt=all(k["ok"] for k in klar))
    # positive kontaktar (skal ligge an)
    del former["D01*"]
    kont = []
    for a, b, maks in [("K20", "D12F", 0.01), ("K20", "D12B", 0.01), ("D02", "D01", 0.01),
                       ("K08", "D01", 0.01), ("D05", "D03", 0.01), ("D07", "D06", 0.01),
                       ("D03", "D02", 0.01), ("D09", "K03", 0.01), ("D10", "D02", 0.01),
                       ("D12F", "D01", 0.01), ("D13F", "D01", 0.15)]:
        d_ = avstand(former[a], former[b])
        kont.append(dict(a=a, b=b, avstand_mm=round(d_, 3), maks_mm=maks, ok=d_ <= maks))
    rap["kontakt"] = dict(par=kont, bestatt=all(k["ok"] for k in kont))

    # ------------------------------------------------ masse, tyngdepunkt, velt
    M, Mx, My, Mz = 0.0, 0.0, 0.0, 0.0
    for i, s in former.items():
        d = meta[i]
        if d[6] == "ekstern":
            continue
        m = s.Volume() / 1e3 * d[4]
        c = cq.Shape.centerOfMass(s)
        M += m; Mx += m * c.x; My += m * c.y; Mz += m * c.z
    lakk = 0.0
    for i in ("D01", "D02", "D10"):
        a_ = former[i].Area() / 100.0
        m = a_ * LAKK_G_PER_CM2
        c = cq.Shape.centerOfMass(former[i])
        lakk += m
        M += m; Mx += m * c.x; My += m * c.y; Mz += m * c.z
    tillegg = [("leidningar og kabelband", 10.0, (110.0, 0.0, 100.0)),
               ("komponentar utover modellen", 12.0, (120.0, 0.0, 26.0)),
               ("termopute, merkelapp", 3.0, (230.0, 0.0, 186.0))]
    for _, m, (x, y, z) in tillegg:
        M += m; Mx += m * x; My += m * y; Mz += m * z
    cg = (Mx / M, My / M, Mz / M)
    hf = P0.fot_h
    R_FOT = 2.5     # effektiv kant: TPE-foten (Ø12) gjev etter, rekna 2,5 mm frå senter
    fot = []
    for sy in (-1, 1):
        for x in P0.fot_x:
            for k in range(36):
                a_ = 2 * math.pi * k / 36
                fot.append((x + R_FOT * math.cos(a_), sy * P0.fl_yc + R_FOT * math.sin(a_)))
    hull = MultiPoint(fot).convex_hull
    d_kant = hull.exterior.distance(Point(cg[0], cg[1]))
    inne = hull.contains(Point(cg[0], cg[1]))
    h = cg[2] + hf
    xs = [p_[0] for p_ in fot]
    ys = [p_[1] for p_ in fot]
    retn = {"mot_utkraginga_+x": max(xs) - cg[0], "mot_hakket_-x": cg[0] - min(xs),
            "framover_-y": cg[1] - min(ys), "bakover_+y": max(ys) - cg[1]}
    velt = {k: round(math.degrees(math.atan2(v, h)), 1) for k, v in retn.items()}
    v_min = math.degrees(math.atan2(d_kant, h))
    g = 9.81e-3
    rap["masse"] = dict(total_g=round(M, 1), lakk_g=round(lakk, 1),
                        tillegg=[dict(namn=n_, g=m) for n_, m, _ in tillegg],
                        krav_F8_g=1200, F8_bestatt=M <= 1200, margin_g=round(1200 - M, 1))
    rap["stabilitet"] = dict(
        tyngdepunkt_mm=[round(v, 1) for v in cg], over_bordet_mm=round(h, 1),
        innanfor_stotteflata=inne, min_avstand_kant_mm=round(d_kant, 1),
        veltevinkel_grad=velt, min_veltevinkel_grad=round(v_min, 1),
        krav_EN60598_2_4_innearmatur_grad=6.0, eige_krav_grad=12.0,
        bestatt_EN=v_min >= 6.0, bestatt_eige=v_min >= 12.0,
        kraft_N_vaagrett_i_toppen_mot_utkraginga=round(M * g * retn["mot_utkraginga_+x"] / (P0.S + hf), 2),
        kraft_N_vaagrett_i_toppen_framover=round(M * g * retn["framover_-y"] / (P0.S + hf), 2),
        fotkant="effektiv kant 2,5 mm frå fotsenteret (TPE Ø12)",
        trykk_paa_punktet=dict(hogd_mm=P0.pkt_z + hf,
                               kraft_N_for_vipp_bakover=round(M * g * retn["bakover_+y"] / (P0.pkt_z + hf), 2),
                               friksjon_N_mu05=round(0.5 * M * g, 2),
                               merknad="berøringa er kapasitiv; eit trykk under vippekrafta flyttar ikkje lampa"))
    print(f"masse {M:.0f} g, TP {cg[0]:.1f} {cg[1]:.1f} {cg[2]:.1f}, min velt {v_min:.1f} grader")

    # ------------------------------------------------ rørsle: innsetjing, batteri, plugg
    if not rask:
        kropp = cq.Compound.makeCompound([former[i] for i in PAA_KROPPEN])
        modul = cq.Compound.makeCompound([former[i] for i in MODUL])
        steg = []
        dzs = [0.5 * k for k in range(1, 21)] + [10.0 + 5.0 * k for k in range(1, 65)]
        for dz in dzs:
            v = snitt(modul.translate(cq.Vector(0, 0, dz)), kropp)
            steg.append((dz, round(v, 3)))
        rap["innsetjing_ovanfra"] = dict(
            metode="modulen flytta opp 0,5..10 mm i steg på 0,5 mm og vidare til 330 mm i steg på 5 mm (diskret); "
                   "berøringspunkta er ikkje i (dei kjem sist og skal ut først ved service)",
            steg_med_kollisjon=[s_ for s_ in steg if s_[1] > 0.05], bestatt=all(s_[1] <= 0.05 for s_ in steg))
        cel = former["K01"]
        hind = cq.Compound.makeCompound([former[i] for i in ("D02", "D09", "K03", "D01", "K13")])
        bsteg = [(5.0 * k, round(snitt(cel.translate(cq.Vector(0, 0, -5.0 * k)), hind), 3)) for k in range(1, 6)]
        rap["batteri_ut"] = dict(metode="luka og skruane av; cella flytta ned 5..25 mm (haldaren fjørar)",
                                 steg=bsteg, bestatt=all(s_[1] <= 0.05 for s_ in bsteg))
        plugg = former["E01"]
        psteg = [(5.0 * k, round(snitt(plugg.translate(cq.Vector(0, 0, -5.0 * k)),
                                       cq.Compound.makeCompound([former["D01"], former["D02"]])), 3))
                 for k in range(1, 7)]
        rap["plugg_ut"] = dict(steg=psteg, bestatt=all(s_[1] <= 0.05 for s_ in psteg))
        print(f"rørsle ferdig, {time.time() - t0:.0f} s")

    # ------------------------------------------------ flatmønster
    flat = {}
    flat["D01_kropp"] = F.kropp_dxf(DXF / "sveip_D01_kropp_flat.dxf")
    flat["D02_chassis"] = F.chassis_dxf(DXF / "sveip_D02_chassis_flat.dxf")
    flat["D03_lysbrett"] = F.enkel_dxf(DXF / "sveip_D03_lysbrett.dxf", L.lysbrett(),
                                       "SVEIP D03 LYSBRETT 5754 H22 t=1,5 + 10 x PEM CLS-M3-1")
    flat["D10_luke"] = F.enkel_dxf(DXF / "sveip_D10_luke.dxf", I.luke(), "SVEIP D10 LUKE 5754 H22 t=1,5")
    flat["D07_diffusor_ned"] = F.enkel_dxf(DXF / "sveip_D07_diffusor_ned.dxf", L.diffusor_ned(),
                                           "SVEIP D07 DIFFUSOR NED PMMA opal 2,0")
    flat["D08_diffusor_opp"] = F.enkel_dxf(DXF / "sveip_D08_diffusor_opp.dxf", L.diffusor_opp(),
                                           "SVEIP D08 DIFFUSOR OPP PMMA opal 1,5")
    # samsvar mellom flatmønster og 3D: areal x t mot volum
    import ezdxf
    from shapely.geometry import Polygon
    doc = ezdxf.readfile(DXF / "sveip_D01_kropp_flat.dxf")
    poly = [e for e in doc.modelspace().query("LWPOLYLINE") if e.dxf.layer == "SKJER"][0]
    from ezdxf import path as epath
    pts = [(v.x, v.y) for v in epath.make_path(poly).flattening(0.01)]
    a_blank = Polygon(pts).area - sum(math.pi * c.dxf.radius ** 2 for c in doc.modelspace().query("CIRCLE")
                                       if c.dxf.layer == "SKJER")
    v3d = former["D01"].Volume()
    flat["D01_kropp"]["samsvar"] = dict(blank_areal_cm2=round(a_blank / 100, 2),
                                        areal_x_t_cm3=round(a_blank * P0.t / 1e3, 2),
                                        volum_3d_cm3=round(v3d / 1e3, 2),
                                        avvik_pst=round(100 * (a_blank * P0.t - v3d) / v3d, 2))
    rap["flatmonster"] = flat

    # ------------------------------------------------ effektkjede og driftstid
    E = dict(lmW_3000=150.0, lmW_2700=140.0, varme_tap=0.95, T_diff_ned=0.65, T_diff_opp=0.70,
             kammer_ned=0.90, romning_opp=0.65, boost=0.88, varmedel=0.58,
             celle_Wh=round(4.9 * 3.6, 2), brukbar=0.90, aldra=0.80)
    led_ned = 400 / (E["T_diff_ned"] * E["kammer_ned"]) / (E["lmW_3000"] * E["varme_tap"])
    led_opp = 200 / (E["T_diff_opp"] * E["romning_opp"]) / (E["lmW_2700"] * E["varme_tap"])
    skinne_ned, skinne_opp = led_ned / E["boost"], led_opp / E["boost"]
    wh = E["celle_Wh"] * E["brukbar"]
    rap["effekt"] = dict(
        foresetnader=E,
        kjelde="lm/W frå Tridonic LLE 24x140 CRI90 (160/155 lm/W ved 100 mA), nedjustert; "
               "transmisjon PMMA opal 50-70 % (må målast); romning opp er eit overslag",
        arbeid_400lm_ut=dict(LED_W=round(led_ned, 2), skinne_W=round(skinne_ned, 2)),
        stemning_200lm_ut=dict(LED_W=round(led_opp, 2), skinne_W=round(skinne_opp, 2)),
        usb_tak_W=dict(standard_0_5A=2.2, A1_5=6.5, merknad="fastvara les CC og avgrensar summen av kanalane"),
        driftstid_t=dict(arbeid_ny=round(wh / skinne_ned, 1), arbeid_aldra=round(wh * E["aldra"] / skinne_ned, 1),
                         stemning_ny=round(wh / skinne_opp, 1),
                         stemning_aldra=round(wh * E["aldra"] / skinne_opp, 1)),
        krav=dict(T5_arbeid_1_5t=bool(wh / skinne_ned >= 1.5), T7_stemning_4t=bool(wh / skinne_opp >= 4.0)))
    # ------------------------------------------------ termisk nettverk (stasjonært, 25 grader C)
    import numpy as np
    a_brett = former["D03"].Area() / 1e6                 # begge sider
    a_kropp = former["D01"].Area() / 1e6                 # inn- og utside
    q_brett = min(led_ned + led_opp, 6.5 * E["boost"]) * E["varmedel"]
    q_bay = 1.2                                          # ladar, boost og MCU ved lading
    R_ta = 1 / (4.0 * a_brett)                           # brettet i lukka skjerm, h = 4
    a_rygg = (98.0 + 2 * 6.5) * P0.tc * 1e-6
    R_ts = 2.0 + 0.18 / (140.0 * a_rygg) + 0.5           # skrueskøyt + rygg + flens
    R_sa = 1 / (8.0 * a_kropp * 0.75)                    # kroppen mot luft, h = 8 (lakk, stråling)
    A = np.array([[1 / R_ta + 1 / R_ts, -1 / R_ts], [-1 / R_ts, 1 / R_ts + 1 / R_sa]])
    T = np.linalg.solve(A, np.array([q_brett, q_bay]))
    rap["termisk"] = dict(
        metode="to nodar (brett, kropp): brett mot luft h = 4 W/m2K, brett til kropp gjennom skrueskøyt, rygg og "
               "flens, kropp mot luft h = 8 W/m2K på 75 % av flata, varmedel 0,58 av LED-effekten; overslag",
        W_brett=round(float(q_brett), 2), W_stamme=q_bay,
        R_K_per_W=dict(brett_luft=round(R_ta, 1), brett_kropp=round(R_ts, 1), kropp_luft=round(R_sa, 2)),
        T_brett_C=round(25 + float(T[0]), 1), T_led_loddepunkt_C=round(25 + float(T[0]) + 3.0, 1),
        T_kropp_C=round(25 + float(T[1]), 1), krav_T8="gripeflater om lag 40 grader C",
        T8_bestatt=bool(25 + T[1] <= 40.0))
    # ------------------------------------------------ flatmønster mot 3D (punktkontroll)
    from sveip_kropp import kropp_flat as _kf
    kf = _kf()
    pk = []
    for namn_, sy in (("punkt framme", -1), ("punkt bak", 1)):
        y0 = -(P0.R + 3) if sy < 0 else P0.R - P0.t - 3
        stav = cq.Solid.makeCylinder(0.5, P0.t + 6.0, cq.Vector(P0.pkt_x, y0, P0.pkt_z), cq.Vector(0, 1, 0))
        pk.append(dict(hol=namn_, s=round(kf["s_framme"](P0.pkt_x) if sy < 0 else kf["s_bak"](P0.pkt_x), 2),
                       fritt=bool(snitt(stav, former["D01"]) < 1e-6)))
    for x in P0.fot_x:
        for sy in (-1, 1):
            stav = cq.Solid.makeCylinder(0.5, 6.0, cq.Vector(x, sy * P0.fl_yc, -3.0), cq.Vector(0, 0, 1))
            pk.append(dict(hol=f"spor x {x:g} y {sy * P0.fl_yc:g}", fritt=bool(snitt(stav, former["D01"]) < 1e-6)))
    rap["flat_mot_3d"] = dict(
        metode="hol frå flatmønsteret ført til 3D; ein stav Ø1 gjennom kvart hol skal ikkje treffe kroppen",
        hol=pk, bestatt=all(h_["fritt"] for h_ in pk))

    # ------------------------------------------------ stykkliste
    with open(ROT / "produksjon" / "sveip_stykkliste.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["id", "namn", "tal", "materiale / delenummer", "type", "masse_per_stk_g", "masse_samla_g",
                    "mål_per_stk_mm", "step"])
        for r in delrap:
            s1 = former[r["id"]]
            solids = s1.Solids()
            eitt = solids[0] if r["tal"] > 1 and len(solids) >= r["tal"] else s1
            bb1 = eitt.BoundingBox()
            d_ = meta[r["id"]]
            w.writerow([r["id"], r["namn"], r["tal"], r["materiale"], r["type"],
                        round(eitt.Volume() / 1e3 * d_[4], 2), r["masse_g"],
                        f"{bb1.xlen:.1f} x {bb1.ylen:.1f} x {bb1.zlen:.1f}", r["step"]])
        for rad in TILLEGG_BOM:
            w.writerow(rad)
    # ------------------------------------------------ geometri for Blender
    geo = []
    for d in SA.DELAR:
        geo.append(dict(id=d[0], namn=d[1], stl=f"produksjon/stl/{namn(d)}.stl", farge=d[5], type=d[6],
                        modul=d[0] in MODUL))
    (RENDER / "geometri.json").write_text(json.dumps(dict(delar=geo, fot_h=P0.fot_h), ensure_ascii=False,
                                                     indent=1), encoding="utf-8")
    rap["status"] = dict(
        digital_kontroll=all([rap["kollisjon"]["bestatt"], rap["klaring"]["bestatt"], rap["kontakt"]["bestatt"],
                              rap["masse"]["F8_bestatt"], rap["stabilitet"]["bestatt_EN"],
                              rap["flat_mot_3d"]["bestatt"], rap["termisk"]["T8_bestatt"]]
                             + ([rap["innsetjing_ovanfra"]["bestatt"], rap["batteri_ut"]["bestatt"],
                                 rap["plugg_ut"]["bestatt"]] if not rask else [])),
        slicer_kontroll=_slicestatus(), fysisk_prototype="ikkje laga",
        rorsle="diskret prøvd (innsetjing 0,5 mm dei siste 10 mm, elles 5 mm; batteri og plugg 5 mm), ikkje kontinuerleg")
    rap["tid_s"] = round(time.time() - t0, 1)
    (KONTROLL / "sveip_kontroll.json").write_text(json.dumps(rap, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: rap[k] for k in ("masse", "stabilitet", "status")}, ensure_ascii=False, indent=1))
    print(f"ferdig {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main(rask="--rask" in sys.argv)
