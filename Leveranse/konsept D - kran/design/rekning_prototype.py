"""Overslag for Kran, prototype: masse, tyngdepunkt, ledd og velting.
Koordinatar: x langs armen (+ mot tuppen), y vinkelrett på stativplata (+ framover, sida armen sit på),
z opp frå bordet. Leddaksen er x=0, z=330."""
import math
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

ZL = 330.0          # leddet over bordet
Z0 = 4.0            # underkant stålplate (står 4 mm ned i spalta i foten, foten 2..8 + gummi 2)
T_ST = 4.0          # stålplate
RHO_ST = 7.85e-3    # g/mm3
RHO_AL = 2.70e-3
R_TOPP = 22.0

# --- stativplata ---
piv = Point(0, ZL)
topp = piv.buffer(R_TOPP, 64)
# venstre botnhjørne, høgre botnhjørne, høgre kant opp under leddet
hull = unary_union([Polygon([(-140, Z0), (36, Z0), (18, 313), (0, ZL), (-14, ZL)]), topp]).convex_hull
spalte = LineString([(-97, 43), (3.7, 311.5)]).buffer(4.25, 32)
pivhol = piv.buffer(5.25, 32)
# bogespor for stoppinnen, r=13, 115..195 grader, breidd 3.4
bue = LineString([(13*math.cos(math.radians(a)), ZL + 13*math.sin(math.radians(a))) for a in range(115, 196, 2)]).buffer(1.7, 16)
m4 = [Point(-100, 14).buffer(1.65), Point(0, 14).buffer(1.65)]
plate = hull.difference(spalte).difference(pivhol).difference(bue)
for h in m4:
    plate = plate.difference(h)
A = plate.area
m_plate = A * T_ST * RHO_ST
cx, cz = plate.centroid.x, plate.centroid.y
print(f"stålplate: areal {A:.0f} mm2, masse {m_plate:.0f} g, tp x {cx:.1f} z {cz:.1f}, bbox {plate.bounds}")
print(f"  minste steg spalte->pivhol {spalte.distance(pivhol):.1f}, bue->kant {bue.distance(hull.exterior):.1f}, bue->spalte {bue.distance(spalte):.1f}, bue->pivhol {bue.distance(pivhol):.1f}")

# --- armen ---
L_ARM = 480.0
X_PROF0, X_PROF1 = 35.0, 470.0     # aluprofilet, 25 mm stikk inn i armhovudet (x 35..60)
prof_gpm = 162 + 20                # g/m: 1715-profil ca. 60 mm2 alu + opal PC-deksel
m_prof = (X_PROF1 - X_PROF0) / 1000 * prof_gpm
X_LED0, X_LED1 = 120.0, 465.0
m_led = (X_LED1 - X_LED0) / 1000 * 12   # COB 8 mm ~12 g/m
arm = [  # namn, masse g, x, y, z
    ("aluprofil 1715 m/deksel", m_prof, (X_PROF0 + X_PROF1) / 2, 17, ZL - 2),
    ("COB-stripe", m_led, (X_LED0 + X_LED1) / 2, 17, ZL - 8),
    ("leidning i armen", 2.0, 80, 17, ZL),
    ("endelokk PLA", 4.0, 475, 17, ZL - 2),
    ("armhovud PLA", 35.0, 14, 13, ZL),
    ("frontlokk/knott PLA", 3.0, 0, 26, ZL),
    ("M10x1-mutter i hovudet", 3.0, 0, 6, ZL),
]
bak = [  # roterer med armen, men ligg i leddaksen
    ("gjengerør M10x1 x 50 messing", 9.0, 0, -16, ZL),
    ("friksjonsskive PETG", 2.0, 0, -3.5, ZL),
    ("2 skiver M10 DIN 125", 6.0, 0, -18, ZL),
    ("trykkfjør 2,5x18x25", 9.0, 0, -18, ZL),
    ("mutter + kontramutter M10x1", 6.0, 0, -34, ZL),
    ("bakre knott PLA", 7.0, 0, -30, ZL),
]
M_arm_g = sum(m * x for _, m, x, _, _ in arm)
m_armsum = sum(m for _, m, *_ in arm)
T_g = M_arm_g * 9.81e-6
print(f"arm: masse {m_armsum:.1f} g, moment om leddet vassrett {M_arm_g:.0f} g*mm = {T_g:.3f} Nm, tp x {M_arm_g/m_armsum:.0f}")
for s in (0.85, 1.15):
    print(f"  skala {s}: moment ~ {T_g*s*s:.3f} Nm")

# --- ledd ---
mu_f = 0.25        # PLA mot lakkert stål, statisk, nedre anslag
mu_b = 0.15        # stål mot stål (fjørende mot skiva), nedre anslag
def reff(D, d):
    R, r = D / 2, d / 2
    return 2 / 3 * (R**3 - r**3) / (R**2 - r**2)
