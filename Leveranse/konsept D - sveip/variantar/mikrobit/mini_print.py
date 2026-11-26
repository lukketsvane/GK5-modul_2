# -*- coding: utf-8 -*-
"""mini_print.py: printdelar for Sveip mini (84 x 84 x 29,4 mm) med micro:bit V2, for Bambu Lab P1S.

Delar (PLA, 0,4 mm dyse)
  M1 kropp      L-forma skal med 1,2 mm vegg. Stamma og skjermen er opne oppe og nede som i rev. B,
                men endeplata på stamma (med hol for USB) og botnen under utkraginga er med. Framme
                er eit forsenka felt med 25 hol for LED-ane og hol for messingskruen.
  M2 chassis    golv i stamma og ein stolpe bak kortet. Lysrista, kortet og stolpen blir skrudde
                saman med fem M3 x 8 senkskruar gjennom ringane på kortet.
  M3 lysrist    D15 (sjå d15_lysrist.py), svart.
  M4 lysplate   kvit plate inni skjermen, på same høgd som D08 i rev. B. Kviler på stolpen og to bein.
Plater
  A  lampefarge, PLA Matte: M1 og M4, begge opp ned. Ingen støtte.
  B  svart PLA Matte: M2 ståande og M3 med kortsida ned. Ingen støtte.
  Alle fire delane ligg òg saman på éi plate i Sveip_mini_alle_delar.3mf.
Køyr frå mikrobit/:
  python mini_print.py           byggjer delane, kontrollerer passform og print, og skriv print/
  python mini_print.py --slice   slicar òg plate A og B med Bambu Studio (som sveip_print.py i rev. B)
"""
import json
import math
import sys
import zipfile
from pathlib import Path

import cadquery as cq
import numpy as np
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

import d15_lysrist as L15
from mini_passform import AVST, D, K, MB, S, X_ST, Z_SK, kortdelar, stadion, til_lampa

HER = Path(__file__).resolve().parent
UT = HER / "print"

T = 1.2                     # vegg i print (aluminium: 1,0)
R_INN = 12.0 * K            # hjørnet mellom stamma og skjermen: 3,36
FELT_DJUPN = 0.3            # forsenka felt (0,12 i aluminium, 0,3 så det syner i print)
HOL_LED = 2.0
HOL_SKRUE = 3.2             # M3-messingskruen
USB_HOL = (13.0, 9.0)       # hol i endeplata for det støypte hovudet på micro-USB-pluggen: høgd (z), breidd (y)
KL = 0.2                    # klaring mellom chassis og kropp
GOLV = 2.0
Z_PLATE = Z_SK + 0.36 * (S - Z_SK)   # lysplata: same høve i skjermen som D08 i rev. B (60,3)
T_PLATE = 1.2
YK = -D / 2 + T + AVST      # framsida av kretskortet: -8,4
MX, MZ = MB
LOGO = (MX + L15.LOGO[1], MZ - L15.LOGO[0])
STOLPE_X = (MX - 19.5, MX - 8.0)     # bak kantkontakten, der baksida av kortet er fri
STOLPE_Y = (YK + 1.6, YK + 1.6 + 6.0)
SKRUE = dict(hovud=(5.6, 2.4), lengd=4.0)   # M3 x 4 messing, linsehovud (DIN 7985)
LED_TOPP = 0.4                       # LED-en er 0,4 høg etter databladet


