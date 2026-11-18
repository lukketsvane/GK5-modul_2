from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent
names=["closed_front.png","open_front.png","closed_3q.png","open_3q.png"]
for width in (400,512,600):
    canvas=Image.new("RGB",(width*2,round(width*.6)*2),(0,0,0))
    height=round(width*.6)
    for i,name in enumerate(names):
        im=Image.open(root/"renders"/name).convert("RGB").resize((width,height),Image.Resampling.LANCZOS)
        canvas.paste(im,((i%2)*width,(i//2)*height))
    for q in (45,65,80):
        p=root/f"preview_sheet_{width}_{q}.webp"
        canvas.save(p,"WEBP",quality=q,method=6)
        print(p.name,p.stat().st_size)
