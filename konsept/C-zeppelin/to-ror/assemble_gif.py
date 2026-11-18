from pathlib import Path
from PIL import Image
p=Path(__file__).resolve().parent/"renders"
frames=sorted(p.glob("blender_frame_*.png"))
assert len(frames)==25,(len(frames),frames)
imgs=[Image.open(path).convert("RGB").resize((960,576)).quantize(colors=128,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE) for path in frames]
out=p/"Blender_kinematikk.gif"
imgs[0].save(out,save_all=True,append_images=imgs[1:],duration=110,loop=0,optimize=True,disposal=2)
assert out.stat().st_size>10000
for file in frames: file.unlink()
print("ANIMATED_FROM_BLENDER_FRAMES",out,out.stat().st_size)
