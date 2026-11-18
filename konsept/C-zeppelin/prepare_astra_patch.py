from pathlib import Path
p=Path(__file__).resolve().parent/"astra_visual_fix.py"
s=p.read_text(encoding="utf-8")
a=s.index('hook = "meshes, objects, moving = import_cad(data, cad, materials)"')
z=s.index('compile(r,',a)
s=s[:a]+'''hook = "meshes, objects, moving = import_cad(data, cad, materials)"
r = edit(r, "main", hook, hook + "\\n" + """for obj in objects:
    if obj.name in ("base", "pedestal"):
        obj.material_slots[0].link = "OBJECT"
        obj.material_slots[0].material = materials["matte"]""")
'''+s[z:]
a=s.index('compile(r,',a)
s=s[:a]+'''compile(r, str(rp), "exec")
compile(b, str(bp), "exec")
bp.write_text(b, encoding="utf-8")
rp.write_text(r, encoding="utf-8")
print("ASTRA_6_2_GEOMETRY_PATCH_APPLIED",flush=True)
'''
p.write_text(s,encoding="utf-8")
print("Prepared Astra geometry patch with scoped material targeting and separate build tests")
