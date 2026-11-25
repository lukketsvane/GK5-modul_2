# -*- coding: utf-8 -*-
"""FYR · rask førehandsvising: isometri, snitt og detaljar som PNG (via SVG frå CadQuery).

    py -3 cad/fyr_forhandsvis.py <utmappe> [vinkel_hylse]
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq
import cairosvg

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402


def svg_png(shape, path: Path, proj=(1, -1, 0.6), w=900, h=1100, hidden=True):
    opt = {"width": w, "height": h, "marginLeft": 20, "marginTop": 20, "showAxes": False,
           "projectionDir": proj, "strokeWidth": 0.4, "strokeColor": (20, 20, 20),
           "hiddenColor": (170, 170, 170), "showHidden": hidden}
    svg = path.with_suffix(".svg")
    cq.exporters.export(shape, str(svg), opt=opt)
    cairosvg.svg2png(url=str(svg), write_to=str(path), background_color="white")
    svg.unlink()


def main():
    ut = Path(sys.argv[1])
    ut.mkdir(parents=True, exist_ok=True)
    vri = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    p = g.FyrParams()
    d = g.bygg_alle(p)
    if vri:
        d["05_hylse"] = d["05_hylse"].rotate((0, 0, 0), (0, 0, 1), vri)
    alle = cq.Compound.makeCompound([w.val() for w in d.values()])
    svg_png(alle, ut / "01_iso.png", proj=(1, -0.8, 0.45), hidden=False)
    # halvsnitt: fjern y < 0
    kniv = cq.Workplane("XY").box(400, 200, 600, centered=(True, False, False)).translate((0, 0, -50))
    snitt = [w.intersect(kniv).val() for k, w in d.items() if k not in ("11_oring",)]
    svg_png(cq.Compound.makeCompound(snitt), ut / "02_snitt.png", proj=(0, -1, 0), hidden=False)
    # innmat utan mantel og hylse
    inn = [w.val() for k, w in d.items() if k not in ("04_mantel", "05_hylse", "11_oring")]
    svg_png(cq.Compound.makeCompound(inn), ut / "03_innmat.png", proj=(1, -0.7, 0.5), hidden=False)
    # hylsa åleine
    svg_png(d["05_hylse"].val(), ut / "04_hylse.png", proj=(1, -0.3, 0.25), hidden=False)
    # lysrista åleine
    svg_png(d["07_lysrist"].val(), ut / "05_lysrist.png", proj=(1, -0.6, 0.35), hidden=False)
    # chassis + fot åleine
    svg_png(cq.Compound.makeCompound([d["03_chassis"].val(), d["01_fot"].val()]), ut / "06_chassis.png", proj=(1, -0.7, 0.6), hidden=False)
    # mantel botn (bajonett)
    svg_png(d["04_mantel"].val(), ut / "07_mantel.png", proj=(-1, 0.4, 0.15), hidden=False)
    print("ok", ut)


if __name__ == "__main__":
    main()
