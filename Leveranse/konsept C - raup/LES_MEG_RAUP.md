# RAUP · Produksjons- og Salgsklar CAD-samanstilling (1:1 mm · H = 200,0 mm)

Parametrisk Class-A B-rep (NURBS grad ≤ 3) i kompakt **1:1-skala** med **200,0 mm** total lampehøgd (bordplate → topp av diffusor), med **komplett mekanisk innfesting av alle 8 komponentar**, **0 kollisjonar** (`0,0000 mm³` overlapp på alle 28 par) og ferdig **innkjøps- og monteringsplan**.

---

## 1. Innkjøpsplan, Stykkliste (BOM) og Monteringsmanual
- **[`INNKJOPSPLAN_OG_MONTERING.md`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/INNKJOPSPLAN_OG_MONTERING.md)** — Komplett innkjøpsguide med eksakte delenummer, norske/europeiske leverandørar (DigiKey.no, Mouser.no, Elfa Distrelec, Kjell & Co, Polyalkemi.no, Xometry.eu), stykkprisar (**476 kr** for 1-stk prototyp / **335 kr** per lampe ved 50 stk) og steg-for-steg montering.
- **[`kontroll/raup_innkjopsliste.csv`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/kontroll/raup_innkjopsliste.csv)** — Strukturert innkjøps-CSV med leverandørar, delenummer og prisar.
- **[`kontroll/raup_BOM.csv`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/kontroll/raup_BOM.csv)** — CAD-volum og massebudsjett (papirmasse vs. PLA-prototyp).

---

## 2. Ferdig-slica Bambu Lab P1S 3MF-filer (1:1 mm)
1. **[`print/RAUP_P1S_H200_2.5mm_fuzzy.3mf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/print/RAUP_P1S_H200_2.5mm_fuzzy.3mf)** — **Plate 1: Hovudskal (`143,44 × 126,60 × 145,72 mm`, `2,5 mm` vegg, open botn)**
   - C2-subdividert nett (`995 886` trekantar, 0 fasettar ved innsprangshjørnet) med **skarp horisontal debossed skuggelinje** (`z = 37,78..39,23 mm`) som tonar mjukt ut rundt front-spiralsøyla, og **ekte 3D taktil mikro-overflatestruktur (`±0,095 mm`)** + Bambu Studio **Fuzzy Skin (`external` / Contour)**.
   - Ferdig-slica (`0,16 mm` laghøgd, `6` veggløkker, `0 %` fylling, `tree(auto)` støtte under det bakre `37,78 mm` innspranget, `220,5 g`, `7 t 58 min`).
2. **[`print/RAUP_P1S_H200_chassis_og_klips.3mf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/print/RAUP_P1S_H200_chassis_og_klips.3mf)** — **Plate 2: Mekanisk botnchassis (`02`)**
   - Ferdig-slica utan fuzzy skin for eksakte mekaniske pasningar (`1,40 mm` diffusorspor, 18650-batterivugge, PCB-piedestall, vertikal LED-sokkel, 3× forsenka M3-hol og 4× `Ø10,4 × 0,6 mm` lommer for 3M Bumpon SJ5312 føter).

---

## 3. Komplett Produksjons-Samanstilling ([`cad/raup_assembly.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_assembly.step), 8 delar, 0 kollisjonar)
- **[`cad/raup_skal.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_skal.step)** + **[`produksjon/raup_skal_P1S.stl`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_skal_P1S.stl)** — Ope-botn Class-A hovudskal (`2,5 mm` vegg, debossed skuggelinje ved `z = 37,78 mm`).
- **[`cad/raup_botn_chassis.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_botn_chassis.step)** — Monolittisk botnchassis med `0,40 mm` registreringsflens, integrert 18650-batterivugge, PCB-piedestall, vertikal sokkelhylse for LED-søyla, `1,40 mm` boga diffusorspor, USB-C kabelutsparing, 3× forsenka M3-skruebrønnar og 4× `Ø10,4 × 0,6 mm` lommer for 3M Bumpon SJ5312 møbelføter.
- **[`cad/raup_ballast.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_ballast.step)** + **[`produksjon/raup_ballast_1til1.dxf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_ballast_1til1.dxf)** — Laserskoren `5,0 mm` S235JR stålballastplate med nøkkelutsparingar rundt chassis-piedestallane og 3× `Ø3,4 mm` M3-hol (veltevinkel **> 50°** papir / **> 45°** PLA; krav EN 60598 ≥ 6°, Northern ≥ 15°).
- **[`cad/raup_batteri_21700.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_batteri_21700.step)** — Brukarutskiftbar 18650 Li-ion-celle med polknapp (`Ø18,4 × 65,2 mm`, 3,6V 3500 mAh / 12,6 Wh), liggande i den konturerte chassisvugga med Keystone 5209 fjørkontaktar.
- **[`cad/raup_drivar_pcb.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_drivar_pcb.step)** — USB-C Li-ion lademodul + flimmerfri touch/trykk PWM-dimmar (`32 × 14 × 4,8 mm` inkl. USB-C-kontakt og IC-pakke), montert på chassisets PCB-piedestall.
- **[`cad/raup_led_berar.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_led_berar.step)** — Vertikal eloksert aluminiums LED-kjølesøyle (`12,0 × 5,5 × 107,4 mm`) med `8,2 × 0,9 mm` frontspor for 8 mm CRI 95+ 2700K COB LED-stripe og 2× bakre kjøleriller/kabelspor, stukke ned i chassis-sokkelen.
- **[`cad/raup_diffusor.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_diffusor.step)** + **[`produksjon/raup_diffusor_1til1.dxf`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/produksjon/raup_diffusor_1til1.dxf)** — Avviklingsbar `1,0 mm` optisk diffusorplate (`139,5 × 189,0 mm`, `R_min = 37,2 mm`, ≥ 1,38 mm klaring til hovudskal).
- **[`cad/raup_filmklips.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_filmklips.step)** — Skånsam boga styreklips med `1,60 mm` ikkje-klemmande spor, forankra direkte på botnchassis-brua.
- **[`cad/raup_stoypform_minus_Y.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_stoypform_minus_Y.step)** & **[`cad/raup_stoypform_pluss_Y.step`](file:///c:/Users/Iver/Documents/github/GK5-modul_2/Leveranse/konsept%20C%20-%20raup/cad/raup_stoypform_pluss_Y.step)** — Todelt støypeform for papirmasse med `Ø5,2 mm` styringspinnar.

---

## 4. Køyring av CAD-byggeskript
```bash
py -3 cad/raup_produksjon.py 2.5 200.0
py -3 cad/raup_skal.py 2.5 200.0
```