r_f = reff(44, 10.5)
r_b = 2 / 3 * 15.5 / 2 * 1.0 + 0  # fjørende: ring med middeldiameter 15.5 -> r ~ 7.75 (tynn ring: r_eff = r_m)
r_b = 15.5 / 2
T_need = 2.0 * T_g
k_per_N = mu_f * r_f / 1000 + mu_b * r_b / 1000
F = T_need / k_per_N
print(f"ledd: r_eff front {r_f:.2f} mm, bak {r_b:.2f} mm; mål {T_need:.3f} Nm -> F {F:.0f} N")
# fjør 2,5 x 18 x 25, 4 aktive vindingar
G, d, D, n = 79000, 2.5, 18 - 2.5, 4
k = G * d**4 / (8 * D**3 * n)
C = D / d
Kw = (4*C - 1) / (4*C - 4) + 0.615 / C
tau = Kw * 8 * F * D / (math.pi * d**3)
print(f"fjør k {k:.1f} N/mm, saman {F/k:.1f} mm, tau {tau:.0f} MPa, C {C:.1f}")
p = F / (math.pi / 4 * (44**2 - 10.5**2))
print(f"flatetrykk front {p:.3f} MPa")

# --- fot ---
FX0, FX1, FY0, FY1 = -150.0, 45.0, -45.0, 70.0
m_fot = 95.0
foter = [(FX0 + 8, FY0 + 8), (FX0 + 8, FY1 - 8), (FX1 - 8, FY0 + 8), (FX1 - 8, FY1 - 8)]
resten = [
    ("stålplate", m_plate, cx, 0, cz),
    ("fot PLA m/ribbe og hus", m_fot, -50, 8, 7),
    ("USB-C + PWM-kort + potensiometer + knott", 22.0, 20, -25, 18),
    ("leidning stativ", 4.0, 25, -4, 170),
    ("4 gummiføter, 2 M4-skruar", 6.0, -55, 10, 4),
]
alle = [(n_, m, x, y, z) for n_, m, x, y, z in arm + bak + resten]
M = sum(m for _, m, *_ in alle)
X = sum(m * x for _, m, x, _, _ in alle) / M
Y = sum(m * y for _, m, _, y, _ in alle) / M
Z = sum(m * z for _, m, _, _, z in alle) / M
print(f"total {M:.0f} g, tp ({X:.1f}, {Y:.1f}, {Z:.1f})")
xs = [f[0] for f in foter]; ys = [f[1] for f in foter]
mot = math.degrees(math.atan((max(xs) - X) / Z))
fra = math.degrees(math.atan((X - min(xs)) / Z))
fram = math.degrees(math.atan((max(ys) - Y) / Z))
bakv = math.degrees(math.atan((Y - min(ys)) / Z))
print(f"vipp: mot armen {mot:.1f}, frå armen {fra:.1f}, framover {fram:.1f}, bakover {bakv:.1f}  (føter {foter})")
# verste: arm opp 60 / ned 20
for ang in (60, -20):
    a = math.radians(ang)
    Xa = (sum(m * x for _, m, x, _, _ in resten + bak) + sum(m * x * math.cos(a) for _, m, x, _, _ in arm)) / M
    Za = (sum(m * z for _, m, _, _, z in resten + bak) + sum(m * (ZL + x * math.sin(a)) for _, m, x, _, _ in arm)) / M
    print(f"  arm {ang:+d}: tp x {Xa:.1f} z {Za:.1f}, mot armen {math.degrees(math.atan((max(xs)-Xa)/Za)):.1f}")
# skala +15 % på armen åleine
s = 1.15
Xs = (sum(m * x for _, m, x, _, _ in resten + bak) + sum(m * s * x * s for _, m, x, _, _ in arm)) / (M + sum(m*(s-1) for _, m, *_ in arm))
print(f"  arm +15 % lengd: tp x {Xs:.1f}, mot armen {math.degrees(math.atan((max(xs)-Xs)/Z)):.1f}")
# PLA-stativ i staden for stål (6 mm PLA, 40 % fyll)
m_pla = A * 6 * 1.24e-3 * 0.55
alle2 = [(n_, (m_pla if n_ == 'stålplate' else m), x, y, z) for n_, m, x, y, z in alle]
M2 = sum(m for _, m, *_ in alle2); X2 = sum(m*x for _, m, x, _, _ in alle2)/M2; Z2 = sum(m*z for _, m, _, _, z in alle2)/M2
print(f"PLA-stativ: {M2:.0f} g, tp x {X2:.1f} z {Z2:.1f}, mot armen {math.degrees(math.atan((max(xs)-X2)/Z2)):.1f}")
