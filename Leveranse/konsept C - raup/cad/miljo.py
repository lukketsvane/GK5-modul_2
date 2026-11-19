from pathlib import Path
import importlib, shutil, sys, json, importlib.metadata as md
r=Path(__file__).resolve().parents[1]; d={'python':sys.version.split()[0]}
for e in ('cadquery','cadquery-ocp','ezdxf','numpy','scipy','pillow','matplotlib','shapely','trimesh','vtk'):
    try:d[e]=md.version(e)
    except md.PackageNotFoundError:d[e]=None
for e in ('FreeCADCmd','FreeCAD','blender'):d[e+' PATH']=bool(shutil.which(e))
(r/'kontroll').mkdir(exist_ok=True); f=r/'kontroll/miljo.json'; f.write_text(json.dumps(d,indent=2),encoding='utf-8');assert json.loads(f.read_text())['cadquery'];print(d)
