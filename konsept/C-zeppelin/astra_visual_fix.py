import ast, math, sys, types
from pathlib import Path
import cadquery as cq

if not __debug__: raise RuntimeError("Run without -O so all acceptance checks are active")
bp, rp = Path("build.py").resolve(), Path("render_blender.py").resolve()
b, r = bp.read_text(encoding="utf-8"), rp.read_text(encoding="utf-8")

def edit(src, function, old, new):
    scopes = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == function]
    assert len(scopes) == 1, function
    pattern = ast.dump(ast.parse(old).body[0])
    hits = [n for n in ast.walk(scopes[0]) if isinstance(n, ast.stmt) and ast.dump(n) == pattern]
    assert len(hits) == 1, (function, old, len(hits))
    n = hits[0]
    lines = src.splitlines(True)
    i, j = n.lineno - 1, n.end_lineno - 1
    pad = lines[i][:n.col_offset]
    assert not pad.strip()
    lines[i:j + 1] = [pad + new.replace("\n", "\n" + pad) + lines[j][n.end_col_offset:]]
    return "".join(lines)

b = edit(b, "blade", "section(z, center - half, center + half)", """left, right = center - half, center + half
if side > 0:
    t = min(1.0, max(0.0, (z - 29.0) / 16.0))
    t = t * t * (3.0 - 2.0 * t)
    root_scale = 36.0 / (width / 2.0 + math.hypot(width / 2.0, sweep))
    scale = root_scale + (1.0 - root_scale) * t
    v = min(1.0, max(0.0, (z - 8.0) / 10.0))
    v = v * v * (3.0 - 2.0 * v)
    left = -5.0 + v * (scale * (left + 12.0) - 7.0)
    right = 5.0 + v * (scale * (right + 12.0) - 17.0)
section(z, left, right)""")
b = edit(b, "blade", "body = cq.Solid.makeLoft(sections, ruled=True)", """upper = cq.Solid.makeLoft(sections[-(n + 1):], ruled=False)
lower = cq.Solid.makeLoft(sections[:-n], ruled=True)
body = lower.fuse(upper)""")
b = edit(b, "blade", "return body.clean().Solids()[0]", """solids = body.clean().Solids()
assert len(solids) == 1 and solids[0].isValid(), ("invalid lamella", kind, sign)
return solids[0]""")
rail = 'c=cq.Workplane("XY").box(376.0,4.0,36.0).translate((0,sign*10.0,113.5)).val()'
b = edit(b, "rail", rail, rail.replace(",36.0)", ",14.0)").replace("113.5", "HEIGHT"))
bar = 'return cq.Workplane("XY").box(6.0,16.0,4.0).translate((x,0,97.0)).val()'
b = edit(b, "bar", bar, bar.replace("97.0", "HEIGHT-5.5"))
base = "return cq.Solid.makeCylinder(55.0,8.0,cq.Vector(0,0,0),cq.Vector(0,0,1))"
b = edit(b, "base", base, base.replace("55.0,8.0", "66.0,12.0"))
post = 'return cq.Workplane("XY").box(46.0,21.0,87.5).edges("|Z").fillet(4.0).translate((0,0,51.75)).val()'
b = edit(b, "pedestal", post, """wires = []
for z, w, d, radius in ((12.0,60.0,28.0,5.0),(60.5,51.0,23.5,4.5),(HEIGHT-7.0,46.0,21.0,4.0)):
    wire = cq.Workplane("XY", origin=(0,0,z)).rect(w,d).val()
    wires.append(wire.fillet2D(radius, wire.Vertices()))
return cq.Solid.makeLoft(wires, ruled=False)""")
hook = "meshes, objects, moving = import_cad(data, cad, materials)"
r = edit(r, "main", hook, hook + "\n" + """for obj in objects:
    if obj.name in ("base", "pedestal"):
        obj.material_slots[0].link = "OBJECT"
        obj.material_slots[0].material = materials["matte"]""")
compile(r, str(rp), "exec")
compile(b, str(bp), "exec")
bp.write_text(b, encoding="utf-8")
rp.write_text(r, encoding="utf-8")
print("ASTRA_6_2_GEOMETRY_PATCH_APPLIED",flush=True)
