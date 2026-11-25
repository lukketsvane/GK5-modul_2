# -*- coding: utf-8 -*-
"""FYR · skjer prototypen for Bambu Lab P1S (0,4 mm dyse) med Bambu Studio CLI.

    py -3 cad/fyr_print.py            # byggjer, orienterer og skjer alle fem platene
    py -3 cad/fyr_print.py 3          # berre plate 3

Skriv print/FYR_P1S_<n>_<namn>.3mf (ferdig skore, G-kode inni) og print/FYR_P1S_plater.json
(tid, filament i gram, støtte, mål). Orientering og prosessval står i PLATER under.
Grunnlag: oppskrifta i konsept C (samle_hovudprosjekt.py / raup_geometri.py), profilane
frå %APPDATA%/BambuStudio/system/BBL (flata ut før --load-settings).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree

import cadquery as cq

HER = Path(__file__).resolve().parent
ROT = HER.parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402

PRINT = ROT / "print"
EXE = Path(os.environ["LOCALAPPDATA"]) / "Programs/BambuStudio/bambu-studio.exe"
PROFILAR = Path(os.environ["APPDATA"]) / "BambuStudio/system/BBL"
MASKIN = "Bambu Lab P1S 0.4 nozzle"
PROSESS = "0.20mm Standard @BBL X1C"
PLA_MATT = "Bambu PLA Matte @BBL P1S 0.4 nozzle"
PLA_SILK = "Bambu PLA Silk+ @BBL P1S 0.4 nozzle"
PETG_HF = "Bambu PETG HF @BBL P1S 0.4 nozzle"

FELLES = {"enable_support": "0", "support_type": "tree(auto)", "support_style": "tree_hybrid",
          "support_on_build_plate_only": "1", "support_threshold_angle": "35",
          "seam_position": "back", "wall_generator": "arachne", "brim_type": "outer_only", "brim_width": "5",
          "brim_object_gap": "0.1", "elefant_foot_compensation": "0.15", "curr_bed_type": "Textured PEI Plate"}
FUZZY = {"fuzzy_skin": "external", "fuzzy_skin_first_layer": "0", "fuzzy_skin_thickness": "0.08",
         "fuzzy_skin_point_distance": "0.25"}


def solid(wp):
    v = wp.vals()
    return v[0] if len(v) == 1 else cq.Compound.makeCompound(v)


def delar_prototype():
    p = g.FyrParams.prototype()
    ned, opp = g.mantel_prototype_delar(p)
    return p, {
        "01_fot": solid(g.fot(p)),
        "03_chassis": solid(g.chassis(p)),
        "04a_mantel_nedre": solid(ned),
        "04b_mantel_ovre": solid(opp),
        "05_hylse_med_fot": solid(g.hylse(p)),
        "06d_mastfot": solid(g.mastfot(p)),
        "07_lysrist": solid(g.lysrist(p)),
        "10_glidering": solid(g.glidering(p)),
    }


# rot = rotasjon om z (grader) slik at lampa sin bakside (asimut 180°) vender bak på plata (+Y) der saumen
# skal liggje (seam_position=back); snu = prent opp ned (rotasjon 180° om X).
PLATER = [
    {"nr": 1, "namn": "mantel_ovre_PLA-Matte-oksebloddraud", "filament": PLA_MATT, "delar": [("04b_mantel_ovre", -90, False)],
     "prosess": {**FELLES, **FUZZY, "wall_loops": "5", "sparse_infill_density": "15%", "top_shell_layers": "4",
                 "bottom_shell_layers": "4"}},
    {"nr": 2, "namn": "mantel_nedre_og_fot_PLA-Matte-oksebloddraud", "filament": PLA_MATT,
     "delar": [("04a_mantel_nedre", -90, False), ("01_fot", -90, False)],
     "prosess": {**FELLES, **FUZZY, "wall_loops": "5", "sparse_infill_density": "25%", "sparse_infill_pattern": "gyroid",
                 "top_shell_layers": "5", "bottom_shell_layers": "4"}},
    {"nr": 3, "namn": "hylse_PLA-Silk-messing", "filament": PLA_SILK, "delar": [("05_hylse_med_fot", 90, False)],
     "prosess": {**FELLES, "enable_support": "1", "wall_loops": "4", "sparse_infill_density": "25%",
                 "sparse_infill_pattern": "gyroid", "top_shell_layers": "5", "bottom_shell_layers": "4"}},
    {"nr": 4, "namn": "chassis_glidering_mastfot_PETG-HF-svart", "filament": PETG_HF,
     "delar": [("03_chassis", 0, False), ("10_glidering", 0, False), ("06d_mastfot", 0, False)],
     "prosess": {**FELLES, "enable_support": "1", "support_on_build_plate_only": "0", "wall_loops": "4", "sparse_infill_density": "25%",
                 "sparse_infill_pattern": "gyroid", "top_shell_layers": "5", "bottom_shell_layers": "4"}},
    {"nr": 5, "namn": "lysrist_PETG-HF-kvit", "filament": PETG_HF, "delar": [("07_lysrist", 0, True)],
     "prosess": {**FELLES, "enable_support": "1", "wall_loops": "2", "sparse_infill_density": "15%",
                 "top_shell_layers": "4", "bottom_shell_layers": "3", "brim_width": "8"}},
]


def flat_ut(mappe: Path, namn: str) -> dict:
    rec = json.loads((mappe / (namn + ".json")).read_text(encoding="utf-8-sig"))
    ut = {}
    if rec.get("inherits"):
        ut.update(flat_ut(mappe, rec["inherits"]))
    for ref in rec.get("include", []):
        ut.update(flat_ut(mappe, ref))
    ut.update({k: v for k, v in rec.items() if k not in {"inherits", "include"}})
    return ut


def plasser(s: cq.Shape, rot: float, snu: bool) -> cq.Shape:
    if snu:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
    if rot:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), rot)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-(bb.xmin + bb.xmax) / 2, -(bb.ymin + bb.ymax) / 2, -bb.zmin))


def kjor(args, cwd):
    t = time.time()
    proc = subprocess.Popen([str(EXE), *args], cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x0200 | 0x0400, False, proc.pid)
        ctypes.windll.kernel32.SetPriorityClass(h, 0x40)
        ctypes.windll.kernel32.SetProcessAffinityMask(h, 0xFC)
    except Exception:  # noqa: BLE001
        pass
    out, err = proc.communicate(timeout=1800)
    if proc.returncode:
        raise RuntimeError((proc.returncode, out[-3000:], err[-3000:]))
    return time.time() - t


def les_3mf(fil: Path) -> dict:
    with zipfile.ZipFile(fil) as z:
        namn = z.namelist()
        info = ElementTree.fromstring(z.read("Metadata/slice_info.config"))
        g_kode = [n for n in namn if n.endswith(".gcode")]
        hovud = z.read(g_kode[0]).decode("utf-8", "ignore")[:20000] if g_kode else ""
    plate = info.find("plate")
    meta = {m.get("key"): m.get("value") for m in plate.findall("metadata")}
    fil_el = plate.findall("filament")
    tid = re.search(r"; model printing time: (.+)", hovud)
    return {"prediksjon_s": meta.get("prediction"), "vekt_g": meta.get("weight"), "utanfor": meta.get("outside"),
            "stotte_brukt": meta.get("support_used"),
            "filament_g": [f.get("used_g") for f in fil_el], "gcode_tid": tid.group(1).strip() if tid else None,
            "gcode_inni": bool(g_kode)}


def main():
    berre = {int(a) for a in sys.argv[1:] if a.isdigit()}
    PRINT.mkdir(parents=True, exist_ok=True)
    p, delar = delar_prototype()
    rapport_fil = PRINT / "FYR_P1S_plater.json"
    rapport = json.loads(rapport_fil.read_text(encoding="utf-8")) if rapport_fil.exists() else {}
    maskin = flat_ut(PROFILAR / "machine", MASKIN)
    for pl in PLATER:
        if berre and pl["nr"] not in berre:
            continue
        with tempfile.TemporaryDirectory(prefix="fyr-p1s-") as td:
            tmp = Path(td)
            prosess = flat_ut(PROFILAR / "process", PROSESS)
            prosess.update(pl["prosess"])
            filament = flat_ut(PROFILAR / "filament", pl["filament"])
            (tmp / "machine.json").write_text(json.dumps(maskin, ensure_ascii=False), encoding="utf-8")
            (tmp / "process.json").write_text(json.dumps(prosess, ensure_ascii=False), encoding="utf-8")
            (tmp / "filament.json").write_text(json.dumps(filament, ensure_ascii=False), encoding="utf-8")
            filer, maal = [], {}
            for (namn, rot, snu) in pl["delar"]:
                s = plasser(delar[namn], rot, snu)
                bb = s.BoundingBox()
                maal[namn] = [round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)]
                f = tmp / f"{namn}.stl"
                cq.exporters.export(s, str(f), tolerance=0.01, angularTolerance=0.05)
                filer.append(f.name)
            ut = f"FYR_P1S_{pl['nr']}_{pl['namn']}.3mf"
            arrange = "1" if len(filer) > 1 else "0"
            if len(filer) == 1:
                # éin del: sentrer på plata sjølv (128, 128)
                s = plasser(delar[pl["delar"][0][0]], pl["delar"][0][1], pl["delar"][0][2]).translate(cq.Vector(128, 128, 0))
                cq.exporters.export(s, str(tmp / filer[0]), tolerance=0.01, angularTolerance=0.05)
            sek = kjor(["--orient", "0", "--arrange", arrange, "--load-settings", "machine.json;process.json",
                        "--load-filaments", "filament.json", "--curr-bed-type", "Textured PEI Plate",
                        "--slice", "0", "--outputdir", str(tmp), "--export-3mf", ut, *filer], tmp)
            shutil.copy2(tmp / ut, PRINT / ut)
            res = les_3mf(PRINT / ut)
            res.update({"delar": maal, "filament_profil": pl["filament"], "prosess_endringar": pl["prosess"],
                        "skjeretid_s": round(sek, 1), "bambu": EXE.name})   # berre filnamnet: repoet er offentleg
            rapport[ut] = res
            print(ut, json.dumps(res, ensure_ascii=False)[:400])
    rapport_fil.write_text(json.dumps(rapport, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
