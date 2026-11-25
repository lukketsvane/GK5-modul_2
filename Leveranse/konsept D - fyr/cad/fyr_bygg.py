# -*- coding: utf-8 -*-
"""FYR · byggjer alle delane, eksporterer STEP/STL og køyrer maskinell kontroll.

Køyr frå mappa «konsept D - fyr»:
    py -3 cad/fyr_bygg.py              # alt (serie + prototype, kontroll i alle ni stillingar)
    py -3 cad/fyr_bygg.py --raskt      # berre delar og eksport, ingen kollisjonskontroll

Skriv:
    cad/fyr_<del>.step                 serie (produksjonsgeometri)
    cad/fyr_samanstilling.step         serie, hylsa i stilling 0° (open)
    produksjon/fyr_<del>_P1S.stl       prototype (P1S-prent)
    kontroll/fyr_CAD_verifisering.json, kontroll/fyr_BOM.csv
"""
from __future__ import annotations

import csv
import itertools
import json
import math
import sys
import time
from pathlib import Path

import cadquery as cq
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

HER = Path(__file__).resolve().parent
ROT = HER.parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402

CAD = ROT / "cad"
PROD = ROT / "produksjon"
KONTROLL = ROT / "kontroll"

TETT = {  # g/cm3
    "serie": {"01_fot": 2.70, "03_chassis": 1.01, "04_mantel": 2.70, "05_hylse": 8.47, "05b_hylsefot": 1.41,
              "05c_stoppskruar": 7.85, "06_lysstav": 2.70, "06b_led_side": 1.8, "06c_led_topp": 1.8,
              "06d_kontakt": 1.6, "07_lysrist": 1.01, "08_lok": 1.19, "10_glidering": 1.41, "11_oring": 1.15,
              "12_brytarar": 1.6, "13_jack": 2.0, "14_kretskort": 1.4, "11b_snor": 1.15},
    "prototype": {"01_fot": 1.24, "03_chassis": 1.27, "04_mantel": 1.24, "05_hylse": 1.24, "05b_hylsefot": 1.24,
                  "05c_stoppskruar": 7.85, "06_lysstav": 2.70, "06b_led_side": 1.8, "06c_led_topp": 1.8,
                  "06d_kontakt": 1.6, "07_lysrist": 1.27, "08_lok": 1.19, "10_glidering": 1.27, "11_oring": 1.15,
                  "12_brytarar": 1.6, "13_jack": 2.0, "14_kretskort": 1.4, "11b_snor": 1.15},
}
ROTERANDE = ("05_hylse", "05b_hylsefot", "05c_stoppskruar")
# kva stillestående delar kvar roterande del kan nå (resten er langt unna og blir ikkje prøvd i kvar stilling)
NABOAR = {
    "05_hylse": ("04_mantel", "10_glidering", "07_lysrist", "08_lok", "03_chassis"),
    "05b_hylsefot": ("03_chassis", "12_brytarar", "04_mantel", "07_lysrist"),
    "05c_stoppskruar": ("03_chassis", "04_mantel"),
}


def klaringar_analytisk(p: g.FyrParams) -> dict:
    """Radielle klaringar i dei rørslene som betyr noko, rekna frå parametrane (designverdiar)."""
    return {
        "hylse_ut_mot_glidering": round(p.r_glide_i - p.r_ho, 3),
        "hylse_ut_mot_mantel": round(p.r_mi - p.r_ho, 3),
        "hylsefot_ut_mot_mantel": round(p.r_mi - p.r_ho, 3),
        "hylsefot_bor_mot_tapp": round(p.bor_r - p.tapp_ro, 3),
        "toppdekk_mot_mantel": round(p.r_mi - p.toppdekk_r, 3),
        "randring_mot_hylse_inn": round(p.r_hi - p.r_rand_ut, 3),
        "lysrist_skjold_mot_hylse_inn": round(p.r_hi - (p.skjold_r + p.skjold_t), 3),
        "mantel_i_fotspor_inn": p.spor_klaring_inn, "mantel_i_fotspor_ut": p.spor_klaring_ut,
    }
