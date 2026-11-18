from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/"render_blender.py").read_text(encoding="utf-8")
a='set_up_poses(scene, moving, data["kinematics"])'
b='set_up_poses(scene, moving, {"closed_deg":-30.0,"open_deg":-7.0,"rack_pitch_radius_mm":10.0})'
assert a in s
s=s.replace(a,b)
assert 'output_dir = root / "renders"' in s
s=s.replace('output_dir = root / "renders"','output_dir = root / "renders" / "test_negative"')
assert 'blend_path = root / "C_zeppelin.blend"' in s
s=s.replace('blend_path = root / "C_zeppelin.blend"','blend_path = root / "test_negative.blend"')
(p/"test_negative_render.py").write_text(s,encoding="utf-8")
print("TEST_NEGATIVE_POSE_RENDER_ONLY",flush=True)
