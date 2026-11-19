import bpy
from mathutils.bvhtree import BVHTree

ctrl = bpy.data.objects["Furu · styring"]
MX = ctrl["Opning_maks"]
meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.name != "Golv"
          and not (o.active_material and o.active_material.name.startswith("Leidning"))]


def grp(o):
    return o.parent.name if o.parent else "statisk"


def tree(o):
    return BVHTree.FromPolygons([o.matrix_world @ v.co for v in o.data.vertices], [p.vertices[:] for p in o.data.polygons])


for a in [MX * i / 8 for i in range(9)]:
    ctrl["Opning"] = a
    ctrl.update_tag()
    bpy.context.view_layer.update()
    T = {o.name: tree(o) for o in meshes}
    hits = [f"{x.name.split()[0]}/{y.name.split()[0]}" for i, x in enumerate(meshes) for y in meshes[i + 1:]
            if grp(x) != grp(y) and T[x.name].overlap(T[y.name])]
    print(f"SJEKK opning={a:.1f}", " ".join(hits) or "ingen kryssingar")
ctrl["Opning"] = 0.0
ctrl.update_tag()
bpy.context.view_layer.update()
