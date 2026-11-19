# -*- coding: utf-8 -*-
"""FURU / B02. FreeCAD 1.0, mm. Run: freecadcmd Furu-B02.FCMacro"""
import os
import sys
import csv
import json
import math
from pathlib import Path
import FreeCAD as A
import Part
import Import

V = A.Vector
pi = math.pi
sin, cos, sqrt = math.sin, math.cos, math.sqrt
rad = math.radians

macro_path = next((p for p in sys.argv if str(p).lower().endswith(".fcmacro")),
                  globals().get("__file__", "Furu-B02.FCMacro"))
ROOT = Path(os.environ.get("FURU_DIR",
            str(Path(macro_path).resolve().parent / "Regenerert-B02")))
OUT = ROOT / "packet"
WORK = ROOT / "work"
DXFDIR = OUT / "Rullesjablonar"
for directory in (OUT, WORK, DXFDIR):
    directory.mkdir(parents=True, exist_ok=True)

N = 40
P = 78.0
Z = 198.0
DX, DZ = 26.0, -4.0
YF, YR = 104.0, 124.0
CY = 14.0                         # foot centre, y
ZA = Z - 55.0                     # exit plane of the desk optic
T = 0.68
BIAS = 0.40
GAP = 1.8                         # measured in x at constant z, not normal to seam
EDGES = [-234., -156., -78., 0., 78., 156., 234.]
CROWN = [24., 73., 88., 89., 80., 60., 24.]
ST = [(l+r)*0.5 for l, r in zip(EDGES, EDGES[1:])]
# (global x, local z, radius) of the two end knives, axes parallel to y
TIP_L, TIP_R = (-213., 3., 28.5), (212., 10., 34.)

doc = A.newDocument("Furu_B02")
controls = doc.addObject("Spreadsheet::Sheet", "Controls")
controls.Label = "Styring"
for cell, val in {
    "A1": "Opning (0 til 40 grader)", "B1": "0 deg",
    "A2": "Stasjonsdeling (mm)", "B2": "78",
    "A3": "Nominell platetjukkleik (mm)", "B3": "0.68",
    "A4": "Revisjon", "B4": "B02",
    "A5": "Lysbru: utgangsplan over bord (mm)", "B5": "143",
    "A6": "Modulbuss (V DC, SELV)", "B6": "24",
    "A7": "Effekt til lyskort, maks (W)", "B7": "6.10",
    "A8": "Hall-styring", "B8": "Sjå Modulgrensesnitt.md"
}.items():
    controls.set(cell, val)
controls.setAlias("B1", "Opening")
controls.setColumnWidth("A", 265)

root = doc.addObject("App::Part", "Furu")
root.Label = "Furu B02"

def group(key, label):
    g = doc.addObject("App::Part", key)
    g.Label = label
    root.addObject(g)
    return g

base = group("Body", "10 Sokkel og lys")
fixed = group("Fixed", "20 Fast røyr")
move = group("Drive", "30 Reguleringsrøyr")
shell_groups = [group("Shell%d" % i, "%d Skjell %d" % (40+i, i))
                for i in range(1, 7)]

aa = "min(40 deg;max(0 deg;Controls.Opening))"
def placement_expr(pos, angle):
    return ("create(<<placement>>;create(<<vector>>;" + pos +
            ");create(<<rotation>>;create(<<vector>>;0;1;0);" + angle + "))")

for xp, g in zip(ST, shell_groups):
    g.setExpression("Placement", placement_expr("%g;0;%g" % (xp, Z), "-" + aa))
move.setExpression("Placement", placement_expr(
    "%g*cos(%s)-(%g)*sin(%s);0;%g+%g*sin(%s)+(%g)*cos(%s)" %
    (DX, aa, DZ, aa, Z, DX, aa, DZ, aa), "0 deg"))

# Material keys used in the mesh exchange. An envelope with an allocated
# mass has an effective density, not a fictitious bulk material density.
materials = {
    "sheet": ("EN AW-5754 H22", 2.68),
    "al": ("EN AW-6061 T6", 2.70),
    "bronze": ("EN AW-6061 T6, bronseeloksert", 2.70),
    "steel": ("AISI 304", 8.00),
    "pom": ("POM-C", 1.41),
    "pc": ("Opal polykarbonat", 1.20),
    "rubber": ("Silikon", 1.15),
    "ledref": ("Innkjøpt LED-lyskort, konvolutt", 0.0),
    "cordref": ("Innkjøpt kabelsett, vist leidning", 0.0),
    "hall": ("Hall-kort med straumregulatorar, konvolutt", 0.0),
    "mag": ("NdFeB, fornikla", 7.5),
    "plug": ("Kontaktinnsats, PBT og koparlegering, konvolutt", 0.0),
}
parts = []
keys = set()

def ax(r, length, pt, direction=(0, 0, 1)):
    return Part.makeCylinder(r, length, V(*pt), V(*direction))

def box(x, y, z, pt):
    return Part.makeBox(x, y, z, V(*pt))

def ring(ro, ri, length, pt, direction=(0, 0, 1)):
    return ax(ro, length, pt, direction).cut(ax(ri, length, pt, direction))

def poly3(pts):
    return Part.makePolygon([V(*p) for p in list(pts)+[pts[0]]])

def xz(pts, y, depth):
    return Part.Face(poly3([(x, y, z) for x, z in pts])).extrude(V(0, depth, 0))

def yz(pts, x, length):
    return Part.Face(poly3([(x, y, z) for y, z in pts])).extrude(V(length, 0, 0))

def turn(pts):
    return Part.Face(poly3([(r, 0, z) for r, z in pts])).revolve(V(), V(0, 0, 1), 360)

