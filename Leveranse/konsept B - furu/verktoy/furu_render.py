import bpy, os, sys

a = sys.argv[sys.argv.index("--") + 1:]
out, pct, views, angles = a[0], int(a[1]), a[2].split(","), a[3:]
sc = bpy.context.scene
sc.render.resolution_percentage = pct
if pct < 100:
    sc.cycles.samples = 48
ctrl = bpy.data.objects["Furu · styring"]
MX = ctrl["Opning_maks"]
cams = {"ref": "Kamera · referanse", "34": "Kamera · 3/4"}
for ang in angles:
    v = MX if ang == "max" else float(ang)
    ctrl["Opning"] = v
    ctrl.update_tag()
    bpy.context.view_layer.update()
    for view in views:
        sc.camera = bpy.data.objects[cams[view]]
        sc.render.filepath = os.path.join(out, f"{view}_{int(round(v)):02d}grader_{pct}.png")
        bpy.ops.render.render(write_still=True)
        print("RENDERED", sc.render.filepath)
sc.camera = bpy.data.objects[cams["ref"]]
