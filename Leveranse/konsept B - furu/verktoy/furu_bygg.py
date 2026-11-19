import bpy, json, math, os, sys
from mathutils import Vector

rig_path, glb, out = sys.argv[sys.argv.index("--") + 1:][:3]
rig = json.load(open(rig_path, encoding="utf-8"))
MX, S = rig["max_deg"], rig["rot_sign"]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.length_unit = "MILLIMETERS"
bpy.ops.import_scene.gltf(filepath=glb)
root = bpy.data.objects[rig["root"]]
root.rotation_mode = "XYZ"
root.rotation_euler = (-math.pi / 2, 0, 0)
bpy.context.view_layer.update()

group_of = {}
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    group_of[o.name] = o.parent.name if o.parent else ""
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
for o in [o for o in bpy.data.objects if o.type == "EMPTY"]:
    bpy.data.objects.remove(o)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
colls = {}
for o in bpy.data.objects:
    g = group_of[o.name]
    if g not in colls:
        colls[g] = bpy.data.collections.new(g)
        sc.collection.children.link(colls[g])
    for c in o.users_collection:
        c.objects.unlink(o)
    colls[g].objects.link(o)

ctrl = bpy.data.objects.new("Furu · styring", None)
sc.collection.objects.link(ctrl)
ctrl.empty_display_type = "SPHERE"
ctrl.empty_display_size = 0.012
ctrl["Opning"] = 0.0
ctrl.id_properties_ui("Opning").update(min=0.0, max=MX, soft_min=0.0, soft_max=MX, step=100, precision=1,
                                      description=f"Opning i grader: 0 = lukka, {MX:g} = open (B1 i FreeCAD)")
ctrl["Opning_maks"] = MX


def drive(obj, path, idx, expr):
    d = obj.driver_add(path, idx).driver
    d.type = "SCRIPTED"
    v = d.variables.new()
    v.name, v.type = "a", "SINGLE_PROP"
    v.targets[0].id = ctrl
    v.targets[0].data_path = '["Opning"]'
    d.expression = expr
    return d


def adopt(parent, group):
    bpy.context.view_layer.update()
    for o in [o for o in bpy.data.objects if group_of.get(o.name) == group]:
        mw = o.matrix_world.copy()
        o.parent = parent
        o.matrix_world = mw


A = f"{S}*radians(clamp(a, 0, {MX:g}))"
drivers = []
for i, g in enumerate(rig["shell_groups"]):
    p = bpy.data.objects.new(f"{g} · vippeakse", None)
    colls[g].objects.link(p)
    p.empty_display_type = "PLAIN_AXES"
    p.empty_display_size = 0.015
    p.location = (rig["stations_mm"][i] / 1000, rig["pivot_y_mm"][i] / 1000, rig["pivot_z_mm"][i] / 1000)
    p.rotation_mode = "XYZ"
    adopt(p, g)
    drivers.append(drive(p, "rotation_euler", 1, A))
if rig.get("drive_group"):
    dx, _, dz = [v / 1000 for v in rig["drive_d_mm"]]
    r = bpy.data.objects.new(f"{rig['drive_group']} · rørsle", None)
    colls[rig["drive_group"]].objects.link(r)
    r.empty_display_size = 0.015
    adopt(r, rig["drive_group"])
    drivers.append(drive(r, "location", 0, f"{dx:.6f}*cos({A}) + {dz:.6f}*sin({A}) - {dx:.6f}"))
    drivers.append(drive(r, "location", 2, f"-{dx:.6f}*sin({A}) + {dz:.6f}*cos({A}) - {dz:.6f}"))
print("DRIVERS simple:", all(d.is_simple_expression for d in drivers), "valid:", all(d.is_valid for d in drivers))


def node_mat(name, base, metal=0.0, rough=0.5, aniso=0.0, emit_k=0, emit=0.0, spec=0.5):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    for k, v in (("Base Color", (*base, 1)), ("Metallic", metal), ("Roughness", rough), ("Anisotropic", aniso),
                 ("Specular IOR Level", spec)):
        if k in b.inputs:
            b.inputs[k].default_value = v
    if aniso:
        t = nt.nodes.new("ShaderNodeTangent")
        t.direction_type, t.axis = "RADIAL", "X"
        nt.links.new(t.outputs[0], b.inputs["Tangent"])
    if emit_k:
        bb = nt.nodes.new("ShaderNodeBlackbody")
        bb.inputs[0].default_value = emit_k
        nt.links.new(bb.outputs[0], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*base, 1)
    return m