def lathe_x(pts, yc, zc):
    return Part.Face(poly3([(x, yc, zc+r) for x, r in pts])).revolve(
        V(0, yc, zc), V(1, 0, 0), 360)

def shift(sh, vec):
    sh.translate(V(*vec))
    return sh

def cut(sh, *tools):
    for tool in tools:
        sh = sh.cut(tool)
    return sh.removeSplitter()

def join(*items):
    sh = items[0]
    for item in items[1:]:
        sh = sh.fuse(item)
    return sh.removeSplitter()

def add(gr, key, name, sh, material, process, grams=None):
    solids = sh.Solids
    if key in keys or len(solids) != 1:
        raise RuntimeError("%s: duplicate ID or %d solids" % (key, len(solids)))
    sh = solids[0]
    if sh.Volume <= 0 or not sh.isValid():
        raise RuntimeError("Invalid solid: " + key)
    keys.add(key)
    ob = doc.addObject("Part::Feature", "P_" + key.replace("-", "_"))
    gr.addObject(ob)
    ob.Label = key + " " + name
    ob.Shape = sh
    spec, density = materials[material]
    if grams is not None:
        density = 1000.0*grams/sh.Volume
        process += " Konvolutt med budsjettert masse %g g." % grams
    for typ, field, value in [
        ("String", "Item", key), ("String", "MaterialSpec", spec),
        ("String", "Process", process), ("Float", "Density_g_cm3", density),
        ("Float", "Mass_g", round(sh.Volume*density/1000.0, 5))
    ]:
        ob.addProperty("App::Property"+typ, field, "Verkstad")
        setattr(ob, field, value)
    parts.append((ob, gr, material))
    return ob

def screw_z(x, y, seat, dia, length, hr, hh, up=True):
    d = 1 if up else -1
    return join(ax(dia/2, length, (x, y, seat), (0, 0, d)),
                ax(hr, hh, (x, y, seat-d*hh), (0, 0, d)))

# One hollow pedestal, including the foot and a machined mounting land.
# The foot is NOT a thin disc standing on four inboard points.
ped = shift(turn([
    (74.8,1.3),(76.8,2.2),(76.8,3.8),(75.6,5.2),(29,5.2),
    (24,6.4),(20,9),(16,15),(13,28),(11.2,54),(10.8,151),
    (12,177),(14,186),(14,190),(5.8,190),(5.8,185),(11.1,185),
    (10,176),(8.9,150),(9.2,54),(11.1,27),(14.1,14),
    (17.8,8),(23.8,4.5),(28.5,3.2),(70,3.2),(70,1.3)
]), (0, CY, 0))
land = xz([(-20,ZA+10),(20,ZA+10),(20,ZA+13),(16,ZA+16),
           (-16,ZA+16),(-20,ZA+13)], -9, 19)
ped = join(ped, land)
ped = cut(ped, ring(74.55,71.65,1.5,(0,CY,1.15)),
          ax(4.08,26,(0,CY,18),(0,1,0)),
          box(7.8,4.8,8,(-3.9,-6.9,ZA+9.8)),
          ax(2.6,22,(0,-5,ZA+14),(0,1,0)))
for x in (-9,9):
    ped = cut(ped, ax(1.52,6,(x,CY,184.5)))
for x in (-13,13):
    ped = cut(ped, ax(1.52,6,(x,-4.5,ZA+9.9)))
add(base,"101","Hol fot med kassettsete",ped,"al",
    "Drei hol fot og stamme frå same emne, fres anlegget frå attståande krage. "
    "Prototype i standard rundstong; vurder trykkforming av foten i serie. "
    "M3 i topp og kassettsete. Gjengar i modellen er frie nominelle konvoluttar.")
sole = shift(turn([(71.8,0),(74.4,0),(74.65,.55),(74.4,1.28),
                   (74.40,2.62),(71.80,2.62),(71.80,1.26),(71.55,.55)]),
             (0,CY,0))
add(base,"102","Heil sålering",sole,"rubber",
    "Strekk inn i dreia ringspor. Brei, samanhengande kontakt; kan vrengjast ut.")
yoke = xz([(-45,Z-4),(-41,Z-8),(41,Z-8),(45,Z-4),
           (45,Z+3),(42,Z+6),(-42,Z+6),(-45,Z+3)], CY-8, 16)
for x in (-39,39):
    yoke = cut(yoke, ax(2.06,18,(x,CY-9,Z),(0,1,0)),
               ax(1.53,5,(x,CY,Z+1.5)))
for j,x in enumerate((-9,9),1):
    yoke = cut(yoke, ax(1.65,16,(x,CY,Z-9)), ax(2.85,3,(x,CY,Z+3.4)))
    add(base,"H1-%d"%j,"M3 toppskrue",
        screw_z(x,CY,Z+3.4,3,16,2.7,2.4,False),"steel",
        "M3 × 16, lågt hovud. Skru ned i toppen av stamma.")
for j,x in enumerate((-39,39),1):
    add(base,"H2-%d"%j,"Låseskrue for beretapp",
        ax(1.5,3.8,(x,CY,Z+2)),"steel",
        "M3 flat ende, låser den gjennomgåande beretappen. Kosmetisk gjenge.")
yoke = cut(yoke, ax(2.45,16,(0,CY,Z-9)))
add(base,"103","Tverrsadel",yoke,"al",
    "Fres frå flatstong. To Ø4,12 på deling 78. Sentral kabelveg frå stamma.")
grom = join(ring(3.98,2.05,7,(0,CY+11.5,18),(0,1,0)),
            ring(5.15,2.05,1.3,(0,CY+18.5,18),(0,1,0)))
