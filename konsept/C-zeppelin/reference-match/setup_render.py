from pathlib import Path
p=Path(__file__).resolve().parent
src=(p.parent/"render_blender.py").read_text(encoding="utf-8")
changes={
 "CAMERA_TARGET = (0.0, 0.0, 0.12)":"CAMERA_TARGET = (0.0, 0.0, 0.090)",
 "LIGHT_TARGET = (0.0, 0.0, 0.11)":"LIGHT_TARGET = (0.0, 0.0, 0.101)",
 "render.resolution_x = 1600":"render.resolution_x = 1536",
 "render.resolution_y = 960":"render.resolution_y = 864",
 "lens.ortho_scale = 0.52":"lens.ortho_scale = 0.485",
 "fit_pose_pair(scene, cameras.values(), objects)":"pass",
 'make_camera(views, "Three-quarter", (0.25, -0.88, 0.21))':'make_camera(views, "Three-quarter", (0.26, -0.98, 0.20))',
 'make_camera(views, "Front", (0.0, -0.85, 0.19))':'make_camera(views, "Front", (0.018, -1.10, 0.22))',
 'make_material("Satin silver aluminum", (0.34, 0.36, 0.38), 0.73, 0.36)':'make_material("Satin silver aluminum", (0.58, 0.59, 0.60), 0.84, 0.24)',
 'make_material("Graphite frame", (0.034, 0.040, 0.049), 0.76, 0.24)':'make_material("Graphite frame", (0.022, 0.023, 0.025), 0.86, 0.23)',
 'make_material("Dark machined metal", (0.085, 0.095, 0.110), 0.83, 0.26)':'make_material("Dark machined metal", (0.14, 0.145, 0.155), 0.89, 0.20)',
 'make_material("Warm ivory strip", (0.93, 0.82, 0.64), 0.0, 0.36':'make_material("Warm ivory strip", (0.91, 0.84, 0.71), 0.0, 0.52',
 'emission=((1.0, 0.76, 0.48), 2.6)':'emission=((1.0, 0.78, 0.55), 3.4)',
 '0.72, 0.42, 6.0':'0.90, 0.35, 8.0',
 '0.52, 0.055, 5.0':'0.62, 0.055, 6.0',
 '0.56, 0.32, 1.7':'0.45, 0.28, 2.0',
 '0.46, 0.19, 1.25':'0.52, 0.25, 2.3'
}
for old,new in changes.items():
 if old not in src: raise RuntimeError("Original renderer changed: "+old)
 src=src.replace(old,new)
(p/"render_match.py").write_text(src,encoding="utf-8")
print("renderer written from Astra 6.2 source",len(src),flush=True)
