import csv, glob, json, os, re, subprocess, sys
import cascadio

rev_dir, macro = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
out = os.path.join(rev_dir, "out")
env = dict(os.environ, FURU_DIR=out, QT_QPA_PLATFORM="offscreen", LANG="C.UTF-8", LC_ALL="C.UTF-8",
           PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
r = subprocess.run(["/opt/fc/bin/freecadcmd", macro], env=env, capture_output=True, text=True, timeout=3600)
log = re.sub(r"\(\d+ %\)", "", (r.stdout + r.stderr).replace("\r", "\n").replace("\t", ""))
open(os.path.join(rev_dir, "freecad.log"), "w", encoding="utf-8").write(log)
errs = [l.strip() for l in log.split("\n") if re.search(r"Exception|Traceback|Error|error:|Invalid", l)]
fcstd = glob.glob(os.path.join(out, "packet", "*.FCStd"))
step = glob.glob(os.path.join(out, "packet", "*.step"))
res = {"freecad_errors": errs[:8], "fcstd": fcstd, "step": step, "bounds_printed": [l.strip() for l in log.split("\n") if l.strip().startswith("Bounds")]}
if fcstd and step:
    rig_path = os.path.join(rev_dir, "rig.json")
    r2 = subprocess.run(["/opt/fc/bin/freecadcmd", "/home/claude/furu/tools/rig_ut.py"], capture_output=True, text=True, timeout=600,
                        env=dict(env, FURU_FCSTD=fcstd[0], FURU_RIG=rig_path))
    if not os.path.exists(rig_path):
        res["rig_error"] = (r2.stdout + r2.stderr)[-1500:]
    else:
        rig = json.load(open(rig_path, encoding="utf-8"))
        bom = list(csv.DictReader(open(os.path.join(out, "packet", "Stykkliste.csv"), encoding="utf-8-sig"), delimiter=";"))
        def cat(m):
            m = m.lower()
            for k, v in (("5754", "skjell"), ("bronse", "bronse"), ("6061", "alu"), ("6082", "alu"), ("aluminium", "alu"),
                         ("aisi", "stal"), ("stål", "stal"), ("pom", "pom"), ("silikon", "silikon"), ("opal", "opal"),
                         ("led", "led"), ("kort", "pom"), ("pbt", "pom"), ("ndfeb", "stal"), ("kabel", "kabel"), ("leidning", "kabel"), ("messing", "bronse"), ("tre", "tre")):
                if k in m:
                    return v
            return "alu"
        rig["materials"] = {b["ID"]: cat(b["Materiale"]) for b in bom}
        rig["name"] = os.path.splitext(os.path.basename(step[0]))[0]
        json.dump(rig, open(rig_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        res["rig"] = {k: v for k, v in rig.items() if k != "materials"}
        res["parts"] = len(bom)
        res["mass_g"] = round(sum(float(b["Masse_g"].replace(",", ".") or 0) for b in bom), 1)
        res["unmapped_materials"] = sorted({b["Materiale"] for b in bom if cat(b["Materiale"]) == "alu" and not re.search("6061|6082|6063|alumin", b["Materiale"].lower())})
        glb = os.path.join(rev_dir, rig["name"] + ".glb")
        cascadio.step_to_glb(step[0], glb, tol_linear=0.02, tol_angular=0.2, merge_primitives=True)
        res["glb_mb"] = round(os.path.getsize(glb) / 1e6, 2)
        ext = {}
        for f in sorted(glob.glob(os.path.join(out, "work", "mesh*.json"))):
            d = json.load(open(f, encoding="utf-8"))
            pts = [p for e in d if e.get("mat") not in ("cordref",) and "leidning" not in e.get("label", "").lower() for p in e["v"]]
            ext[os.path.basename(f)] = [round(max(p[i] for p in pts) - min(p[i] for p in pts), 1) for i in range(3)]
        res["mesh_extents_mm"] = ext
print(json.dumps(res, ensure_ascii=False, indent=1))
