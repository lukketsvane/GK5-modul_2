"""Skiv restdelane til Raup svart på éi P1S-plate (kvit PLA, AMS A2).

D01 og D02 er ferdig printa (sjå ../print/ferdig). Resten: formklossane D03/D04
og lampedelane B01-tupp, B02 x2, B04 x2, E04 og M01. Berre M01 får støtte.
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "print" / "Raup-svart-hovudprosjekt-A2-PLA.3mf"
EXE = Path(os.environ["LOCALAPPDATA"]) / "Programs/BambuStudio/bambu-studio.exe"
PROFILES = Path(os.environ["APPDATA"]) / "BambuStudio/system/BBL"
PARTS = ["former/D03-retur.stl", "former/D04-rand.stl", "delar/B01-tupp.stl",
         "delar/B02_1_Limfot.stl", "delar/B02_2_Limfot.stl", "delar/B04_1_Skivehaldar.stl",
         "delar/B04_2_Skivehaldar.stl", "delar/E04_Kabelbru.stl", "delar/M01-Nedrelist.stl"]
SUPPORTED = {"M01-Nedrelist.stl"}
# Fast plassering (x, y nedre hjørne i mm, roter 90°). Auto-arrange la smådelane
# inne i bogen til M01 og gav G-code-konflikt med støtta.
LAYOUT = {"B01-tupp.stl": (12, 135, 0), "M01-Nedrelist.stl": (12, 12, 0),
          "D03-retur.stl": (138, 14, 0), "D04-rand.stl": (192, 140, 1),
          "B02_1_Limfot.stl": (182, 14, 0), "B02_2_Limfot.stl": (216, 14, 0),
          "B04_1_Skivehaldar.stl": (182, 50, 0), "B04_2_Skivehaldar.stl": (216, 50, 0),
          "E04_Kabelbru.stl": (184, 86, 1)}


def flatten(directory, name):
    record = json.loads((directory / (name + ".json")).read_text(encoding="utf-8-sig"))
    merged = {}
    if record.get("inherits"):
        merged.update(flatten(directory, record["inherits"]))
    for ref in record.get("include", []):
        merged.update(flatten(directory, ref))
    merged.update({k: v for k, v in record.items() if k not in {"inherits", "include"}})
    return merged


def run(args, cwd):
    done = subprocess.run([str(EXE), *args], cwd=cwd, capture_output=True, timeout=600)
    if done.returncode:
        raise RuntimeError((done.returncode, done.stdout[-3000:], done.stderr[-3000:]))


def mark_support(archive):
    """Slå på støtte berre for M01 i prosjektfila (per-objekt-innstilling)."""
    with zipfile.ZipFile(archive) as z:
        files = {n: z.read(n) for n in z.namelist()}
    cfg = files["Metadata/model_settings.config"].decode()

    def patch(m):
        block = m.group(0)
        name = re.search(r'key="name" value="([^"]+)"', block).group(1)
        if any(name.startswith(s) for s in SUPPORTED) and 'key="enable_support"' not in block:
            block = block.replace('<metadata key="name"', '<metadata key="enable_support" value="1"/>\n    <metadata key="name"', 1)
        return block

    files["Metadata/model_settings.config"] = re.sub(r"<object id=.*?</object>", patch, cfg, flags=re.S).encode()
    for n in [n for n in files if n.startswith("Metadata/plate_") and n.endswith((".gcode", ".md5"))]:
        del files[n]
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for n, data in files.items():
            z.writestr(n, data)


def main():
    with tempfile.TemporaryDirectory(prefix="raup-svart-") as td:
        temp = Path(td)
        process = flatten(PROFILES / "process", "0.20mm Standard @BBL X1C")
        process.update({"enable_support": "0", "support_type": "tree(auto)", "support_on_build_plate_only": "1",
                        "wall_loops": "4", "sparse_infill_density": "20%", "sparse_infill_pattern": "gyroid",
                        "top_shell_layers": "5", "bottom_shell_layers": "4",
                        "brim_type": "outer_only", "brim_width": "4"})
        filament = flatten(PROFILES / "filament", "Generic PLA")
        settings = {"machine": flatten(PROFILES / "machine", "Bambu Lab P1S 0.4 nozzle"),
                    "process": process, "filament": filament}
        for k, v in settings.items():
            (temp / f"{k}.json").write_text(json.dumps(v, ensure_ascii=False), encoding="utf8")
        names = []
        for p in PARTS:
            mesh = trimesh.load_mesh(ROOT / p)
            x, y, rot = LAYOUT[Path(p).name]
            if rot:
                mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
            mesh.apply_translation([x, y, 0] - mesh.bounds[0])
            assert mesh.bounds[1][0] < 250 and mesh.bounds[1][1] < 250, p
            mesh.export(temp / Path(p).name)
            names.append(Path(p).name)
        common = ["--load-settings", "machine.json;process.json", "--load-filaments", "filament.json",
                  "--curr-bed-type", "Textured PEI Plate", "--outputdir", str(temp)]
        run([*common, "--orient", "0", "--arrange", "0", "--export-3mf", "steg1.3mf", *names], temp)
        mark_support(temp / "steg1.3mf")
        run(["--slice", "0", "--outputdir", str(temp), "--export-3mf", "ferdig.3mf", "steg1.3mf"], temp)
        with zipfile.ZipFile(temp / "ferdig.3mf") as z:
            info = ElementTree.fromstring(z.read("Metadata/slice_info.config"))
            cfg = json.loads(z.read("Metadata/project_settings.config"))
        plate = info.find("plate")
        meta = {m.get("key"): m.get("value") for m in plate.findall("metadata")}
        objs = [o.get("name") for o in plate.findall("object")]
        assert meta["outside"] == "false" and len(objs) == len(PARTS), (meta, objs)
        OUT.parent.mkdir(exist_ok=True)
        shutil.copyfile(temp / "ferdig.3mf", OUT)
        report = {"fil": OUT.name, "delar": objs, "tid_s": int(meta["prediction"]),
                  "vekt_g": float(plate.find("filament").get("used_g")), "stotte_brukt": meta["support_used"],
                  "filament": cfg["filament_settings_id"][0], "prosess": cfg["print_settings_id"]}
        (OUT.with_suffix(".json")).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
        print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