mats = {
    "skjell": node_mat("Skjell · mattbørsta aluminium", (0.82, 0.82, 0.81), 1, 0.22, 0.35),
    "alu": node_mat("Aluminium · satinert", (0.78, 0.78, 0.77), 1, 0.30),
    "stal": node_mat("Rustfritt stål", (0.72, 0.72, 0.73), 1, 0.20),
    "bronse": node_mat("Aluminium · bronseeloksert", (0.45, 0.28, 0.14), 1, 0.33),
    "pom": node_mat("POM-C · svart", (0.025, 0.025, 0.026), 0, 0.45),
    "silikon": node_mat("Silikon · svart", (0.02, 0.02, 0.02), 0, 0.75),
    "opal": node_mat("Opal polykarbonat · lys", (0.95, 0.92, 0.86), 0, 0.5, 0, 2700, 60.0),
    "led": node_mat("LED-band 2700 K", (1.0, 0.9, 0.75), 0, 0.5, 0, 2700, 60.0),
    "kabel": node_mat("Leidning · svart", (0.015, 0.015, 0.015), 0, 0.55),
    "tre": node_mat("Tre", (0.45, 0.30, 0.18), 0, 0.5),
}
cat_of = {}
for o in [o for o in bpy.data.objects if o.type == "MESH"]:
    k = rig["materials"].get(o.name.split(" ")[0], "alu")
    cat_of[o.name] = k
    o.data.materials.clear()
    o.data.materials.append(mats[k])

lamp = [o for o in bpy.data.objects if o.type == "MESH" and cat_of[o.name] != "kabel"]
bpy.context.view_layer.update()
pts = [o.matrix_world @ Vector(c) for o in lamp for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
mid, L = (lo + hi) / 2, hi.x - lo.x

bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, lo.z))
floor = bpy.context.object
floor.name = "Golv"
floor.data.materials.append(node_mat("Golv · svart", (0.0, 0.0, 0.0), 0, 1.0, spec=0.0))

w = bpy.data.worlds.new("Svart studio")
sc.world = w
try:
    w.use_nodes = True
    wn = w.node_tree
    bg = wn.nodes["Background"]
    bg.inputs[0].default_value = (0.5, 0.5, 0.5, 1)
    bg.inputs[1].default_value = 0.02
    black = wn.nodes.new("ShaderNodeBackground")
    black.inputs[0].default_value = (0, 0, 0, 1)
    lp = wn.nodes.new("ShaderNodeLightPath")
    mix = wn.nodes.new("ShaderNodeMixShader")
    wn.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    wn.links.new(bg.outputs[0], mix.inputs[1])
    wn.links.new(black.outputs[0], mix.inputs[2])
    wn.links.new(mix.outputs[0], wn.nodes["World Output"].inputs[0])
except Exception as e:
    print("WORLD", e)


def aim(o, loc, tgt):
    o.location = loc
    o.rotation_euler = (tgt - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def area(name, loc, size, power, size_y=None):
    l = bpy.data.lights.new(name, "AREA")
    l.shape = "RECTANGLE" if size_y else "DISK"
    l.size, l.energy = size, power
    if size_y:
        l.size_y = size_y
    o = bpy.data.objects.new(name, l)
    sc.collection.objects.link(o)
    aim(o, mid + Vector(loc), mid)


area("Topplys", (0.0, -0.15, 0.87), 1.6, 70, 0.8)
area("Hovudlys", (-0.8, -1.0, 0.67), 0.5, 25)
area("Kantlys", (0.2, 1.0, 0.47), 1.2, 40, 0.3)
area("Fyllys", (0.9, -0.9, 0.02), 0.4, 6)


def camera(name, loc, lens):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    sc.collection.objects.link(c)
    c.data.lens = lens
    aim(c, loc, mid)
    return c


d = (L / 0.79) / (2 * math.tan(math.atan(18 / 100)))
e = math.radians(9)
sc.camera = camera("Kamera · referanse", mid + Vector((0, -d * math.cos(e), d * math.sin(e))), 100)
camera("Kamera · 3/4", mid + Vector((-0.70, -1.05, 0.43)).normalized() * 2.83 * L, 70)

sc.render.engine = "CYCLES"
sc.render.resolution_x, sc.render.resolution_y = 1536, 864
sc.cycles.device = "CPU"
sc.cycles.samples = 128
sc.cycles.use_denoising = True
for k, v in (("denoiser", "OPENIMAGEDENOISE"),):
    try:
        setattr(sc.cycles, k, v)
    except Exception:
        pass
try:
    sc.view_settings.view_transform = "AgX"
except Exception:
    pass
for look in ("AgX - Medium High Contrast", "Medium High Contrast"):
    try:
        sc.view_settings.look = look
        break
    except Exception:
        pass


def dims(a):
    ctrl["Opning"] = a
    ctrl.update_tag()
    bpy.context.view_layer.update()
    P = [o.matrix_world @ v.co for o in lamp for v in o.data.vertices]
    s = [(max(p[i] for p in P) - min(p[i] for p in P)) * 1000 for i in range(3)]
    print(f"DIMS opning={a:>5.1f}  L x B x H = {s[0]:.1f} x {s[1]:.1f} x {s[2]:.1f} mm")


for a in (0.0, MX / 2, MX):
    dims(a)
ctrl["Opning"] = 0.0
ctrl.update_tag()
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=out)
print("SAVED", out)
