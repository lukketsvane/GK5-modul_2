from pathlib import Path
p=Path(__file__).resolve().parent
f=p/"build_match.py"
s=f.read_text(encoding="utf-8")
replacements={
"HEIGHT = 102.0":"HEIGHT = 111.0",
"HALF_CHORD = [65, 58, 47, 33, 20]":"HALF_CHORD = [56, 49, 35, 20, 4]",
"WING_WIDTH = [57, 51, 47, 37, 25]":"WING_WIDTH = [57, 51, 47, 37, 30]",
"[40,37,32,25,16][kind]":"[40,35,28,16,5][kind]",
"cq.Vector(-188,-82.0,102.0)":"cq.Vector(-188,-82.0,111.0)",
"cq.Vector(0,-10.0,38.0)":"cq.Vector(0,-10.0,31.0)",
"points=[(-end,118.0),(-end,113.25)]":"points=[(-end,127.0),(-end,122.25)]",
"113.25)":"122.25)",
"111.0)":"120.0)",
"118.0)":"127.0)",
"translate((0,sign*2.9,116.5))":"translate((0,sign*2.9,125.5))",
"translate((0,sign*4.9,116.75))":"translate((0,sign*4.9,125.75))",
"translate((0,sign*4.05,118.1))":"translate((0,sign*4.05,127.1))",
"translate((0,sign*4.05,114.9))":"translate((0,sign*4.05,123.9))",
"translate((x,0,115.85))":"translate((x,0,124.85))",
"cq.Workplane(\"XY\").box(376.0,4.0,36.0).translate((0,sign*10.0,99.5))":"cq.Workplane(\"XY\").box(376.0,4.0,14.0).translate((0,sign*10.0,111.0))",
"translate((x,0,83.0))":"translate((x,0,92.0))",
"translate((0,sign*14.0,81.0))":"translate((0,sign*14.0,90.0))",
"cq.Workplane(\"XY\").box(376.0,24.0,1.6).translate((0,0,120.0))":"cq.Workplane(\"XY\").box(350.0,20.0,1.6).translate((0,0,129.0))",
'add("opal_strip","fixed","fixed_warm_diffuser",color="light")':'',
'        add(f"shoe_{sign}","leaf",f"station_{i}_shoe_{sign}",x,sign*16*lane,HEIGHT,color="metal")':'',
'        add(f"shoe_lock_{sign}","leaf",f"station_{i}_shoe_lock_{sign}",x,sign*16*lane,HEIGHT,color="frame")':''
}
for old,new in replacements.items():
 if old not in s:print("WARN unmatched",old)
 s=s.replace(old,new)
s=s.replace("    \"kinematics\":{", "    \"kinematics\":{")
f.write_text(s,encoding="utf-8")
g=p/"render_match.py"
r=g.read_text(encoding="utf-8")
repls={
"CAMERA_TARGET = (0.0, 0.0, 0.090)":"CAMERA_TARGET = (0.0, 0.0, 0.091)",
"lens.ortho_scale = 0.485":"lens.ortho_scale = 0.470",
"make_camera(views, \"Front\", (0.018, -1.10, 0.22))":"make_camera(views, \"Front\", (0.018, -1.10, 0.20))",
"make_material(\"Satin silver aluminum\", (0.58, 0.59, 0.60), 0.84, 0.24)":"make_material(\"Satin silver aluminum\", (0.39, 0.40, 0.41), 0.83, 0.30)",
"make_material(\"Dark machined metal\", (0.14, 0.145, 0.155), 0.89, 0.20)":"make_material(\"Dark machined metal\", (0.30, 0.31, 0.33), 0.80, 0.24)",
"0.52, 0.25, 2.3":"0.52, 0.25, 8.0"
}
for a,b in repls.items():
 if a not in r:raise RuntimeError("Cannot find render string "+a)
 r=r.replace(a,b)
r=r.replace('    output_dir = root / "renders"','''    make_softbox(studio, "Pedestal soft fill", (0.02, -0.39, 0.045),
                 0.35, 0.30, 4.0, (1.0, 0.96, 0.90))
    output_dir = root / "renders"''')
g.write_text(r,encoding="utf-8")
print("matched rail height, nose taper, fasteners, foot and lighting",flush=True)