def boks(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def tomrom(vekst=0.0):
    """Utskjeringa under skjermen (x > X_ST, z < Z_SK) med avrunda hjørne, vaksen vekst mm inn i lampa."""
    r = R_INN + vekst
    cx, cz = X_ST + R_INN, Z_SK - R_INN
    midt = (cx - r * math.sqrt(0.5), cz + r * math.sqrt(0.5))
    return (cq.Workplane("XZ").moveTo(X_ST - vekst, -10).lineTo(S + 10, -10).lineTo(S + 10, Z_SK + vekst)
            .lineTo(cx, Z_SK + vekst).threePointArc(midt, (X_ST - vekst, cz)).close()
            .extrude(D + 10, both=True))


def led_lampa():
    """Sentera til dei 25 LED-ane i lampa (x, z)."""
    return [(MX + v, MZ - u) for u, v in L15.LED]


def fram(y_inne):
    """Arbeidsplan i x-z som skjer framover (mot -y) frå y_inne."""
    return cq.Workplane("XZ", origin=(0, y_inne, 0))


# ---------------------------------------------------------------- delane i lampa


def kropp():
    ytre = stadion(S, D, 0, S).cut(tomrom())
    indre = stadion(S - 2 * T, D - 2 * T, -1, S + 1, x0=T).cut(tomrom(T))
    k = ytre.cut(indre)
    # forsenka felt framme: rundt matrisa og messingskruen, følgjer flata òg der ho krummar
    fx0, fz0, fx1, fz1 = MX - 11.5, MZ - 11.5, LOGO[0] + 6.5, MZ + 11.5
    felt = (cq.Workplane("XY").box(fx1 - fx0, D / 2 + 1, fz1 - fz0).edges("|Y").fillet(3.5)
            .translate(((fx0 + fx1) / 2, -(D / 2 + 1) / 2, (fz0 + fz1) / 2)))
    hud = stadion(S, D, -1, S + 1).cut(stadion(S - 2 * FELT_DJUPN, D - 2 * FELT_DJUPN, -2, S + 2, x0=FELT_DJUPN))
    k = k.cut(felt.intersect(hud))
    k = k.cut(fram(-D / 2 + T + 0.5).pushPoints(led_lampa()).circle(HOL_LED / 2).extrude(T + 1.5))
    k = k.cut(fram(-D / 2 + T + 0.5).center(*LOGO).circle(HOL_SKRUE / 2).extrude(T + 1.5))
    # hol for micro-USB i endeplata, midt for kontakten på baksida av kortet
    yu, zu = YK + 1.6 + 1.2, MZ - 0.13
    hol = boks(-(T + 2) / 2, (T + 2) / 2, -USB_HOL[1] / 2, USB_HOL[1] / 2, -USB_HOL[0] / 2, USB_HOL[0] / 2)
    k = k.cut(hol.edges("|X").fillet(1.5).translate((X_ST - T / 2, yu, zu)))
    return k


def chassis():
    golv = stadion(S - 2 * (T + KL), D - 2 * (T + KL), 0, GOLV, x0=T + KL)
    golv = golv.intersect(boks(-1, X_ST - T - KL, -D, D, -1, GOLV + 1))
    (sx0, sx1), (sy0, sy1) = STOLPE_X, STOLPE_Y
    c = golv.union(boks(sx0, sx1, sy0, sy1, GOLV - 0.5, Z_PLATE))
    avstivar = (cq.Workplane("YZ", origin=(sx0 + 3.0, 0, 0))
                .polyline([(sy1 - 0.5, GOLV - 0.5), (sy1 + 5.0, GOLV - 0.5), (sy1 - 0.5, GOLV + 5.0)]).close()
                .extrude(sx1 - sx0 - 6.0))
    c = c.union(avstivar)
    # styrehol for M3 (sjølvgjengande) i stolpen, der ringane på kortet er
    ringar = [(MX + L15.RING_V, MZ - u) for u in L15.RINGAR]
    return c.cut(cq.Workplane("XZ", origin=(0, sy1 + 0.5, 0)).pushPoints(ringar).circle(1.3).extrude(sy1 - sy0 + 1.0))


def lysplate():
    p = stadion(S - 2 * (T + 0.3), D - 2 * (T + 0.3), Z_PLATE, Z_PLATE + T_PLATE, x0=T + 0.3)
    bein = (cq.Workplane("XY", origin=(0, 0, Z_SK + T)).pushPoints([(66.0, 7.0), (66.0, -7.0)])
            .circle(2.0).extrude(Z_PLATE - (Z_SK + T) + 0.1))
    return p.union(bein)


def messingskrue():
    yf = -D / 2 + FELT_DJUPN                     # framflata i feltet
    d, h = SKRUE["hovud"]
    hovud = cq.Workplane("XZ", origin=(0, yf, 0)).center(*LOGO).circle(d / 2).extrude(h)
    skaft = cq.Workplane("XZ", origin=(0, yf, 0)).center(*LOGO).circle(1.5).extrude(-SKRUE["lengd"])
    return hovud, skaft


def fjor():
    tupp = -D / 2 + FELT_DJUPN + SKRUE["lengd"]
    return cq.Workplane("XZ", origin=(0, YK, 0)).center(*LOGO).circle(1.75).circle(1.35).extrude(YK - tupp)


def lysleiarar():
    y0, y1 = YK - L15.T, YK - LED_TOPP
    return fram(y1).pushPoints(led_lampa()).circle(1.75 / 2).extrude(y1 - y0)


def usb_plugg():
    """micro-USB-pluggen i kontakten: metallet 6,85 x 1,8 inn 5,0, støypt hovud 10,6 x 7,0 x 15."""
    xk = MX + 22.0 + 1.4                          # opninga på kontakten
    yu, zu = YK + 1.6 + 1.2, MZ - 0.13
    metall = boks(xk - 5.0, xk + 1.0, yu - 0.9, yu + 0.9, zu - 3.425, zu + 3.425)
    hovud = boks(xk + 1.0, xk + 16.0, yu - 3.5, yu + 3.5, zu - 5.3, zu + 5.3).edges("|X").fillet(1.0)
    return metall, hovud


# ---------------------------------------------------------------- kontroll


def avstand(a, b):
    d = BRepExtrema_DistShapeShape(a.val().wrapped, b.val().wrapped)
    d.Perform()
    return d.Value()


def snitt(a, b):
    try:
        return a.intersect(b).val().Volume()
    except Exception:
        return 0.0


def kontroll_passform(m1, m2, m4):
    kort = kortdelar(YK)
    m3 = kort["lysrist D15"]
    elektronikk = {k: v for k, v in kort.items() if k != "lysrist D15"}
    hovud, skaft = messingskrue()
    metall, plugg = usb_plugg()
    leiar = lysleiarar()
    funn, ok = [], True

    def krav(tekst, verdi, grense, eining="mm"):
        nonlocal ok
        bra = verdi >= grense - 1e-6
        ok &= bra
        funn.append(dict(kontroll=tekst, verdi=round(verdi, 3), krav=f">= {grense} {eining}", ok=bra))

    def ingen(tekst, vol):
        nonlocal ok
        bra = vol < 1e-3
        ok &= bra
        funn.append(dict(kontroll=tekst, verdi=round(vol, 4), krav="0 mm3", ok=bra))

    for n, d in elektronikk.items():
        krav(f"kropp til {n}", avstand(m1, d), 0.3)
    krav("kropp til lysrista D15", avstand(m1, m3), 0.1)
    krav("kropp til chassis", avstand(m1, m2), KL - 0.01)
    krav("kropp til lysleiarane", avstand(m1, leiar), 0.3)
    for n, d in elektronikk.items():
        ingen(f"chassis i {n}", snitt(m2, d))
        ingen(f"lysrista i {n}", snitt(m3, d))
        ingen(f"lysplata i {n}", snitt(m4, d))
    ingen("chassis i lysrista", snitt(m2, m3))
    ingen("lysplata i kropp", snitt(m4, m1))
    ingen("lysplata i chassis", snitt(m4, m2))
    ingen("lysleiarane i lysrista", snitt(leiar, m3))
    ingen("messingskruen gjennom kroppen", snitt(skaft, m1) + snitt(hovud, m1))
    krav("tuppen på messingskruen til kretskortet", avstand(skaft, elektronikk["kretskort"]), 1.5)
    # lina gjennom kvart LED-hol og kvar kanal skal vere fri: rista og hola står på same akse
    sikt = fram(YK - LED_TOPP).pushPoints(led_lampa()).circle(0.5).extrude(D / 2)
    ingen("siktlina gjennom LED-hol og kanalar", snitt(sikt, m1) + snitt(sikt, m3))
    ingen("USB-pluggen i kroppen", snitt(plugg, m1) + snitt(metall, m1))
    krav("USB-pluggen til kroppen", avstand(plugg, m1), 0.3)
    # innsetjing: chassis med kort og rist går opp i stamma nedanfrå, lysplata ned i skjermen ovanfrå
    pakke = m2.union(m3).union(leiar)
    for d in elektronikk.values():
        pakke = pakke.union(d)
    verste = max(snitt(pakke.translate((0, 0, -dz)), m1) for dz in (2, 5, 10, 20, 30, 40, 50, 63))
    ingen("chassis med kort på veg opp i stamma", verste)
    ingen("lysplata på veg ned i skjermen", max(snitt(m4.translate((0, 0, dz)), m1) for dz in (5, 10, 20, 30)))
    return ok, funn


# ---------------------------------------------------------------- print


def opp_ned(f):
    return f.rotate((0, 0, 0), (1, 0, 0), 180)


def til_plata(f, cx, cy):
    bb = f.val().BoundingBox()
    return f.translate((cx - (bb.xmin + bb.xmax) / 2, cy - (bb.ymin + bb.ymax) / 2, -bb.zmin))


def nett(f, tol=0.02):
    v, t = f.val().tessellate(tol, 0.1)
    v = np.array([(p.x, p.y, p.z) for p in v])
    t = np.array(t, dtype=np.int64)
    nokkel = np.round(v, 5)
    _, inv = np.unique(nokkel, axis=0, return_inverse=True)
    inv = inv.ravel()
    ny, idx = np.unique(inv, return_index=True)
    return v[idx], inv[t]


def kontroll_nett(v, t):
    """Lukka og manifold: kvar kant i nøyaktig to trekantar, i motsett retning. Volum med forteikn."""
    kantar = np.concatenate([t[:, [0, 1]], t[:, [1, 2]], t[:, [2, 0]]])
    rett = {tuple(k) for k in kantar}
    lukka = len(rett) == len(kantar) and all((b, a) in rett for a, b in rett)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    vol = float(np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6.0)
    return lukka, vol


def overheng(v, t, plate=0.3):
    """Flater som vender nedover meir enn 45° og ikkje ligg på plata, med areal og høgd."""
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    n = np.cross(b - a, c - a)
    ar = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(2 * ar, 1e-12)
    zmin = np.minimum(np.minimum(a[:, 2], b[:, 2]), c[:, 2])
    m = (nz < -math.sqrt(0.5)) & (zmin > plate)
    if not m.any():
        return []
    grupper = {}
    for z, ar_, p in zip(np.round(zmin[m], 1), ar[m], ((a[m] + b[m] + c[m]) / 3)):
        g = grupper.setdefault(float(z), dict(areal=0.0, x=[], y=[]))
        g["areal"] += float(ar_)
        g["x"].append(p[0]); g["y"].append(p[1])
    ut = []
    for z, g in sorted(grupper.items()):
        if g["areal"] < 2.0:
            continue
        ut.append(dict(z=z, areal_mm2=round(g["areal"], 1),
                       x=[round(min(g["x"]), 1), round(max(g["x"]), 1)], y=[round(min(g["y"]), 1), round(max(g["y"]), 1)]))
    return ut


FARGAR = {"lampefarge": "#C9C7C1FF", "svart": "#1E1E1EFF"}


def skriv_3mf(sti, objekt, tittel, fargar=None):
    """Enkel 3MF (kjernespesifikasjonen) med eitt objekt per del, plassert på plata. fargar er
    ei liste med fargenamn (sjå FARGAR), éin per del, som visingsfarge."""
    res, bygg = [], []
    if fargar:
        namn_ = list(FARGAR)
        res.append('<basematerials id="900">' + "".join(
            f'<base name="{n}" displaycolor="{FARGAR[n]}"/>' for n in namn_) + "</basematerials>")
    for i, (namn, (v, t)) in enumerate(objekt, start=1):
        vs = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in v)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in t)
        farge = f' pid="900" pindex="{list(FARGAR).index(fargar[i - 1])}"' if fargar else ""
        res.append(f'<object id="{i}" name="{namn}" type="model"{farge}><mesh><vertices>{vs}</vertices>'
                   f'<triangles>{ts}</triangles></mesh></object>')
        bygg.append(f'<item objectid="{i}"/>')
    modell = ('<?xml version="1.0" encoding="UTF-8"?>\n'
              '<model unit="millimeter" xml:lang="nn-NO" '
              'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
              f'<metadata name="Title">{tittel}</metadata><resources>{"".join(res)}</resources>'
              f'<build>{"".join(bygg)}</build></model>')
    typar = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
            'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(sti, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", typar)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", modell)


