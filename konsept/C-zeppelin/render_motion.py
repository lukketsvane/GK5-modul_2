import os
import subprocess
from pathlib import Path
p=Path(__file__).resolve().parent
blender=Path(r"C:\Program Files\Blender Foundation\Blender 5.3\blender.exe")
env=dict(os.environ,C_RENDER_MOTION="1")
subprocess.run([str(blender),"--background","--factory-startup","--python",str(p/"render_blender.py")],check=True,env=env)
subprocess.run(["py","-3.13",str(p/"assemble_gif.py")],check=True)
