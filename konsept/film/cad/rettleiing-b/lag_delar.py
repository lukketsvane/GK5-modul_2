import math
import os
import sys

import numpy as np
import trimesh

HER = os.path.dirname(os.path.abspath(__file__))
SAMLA = os.path.join(HER, "..", "ut-b", "samla")
UT = os.path.join(HER, "delar")
VINKEL, YT, AKSE_H = 35.0, 22.0, 260.0
BJELKE = ["05", "06", "07", "08", "09", "10", "11", "13", "E"]
FASTE = ["01", "02", "03", "04", "12"]


def last(i):
    return trimesh.load(os.path.join(SAMLA, f"{i}.stl"), force="mesh")


def drei(m, vinkel):
    m = m.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(vinkel - VINKEL), [1, 0, 0], [0, YT, AKSE_H]))
    return m


def main():
    os.makedirs(UT, exist_ok=True)
    for i in FASTE:
        last(i).export(os.path.join(UT, f"{i}.stl"))
    for v in (0, 35, 80):
        for i in BJELKE:
            drei(last(i), v).export(os.path.join(UT, f"{i}@{v}.stl"))
    skruar = sorted(drei(last("E"), 0).split(only_watertight=False), key=lambda s: s.centroid[0])
    ein = skruar[0].copy()
    c = ein.bounds.mean(axis=0)
    ein.apply_translation(-c)
    ein.export(os.path.join(UT, "E-ein.stl"))
    pos = [np.round(s.bounds.mean(axis=0), 2).tolist() for s in skruar]
    with open(os.path.join(UT, "E-posisjonar.txt"), "w") as f:
        f.write("\n".join(str(p) for p in pos) + "\n")
    print(len(skruar), "skruar E ved 0°:", pos)


if __name__ == "__main__":
    sys.exit(main())