FORVENTA_KONTAKT = {  # par som skal røre kvarandre (null volum, men avstand 0)
    ("05b_hylsefot", "12_brytarar"), ("01_fot", "03_chassis"), ("01_fot", "04_mantel"), ("01_fot", "11_oring"),
    ("05_hylse", "05b_hylsefot"), ("05b_hylsefot", "05c_stoppskruar"), ("04_mantel", "10_glidering"),
    ("07_lysrist", "08_lok"), ("06_lysstav", "07_lysrist"), ("06_lysstav", "06b_led_side"), ("06_lysstav", "06c_led_topp"),
    ("06_lysstav", "06d_kontakt"), ("03_chassis", "06d_kontakt"), ("03_chassis", "12_brytarar"), ("03_chassis", "05b_hylsefot"),
    ("03_chassis", "13_jack"), ("03_chassis", "14_kretskort"), ("06d_kontakt", "13_jack"), ("07_lysrist", "06c_led_topp"),
    ("05_hylse", "05c_stoppskruar"), ("01_fot", "11b_snor"), ("04_mantel", "11b_snor"), ("03_chassis", "04_mantel"),
}


def shape_of(wp) -> cq.Shape:
    vals = wp.vals()
    return vals[0] if len(vals) == 1 else cq.Compound.makeCompound(vals)


def bbox_overlap(a: cq.Shape, b: cq.Shape, m: float = 0.05) -> bool:
    A, B = a.BoundingBox(), b.BoundingBox()
    return not (A.xmax + m < B.xmin or B.xmax + m < A.xmin or A.ymax + m < B.ymin or B.ymax + m < A.ymin
                or A.zmax + m < B.zmin or B.zmax + m < A.zmin)


def overlapp(a: cq.Shape, b: cq.Shape) -> float:
    try:
        r = a.intersect(b)
        return r.Volume() if r is not None else 0.0
    except Exception:  # noqa: BLE001
        return float("nan")


def avstand(a: cq.Shape, b: cq.Shape) -> float:
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value() if d.IsDone() else float("nan")


def inni(s: cq.Shape, x, y, z) -> bool:
    return s.isInside(cq.Vector(x, y, z), 1e-4)


def stilling_tilstand(p: g.FyrParams, theta: float, hylse: cq.Shape, fotring: cq.Shape) -> dict:
    """Kor mange spalter er opne, og kva brytarar er trykte, når hylsa står i theta."""
    zm = (p.z_spalte_0 + p.z_spalte_1) / 2.0
    opne = 0
    for a in p.vindauge_vinklar:
        r = (p.r_ho + p.r_hi) / 2.0
        blokk = False
        for dy in (-1.4, 0.0, 1.4):
            da = math.degrees(dy / r)
            x, y = g.polar(r, a + da)
            for dz in (-50.0, 0.0, 50.0):
                if inni(hylse, x, y, zm + dz):
                    blokk = True
        opne += 0 if blokk else 1
    ut = {"theta": theta, "opne_spalter": opne}
    for (a_sw, _t), namn in zip(p.sw, p.sw_namn):
        x, y = g.polar(p.sw_r, a_sw)
        # brytaren er trykt (lukka) når fotringen har materiale 0,3 mm over toppdekket der armen ligg
        ut[namn.split(" ")[0] + "_lukka"] = bool(inni(fotring, x, y, p.toppdekk_z1 + 0.3))
    return ut


def bygg_variant(p: g.FyrParams, theta: float = 0.0) -> dict:
    return {k: shape_of(v) for k, v in g.bygg_alle(p, theta).items()}