add(base,"104","Strekkavlasting",grom,"rubber","Tre inn frå baksida. Ingen limfuge.")
path = Part.BSplineCurve()
path.interpolate([V(0,CY+12,18),V(0,CY+28,18),V(3,65,13),
                  V(9,88,4.2),V(18,110,2.3),V(35,138,2.3),V(48,154,2.3)])
wire = Part.Wire([path.toShape()])
cord = wire.makePipeShell([Part.Wire([Part.makeCircle(
    1.85,V(0,CY+12,18),path.tangent(path.FirstParameter)[0])])],True,False)
add(base,"E03","Lågspenningsleidning",cord,"cordref",
    "Berre føring. Heile lausleidninga er rekna éin gong i totalbudsjettet.")

# Downward slide-in optic, and a separate, roofed, rearward wash aperture.
# Both boards, lenses and end catches leave with ONE cassette.
L = 352.
section = [
    (-52,-2),(-49,-2),(-49,-.18),(-50.6,-.18),(-50.6,1.65),
    (-50.3,1.65),(-50.3,8.2),(-11.7,8.2),(-11.7,1.65),
    (-11.4,1.65),(-11.4,-.18),(-13,-.18),(-13,-2),(-10,-2),
    (-10,10),(-33,10),(-33,17),(-9,17),(-9,18.5),(-34.5,18.5),
    (-34.5,10),(-52,10)
]
tray = yz([(y,ZA+z) for y,z in section],-L/2,L)
tray = join(tray, box(40,11,1.8,(-20,-10.5,ZA+8.2)),
            box(L,2.2,.75,(-176,-50.5,ZA+5.90)),
            box(L,2.2,.75,(-176,-13.7,ZA+5.90)),
            box(L,2.05,.65,(-176,-33.1,ZA+10.05)),
            box(L,2.05,.65,(-176,-33.1,ZA+16.32)))
tray = cut(tray, box(L+2,1.50,.85,(-177,-25.85,ZA+9.40)),
           box(L+2,1.50,.85,(-177,-25.85,ZA+16.76)),
           box(7.55,4.65,2.3,(-3.775,-6.825,ZA+8.1)))
for j,x in enumerate((-13,13),1):
    tray = cut(tray,ax(1.67,2.5,(x,-4.5,ZA+8.0)))
    add(base,"H3-%d"%j,"Serviceskrue M3",
        screw_z(x,-4.5,ZA+8.2,3,7,2.75,2.4),"steel",
        "M3 × 7, innvendig sekskant 2 mm. Tilgjengeleg rett nedanfrå.")
for s in (-1,1):
    # Snap windows in front wall, below the PCB, above the optical blade.
    tray = cut(tray,box(2.45,3,2.25,
                        ((-173.6 if s<0 else 171.15),-52.5,ZA+3.0)))
add(base,"106","Lyskjøl med dobbel optikk",tray,"al",
    "Langsgåande profil; prototype kan fresast i to oppspenningar. "
    "Tørr anleggsflate mot metallkjernekort. Fres bort monteringsleppa utanfor "
    "midtre 40 mm. Børst ytterflate, matt innside. Merking B02 / 24 V / pil mot brukar.")
add(base,"107","Arbeidsoptikk med spreiesjikt",
    box(349,38.9,1.50,(-174.5,-50.45,ZA)),"pc",
    "Innkjøpskrav: asymmetrisk hylleoptikk i opal PC med prismatisk utgang, "
    "ikkje berre mjølkekvitt glas. Glir i to spor. Fotometrisk mål i Lysmaal.json.")
add(base,"108","Skjult vaskelyslist",
    box(349,1.22,7.98,(-174.5,-25.71,ZA+9.50)),"pc",
    "Opal list, innskoven under taket i det bakovervende lyskammeret.")
for j,s in enumerate((-1,1),1):
    xend = s*176.
    cap = yz([(-52,ZA-2),(-10,ZA-2),(-10,ZA+10),(-9,ZA+17),
              (-9,ZA+18.5),(-34.5,ZA+18.5),(-36,ZA+10),(-52,ZA+10)],
             xend if s>0 else xend-1.6,1.6)
    def from_end(inside, outside):
        return min(xend-s*inside,xend-s*outside)
    cap = join(cap, box(5.0,1.15,2.0,(from_end(4.9,-.1),-50.28,ZA+3.12)),
               box(2.15,1.42,1.92,(from_end(4.72,2.57),-51.64,ZA+3.15)))
    add(base,"109-%d"%j,"Løysbar endefj ø r".replace("fj ø r","fjør"),cap,"pom",
        "Fjørkrok inn i vindauget. Trykk inn frå sida for å ta ut optikken.")
add(base,"E01","Arbeidskort 2700 K",
    box(328,38.2,1.50,(-164,-50.1,ZA+6.70)),"ledref",
    "Høg tettleik, Ra ≥ 90. Lysfelt på undersida; 2 mm mørk kant. "
    "Kortkantane i glidespor, fjørande endelås, utan tape.",15.)
add(base,"E02","Tokanals vaskelyskort",
    box(328,1.45,5.50,(-164,-33,ZA+10.74)),"ledref",
    "2000 K og 2700 K på same kort, Ra ≥ 90 på begge. Lyset går mot +Y "
    "inn i den innfelte opallista, ikkje opp frå nakne diodar.",4.)

# Keyed four-way blind mate. Simplified insulator/contact envelopes; the
# tongue is NOT modelled occupying the material of the mating receptacle.
plug = join(box(8.8,5.6,.9,(-4.4,-7.3,ZA+7.30)),
            box(7.34,4.44,1.85,(-3.67,-6.72,ZA+8.20)),
            box(4.85,2.35,3.2,(-2.425,-5.675,ZA+10.05)))
sock = cut(box(7.55,4.55,5.85,(-3.775,-6.775,ZA+10.07)),
           box(5.05,2.55,3.50,(-2.525,-5.775,ZA+10.05)))
