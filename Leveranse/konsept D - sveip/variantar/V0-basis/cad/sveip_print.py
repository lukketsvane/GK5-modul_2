# -*- coding: utf-8 -*-
"""Printfiler for Sveip på Bambu Lab P1S (0,4 mm dyse, Textured PEI), slica med Bambu Studio CLI.

Plater:
  A  skissemodell 1:2, kroppen med 1,6 mm vegg, opp ned (toppkanten mot plata): ingen støtte
  B  volummodell 1:1, skjermen (z 167,5..300), opp ned og diagonalt på plata
  C  volummodell 1:1, stamma (z 0..167,5), opp ned
  D  prototypedelar 1:1: ramme D06 og to hylser D13, PETG
  E  skøyteband (U) som blir limt inni over skøyten mellom B og C
Køyr frå cad/: python sveip_print.py [A B C D]
"""
from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import replace
from pathlib import Path

sys.dont_write_bytecode = True
from lagprio import lag_prioritet  # noqa: E402

lag_prioritet()
import cadquery as cq  # noqa: E402

import sveip_innmat as I  # noqa: E402
import sveip_kropp as K  # noqa: E402
import sveip_lys as L  # noqa: E402
from sveip_geometri import P0, boks, stadion  # noqa: E402

ROT = Path(__file__).resolve().parent.parent
PRINT = ROT / "print"
PRINT.mkdir(exist_ok=True)
BBL = Path(os.environ.get("APPDATA", "")) / "BambuStudio" / "system" / "BBL"
EXE = [Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "BambuStudio" / "bambu-studio.exe",
       Path(r"C:\Program Files\Bambu Studio\bambu-studio.exe")]
PLATE = 256.0
LIM = 245.0           # brukbart: sperresone 18 x 28 i fremre venstre hjørne og brim


def profil(kind, namn):
    kjede, cur = [], namn
    while cur:
        p = BBL / kind / f"{cur}.json"
        if not p.exists():
            treff = list((BBL / kind).rglob(f"{cur}.json"))
            if not treff:
                raise FileNotFoundError(f"{kind}/{cur}.json")
            p = treff[0]
        d = json.loads(p.read_text(encoding="utf-8"))
        kjede.append(d)
        cur = d.get("inherits")
    ut = {}
    for d in reversed(kjede):
        ut.update(d)
    ut.pop("inherits", None)
    return ut


def til_plata(form, rot_z=0.0, cx=128.0, cy=128.0):
    s = form.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rot_z) if rot_z else form
    bb = s.BoundingBox()
    return s.translate(cq.Vector(cx - (bb.xmin + bb.xmax) / 2, cy - (bb.ymin + bb.ymax) / 2, -bb.zmin))


def opp_ned(form):
    return form.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)


def kropp_print(t, flens=False, hol=True):
    p = replace(P0, t=t)
    k = K.kropp(p, med_hol=hol).val()
    if not flens:   # skjer bort botnflensane (dei er innanfor veggen, under z = 6)
        inne = stadion(p.S - 2 * t, p.D - 2 * t, -1, 7, x0=t).val()
        k = k.cut(inne)
    return k


def plate_A():
    k = kropp_print(3.2, hol=False).scale(0.5)
    return [("Sveip_1-2_skissemodell", til_plata(opp_ned(k)))], dict(
        filament="Bambu PLA Matte @BBL P1S 0.4 nozzle", vegg=1.6, ams="A4 Bambu PLA Matte")


def _skoyteband(t, h=16.0, kl=0.3, tb=1.6):
    """U-band som ligg inni stamma og skjermen over skøyten (limast)."""
    p = P0
    ytre = stadion(p.S - 2 * (t + kl), p.D - 2 * (t + kl), p.z_skjerm - h / 2, h, x0=t + kl).val()
    indre = stadion(p.S - 2 * (t + kl + tb), p.D - 2 * (t + kl + tb), p.z_skjerm - h, 2 * h,
                    x0=t + kl + tb).val()
    band = ytre.cut(indre)
    return band.intersect(boks(-10, p.x_stamme - 4.0, -100, 100, -10, 400).val())


def plate_B():
    t = 2.0
    k = kropp_print(t)
    skjerm = k.intersect(boks(-10, 400, -100, 100, P0.z_skjerm, 400).val())
    s = til_plata(opp_ned(skjerm), rot_z=-45.0)
    return [("Sveip_1-1_skjerm", s)], dict(filament="Bambu PLA Matte @BBL P1S 0.4 nozzle", vegg=t,
                                           ams="A4 Bambu PLA Matte", brim=3)


def plate_C():
    t = 2.0
    k = kropp_print(t)
    stamme = k.intersect(boks(-10, 400, -100, 100, -10, P0.z_skjerm).val())
    return [("Sveip_1-1_stamme", til_plata(opp_ned(stamme)))], dict(
        filament="Bambu PLA Matte @BBL P1S 0.4 nozzle", vegg=t, ams="A4 Bambu PLA Matte", brim=3)


def plate_E():
    band = _skoyteband(2.0)
    return [("Sveip_1-1_skoyteband", til_plata(band))], dict(
        filament="Bambu PLA Matte @BBL P1S 0.4 nozzle", vegg=1.6, ams="A4 Bambu PLA Matte", brim=3)


