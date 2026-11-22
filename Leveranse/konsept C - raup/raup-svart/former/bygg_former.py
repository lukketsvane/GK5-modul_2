import hashlib
import json
import sys
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from shapely.geometry import LineString, Point


HERE = Path(__file__).resolve().parent
UNDER = HERE.parent/"Underkutt"
sys.path.insert(0,str(UNDER))
import fasade
from bygg import fiberskal
from formingskloss import check_contact, die_profile
from verkstadmal import planar_section, section_line


def store(name,solid):
    assert solid.isValid() and len(solid.Solids())==1
    box=solid.BoundingBox()
    placed=solid.translate((-box.xmin,-box.ymin,-box.zmin))
    path=HERE/(name+".stl")
    placed.exportStl(str(path),tolerance=.025,angularTolerance=.08)
    mesh=trimesh.load_mesh(path)
    assert mesh.is_volume and len(mesh.split())==1 and abs(mesh.bounds[0,2])<.001
    assert max(mesh.extents)<245
    return {"stl":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "xyz_mm":np.round(mesh.extents,3).tolist()}


def return_die(wall):
    pts=wall.tessellate(.04,.10)[0]
    stations=[p.x*fasade.U[0]+p.y*fasade.U[1] for p in pts]
    us=np.linspace(min(stations),max(stations),140)
    bounds=wall.BoundingBox()
    heights=[bounds.zmin,7,bounds.zmax,bounds.zmax+3]
    die=fiberskal.indexed_loft([die_profile(z,us) for z in heights],True)
    middle=LineString([fasade.projected(u,7,-1.5) for u in us])
    gaps=check_contact(middle,1,wall,die)
    overlap=sum(abs(s.Volume()) for s in die.intersect(wall).Solids())
    assert overlap<.1
    return {**store("D03-retur",die),"prover":gaps,"overlapp_mm3":overlap}


def skirt_die(shell):
    z=3.95
    wall=planar_section(shell,z)
    neutral=section_line(fiberskal.outer_wire(1.5,z))
    arc=neutral.intersection(wall)
    assert arc.geom_type=="LineString" and 73<arc.length<80
    points=np.array(arc.coords)
    ends=points[[0,-1]]
    t=ends-points[[1,-2]]
    guides=ends+3*t/np.linalg.norm(t,axis=1)[:,None]
    middle=LineString(np.vstack((guides[0],points,guides[1]))).simplify(.012)
    for side in (-1,1):
        edge=middle.offset_curve(side*1.65)
        foot=edge.buffer(side*10,single_sided=True).simplify(.015)
        if fiberskal.polygon().contains(foot.representative_point()):
            break
    assert foot.is_valid and foot.geom_type=="Polygon"
    overlap=foot.intersection(wall).area
    assert overlap<.05,overlap
    solid=cq.Workplane("XY").polyline(list(foot.exterior.coords)[:-1]).close().extrude(12).val()
    samples=[edge.distance(arc.interpolate(t,normalized=True)) for t in np.linspace(.02,.98,35)]
    assert max(abs(d-1.65) for d in samples)<.08
    return {**store("D04-rand",solid),"strimmel_lengd_mm":round(arc.length,3),
            "strimmel_hogd_mm":6.1,"snitt_mm2":overlap}


def main():
    source=HERE.parent/"Fotprove/Raup-tupp.step"
    scene=cq.Assembly.load(str(source))
    parts={p.name:p.obj.moved(p.loc) for p in scene.children}
    report={"step":source.name,"sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "D03":return_die(parts["P02-Retur"]),"D04":skirt_die(parts["P01"])}
    (HERE/"Kontroll.json").write_text(json.dumps(report,indent=2),encoding="utf8")
    print(report,flush=True)


if __name__=="__main__":
    main()