add(base,"J01","Kassettplugg",plug,"plug",
    "Polarisert 4-pol, på kassett. Krav ≥ 30 V DC / 0,5 A per kontakt.",1.2)
add(base,"J02","Fast kontaktinnsats",sock,"plug",
    "Klipsfeste i sokkelsete. Frigang mot tunga; metallkontaktar ikkje detaljmodellerte.",1.4)

for drive,gr,y,ro in [(False,fixed,-YF,4.5),(True,move,YR,5.)]:
    rz = 0. if drive else Z
    rail = ring(ro,ro-1,414,(-207,y,rz),(1,0,0))
    for xp in ST:
        rail = cut(rail,ax(2.035,2*ro+2,(xp,y-ro-1,rz),(0,1,0)))
    add(gr,"301" if drive else "201","Reguleringsrøyr" if drive else "Fast røyr",
        rail,"bronze" if drive else "al",
        "Røyr Ø%g × 1. Seks tverrboringar Ø4,07 i same jigg, deling 78. "
        "Skuldertappane vert kaldstukne i ytste røyrvegg." % (2*ro))
    for s in (-1,1):
        cap = join(ax(ro-1.02,3,(s*204,y,rz),(s,0,0)),
                   ax(ro,.8,(s*207,y,rz),(s,0,0)))
        add(gr,("302" if drive else "202")+("-L" if s<0 else "-R"),
            "Endeplugg",cap,"pom","Lett presspassning, kan drivast ut.")
grip = lathe_x([(-33.5,5.03),(-33.5,5.8),(-32,7.15),(-27,8.4),
                (-18,9.5),(-7,10),(7,10),(18,9.5),(27,8.4),(32,7.15),
                (33.5,5.8),(33.5,5.03)],YR,0)
add(move,"303","Løftegrep",grip,"rubber",
    "Matt, varmgrå silikon, nominell montert form. Tre på før midttappane. "
    "Lett strekkpassning i fri tilstand. 67 mm for tre fingrar; ingen knappar.")

def dxf(name, pts):
    # R2000 closed lightweight polyline, millimetres at 1:1
    h = ("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1015\n9\n$INSUNITS\n70\n4\n"
         "0\nENDSEC\n0\nSECTION\n2\nENTITIES\n0\nLWPOLYLINE\n100\nAcDbEntity\n"
         "8\nCUT\n100\nAcDbPolyline\n90\n%d\n70\n1\n" % len(pts))
    with (DXFDIR/(name+".dxf")).open("w",encoding="ascii",newline="\n") as f:
        f.write(h)
        for x,y in pts:
            f.write("10\n%.6f\n20\n%.6f\n" % (x,y))
        f.write("0\nENDSEC\n0\nEOF\n")

def write_blank(i,b,k,rear,front):
    xp = ST[i]
    def edge_x(right,a):
        c = cos(a)
        if (not right and i==0) or (right and i==5):
            xc,zc,rr = TIP_R if right else TIP_L
            u,v = xc-xp,b*c-zc
            d = k*c
            # Intersection of the generator with the cylindrical end knife.
            disc = (d*v-u)**2-(1+d*d)*(u*u+v*v-rr*rr)
            return (u-d*v+(1 if right else -1)*sqrt(max(0.,disc)))/(1+d*d)
        e = P/2-GAP/2 if right else -P/2+GAP/2
        return (e+BIAS*b*c)/(1-BIAS*k*c)
    def flat(right,a):
        x = edge_x(right,a)
        h = sqrt(1+k*k)
        if abs(k)<1.e-9:
            return (x,b*a)
        g = (b+k*x)*h/k
        return (g*cos(k*a/h)-b*h/k, g*sin(k*a/h))
    an = [-rear+(rear+front)*n/240 for n in range(241)]
    dxf("S%02d"%(i+1),[flat(False,a) for a in an]+[flat(True,a) for a in reversed(an)])

def along(side,r,a,b,xx,zz):
    return ax(r,b-a,(xx,side*a,zz),(0,side,0))