PLATER = {
    "A": dict(namn="Sveip_mini_A_kropp_PLA", filament="Bambu PLA Matte @BBL P1S 0.4 nozzle",
              farge="lampefarge (grå eller kvit)", vegg=1.2, brim=5),
    "B": dict(namn="Sveip_mini_B_innmat_PLA_svart", filament="Bambu PLA Matte @BBL P1S 0.4 nozzle",
              farge="svart", vegg=1.2, brim=3),
}


def alle_paa_ei_plate(m1, m2, m3_lokal, m4):
    """Alle fire delane på éi plate (256 x 256), med farge: M3 svart, resten i lampefarge."""
    return [("M1_kropp", til_plata(opp_ned(m1), 128.0, 80.0), "lampefarge"),
            ("M4_lysplate", til_plata(opp_ned(m4), 128.0, 140.0), "lampefarge"),
            ("M2_chassis", til_plata(m2, 75.0, 195.0), "lampefarge"),
            ("M3_lysrist_D15", til_plata(m3_lokal, 175.0, 195.0), "svart")]


def plater(m1, m2, m3_lokal, m4):
    return {
        "A": [("M1_kropp", til_plata(opp_ned(m1), 128.0, 95.0)),
              ("M4_lysplate", til_plata(opp_ned(m4), 128.0, 170.0))],
        "B": [("M2_chassis", til_plata(m2, 90.0, 128.0)),
              ("M3_lysrist_D15", til_plata(m3_lokal, 175.0, 128.0))],
    }


