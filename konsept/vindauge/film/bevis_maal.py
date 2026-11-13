"""bevis_maal.py - enkle maalingar i foto 01 og 07 av arket (estimat fraa foto).

Koyr:  python konsept/vindauge/film/bevis_maal.py
Skriv berre til context/delar-foto/analyse/ (ikkje publisert) og til stdout.
Koordinatar er i full opploysing (1932 x 2576). Ein prosess, ingen traadar.
"""
import os
import numpy as np
from PIL import Image

ROT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FOTO = os.path.join(ROT, "context", "delar-foto")
UT = os.path.join(FOTO, "analyse")


def lin(a):
    """sRGB (0-255) -> lineaer (0-1)."""
    a = a.astype(np.float64) / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def les(namn):
    return np.asarray(Image.open(os.path.join(FOTO, namn)).convert("RGB"))


def felt(im, x0, y0, x1, y1):
    """Middel i eit felt: sRGB-middel og relativ luminans Y (lineaer)."""
    r = im[y0:y1, x0:x1].reshape(-1, 3)
    l = lin(r)
    Y = (0.2126 * l[:, 0] + 0.7152 * l[:, 1] + 0.0722 * l[:, 2]).mean()
    return r.mean(0).round(0), Y


def profil(im, x0, x1, y0, y1, steg=20):
    ut = []
    for y in range(y0, y1, steg):
        rgb, Y = felt(im, x0, y, x1, y + steg)
        ut.append((y + steg // 2, rgb, Y))
    return ut


if __name__ == "__main__":
    im7 = les("07-prismefilm-heil-mot-vindauge.jpg")
    im1 = les("01-prismefilm-mot-vindauge.jpg")
    print("== foto 07: referansefelt ==")
    for namn, b in [
        ("himmel direkte (over taka)", (400, 5, 560, 45)),
        ("ark, oevst", (500, 300, 1300, 450)),
        ("ark, midt", (500, 1100, 1300, 1250)),
        ("snoe i skugge direkte (hoegre)", (1620, 1350, 1900, 1500)),
        ("moerk asfalt direkte (venstre)", (20, 1500, 200, 1650)),
        ("ark, moerk sone nedst", (500, 2100, 1300, 2200)),
        ("vindaugsramme direkte", (1560, 1960, 1900, 2010)),
    ]:
        rgb, Y = felt(im7, *b)
        print(f"  {namn:34s} sRGB={rgb}  Y={Y:.3f}")
    print("== foto 07: loddrett profil x=500..1300 ==")
    for y, rgb, Y in profil(im7, 500, 1300, 180, 2400, 40):
        print(f"  y={y:5d}  sRGB={rgb}  Y={Y:.3f}")
    print("== foto 01: referansefelt ==")
    for namn, b in [
        ("ark, oevst", (500, 560, 1300, 700)),
        ("ark, midt", (500, 1000, 1300, 1150)),
        ("snoe direkte (hoegre)", (1600, 1000, 1900, 1150)),
    ]:
        rgb, Y = felt(im1, *b)
        print(f"  {namn:34s} sRGB={rgb}  Y={Y:.3f}")
    print("== foto 01: loddrett profil x=450..1350 ==")
    for y, rgb, Y in profil(im1, 450, 1350, 480, 1960, 40):
        print(f"  y={y:5d}  sRGB={rgb}  Y={Y:.3f}")