for i,(xp,sg) in enumerate(zip(ST,shell_groups)):
    sid = i+1
    q = (CROWN[i+1]-CROWN[i])/P
    # Upper envelope in seam coordinate U = X - BIAS*z is linear on each band.
    # Solve for a true RIGHT circular cone r=b+k*x, x local to the pivot.
    k = q/(1+BIAS*q)
    b = (CROWN[i]+q*P/2)/(1+BIAS*q)
    def hem(lam):
        return math.acos(-lam/(1-BIAS*k*(1+lam)))
    front,rear = hem(.22),hem(.54)
    off = T*.5*sqrt(1+k*k)
    xl = -58. if i==0 else -85.
    xr = 59. if i==5 else 100.
    def cone_solid(pad):
        return Part.makeCone(b+k*xl+pad,b+k*xr+pad,xr-xl,V(xl,0,0),V(1,0,0))
    def skin_at_ends():
        a1,a2 = b+k*xl,b+k*xr
        wire = poly3([(xl,0,a1-off),(xr,0,a2-off),(xr,0,a2+off),(xl,0,a1+off)])
        sh = Part.Face(wire).revolve(V(),V(1,0,0),math.degrees(rear+front))
        sh.rotate(V(),V(1,0,0),-math.degrees(rear))
        return sh
    sh = skin_at_ends()
    el = -P/2+GAP/2 if i else -180.
    er = P/2-GAP/2 if i<5 else 180.
    sh = sh.common(xz([(el-BIAS*130,-130),(er-BIAS*130,-130),
                       (er+BIAS*130,130),(el+BIAS*130,130)],-135,270))
    if i in (0,5):
        xc,zc,rr = TIP_L if i==0 else TIP_R
        xc -= xp
        outside = box(150,280,280,(xc-150 if i==0 else xc,-140,-140))
        sh = cut(sh, outside.cut(ax(rr,282,(xc,-141,zc),(0,1,0))))
    outer_clear = cone_solid(off+.08)
    inner_clear = cone_solid(-off-.08)
    for xx,zz,side in [(0,0,-1),(DX,DZ,1)]:
        sh = cut(sh,ax(3.19,132,(xx,0,zz),(0,side,0)))
    if sid==3:
        sh = cut(sh,ax(1.59,130,(-14,0,0),(0,-1,0)))
    add(sg,"S%02d"%sid,"Samanhengande skjell",sh,"sheet",
        "Skjer nøytral DXF, konvals, jiggbor Ø6,38 frå kvar side. "
        "Brot alle kantar. Silkematt utside, lys diffusblåst innside. "
        "Kjeglestiging dr/dx = %.6f; nøytral radius ved hengsla %.3f." % (k,b))
    write_blank(i,b,k,rear,front)

    for drive in (False,True):
        side = 1 if drive else -1
        suf = "%d%s"%(sid,"R" if drive else "F")
        xx,zz = (DX,DZ) if drive else (0.,0.)
        gr,rz = (move,0.) if drive else (fixed,Z)
        ydist,ro = (YR,5.) if drive else (YF,4.5)
        ray = (0,side,0)
        mid = sqrt((b+k*xx)**2-zz**2)
        half = 3.35+4.7*abs(k)
        lo,hi = mid-half,mid+half
        def sleeve(r):
            return ring(r,2.055,hi-lo,(xx,side*lo,zz),ray)
        bush = join(sleeve(3.12),sleeve(4.9).cut(outer_clear),
                    sleeve(3.68).common(inner_clear))
        # Two spring fingers at insertion end; outer flange remains continuous.
        slit_a,slit_b = sorted((side*(lo-.1),side*(hi-.95)))
        bush = cut(bush,box(8.4,slit_b-slit_a,.85,(xx-4.2,slit_a,zz-.425)))
        add(sg,"B"+suf,"Eittstykkes salforing",bush,"pom",
            "Splitta innføringsende, to integrerte flensar med konisk anlegg. "
            "Boring Ø4,11. Knepp i avgrada hol; kan løysast frå innsida.")
        ext = not drive and sid in (3,4)
        def shaft(r,a,b_):
            return along(side,r,a,b_,xp,rz)
        shoulder = hi if ext else hi+.18
        pin = join(shaft(2,-22.5 if ext else lo-1.9,shoulder),
                   shaft(3.15,shoulder,ydist-ro),
                   shaft(2,ydist-ro,ydist+ro),
                   shaft(3.45,ydist+ro,ydist+ro+1))
        if not ext:
            pin = cut(pin,ring(2.15,1.55,.73,(xp,side*(lo-1.10),rz),ray))
        add(gr,"P"+suf,"Beretapp" if ext else "Skuldertapp",pin,"al",
            "Drei Ø4 journal og Ø4 røyrende. Kaldstukket hovud, same legering "
            "som røyret, ikkje lim. "+("Gjennomgåande til tverrsadelen." if ext
            else "Spor for radiell låsering på innsida."))
        if ext:
            col = ring(4.9,2.025,3.65,(xp,side*(lo-4.45),rz),ray)
            yc = side*(lo-2.65)
            col = cut(col,ax(1.02,3.4,(xp,yc,rz+1.8)))
            add(gr,"K"+suf,"Justerkrage",col,"al",
                "M2 radielt. Juster aksialtrykk med kraftmålar på løftegrepet.")
            add(gr,"G"+suf,"Låseskrue M2",ax(1,2.75,(xp,yc,rz+2)),"steel",
                "Flat ende mot Ø4. Løys før justering.")
            disc = turn([(2.09,0),(4.43,.55),(4.43,.80),(2.09,.25)])
            disc.rotate(V(),V(1,0,0),90)
            disc.translate(V(xp,side*(lo-.80),rz))
            add(gr,"F"+suf,"Aksial friksjonsfjør",disc,"steel",
                "Fjørhard rustfri tallerkenskive, montert høgd 0,80. Vel fjørkurve "
                "etter målt losrivingsmoment; ikkje dimensjoner frå tettleik.")
        else:
            clip = ring(3.55,1.58,.62,(xp,side*(lo-1.055),rz),ray)
            clip = cut(clip,box(4.0,2.0,2.45,
                       (xp,min(side*(lo-1.055),side*(lo-.435))-.5,rz-1.225)))
            add(gr,"K"+suf,"Radiell låsering",clip,"steel",
                "Fjørande C-ring, nominell konvolutt i dreia spor. Løys med lita tang.")

    if sid==3:
        # The stop rivet also carries the moving magnet. No electrical
        # connection, harness or wiper crosses a moving joint.
        rr = b-14*k
        stem = along(-1,1.53,56.8,rr+1.9,-14,0)
        head = along(-1,2.65,rr-1.8,rr+1.9,-14,0).cut(outer_clear)
        back = along(-1,2.46,rr-1.75,rr+1.55,-14,0).common(inner_clear)
        peg = cut(join(stem,head,back),ax(1.025,2.24,(-14,-56.77,0),(0,-1,0)))
        add(sg,"206","Stopptapp med magnetsete",peg,"al",
            "Ø3,06 følgjetapp; stukne skuldrer rundt eige jiggbor i skjell 3.")
        add(sg,"207","Posisjonsmagnet",ax(1,2,(-14,-56.92,0),(0,-1,0)),"mag",
            "Press inn med mekanisk sikra leppe. Luftgap til fast Hall-kort.")

