import json
from pathlib import Path
p=Path(__file__).resolve().parent
t=(p/"viewer_template.html").read_text(encoding="utf-8")
data=(p/"scene.json").read_text(encoding="utf-8")
(p/"viewer.html").write_text(t.replace("__SCENE__",data),encoding="utf-8")
print("viewer.html bytes",(p/"viewer.html").stat().st_size)
