"""bevis_rekna.py - smaa kontrollrekningar bak bevis.md (alt her er REKNA, ikkje maalt).

Koyr:  python konsept/vindauge/film/bevis_rekna.py
Ingen filer blir skrivne. Rein numpy, ein prosess.

Modell: ideell lineaer prismefilm, toppvinkel 90 grader, brytingsindeks n (ANTAKING),
riller vassrett. Vinkel a = synsstraalen sin vinkel mot arknormalen i planet
vinkelrett paa rillene; a < 0 tyder at auget er OVER normalen (ser nedover paa arket).
D = kor mykje synslinja blir boegd oppover (grader) = kor langt nede paa arket
ein fjern ting dukkar opp i hoeve til der han eigentleg er.
"""
import math
import numpy as np

deg = math.degrees
rad = math.radians


def s1_opp(a, n=1.59):
    """S1: prismesida mot auget, flat side mot vindauget. Biletet via dei
    nedvende flatene (gir forskyving oppover). Returnerer (D, del av straalane)
    eller (None, 0) om vegen er stengd."""
    inn = 45.0 - a  # innfallsvinkel mot den nedvende flata
    if inn >= 90 or inn <= -90:
        return None, 0.0
    r = deg(math.asin(math.sin(rad(inn)) / n))
    indre = 45.0 - r  # vinkel mot arknormalen inne i filmen
    s = n * math.sin(rad(indre))
    if abs(s) >= 1:
        return None, 0.0  # totalrefleksjon i den flate baksida
    ut = deg(math.asin(s))
    andel = max(0.0, min(1.0, 0.5 * (1 + math.tan(rad(a)))))  # del av rillebreidda som treffer flata
    return ut - a, andel


def s2_opp(a, n=1.59):
    """S2: flat side mot auget, prisma mot vindauget. Returnerer D eller None
    (None = dobbel totalrefleksjon, arket er blindt og speglar rommet)."""
    g = deg(math.asin(math.sin(rad(a)) / n))  # inne i filmen
    i = 45.0 + g  # innfall mot flata som slepper lyset ut oppover (for a < 0)
    s = n * math.sin(rad(i))
    if s >= 1:
        return None
    t = deg(math.asin(s))
    return (-45.0 + t) - a


def blindsone_s2(n):
    """Halv breidd (grader i luft) paa sona der S2 ikkje slepp noko gjennom."""
    kritisk = deg(math.asin(1 / n))
    g = 45.0 - kritisk
    return deg(math.asin(n * math.sin(rad(g))))


def helling_fraa_avsmalning(b_topp, b_botn, dy, b_midt, f_px):
    """Vinkel mellom kameraaksen og arknormalen (plant ark) fraa korleis
    breidda i biletet minkar nedover. tan(theta) = -(db/dy) * f / b(midt)."""
    return deg(math.atan(((b_topp - b_botn) / dy) * f_px / b_midt))


if __name__ == "__main__":
    print("== Forskyving D(a), n = 1.59 ==")
    print("   a    S1: D   andel   ut(=D+a)    S2: D")
    for a in (20, 10, 5, 0, -5, -10, -15, -20, -25, -30, -35, -40, -44):
        d1, andel = s1_opp(a)
        d2 = s2_opp(a)
        t1 = f"{d1:5.1f}  {andel:4.2f}   {d1 + a:6.1f}" if d1 is not None else "  --    --      --"
        t2 = f"{d2:5.1f}" if d2 is not None else "blind"
        print(f"{a:5d}   {t1}      {t2}")
    print()
    print("== S1 ved loddrett innsyn (a=0) for ulike n ==")
    for n in (1.49, 1.53, 1.56, 1.59, 1.62, 1.65):
        print(f"  n={n:.2f}  D={s1_opp(0, n)[0]:.1f} grader   blindsone S2: +/-{blindsone_s2(n):.1f} grader")
    print()
    # Fargespreiing: dn mellom blaatt (486 nm) og raudt (656 nm) = (n-1)/V
    for V in (30, 35, 45, 57):
        n0 = 1.59
        dn = (n0 - 1) / V
        dD = s1_opp(-20, n0 + dn / 2)[0] - s1_opp(-20, n0 - dn / 2)[0]
        print(f"  Abbe-tal {V}: fargespreiing ved a=-20: {dD:.2f} grader")
    print()
    # Diffraksjon: gitterordenar ved lambda/pitch; konvolutten er sett av ei flate ~ pitch/2
    for pitch in (24, 50):
        print(f"  pitch {pitch} um: ordensavstand lambda/pitch = {deg(0.55 / pitch):.2f} grader,"
              f" konvolutt lambda/(pitch/2) = {deg(0.55 / (pitch / 2)):.2f} grader")
    print()
    f = 1505.0  # px ved 1500 px biletbreidd, ANTAKING 26 mm-ekvivalent
    print("== Helling fraa avsmalning (plant ark) ==")
    print(f"  foto 07: theta = {helling_fraa_avsmalning(1107, 938, 1728, 1022, f):.1f} grader")
    print(f"  foto 01: theta = {helling_fraa_avsmalning(964, 722, 1155, 831, f):.1f} grader")
    f24 = 1505.0 * 24 / 26
    print(f"  (24 mm-ekv.: foto 07 {helling_fraa_avsmalning(1107, 938, 1728, 1022, f24):.1f},"
          f" foto 01 {helling_fraa_avsmalning(964, 722, 1155, 831, f24):.1f})")
    print()
    print("== Storleik fraa linjeavstanden paa arket ved sida (foto 07) ==")
    F = 1938.0  # px i full opploysing
    beta_t = math.atan((2525 - 1288) / F)
    beta_f = math.atan((2395 - 1288) / F)
    for p in (20.0, 28.0):
        for linje in (4.2, 4.7, 5.1, 5.6):
            dX = 17.5 * math.cos(beta_t) / math.sin(rad(p) + beta_t)
            px_per_z = math.hypot(dX, 4.8)  # linjeavstand = px_per_z * z / F
            z_t = linje * F / px_per_z
            z_f = z_t * (math.cos(beta_f) / math.sin(rad(p) + beta_f)) / (math.cos(beta_t) / math.sin(rad(p) + beta_t))
            z0 = z_f * (1 - 860 * math.tan(rad(8.2)) / 1505)
            W = 1022 / 1505 * z0
            H = 1.74 * W
            print(f"  p={p:.0f}  linjeavstand {linje} mm -> avstand {z0:4.0f} mm, ark {W:4.0f} x {H:4.0f} mm,"
                  f" diagonal {math.hypot(W, H) / 25.4:4.1f} tommar")