# A round-ended milled slot, cut with an actual annular sector (not a
# faceted slot). Centre of the follower describes exactly the slot median.
sx = ST[2]
RSTOP,WSTOP = 14.,1.58
slotsec = Part.Face(poly3([(sx-RSTOP-WSTOP,-65,Z),(sx-RSTOP+WSTOP,-65,Z),
                           (sx-RSTOP+WSTOP,-58,Z),(sx-RSTOP-WSTOP,-58,Z)]))
slot = slotsec.revolve(V(sx,0,Z),V(0,-1,0),N)
for a in (0,N):
    slot = join(slot,ax(WSTOP,7,(sx-RSTOP*cos(rad(a)),-65,Z-RSTOP*sin(rad(a))),
                        (0,1,0)))
plate = xz([(-61,Z-12),(-42,Z-12),(-34,Z-4),(41,Z-4),(44,Z-1),
            (44,Z+3),(42,Z+5),(-59,Z+5),(-61,Z+3)],-63.2,3.)
for x in (-58.,-45.):
    plate = join(plate,ax(2.0,4.50,(x,-60.3,Z-5),(0,1,0)))
    plate = cut(plate,ax(1.02,5.1,(x,-60.7,Z-5),(0,1,0)))
plate = cut(plate,slot)
for j,x in enumerate((-39,39),1):
    plate = cut(plate,ax(2.055,5,(x,-64,Z),(0,1,0)),
                ax(.82,4,(x,-61.7,Z+1.8)))
    add(fixed,"H4-%d"%j,"Stopplatelås",ax(.8,2.9,(x,-61.7,Z+2)),"steel",
        "M1,6 flat ende. Lås plata etter innstilling i monteringsjigg.")
add(fixed,"205","Stopplate og sensorfeste",plate,"al",
    "Fres 40 graders bogespor R14, Ø3,16 endar. To avstandsknastar for Hall-kortet.")
pcb = box(34,3.1,20,(-77,-55.8,Z-15))
for j,x in enumerate((-58.,-45.),1):
    pcb = cut(pcb,ax(1.08,4,(x,-56.0,Z-5),(0,1,0)))
    add(fixed,"H5-%d"%j,"Kortskrue M2",
        join(ax(1,6,(x,-52.7,Z-5),(0,-1,0)),
             ax(1.75,1.4,(x,-52.7,Z-5),(0,1,0))),"steel",
        "M2 × 6, inn i avstandsknasten.")
add(fixed,"E04","Vinkelgjevar og dimmetrinn",pcb,"hall",
    "Fast 3D Hall-gjevar ved midten av magnetbogen, kalibrer ved begge stoppa. "
    "24 V inn, tre analoge straumreturar til kassetten. Reservert kortvolum.",6.)

def write_json(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),
                    encoding="utf-8")

def setangle(a):
    controls.set("B1","%d deg"%a)
    doc.recompute()
    for g in [move]+shell_groups:
        if "Invalid" in g.State:
            raise RuntimeError("Expression error: "+g.Label)
    c,s = cos(rad(a)),sin(rad(a))
    if (move.Placement.Base-V(DX*c-DZ*s,0,Z+DX*s+DZ*c)).Length>1.e-6:
        raise RuntimeError("Drive placement not evaluated")
    for xp,g in zip(ST,shell_groups):
        if (g.Placement.multVec(V(1,0,0))-V(xp+c,0,Z+s)).Length>1.e-6:
            raise RuntimeError("Shell placement not evaluated: "+g.Label)

def globalshape(ob,gr):
    sh = ob.Shape.copy()
    sh.Placement = gr.Placement.multiply(sh.Placement)
    return sh

# Procurement allocations: cassette boards, inserts and Hall board ALREADY
# carry their allocated mass in the BOM. Do not add them again here.
PSU,LEADS,LOOM,RESERVE = 205.,52.,10.,35.
def dump(a):
    setangle(a)
    data = []
    low,high = [float("inf")]*3,[-float("inf")]*3
    moment,mass = V(),0.
    for ob,gr,mat in parts:
        sh = globalshape(ob,gr)
        vs,fs = sh.tessellate(.085)
        verts = [[round(v.x,4),round(v.y,4),round(v.z,4)] for v in vs]
        if mat!="cordref":
            for j,col in enumerate(zip(*verts)):
                low[j] = min(low[j],min(col))
                high[j] = max(high[j],max(col))
            moment = moment + sh.CenterOfMass*ob.Mass_g
            mass += ob.Mass_g
        data.append({"key":ob.Item,"label":ob.Label,"group":gr.Name,"mat":mat,
                     "v":verts,"f":fs})
    write_json(WORK/("mesh%d.json"%a),data)
    cm = moment*(1./mass)
    rho = math.hypot(cm.x,cm.y-CY)
    # Conservative support circle inside the actual annular contact.
    # Also check putting ALL onboard uncertainty at the worst upper corner.
    rw = max(math.hypot(x,y-CY) for x in (low[0],high[0]) for y in (low[1],high[1]))
    extra = LOOM+RESERVE
    run = (rho*mass+rw*extra)/(mass+extra)
    h = (cm.z*mass+high[2]*extra)/(mass+extra)
    stability = {"cad_mass_g":mass,"com_mm":[cm.x,cm.y,cm.z],
                 "support_radius_used_mm":72.0,"foot_centre_xy":[0.,CY],
                 "tilt_deg":10,"nominal_margin_mm":72.-rho-cm.z*math.tan(rad(10)),
                 "adverse_margin_mm":72.-run-h*math.tan(rad(10)),
                 "nominal_tip_deg":math.degrees(math.atan2(72.-rho,cm.z)),
                 "min_mm":low,"max_mm":high}
    return [round(b-a_,4) for a_,b in zip(low,high)],stability