def plate_D():
    r = L.ramme().val()
    r = r.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)     # leppa (diffusorsida) opp
    h1 = I.bossing(-1).val().rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90)
    h2 = I.bossing(1).val().rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 90)
    return [("Sveip_D06_ramme", til_plata(r, cx=110.0, cy=128.0)),
            ("Sveip_D13_hylse_1", til_plata(h1, cx=200.0, cy=110.0)),
            ("Sveip_D13_hylse_2", til_plata(h2, cx=200.0, cy=150.0))], dict(
        filament="Bambu PETG HF @BBL P1S 0.4 nozzle", vegg=1.2, ams="A3 PETG", brim=4, stotte=False)


def slice_plate(namn, delar, info):
    tmp = Path(tempfile.mkdtemp(prefix="sveip_bambu_"))
    stler = []
    for dn, form in delar:
        bb = form.BoundingBox()
        assert bb.xmin >= 0 and bb.ymin >= 0 and bb.xmax <= PLATE and bb.ymax <= PLATE, (dn, bb.xmin, bb.xmax, bb.ymin, bb.ymax)
        assert bb.zmax <= 250.0, (dn, bb.zmax)
        sti = tmp / f"{dn}.stl"
        cq.exporters.export(cq.Workplane().add(form), str(sti), tolerance=0.03, angularTolerance=0.1)
        shutil.copy(sti, PRINT / f"{dn}.stl")
        stler.append(sti)
    mach = profil("machine", "Bambu Lab P1S 0.4 nozzle")
    proc = profil("process", "0.20mm Standard @BBL X1C")
    fil = profil("filament", info["filament"])
    loops = max(2, math.ceil(info["vegg"] / 0.42))
    proc.update({"wall_loops": str(loops), "wall_generator": "arachne", "sparse_infill_density": "15%",
                 "sparse_infill_pattern": "gyroid", "seam_position": "back",
                 "enable_support": "1" if info.get("stotte") else "0",
                 "brim_type": "outer_only", "brim_width": str(info.get("brim", 3)), "brim_object_gap": "0.1",
                 "elefant_foot_compensation": "0.15", "curr_bed_type": "Textured PEI Plate"})
    for nm, d in (("m.json", mach), ("p.json", proc), ("f.json", fil)):
        (tmp / nm).write_text(json.dumps(d, indent=1), encoding="utf-8")
    exe = next((e for e in EXE if e.exists()), None)
    ut = PRINT / f"{namn}.3mf"
    rapport = dict(plate=namn, delar=[d for d, _ in delar], filament=info["filament"], ams=info["ams"],
                   prosess="0.20mm Standard @BBL X1C", veggloekker=loops, skrivar="Bambu Lab P1S 0.4 nozzle",
                   plate_type="Textured PEI Plate")
    if exe is None:
        rapport["slica"] = False
        rapport["feil"] = "fann ikkje bambu-studio.exe"
        return rapport
    cmd = [str(exe), "--orient", "0", "--arrange", "0", "--load-settings", f"{tmp / 'm.json'};{tmp / 'p.json'}",
           "--load-filaments", str(tmp / "f.json"), "--slice", "0", "--outputdir", str(tmp),
           "--export-3mf", ut.name] + [str(s) for s in stler]
    res = subprocess.run(cmd, capture_output=True, text=True, creationflags=0x40, timeout=1800)
    laga = tmp / ut.name
    rapport["returkode"] = res.returncode
    if laga.exists():
        shutil.copy(laga, ut)
        with zipfile.ZipFile(ut) as z:
            namn_ = z.namelist()
            gk = [n for n in namn_ if n.endswith(".gcode")]
            info_ = z.read("Metadata/slice_info.config").decode() if "Metadata/slice_info.config" in namn_ else ""
        rapport["slica"] = bool(gk)
        m = re.search(r'key="prediction" value="(\d+)"', info_)
        w = re.search(r'key="weight" value="([\d.]+)"', info_)
        o = re.findall(r'key="outside" value="(\w+)"', info_)
        rapport["tid_t"] = round(int(m.group(1)) / 3600, 2) if m else None
        rapport["masse_g"] = float(w.group(1)) if w else None
        rapport["utanfor_plata"] = o
    else:
        rapport["slica"] = False
        rapport["feil"] = (res.stdout[-400:] + res.stderr[-400:])
    shutil.rmtree(tmp, ignore_errors=True)
    return rapport


def main(val):
    plater = {"A": plate_A, "B": plate_B, "C": plate_C, "D": plate_D, "E": plate_E}
    namn = {"A": "Sveip_A_skissemodell_1-2_PLA", "B": "Sveip_B_volum_1-1_skjerm_PLA",
            "C": "Sveip_C_volum_1-1_stamme_PLA", "D": "Sveip_D_prototypedelar_PETG",
            "E": "Sveip_E_volum_1-1_skoyteband_PLA"}
    rap = []
    for k in val:
        delar, info = plater[k]()
        r = slice_plate(namn[k], delar, info)
        print(json.dumps(r, ensure_ascii=False))
        rap.append(r)
    sti = PRINT / "print_rapport.json"
    gamal = json.loads(sti.read_text(encoding="utf-8")) if sti.exists() else []
    gamal = [g for g in gamal if g["plate"] not in {r["plate"] for r in rap}] + rap
    sti.write_text(json.dumps(gamal, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if a in "ABCDE"] or ["A", "B", "C", "D", "E"])