def main() -> None:
    raskt = "--raskt" in sys.argv
    t0 = time.time()
    for d in (CAD, PROD, KONTROLL):
        d.mkdir(parents=True, exist_ok=True)

    rapport = {"skildring": f"FYR {g.REVISJON} maskinell kontroll ({g.DATO})", "revisjon": g.REVISJON, "dato": g.DATO, "variantar": {}}
    for p in (g.FyrParams(), g.FyrParams.prototype()):
        v = p.variant
        print(f"===== {v} =====")
        delar = bygg_variant(p, 0.0)
        r = {"params": {k: (list(x) if isinstance(x, tuple) else x) for k, x in p.__dict__.items()}, "delar": {}}
        for namn, s in delar.items():
            gyldig = bool(BRepCheck_Analyzer(s.wrapped).IsValid())
            vol = s.Volume() / 1000.0
            m = vol * TETT[v][namn]
            bb = s.BoundingBox()
            com = cq.Shape.centerOfMass(s)
            r["delar"][namn] = {"materiale": g.DELAR[namn][1], "gyldig_brep": gyldig, "lekamar": len(s.Solids()),
                                "volum_cm3": round(vol, 3), "masse_g": round(m, 1),
                                "bbox_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
                                "z_mm": [round(bb.zmin, 2), round(bb.zmax, 2)],
                                "tyngdepunkt_mm": [round(com.x, 2), round(com.y, 2), round(com.z, 2)]}
            print(f"  {namn:18s} V={vol:8.2f} cm3  m={m:7.1f} g  gyldig={gyldig}  lekamar={len(s.Solids())}")
        mt = sum(x["masse_g"] for x in r["delar"].values())
        zc = sum(x["masse_g"] * x["tyngdepunkt_mm"][2] for x in r["delar"].values()) / mt
        rs = p.oring_id / 2.0 + p.oring_strekk_r + p.oring_snor / 2.0      # senterlinja til O-ringen (veltekant, konservativt)
        r["sum"] = {"masse_g": round(mt, 1), "tyngdepunkt_z_mm": round(zc, 1), "stotteradius_mm": round(rs, 2),
                    "veltevinkel_grader": round(math.degrees(math.atan2(rs, zc)), 1),
                    "total_hogd_mm": round(p.z_hylse_1, 1), "fotavtrykk_cm2": round(math.pi * (p.fot_d / 2) ** 2 / 100, 1)}
        print("  SUM", r["sum"])

        # eksport
        if v == "serie":
            for namn, s in delar.items():
                cq.exporters.export(s, str(CAD / f"fyr_{namn}.step"))
            assy = cq.Assembly(name="FYR")
            for namn, s in delar.items():
                assy.add(s, name=namn, color=cq.Color(*g.DELAR[namn][2]))
            assy.export(str(CAD / "fyr_samanstilling.step"))
        else:
            hm = shape_of(g.hylse(p))
            m_ned, m_opp = g.mantel_prototype_delar(p)
            prent = {"01_fot": delar["01_fot"], "03_chassis": delar["03_chassis"],
                     "04a_mantel_nedre": shape_of(m_ned), "04b_mantel_ovre": shape_of(m_opp),
                     "05_hylse_med_fot": hm, "06d_mastfot": shape_of(g.mastfot(p)), "07_lysrist": delar["07_lysrist"],
                     "10_glidering": delar["10_glidering"]}
            for namn, s in prent.items():
                bb = s.BoundingBox()
                n_lek = len(s.Solids())
                r.setdefault("prent", {})[namn] = {"bbox_mm": [round(bb.xlen, 2), round(bb.ylen, 2), round(bb.zlen, 2)],
                                                             "gyldig_brep": bool(BRepCheck_Analyzer(s.wrapped).IsValid()),
                                                             "lekamar": n_lek, "eitt_stykke": n_lek == 1,
                                                             "passar_P1S_256": bool(max(bb.xlen, bb.ylen, bb.zlen) <= 250.0)}
                print(f"  prent {namn:20s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f}  P1S: {max(bb.xlen, bb.ylen, bb.zlen) <= 250.0}"
                      f"  lekamar: {n_lek}{'' if n_lek == 1 else '  <<< FLEIRE LEKAMAR'}")
            for namn, s in prent.items():
                cq.exporters.export(s, str(PROD / f"fyr_{namn}_P1S.stl"), tolerance=0.01, angularTolerance=0.05)
                cq.exporters.export(s, str(CAD / f"fyr_{namn}_prototype.step"))

        if not raskt:
            # 1) kollisjonar mellom stillestående delar (éin gong)
            statiske = [k for k in delar if k not in ROTERANDE]
            par = []
            for a, b in itertools.combinations(statiske, 2):
                if not bbox_overlap(delar[a], delar[b]):
                    continue
                ov = overlapp(delar[a], delar[b])
                par.append({"a": a, "b": b, "theta": None, "overlapp_mm3": round(ov, 4)})
            # 2) roterande mot dei stillestående naboane sine i alle ni stillingar (volumsnitt)
            tilstandar = []
            klaring_min = klaringar_analytisk(p)
            for k in range(int(round(p.vandring / p.deling)) + 1):
                th = k * p.deling
                rot = {a: delar[a].rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), -th) for a in ROTERANDE}
                tilstandar.append(stilling_tilstand(p, th, rot["05_hylse"], rot["05b_hylsefot"]))
                for a in ROTERANDE:
                    for b in NABOAR[a]:
                        if not bbox_overlap(rot[a], delar[b]):
                            continue
                        ov = overlapp(rot[a], delar[b])
                        par.append({"a": a, "b": b, "theta": th, "overlapp_mm3": round(ov, 4)})
                print(f"  θ={th:6.2f}  {tilstandar[-1]}", flush=True)
            # 3) innføringsveg for lysmodulen ovanfrå: sveip av mastfoten og av omrisset til rista ned til plassen sin
            fot_sveip = cq.Workplane("XY").workplane(offset=p.mastfot_z0).rect(p.mastfot_b, p.mastfot_l).extrude(320 - p.mastfot_z0).val()
            veg = {}
            for b in ("03_chassis", "05b_hylsefot", "05_hylse", "13_jack"):
                veg[f"mastfot_gjennom_{b}_mm3"] = round(overlapp(fot_sveip, delar[b]), 4)
            r_maks_modul = max(p.r_rand_ut, p.skjold_r + p.skjold_t)
            veg["modul_storste_radius_mm"] = round(r_maks_modul, 2)
            veg["kragen_bor_radius_mm"] = round(p.r_hi, 2)
            veg["klaring_modul_i_kragen_mm"] = round(p.r_hi - r_maks_modul, 2)
            veg["bestatt"] = all(v < 1e-3 for kk, v in veg.items() if kk.endswith("_mm3")) and p.r_hi - r_maks_modul > 0.2
            r["innforingsveg_lysmodul"] = veg
            print("  innføringsveg lysmodul:", veg, flush=True)
            r["par"] = par
            r["kollisjonar"] = [x for x in par if (x["overlapp_mm3"] > 1e-3 or x["overlapp_mm3"] != x["overlapp_mm3"])]
            r["stillingar"] = tilstandar
            r["minste_klaring_rorsle_mm"] = klaring_min
            for x in r["kollisjonar"]:
                print(f"  KOLLISJON {x['a']} x {x['b']} θ={x['theta']}: {x['overlapp_mm3']} mm3")
            for kk, vv in sorted(klaring_min.items(), key=lambda t: t[1]):
                print(f"  minste klaring {kk}: {vv} mm")
        rapport["variantar"][v] = r

    (KONTROLL / "fyr_CAD_verifisering.json").write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(KONTROLL / "fyr_BOM.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["variant", "del", "materiale", "volum_cm3", "masse_g", "bbox_x", "bbox_y", "bbox_z"])
        for v, r in rapport["variantar"].items():
            for namn, d in r["delar"].items():
                w.writerow([v, namn, d["materiale"], d["volum_cm3"], d["masse_g"], *d["bbox_mm"]])
    print(f"ferdig på {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