bounds,stat = {},{}
for angle in (N,0):
    bounds[angle],stat[angle] = dump(angle)
write_json(WORK/"bounds.json",bounds)
write_json(WORK/"stability.json",stat)

# The common oblique cut gives a useful analytic check independent of
# tessellation: in the rotating frame adjacent seam slabs separate by
# GAP + P*(cos(a)+BIAS*sin(a)-1). This concerns skins, NOT the hardware.
def torque(a):
    c,s = cos(rad(a)),sin(rad(a))
    gm = 0.
    for ob,g,m in parts:
        if g in shell_groups:
            p = ob.Shape.CenterOfMass
            gm += ob.Mass_g*(c*p.x-s*p.z)
        elif g==move:
            gm += ob.Mass_g*(c*DX-s*DZ)
    return gm*9.80665e-6

write_json(WORK/"mechanism.json",[
    {"angle_deg":a,"skin_slab_gap_x_mm":GAP+P*(cos(rad(a))+BIAS*sin(rad(a))-1),
     "gravity_torque_to_overcome_Nm":torque(a),
     "drive_rise_mm":DX*sin(rad(a))+DZ*(cos(rad(a))-1)} for a in range(0,N+1,5)])

# Optional slow BRep audit. A loose OCC box is suitable for REJECTING
# pairs here, but is never used to measure the envelope of the lamp.
if os.environ.get("FURU_CHECK","0")=="1":
    hits = []
    for a in range(0,N+1,5):
        setangle(a)
        shapes = [(ob.Item,g,globalshape(ob,g)) for ob,g,m in parts]
        for n,(k,g,sh) in enumerate(shapes):
            for k2,g2,sh2 in shapes[n+1:]:
                if g==g2 or (g in (base,fixed) and g2 in (base,fixed)):
                    continue
                if sh.BoundBox.intersect(sh2.BoundBox):
                    vol = sum(abs(so.Volume) for so in sh.common(sh2).Solids)
                    if vol>1.e-4:
                        hits.append([a,k,k2,vol])
    write_json(WORK/"crossings.json",hits)
    print("Positive-volume moving pairs:",len(hits),flush=True)
    setangle(0)

rows = []
for o,g,m in parts:
    rows.append({"ID":o.Item,"Del":o.Label[len(o.Item)+1:],"Gruppe":g.Label,
                 "Materiale":o.MaterialSpec,"Volum_mm3":round(o.Shape.Volume,3),
                 "Tettleik_g_cm3":round(o.Density_g_cm3,6) if o.Density_g_cm3 else "",
                 "Masse_g":o.Mass_g if o.Density_g_cm3 else "","Prosess":o.Process})
with (OUT/"Stykkliste.csv").open("w",encoding="utf-8-sig",newline="") as f:
    w = csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=";")
    w.writeheader()
    w.writerows(rows)
write_json(WORK/"parts.json",rows)

# Explicit optical hypothesis for procurement, NOT a measured IES file.
# For a point on the luminous line: px=(x-xLED)/h, py=(yLED-y)/h.
# A rectangular asymmetric fan with equal flux per dpx*dpy has a uniform
# patch on the desk. Integrate the overlapping patches along the finite
# line analytically, rather than assuming a uniform rectangle for the lamp.
LED_W,EFFICACY,TASK,T_OPT,FAN = 6.10,112.,.80,.75,.45
raw = LED_W*EFFICACY
exit_task = raw*TASK*T_OPT
h = ZA/1000.
sxmax,sy0,sy1 = 2.40,.32,3.42
lboard = .328
def lux(x,y):
    sy = (-.031-y)/h
    if not sy0<=sy<=sy1:
        return 0.
    left = max(-lboard/2,x-h*sxmax)
    right = min(lboard/2,x+h*sxmax)
    return (max(0.,right-left)/lboard*FAN*exit_task/
            (2*sxmax*(sy1-sy0)*h*h))
grid = [{"x_mm":x,"y_mm":y,"lx":round(lux(x/1000.,y/1000.),1)}
        for y in range(-500,-99,50) for x in range(-300,301,50)]
emin = min(d["lx"] for d in grid)
eavg = sum(lux(-.3+(i+.5)*.6/600.,-.300) for i in range(600))/600.
draw = (LED_W/.94+.14)/.90
photo = {
    "status":"Optisk innkjøpsmål / førehandsestimat, ikkje måledata",
    "height_mm":ZA,"field_xy_mm":[[-300,-500],[300,-100]],"pitch_mm":50,
    "led_w":LED_W,"raw_work_lm":raw,"exit_task_lm":exit_task,
    "assumed_room_wash_lm":raw*(1-TASK)*.58,"estimated_input_w":draw,
    "task_transmission_including_lip":T_OPT,"fraction_in_specified_fan":FAN,
    "fan_slope_intervals":[[-sxmax,sxmax],[sy0,sy1]],
    "fan_flux_density":"constant per unit slope product, NOT per steradian",
    "field_avg_lx":eavg,"grid_min_lx":emin,"grid":grid,
    "render":{
        "positive_y":"bakside","E01":{"face":"-Z","behind":"107"},
        "E02":{"face":"+Y","behind":"108"},
        "closed":"Berre E02, 2 % av full systemeffekt, 2000 K",
        "open":"E01:E02 = 80:20, 2700 K. Ikkje gjer heile konvoluttane sjølvlysande."
    }}
write_json(OUT/"Lysmaal.json",photo)

onboard = sum(o.Mass_g for o,g,m in parts)
total = onboard+PSU+LEADS+LOOM+RESERVE
write_json(WORK/"budget.json",{
    "model_including_purchased_envelopes_g":onboard,"external_supply_g":PSU,
    "external_lead_and_primary_switch_g":LEADS,"internal_loom_g":LOOM,
    "reserve_g":RESERVE,"total_g":total,"bom_items":len(parts),"main_assemblies":10})

