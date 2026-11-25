# -*- coding: utf-8 -*-
"""Lagar ei ny variantmappe av Sveip: variantar/<id>/cad/ med kopi av CAD-skripta frå rev. B.

Køyr frå variantar/:  python ny_variant.py V1-namn
Etterpå, frå variantar/<id>/cad/:
  python sveip_produksjon.py --rask      (byggjer, kontrollerer, skriv STL og render/geometri.json)
  python sveip_lystal.py                 (lystal, om lag 20 s)
  python ../../render_variant.py front trekvart svart lys topp naer
"""
import re
import shutil
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
BASIS = HER.parent / "cad"


def main(vid):
    mal = HER / vid
    cad = mal / "cad"
    if cad.exists():
        sys.exit(f"{cad} finst alt")
    cad.mkdir(parents=True)
    for f in sorted(BASIS.glob("*.py")):
        shutil.copy(f, cad / f.name)
    # lysmotoren ligg i <repo>/konsept/lysskisse: leit oppover i staden for to nivå opp
    lt = cad / "sveip_lystal.py"
    s = lt.read_text(encoding="utf-8")
    s2 = s.replace(
        "REPO = ROT.parent.parent\n",
        "REPO = next(p for p in ROT.parents if (p / 'konsept' / 'lysskisse').is_dir())\n")
    assert s != s2, "fann ikkje REPO-lina i sveip_lystal.py"
    lt.write_text(s2, encoding="utf-8")
    for d in ("render", "kontroll"):
        (mal / d).mkdir(exist_ok=True)
    print("laga", mal)


if __name__ == "__main__":
    if len(sys.argv) != 2 or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", sys.argv[1]):
        sys.exit("bruk: python ny_variant.py V1-namn")
    main(sys.argv[1])
