from pathlib import Path
import py_compile
p = Path(__file__).with_name("render_blender.py")
backup = p.with_name("render_blender_before_light_tune.py")
raw = p.read_text(encoding="utf-8-sig")
if not backup.exists():
    backup.write_text(raw, encoding="utf-8")
for a,b in [
    ('bar.color = (1.0, 0.516, 0.193)', 'bar.color = (1.0, 0.72, 0.44)'),
    ('bar.energy = 3.0','bar.energy = 12.0'),
    ('tree.links.new(mix.outputs[0], tree.nodes["Material Output"].inputs["Surface"])', 'tree.links.new(mix.outputs[0], tree.nodes["Material Output"].inputs["Surface"])\n        warm_emission(mat, bs, 2.7)'),
    ('background.inputs["Strength"].default_value = 0.0 if black else 0.46','background.inputs["Strength"].default_value = 0.0 if black else 0.65'),
    ('(0.49, 0.46, 0.42, 1.0)','(0.72, 0.69, 0.66, 1.0)'),
]:
    if raw.count(a) != 1:
        raise ValueError(a)
    raw=raw.replace(a,b,1)
compile(raw,str(p),"exec")
p.write_text(raw,encoding="utf-8")
py_compile.compile(str(p),doraise=True)
print("RENDER_TUNE_PATCHED")
