import FreeCAD as A, json, math, os, re
doc = A.openDocument(os.environ["FURU_FCSTD"])
sheet = [o for o in doc.Objects if o.TypeId == "Spreadsheet::Sheet"][0]
parts = [o for o in doc.Objects if o.TypeId == "App::Part"]
root = [p for p in parts if not any(p in q.Group for q in parts if q is not p)][0]
groups = [p for p in parts if p is not root]
def at(a):
    sheet.set("B1", f"{a} deg"); doc.recompute()
    return {p.Label: A.Placement(p.Placement) for p in groups}
P = {a: at(a) for a in range(0, 95, 5)}
p0 = P[0]
def ang(pl):
    r = pl.Rotation; return math.degrees(r.Angle) * (1 if r.Axis.y >= 0 else -1)
shells = sorted([k for k in p0 if any(abs(ang(P[a][k])) > 1e-6 for a in P)], key=lambda k: p0[k].Base.x)
drive = [k for k in p0 if k not in shells and any((P[a][k].Base - p0[k].Base).Length > 1e-6 for a in P)]
seq = [abs(ang(P[a][shells[0]])) for a in sorted(P)]
mx = max(seq)
m = re.search(r"0 til (\d+)", str(sheet.get("A1")))
if mx > 89 and m: mx = float(m.group(1))
s = -1 if ang(P[90][shells[0]]) < 0 else 1
Z = p0[shells[0]].Base.z
rig = {"root": root.Label, "shell_groups": shells, "stations_mm": [round(p0[k].Base.x, 4) for k in shells],
       "pivot_z_mm": [round(p0[k].Base.z, 4) for k in shells], "pivot_y_mm": [round(p0[k].Base.y, 4) for k in shells],
       "max_deg": round(mx, 4), "rot_sign": s, "drive_group": drive[0] if drive else None}
if drive:
    d = p0[drive[0]].Base - A.Vector(0, 0, Z); rig["drive_d_mm"] = [round(d.x, 4), round(d.y, 4), round(d.z, 4)]
    err = 0
    for a in P:
        aa = math.radians(s * min(a, mx)); x = d.x * math.cos(aa) + d.z * math.sin(aa); z = -d.x * math.sin(aa) + d.z * math.cos(aa)
        err = max(err, (P[a][drive[0]].Base - A.Vector(x, d.y, Z + z)).Length)
    rig["drive_model_err_mm"] = round(err, 6)
rig["shell_axis_ok"] = all(abs(abs(P[90][k].Rotation.Axis.y) - 1) < 1e-6 for k in shells)
rig["shell_origin_fixed"] = all((P[a][k].Base - p0[k].Base).Length < 1e-6 for a in P for k in shells)
json.dump(rig, open(os.environ["FURU_RIG"], "w"), ensure_ascii=False, indent=1)
print("RIG", json.dumps(rig, ensure_ascii=False))
