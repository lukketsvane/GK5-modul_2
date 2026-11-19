import sys, json, os, subprocess, numpy as np, trimesh
# saman.py oppsett.json : set fleire skorne kroppar saman i éi scene (kvar med eiga flytting og dreiing) og teikn arket
a = json.load(open(sys.argv[1])); HER = "/home/claude/arb2"
def T_flytt(t): M = np.eye(4); M[:3, 3] = t; return M
def T_drei(akse, grader, om):
    R = trimesh.transformations.rotation_matrix(np.radians(grader), akse, om); return R
ut = {"namn": a["namn"], "delar": [], "steg": [], "utstyr": []}
steg0 = 0
for g in a["grupper"]:
    sc = json.load(open(f"{HER}/{g['scene']}")); b = trimesh.load(f"{HER}/{g['stl']}", force="mesh").bounds
    S = np.array([-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]])
    T = T_flytt(-S)
    if "flytt" in g: T = T_flytt(g["flytt"]) @ T
    for d in g.get("drei", []): T = T_drei(d["akse"], d["grader"], d["om"]) @ T
    pre = g.get("prefiks", "")
    for k in ("material", "tjukn"): ut.setdefault(k, sc.get(k))
    for d in sc["delar"]:
        M = np.array(d["matrise"]).reshape(4, 4).T
        q = dict(d); q["matrise"] = (T @ M).T.reshape(-1).round(5).tolist(); q["adr"] = pre + str(d["adr"]); q["namn"] = q["adr"]
        if d.get("normal"): q["normal"] = (T[:3, :3] @ np.array(d["normal"])).round(5).tolist()
        q["steg"] = (d.get("steg") or 1) + steg0; q.pop("stabel", None); q.pop("paaArk", None)
        ut["delar"].append(q)
    for s in sc.get("steg", []):
        r = s.get("retning"); ut["steg"].append({"delar": [pre + str(x) for x in s["delar"]], "retning": (T[:3, :3] @ np.array(r)).round(5).tolist() if r else None})
    steg0 = len(ut["steg"])
    P = lambda p: (T @ np.array([*p, 1.0]))[:3].round(3).tolist()
    D = lambda v: (T[:3, :3] @ np.array(v)).round(5).tolist()
    for u in sc.get("utstyr", []):
        w = dict(u)
        if "senter" in w: w["senter"] = P(w["senter"])
        if "retning" in w and w["retning"]: w["retning"] = D(w["retning"])
        if "punkt" in w: w["punkt"] = [P(p) for p in w["punkt"]]
        ut["utstyr"].append(w)
    for l in ([sc["lys"]] if isinstance(sc.get("lys"), dict) else sc.get("lys", [])):
        ut.setdefault("lys", []).append({**l, "punkt": P(l["punkt"])})
v = a.get("vegg", 300); sn = a.get("snudd", False)
ut["vegg"] = {"punkt": [0, -v if sn else v, 0], "normal": [0, 1 if sn else -1, 0]}
for k in ("kamera", "golv", "lysstyrke", "bakgrunn"):
    if k in a: ut[k] = a[k]
mappe = f"{HER}/{a['ut']}"; os.makedirs(mappe, exist_ok=True)
json.dump(ut, open(f"{mappe}/scene.json", "w"))
r = subprocess.run(["npx", "tsx", f"{HER}/verkty/syn.ts", f"{mappe}/scene.json", "--ut", mappe, "--syn", a.get("syn", "ark"), "--namn", "x"] + (["--stor"] if a.get("stor") else []), cwd="/home/claude/slicer", capture_output=True, text=True)
print(a["namn"], len(ut["delar"]), "delar", (r.stdout + r.stderr).strip()[-300:])