def main(slice_=False):
    UT.mkdir(exist_ok=True)
    m1, m2, m4 = kropp(), chassis(), lysplate()
    ok, funn = kontroll_passform(m1, m2, m4)
    for f in funn:
        print(f"  {'OK ' if f['ok'] else 'FEIL'} {f['kontroll']}: {f['verdi']} (krav {f['krav']})")
    assert ok, "passforma held ikkje"
    rapport = dict(lampe="Sveip mini 84 x 84 x 29,4 mm", skrivar="Bambu Lab P1S 0.4 nozzle",
                   prosess="0.20mm Standard @BBL X1C", passform=funn, plater=[])
    for p, delar in plater(m1, m2, L15.lysrist(), m4).items():
        info = PLATER[p]
        objekt, deler = [], []
        for namn, f in delar:
            bb = f.val().BoundingBox()
            assert 0 <= bb.xmin and bb.xmax <= 256 and 0 <= bb.ymin and bb.ymax <= 256 and bb.zmax <= 250, namn
            v, t = nett(f)
            lukka, vol = kontroll_nett(v, t)
            assert lukka, f"{namn}: nettet er ikkje lukka"
            assert abs(vol - f.val().Volume()) < 0.01 * f.val().Volume(), f"{namn}: volumet stemmer ikkje"
            cq.exporters.export(f, str(UT / f"Sveip_mini_{namn}.stl"), tolerance=0.02, angularTolerance=0.1)
            objekt.append((namn, (v, t)))
            oh = overheng(v, t)
            deler.append(dict(del_=namn, mal_mm=[round(bb.xlen, 1), round(bb.ylen, 1), round(bb.zlen, 1)],
                              volum_cm3=round(vol / 1000, 2), masse_g_pla=round(vol / 1000 * 1.24, 1),
                              lukka_nett=lukka, overheng=oh))
            print(f"  {namn}: {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm, {vol / 1000:.2f} cm3, "
                  f"om lag {vol / 1000 * 1.24:.0f} g PLA (massivt), lukka nett, {len(oh)} overhengsone(r)")
            for o in oh:
                print(f"      overheng i z {o['z']}: {o['areal_mm2']} mm2, x {o['x']}, y {o['y']}")
        skriv_3mf(UT / f"{info['namn']}.3mf", objekt, info["namn"])
        rapport["plater"].append(dict(plate=info["namn"], filament=info["filament"], farge=info["farge"],
                                      brim_mm=info["brim"], stotte=False, delar=deler))
    # alle delane i éi fil, på éi plate
    alle = alle_paa_ei_plate(m1, m2, L15.lysrist(), m4)
    boksar = []
    for namn, f, _ in alle:
        bb = f.val().BoundingBox()
        assert 0 <= bb.xmin and bb.xmax <= 256 and 0 <= bb.ymin and bb.ymax <= 256 and bb.zmax <= 250, namn
        assert not (bb.xmin < 18 and bb.ymin < 28), f"{namn} ligg i sperresona framme til venstre"
        boksar.append((namn, bb))
    for i, (na, a) in enumerate(boksar):           # minst 8 mm mellom delane, så brim og dyse går klar
        for nb, b in boksar[i + 1:]:
            gap = max(b.xmin - a.xmax, a.xmin - b.xmax, b.ymin - a.ymax, a.ymin - b.ymax)
            assert gap >= 8.0, f"{na} og {nb} står for tett ({gap:.1f} mm)"
    skriv_3mf(UT / "Sveip_mini_alle_delar.3mf", [(n, nett(f)) for n, f, _ in alle], "Sveip mini, alle delar",
              fargar=[fa for _, _, fa in alle])
    rapport["alle_delar"] = dict(fil="Sveip_mini_alle_delar.3mf", delar={n: fa for n, _, fa in alle})
    if slice_:
        sys.path.insert(0, str(HER.parent.parent / "cad"))
        import sveip_print as SP          # Bambu Studio CLI, same oppsett som rev. B
        SP.PRINT = UT
        for p, delar in plater(m1, m2, L15.lysrist(), m4).items():
            info = PLATER[p]
            r = SP.slice_plate(info["namn"], [(f"Sveip_mini_{n}", f.val()) for n, f in delar],
                               dict(filament=info["filament"], vegg=info["vegg"], ams=info["farge"],
                                    brim=info["brim"], stotte=False))
            print(json.dumps(r, ensure_ascii=False))
            rapport.setdefault("slicing", []).append(r)
    (UT / "print_rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
    print("SKREIV", UT)


if __name__ == "__main__":
    main(slice_="--slice" in sys.argv)
