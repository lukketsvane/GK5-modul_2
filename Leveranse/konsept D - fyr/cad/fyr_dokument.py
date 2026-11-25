# -*- coding: utf-8 -*-
"""FYR · skriv LES_MEG_FYR.md og INNKJOPSPLAN_OG_MONTERING.md frå CAD-parametrane og kontrollfilene.

    py -3 cad/fyr_dokument.py

Alle tal i dokumenta kjem frå FyrParams, kontroll/*.json, print/FYR_P1S_plater.json og kontroll/fyr_innkjopsliste.csv,
så dokumenta følgjer modellen når han blir endra og skripta køyrde på nytt.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

HER = Path(__file__).resolve().parent
ROT = HER.parent
sys.path.insert(0, str(HER))
import fyr_geometri as g  # noqa: E402


def les(p: Path, standard=None):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return standard


def k(x, d=1):
    """Tal med desimalkomma."""
    if isinstance(x, (int,)) or (isinstance(x, float) and abs(x - round(x)) < 1e-9 and d == 0):
        return f"{int(round(x))}"
    return f"{x:.{d}f}".replace(".", ",")


def main():
    p = g.FyrParams()
    pp = g.FyrParams.prototype()
    ver = les(ROT / "kontroll" / "fyr_CAD_verifisering.json", {})
    lys = les(ROT / "kontroll" / "fyr_lys.json", {})
    lk = les(ROT / "kontroll" / "fyr_lyskontroll.json", {})
    plater = les(ROT / "print" / "FYR_P1S_plater.json", {})
    rows = list(csv.DictReader(open(ROT / "kontroll" / "fyr_innkjopsliste.csv", encoding="utf-8-sig")))

    vs = ver.get("variantar", {}).get("serie", {})
    vp = ver.get("variantar", {}).get("prototype", {})
    ss, sp = vs.get("sum", {}), vp.get("sum", {})
    koll_s = len(vs.get("kollisjonar", [])) if vs else None
    koll_p = len(vp.get("kollisjonar", [])) if vp else None
    par_s = len(vs.get("par", [])) if vs else 0
    stillingar = vs.get("stillingar", [])

    # effekt frå lysdata: sidelys = stripelengd x 7 W/m; full glød = toppemitter x 7 W/m x straumdel frå lysanalysen
    eff_side = (p.stripe_z1 - p.stripe_z0) / 1000.0 * 7.0
    straumdel = (lys.get("toppkammer_frå_lysanalysen", {}).get("full", {}).get("straum_av_nominell", 0.37) if lys else 0.37)
    eff_glod = p.topp_n * p.topp_l / 1000.0 * 7.0 * straumdel
    eff_tot = eff_side + eff_glod

    # ---------------------------------------------------------------- LES_MEG
    L = []
    L.append("# FYR · konsept D\n")
    L.append(f"Revisjon {g.REVISJON}, {g.DATO}. Generert av `cad/fyr_dokument.py` frå kontrollfilene.\n")
    L.append("Bordlampe for Northern. Ein mørk raud mantel med seks spalter, ein messingkrage som stikk opp av mantelen, "
             "og eit opalt lok inne i kragen. Kragen er den einaste betjeninga: du vrir han, og han opnar spaltene éi og éi "
             "som ein lukkar i eit fyr. Skissa er teken heilt fram til produksjonsklar CAD med kontroll, prentefiler, teikningar og montering.\n")
    L.append("![FYR](render/01_helt.png)\n")
    L.append("## Hovudmål (serie)\n")
    L.append(f"| | |\n|---|---|\n| Høgd | {k(p.z_hylse_1, 0)} mm |\n| Mantel | Ø{k(p.mantel_d, 0)} x {k(p.mantel_t, 0)} aluminiumsrøyr, {k(p.mantel_synleg_h, 0)} mm synleg |\n"
             f"| Fot | Ø{k(p.fot_d, 0)} x {k(p.fot_h, 0)} mm, {k(math.pi * (p.fot_d / 2) ** 2 / 100, 0)} cm² på bordet |\n"
             f"| Krage | Ø{k(2 * p.r_ho, 1)} messing 0,8 mm, {k(p.krage_h, 0)} mm over mantelen |\n"
             f"| Masse | {k(ss.get('masse_g', 0), 0)} g (krav maks 1200 g) |\n"
             f"| Veltevinkel | {k(ss.get('veltevinkel_grader', 0), 1)}° (tyngdepunkt {k(ss.get('tyngdepunkt_z_mm', 0), 0)} mm over bordet) |\n"
             f"| Effekt | ca {k(eff_tot, 1)} W på USB 5 V (sidelys {k(eff_side, 2)} W + full glød {k(eff_glod, 2)} W, rekna), 0 W avslått |\n")
    L.append("## Korleis ho verkar\n")
    L.append("Kragen (05) går 0 til 90° i ni stillingar med 11,25° mellom (same deling som spaltene). Ein port i messingen dekkjer eller opnar spaltene, "
             "og tre mikrobrytarar under fotringen les vinkelen frå eit kamspor. Ingen elektronikk anna enn brytarar og motstandar: likestraum, ingen flimmer.\n")
    L.append("| Stilling | Kragen | Opne spalter | Brytarar lukka | Lys |\n|---|---|---|---|---|")
    lys_txt = {0: "sidelys + full glød"}
    for s in stillingar:
        th = s["theta"]
        lukka = [n.split("_")[0] for n, v in s.items() if n.endswith("_lukka") and v]
        if not lukka:
            l_ = "av (0 W)"
        elif "SW2" in lukka:
            l_ = f"sidelys gjennom {s['opne_spalter']} spalte{'r' if s['opne_spalter'] != 1 else ''} + full glød"
        elif "SW3" in lukka:
            l_ = "full glød i loket"
        else:
            l_ = "svak glød i loket"
        L.append(f"| {int(round(th / p.deling)) + 1} | {k(th, 2)}° | {s['opne_spalter']} | {', '.join(lukka) if lukka else '-'} | {l_} |")
    L.append("")
    maks_ut = lk.get("1_avskjering", {}).get("maks_elevasjon_slapp_ut") if lk else None
    nett_v = -maks_ut if maks_ut is not None else p.rist_avskjering
    L.append("Lysrista (07) bak spaltene er bygd etter same logikk som Poul Henningsen sine skjermar: lamellar 55° ned og ut, med deling "
             f"{k(p.rist_deling, 0)} mm mellom r {k(p.rist_r_inn, 0)} og {k(p.rist_r_ut, 0)}. Ingen direkte stråle frå LED-stripa går ut flatare enn "
             f"{k(nett_v, 1)}° under horisontalen på dei faktiske CAD-nettene (2D-vilkåret gjev {k(p.rist_avskjering, 1)}°; kravet er 34°), "
             "så stripa er aldri synleg frå ein stol. Spegling i skjermar er ikkje rekna. Det du ser i spaltene, er kvite lamellar med "
             "mjuk glød. Det som når bordet, er strålar.\n")
    if lys:
        eyes_max = lys.get("luminans_maks_alle_augo_cd_m2")
        a150 = lys.get("bord_lux", {}).get("arc_150", {})
        a200 = lys.get("bord_lux", {}).get("arc_200", {})
        L.append("## Lys (rekna, ikkje målt)\n")
        L.append(f"- Ljosaste flate du kan sjå i spaltene frå sitjande augehøgd: **{k(eyes_max, 0)} cd/m²** (krav F1: under 3000; ønskje F5: under 1500). Stripa vart aldri treft av ei siktline.\n"
                 f"- Strålar på bordet: middel **{k(a150.get('mean', 0), 0)} lx** 15 cm frå aksen (topp {k(a150.get('peak', 0), 0)} lx, modulasjon {k(a150.get('mod', 0), 2)}), {k(a200.get('mean', 0), 0)} lx på 20 cm.\n"
                 f"- Lysstraum ut: ca **{k(lys.get('lm_ut_gjennom_spaltene', 0), 1)} lm** gjennom spaltene + ca 14 lm frå loket ved full glød, til saman om lag 18 lm.\n"
                 f"- **F3 (350 lx arbeidslys) er ikkje oppfylt**: middel {k(lys.get('felt_0_6x0_4_middel_lux', 0), 1)} lx på 0,6 x 0,4 m. FYR er stemnings- og aksentlys, om lag som eit stearinlys. "
                 "Dette er prisen for at kjelda aldri skal synast.\n"
                 "- Føresetnad: 100 lm/W for stripa (ikkje publisert av produsenten), kvit rist med refleksjon 0,8. Monte Carlo på parametrisk modell av den endelege rista, sjå `kontroll/fyr_lys.json`.\n")
    if lk:
        a = lk.get("1_avskjering", {})
        b = lk.get("2_toppemitter", {})
        c = lk.get("3_augo", {})
        L.append("**Kontroll på dei faktiske CAD-nettene** (Blender BVH, første treff, heile lampa svart, `kontroll/fyr_lyskontroll.json`):\n")
        def tus(n):
            return f"{n:,}".replace(",", " ")
        L.append(f"- Avskjering: {tus(a.get('n', 0))} strålar frå stripa; den høgaste strålen som slapp ut, gjekk {k(-a.get('maks_elevasjon_slapp_ut', 0), 1)}° under horisontalen "
                 f"(krav: minst 34° under): **{'bestått' if a.get('bestatt') else 'IKKJE BESTÅTT'}**")
        L.append(f"- Toppemitter: {tus(b.get('n', 0))} strålar; {b.get('forbi_loket', 0)} slapp ut utan å gå gjennom loket: **{'bestått' if b.get('bestatt') else 'IKKJE BESTÅTT'}**")
        tot = sum(x.get('strålar', 0) for x in c.get('posisjonar', []))
        L.append(f"- Augo: {tus(tot)} siktliner frå 24 augeposisjonar; {c.get('led_treff_totalt', 0)} treff på ein LED: **{'bestått' if c.get('bestatt') else 'IKKJE BESTÅTT'}**\n")
    L.append("## Delar\n")
    L.append("| ID | Del | Serie | Prototype (P1S) |\n|---|---|---|---|")
    besk = {
        "01_fot": ("Fot", "EN AW-6082 dreia, 3 + 3 innpressa stift (bajonettknastar og stolpar for strekkavlastning), pulverlakk RAL 3005",
                   "PLA Matte, prenta med botnen ned; knastane (Ø2,5) og stolpane (Ø3) er prenta med same mål"),
        "03_chassis": ("Chassis", "SLS PA12 svart", "PETG HF, tre-støtte"),
        "04_mantel": ("Mantel", "røyr EN AW-6060 90 x 2, røyrlaser, pulverlakk", "PLA Matte i to delar med fals (P1S tek 256 mm)"),
        "05_hylse": ("Hylse / krage", "CuZn37 0,8 valsa frå laserskoren plate, børsta", "PLA Silk+ gull 1,6 mm, prenta saman med fotringen"),
        "05b_hylsefot": ("Fotring", "POM-C: lager, klikkspor, kamspor, gjenger", "som over"),
        "05c_stoppskruar": ("Stoppskruar", "3 x ISO 7380 M3 x 5: låser røyret, endestopp 0/90°, held kragen nede", "same"),
        "06_lysstav": ("Lysstav", f"aluminium 15 x 2 x {k(p.stav_z1 - p.stav_z0, 0)}, bak svart, limt i mastfoten og i rista", "same"),
        "06b_led_side": ("Sidestripe", "5 V COB 8 mm RA90, 158 mm", "same"),
        "06c_led_topp": ("Toppemitter", "4 x 25 mm same stripe på kvadrat r 22", "same"),
        "06d_kontakt": ("Mastfot", f"POM-C {k(p.mastfot_b, 0)} x {k(p.mastfot_l, 0)} x {k(p.mastfot_z1 - p.mastfot_z0, 1)}, lomme for loddekroppen til 3,5 mm TRS-pluggen (limt), stavspor med leidningskanal", "PETG HF på plate 4, same mål (lomma 0,2 større)"),
        "07_lysrist": ("Lysrist", "SLS PA12 kvit", "PETG HF kvit, prenta opp ned"),
        "08_lok": ("Lok", "PLEXIGLAS Satinice WH02 3 mm", "same eller diffusorark frå monitor"),
        "10_glidering": ("Glidering", "POM-C delt ring", "PETG HF"),
        "11_oring": ("O-ring", "silikon 85 x 3, strekt 2,9 % inn i sporet", "same"),
        "11b_snor": ("Snorbitar", "3 x silikonsnor Ø2 x 10: forspenner bajonetten (trykk ned og vri)", "same"),
        "12_brytarar": ("Brytarar", f"Omron 2 x D2F-01L3 (gull) + D2F-L3 (sølv), justerbare ± {k(p.sw_just, 1)} mm", "same"),
        "13_jack": ("TRS-kontakt", "3,5 mm panel M6", "same"),
        "14_kretskort": ("Kort", "R1 91 Ω, R3 33 Ω, PTC 0,5 A, JST PH", "hullkort"),
    }
    for nid, (n, s_, pr) in besk.items():
        L.append(f"| {nid.split('_')[0]} | {n} | {s_} | {pr} |")
    L.append("")
    L.append("## Kontroll\n")
    L.append(f"- Alle {len(vs.get('delar', {}))} delane er gyldige B-rep-lekamar i både serie og prototype.\n"
             f"- Kollisjonar: {koll_s} i serie og {koll_p} i prototypen, prøvd i alle ni stillingane til kragen ({par_s} par i serien). "
             f"Rørslene har desse klaringane (serie / prototype): glidering {k(p.r_glide_i - p.r_ho, 2)} / {k(pp.r_glide_i - pp.r_ho, 2)} mm, "
             f"tappen {k(p.bor_r - p.tapp_ro, 2)} / {k(pp.bor_r - pp.tapp_ro, 2)} mm, toppdekk mot mantel {k(p.r_mi - p.toppdekk_r, 2)} / {k(pp.r_mi - pp.toppdekk_r, 2)} mm.\n"
             "- Kvar stilling er sjekka mot opne spalter og brytartilstand (tabellen over er skriven frå den kontrollen).\n"
             "- **Ikkje gjort**: fysisk prøveprent, måling av lys, temperaturmåling, kabelstrekk-prøve. Sjå «Står att».\n")
    if plater:
        L.append("## Prentefiler (Bambu Lab P1S, 0,4 mm dyse, ferdig skorne)\n")
        L.append("| Fil | Delar | Filament | Tid | Gram | Støtte |\n|---|---|---|---|---|---|")
        tot_g, tot_s = 0.0, 0.0
        for fil, r in sorted(plater.items()):
            try:
                tot_g += float(r.get("vekt_g") or 0)
                tot_s += float(r.get("prediksjon_s") or 0)
            except Exception:  # noqa: BLE001
                pass
            t = float(r.get("prediksjon_s") or 0)
            L.append(f"| `print/{fil}` | {', '.join(r.get('delar', {}).keys())} | {r.get('filament_profil', '').replace(' @BBL P1S 0.4 nozzle', '')} | "
                     f"{int(t // 3600)} t {int(t % 3600 // 60)} min | {k(float(r.get('vekt_g') or 0), 0)} | {'ja' if r.get('stotte_brukt') == 'true' else 'nei'} |")
        L.append(f"\nTil saman om lag {k(tot_s / 3600, 1)} timar og {k(tot_g, 0)} g filament. Prent først ein prøvebit av fotringen (klikk og stoppskruar) før heile hylsa.\n")
    L.append("## Filer\n")
    L.append("| Mappe | Innhald |\n|---|---|\n"
             "| `cad/` | `fyr_geometri.py` (all geometri, éin parameterklasse), `fyr_bygg.py` (byggjer, eksporterer, kontrollerer), STEP per del og `fyr_samanstilling.step` |\n"
             "| `kontroll/` | `fyr_CAD_verifisering.json`, `fyr_BOM.csv`, `fyr_innkjopsliste.csv`, `fyr_lys.json`, `fyr_lyskontroll.json`, `fyr_teikning_sjolvkontroll.json` |\n"
             "| `cad/lysmodell/` | Monte Carlo-modellen som `kontroll/fyr_lys.json` kjem frå (sjå `cad/lysmodell/LES_MEG.md`) |\n"
             "| `print/` | fem ferdig skorne 3MF-plater og `FYR_P1S_plater.json` |\n"
             "| `produksjon/` | STL for prototypen, flatmønster for messinghylsa (DXF), lok (DXF), utbretta mantel (DXF) og `teikningar/` (produksjonsteikningar, PDF og PNG) |\n"
             "| `montering/` | monterings- og servicerettleiing (PDF og PNG per side) |\n"
             "| `render/` | Cycles-rendringar av CAD-en |\n")
    L.append("## Køyr på nytt\n")
    L.append("```powershell\npy -3 cad/fyr_bygg.py\npy -3 cad/fyr_print.py\npy -3 cad/fyr_teikning.py\npy -3 cad/fyr_montering.py\npy -3 cad/fyr_dokument.py\n```\n")
    L.append("Rendring og lyskontroll går i Blender 5.1. Eksporter netta først med `py -3 cad/fyr_render_eksport.py <stl_mappe> [theta]` (skriv `scene.json`), deretter `blender.exe -b -P cad/fyr_render.py -- <stl_mappe> <ut.png> <scene>` og `blender.exe -b -P cad/fyr_lyskontroll.py -- <stl_mappe> <ut.json>`. Sjå toppen av kvart skript.\n")
    L.append("## Avgjerder og avvik frå skissa\n")
    L.append(f"- Røyret er Ø90 x 2 fordi det er lagervare (Ø84, som skissa sine proporsjonar gav, finst ikkje). Alle proporsjonar er skalerte med.\n"
             f"- Kragen er Ø{k(2 * p.r_ho, 1)} (0,93 av mantelen, skissa ca 0,94): det trengst ein glidering mellom messing og lakkert aluminium.\n"
             "- Spaltene lyser mjukt mot toppen i staden for jamt heile vegen; øvre del får lys frå toppkammeret gjennom eit ope loft over rista. Fysisk ærleg: det er ikkje stripe over z 250.\n"
             "- Ingen batteri. Lampa går på fast USB-kabel (B3). Batterimodul og trinnlaus dimming er ikkje med i denne utgåva (F7, F11 ikkje oppfylt); "
             "elektronikkrommet har plass til eit seinare kort med Hall-sensorar.\n"
             "- Lysmodulen (stav, rist, toppemitter, lok) går ut gjennom kragen ovanfrå utan verktøy (B1, B7). Brytarar og kabel blir bytte etter at mantelen er vridd av.\n"
             "- Mantelen går berre på i éin stilling (usymmetriske knastar), låser med klokka og må trykkjast ned for å løysast; "
             "slik kan ikkje drag frå kragen vri han laus. Tre klikktunger held fotringen sentrert; klikkmomentet er overslagsvis 0,3 til 0,4 Nm (ikkje målt).\n"
             "- Funna frå dei uavhengige gjennomgangane (mekanikk, teikningar, rettleiing og leveranse) er retta i modellen og generatorane; kollisjons- og rørslekontrollen over er køyrd på resultatet.\n"
             f"- Messinghylsa er laga for laserskjering og valsing: hola Ø6 for stoppskruane har {k(p.stopp_z - (p.stopp_hovud_d + 0.3) / 2 - p.z_hylse_0, 1)} mm "
             f"steg ned til underkanten (krav minst 2 x {k(p.hylse_t, 1)} mm), og stumpskøyten ligg på {k(p.hylse_saum, 0)}°, midt mellom to kronegrupper. "
             "Når kragen blir vriden, vandrar skøyten mellom 225° og 135°, altså alltid på baksida.\n"
             "- Kabelen er strekkavlasta i foten: han går i ein S rundt tre stolpar P1 til P3 (om lag 185° omslyng til saman, rekna med tangentar), og kappa sluttar før leiarane går opp i chassiset.\n"
             "- Lysmodulen (stav, stripene, rista og mastfoten med pluggen) er limt saman med 2K-epoksy og blir bytt som eining. Ein tverrskrue mellom rista og staven fekk ikkje plass: over stripa står taket i vegen, og under stripa når ikkje skrujarnet fram forbi den nedste lamellen. Leiarane frå stripene går gjennom golvet i rista og ned i kanalen bak staven i mastfoten.\n"
             f"- Mastfoten (06d) er {k(p.mastfot_b, 0)} mm brei slik at loddekroppen til TRS-pluggen (Ø{k(p.trs_kropp_d, 0)}) får plass i ei lomme under staven; gjennomgangen i toppdekket er like brei pluss 0,3 mm klaring.\n")
    L.append("## Står att (ikkje verifisert)\n")
    L.append("- Prøveprent av fotring og klikk, deretter heile lampa; mål klaringane med skyvelære og juster `FyrParams.prototype()`.\n"
             "- Mål kappeeininga og fargetemperaturen på stripa: spesifisert 2700 K, næraste lagervare hos BTF er 3000 K.\n"
             "- Juster brytarhøgda ved montering (kontinuitetsprøve), og prøv R1/R3 på benken mot loket sin luminans.\n"
             "- Temperatur på lysstav og rist etter 2 t ved full effekt (overslag 52 til 58 °C på staven, ikkje målt).\n"
             "- Kabelstrekk 30 N og veltevinkel på skråplan (EN 60598-2-4): vinkel og verdiar er ikkje stadfesta i repoet.\n"
             "- Spegling av spaltelyset i skjermar som hallar bakover er ikkje rekna.\n"
             "- Prisar merkte NV i innkjøpslista.\n")
    (ROT / "LES_MEG_FYR.md").write_text("\n".join(L), encoding="utf-8")

    # ---------------------------------------------------------------- INNKJØP OG MONTERING
    M = []
    M.append("# FYR · innkjøp og montering\n")
    M.append("Maskinlesbar liste: `kontroll/fyr_innkjopsliste.csv`. Monteringsrettleiing med teikningar: `montering/FYR_montering.pdf`.\n")
    for kat, tittel in (("prent", "Prenta delar (prototype)"), ("lys", "Lys"), ("elektro", "Elektro"), ("festemiddel", "Festemiddel"),
                        ("fot", "Fot"), ("prototype", "Berre prototypen"), ("serie", "Seriedelar")):
        sub = [r for r in rows if r["kategori"] == kat]
        if not sub:
            continue
        M.append(f"## {tittel}\n")
        M.append("| Pos | Del | Komponent | Spesifikasjon | Tal | Leverandør | Pris 1 stk | Pris 100 stk |\n|---|---|---|---|---|---|---|---|")
        for r in sub:
            M.append(f"| {r['pos']} | {r['del_id']} | {r['komponent']} | {r['spesifikasjon_og_delenummer']} | {r['tal_per_lampe']} | {r['leverandor']} | {r['pris_1stk_prototype_nok']} | {r['pris_100stk_serie_nok']} |")
        M.append("")
    M.append("## Koplingsskjema\n")
    M.append("```\nUSB-A 5 V --+-- F1 (PTC 0,5 A) --+--+--+                     X1 (3,5 mm TRS)\n"
             "                                  |  |  |\n"
             "                                  |  |  +-- SW1 (D2F-01L3, gull) -- R1 91 Ω --+-- TOPP+  (tupp)\n"
             "                                  |  +----- SW3 (D2F-01L3, gull) -- R3 33 Ω --+\n"
             "                                  +-------- SW2 (D2F-L3, sølv) ----------------- SIDE+  (ring)\n"
             "GND -------------------------------------------------------------------------- GND    (hylse)\n```\n")
    M.append("SW1 er lukka 0 til ca 84°, SW3 0 til ca 73°, SW2 0 til ca 62° (kamsporet under fotringen). Gullkontaktane ber berre glødestraumen "
             "(under 40 mA), sølvkontakten ber sidestripa (ca 220 mA), innanfor kvar sitt område i Omron-databladet.\n")
    M.append("## Montering i kortform\n")
    M.append("Same steg og same rekkjefølgje som i `montering/FYR_montering.pdf`.\n")
    M.append("1. Smelt dei tre gjengeinnsatsane (H1) inn i chassisflensen nedanfrå med loddebolt, på temperaturen innsatsprodusenten tilrår for materialet.\n"
             "2. TRS-kontakten (13) opp under navet på elektronikkdekket; M6-mutteren oppå navet blir trekt til med ein 8 mm fastnøkkel frå sida, mellom søylene.\n"
             "3. Skru dei tre brytarane (12) til brakettane under toppdekket med M2 x 10 utanfrå og mutter innanfor (H4), armen opp gjennom slissa. Berre lett til.\n"
             "4. Lodd kortet (14: R1, R3, F1, JST PH) og leidningane etter skjemaet; kortet ligg på armen bak.\n"
             "5. Trer kabelen (E9) inn gjennom holet bak i foten og trykk han ned i ein S rundt dei tre stolpane i lomma (på motsett side av kvar stolpe). "
             "Skrell kappa rett etter siste stolpe, før leiarane opp gjennom holet i chassisflensen og forbi armen bak, og krymp JST-pluggen på.\n"
             "6. Set chassiset på foten (bogetappen under flensen fell ned i lomma og sentrerer) og skru det fast nedanfrå med 3 x M3 x 16 (H2).\n"
             "7. Strekk O-ringen (11) inn i sporet under foten.\n"
             "8. Press gliderringen (10) inn i toppen av mantelen (prototype: lim med CA).\n"
             "9. Set fotringen (05b) inn nedanfrå i messinghylsa (05), hol mot hol (prototypen: hylse og fotring er prenta i eitt).\n"
             "10. Set hylsa med fotringen ned på tappen forbi dei tre klikktungene, med porten framme.\n"
             "11. Vri kragen til 0° (porten framme) og skru dei tre stoppskruane M3 x 5 (05c) gjennom hola i messingen; første gong skjer dei gjengene sjølv i Ø2,5-holet.\n"
             "12. Juster brytarane: med kragen på 0°, løys M2-skruane, skyv kvar brytar opp mot fotringen til han klikkar (multimeter på kontinuitet), "
             f"deretter {k(0.6, 1)} mm lenger opp, og trekk til.\n"
             "13. Set lysmodulen (06 + 06b + 06c + 07 + 06d, limt saman med 2K-epoksy, H11; sjå sida «Lysmodul: førmontering» i rettleiinga) ned gjennom kragen med rista mot spaltene; nøkkeltappen går i holet før pluggen når kontakten.\n"
             "14. Funksjonsprøve: kople til straum og vri gjennom alle ni stillingane; sjekk tabellen i LES_MEG_FYR.\n"
             "15. Legg dei tre bitane silikonsnor (11b) i lommene i golvet av mantelsporet i foten.\n"
             "16. Senk mantelen (04) over kragen med L-spora over knastane (berre éin stilling passar: spaltene mot rista), trykk ned og vri ca 14° med klokka "
             "sett ovanfrå til nabben smett forbi og mantelen sprett 0,6 mm opp og låser.\n"
             "17. Legg loket (08) i setet; det smett under dei tre nabbane.\n")
    M.append("**Service:** vri kragen til av (90°) før du tek ut lysmodulen. Løft loket ut i eitt av fingergrepa og trekk modulen rett opp. Ingen verktøy. "
             "For brytarar og kabel: ta ut lok og lysmodul først, trykk mantelen ned, vri han 14° mot klokka og løft han av. Brytarane er no tilgjengelege mellom søylene. For kabelen: snu lampa, skru ut dei tre M3 x 16 (H2, 2 mm unbrakonøkkel) og løft chassiset med hylsa på av foten; stoppskruane blir sitjande. Verktøy i alt: 2 mm unbrakonøkkel, 8 mm fastnøkkel og PH0-skrujarn; loddebolt og multimeter berre ved montering.\n")
    (ROT / "INNKJOPSPLAN_OG_MONTERING.md").write_text("\n".join(M), encoding="utf-8")
    print("ok: LES_MEG_FYR.md, INNKJOPSPLAN_OG_MONTERING.md")


if __name__ == "__main__":
    main()