(OUT/"Modulgrensesnitt.md").write_text(
"""# FURU B02 · servicegrense L24-4

Framover er −Y. Ikkje opne nettdelen. Slå av på primærbrytaren og trekk ut
SELV-leidninga. Legg lampa på eit mjukt underlag. Hald om lyskjølen, ikkje
om optikken. Løys dei to H3 med 2 mm sekskant og senk heile kjølen rett ned
minst 8 mm. J01 går då fri av J02. Før ut kassetten framover under skala.
Set inn i motsett rekkjefølgje. Ingen skjell, aksling eller fot skal av.
Prøv full rørsle og begge lysvegane. Mål tidsbruk med ein førstegongsbrukar.

* Mekanisk null: midt mellom H3 på anleggsplanet, (0, −4,5, 153) i CAD.
  To M3, 26 mm deling i X, Ø3,34 i laus flens, 1,8 mm flenstjukkleik.
  Serviceskrue M3 × 7. Tørr metallkontakt mot sete. Kjøl 352 mm utan endelås.
  Pila på kassetten skal peike mot arbeidsfeltet.
* J01/J02: polarisert firepol, blindparande i Z; kontaktklasse minst
  30 V DC og 0,5 A/pol. Pinnar i aukande X: 1 felles +24 V, 2 retur
  arbeidskort 2700 K, 3 retur vask 2700 K, 4 retur vask 2000 K.
  Berre spenningslaus service. Kontaktserie, toleranse for blindparing og
  endeleg pinneteikning skal frysast etter prøve med leverandør.
* 24 V SELV, regulert forsyning med kortslutningsvern. Tilpassa kort for
  straumsøkkje; sams driftstak 6,10 W / om lag 254 mA ved 24 V. Ikkje
  nettdelar i sokkelen. Full lysstyrke er uavhengig av batteri.
* Kalibrer Hall-signalet med begge mekaniske endestopp. Normaliser vinkel
  til t = vinkel/40, avgrensa til [0,1]. u = t²(3−2t).
  Samla relativ effekt = 0,02 + 0,98u. Av denne går 0,80u til arbeidskortet.
  Av resten skal delen u gå til kjølegare vaskekanal og 1−u til varmare.
  Kalibrer straum mot bin og lysfluks. Ingen modusknapp eller tidssekvens.
  Straumregulering utan lågfrekvent pulsdrift; mål PstLM/SVM og kamerabanding
  også ved minste pådrag. 8 timar varmgang med temperaturmåling på grep,
  lyskort og kjøl. Ved feil i vinkelgjevar: avgrens til lågt pådrag.
* Løys endekrokane for å skyve ut kort og optikk kvar for seg. Inga tape
  eller lim mellom metall, plast og kort. Elektronikk er ei eiga avfallsfraksjon.
  Reservedelsmål: kassett, foringar, såle og grep i 10 år; ikkje eit
  leverandørløfte. Ingen batteripakke i denne revisjonen.
""",encoding="utf-8")

def fmt_dims(v):
    return " × ".join("%.1f"%a for a in v)
(OUT/"Endringar-B02.md").write_text(
    "# Endringar B01 → B02\n\n"
    "- E1/E3: lukka %s mm; open %s mm. Nettmål utan lausleidning.\n"
    "- F2/F3/B3: %.2f W til korta, %.0f lm råfluks; estimert %.2f W på nett. "
    "Optikkmålet gjev %.0f lx i middel og %.0f lx som lågaste rutenettpunkt "
    "ved %.0f mm høgd; ikkje verifisert fotometri.\n"
    "- F8: %.1f g i CAD inkl. budsjetterte konvoluttar; %.1f g komplett "
    "med nettdel, leidningar og reserve.\n"
    "- T2/F9: open massesentrumsposisjon (%.1f, %.1f, %.1f) mm. "
    "Minste nominelle margin på 10° plan %.1f mm, med ugunstig reserve %.1f mm. "
    "Fotavtrykk %.1f cm². Ikkje medrekna drag i leidninga.\n"
    "- B1/B2/T6: %d BOM-posisjonar; 10 hovudeiningar "
    "(6 skjell, 2 røyr, sokkeleining, lyskassett). Sjå Modulgrensesnitt.md.\n" %
    (fmt_dims(bounds[0]),fmt_dims(bounds[N]),LED_W,raw,draw,eavg,emin,ZA,
     onboard,total,*stat[N]["com_mm"],stat[N]["nominal_margin_mm"],
     stat[N]["adverse_margin_mm"],pi*76.8**2/100,len(parts)),encoding="utf-8")

# STEPCAF (Import), assembly at zero, not a flattened Part.export compound.
doc.recompute()
doc.saveAs(str(OUT/"Furu-B02.FCStd"))
step_prefs = A.ParamGet("User parameter:BaseApp/Preferences/Mod/Part/STEP")
step_prefs.SetString("Scheme","AP214IS")
step_prefs.SetString("Unit","MM")
import_prefs = A.ParamGet("User parameter:BaseApp/Preferences/Mod/Import")
import_prefs.SetBool("ExportLegacy",False)
stepfile = OUT/"Furu-B02.step"
Import.export([root],str(stepfile))
with stepfile.open("rb") as f:
    header = f.read(8192).upper()
if b"AUTOMOTIVE_DESIGN" not in header:
    raise RuntimeError("Expected AP214 STEP schema; inspect FILE_SCHEMA in "+str(stepfile))
print("FURU B02 |",len(parts),"items | bounds",bounds,"| budget %.1f g"%total,
      "| open 10-deg margin %.1f mm"%stat[N]["adverse_margin_mm"],flush=True)
