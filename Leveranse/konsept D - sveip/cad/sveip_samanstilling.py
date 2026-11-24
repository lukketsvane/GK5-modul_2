# -*- coding: utf-8 -*-
"""Delregister for Sveip rev. B: alle delar i montert stilling.

Kvar post: id, namn, form, materiale, tettleik g/cm3, farge (r,g,b), type, tal.
type: 'lag' (eigen produksjon), 'kjop' (katalogdel), 'ekstern' (følgjer med, ikkje i lampa).
"""
from __future__ import annotations

import sveip_innmat as I
import sveip_kropp as K
import sveip_lys as L
from sveip_geometri import P0

GRAA = (0.80, 0.80, 0.79)       # pulverlakk lys grå, matt (fargeprøve krevst)
ALU = (0.75, 0.76, 0.78)
KVIT = (0.95, 0.95, 0.94)
OPAL = (0.97, 0.97, 0.96)
MESSING = (0.78, 0.62, 0.32)
SVART = (0.08, 0.08, 0.08)
GROEN = (0.10, 0.30, 0.15)      # kretskort
STAAL = (0.62, 0.63, 0.65)
LED_GUL = (0.95, 0.85, 0.45)
CELLE_BLAA = (0.20, 0.35, 0.65)

# (id, namn, byggjar, materiale, tettleik, farge, type, tal)
DELAR = [
    ("D01", "Kropp", lambda: K.kropp(), f"EN AW-5754 H22 {P0.t:.1f} mm, pulverlakk".replace(".", ","), 2.67, GRAA, "lag", 1),
    ("D02", "Chassis", lambda: K.chassis(), f"EN AW-5754 H22 {P0.tc:.1f} mm, pulverlakk".replace(".", ","), 2.67, GRAA, "lag", 1),
    ("D03", "Lysbrett", lambda: L.lysbrett(), f"EN AW-5754 H22 {P0.tb:.1f} mm, blank".replace(".", ","), 2.67, ALU, "lag", 1),
    ("D04", "LED-kort opp", lambda: L.opp_kort(), "FR-4 1,0 mm, 2 lag, termiske via", 1.85, GROEN, "lag", 1),
    ("D04L", "LED opp 2700K x16", lambda: L.opp_led(), "3030 LED", 1.80, LED_GUL, "kjop", 16),
    ("D05", "LED-kort ned", lambda: L.ned_kort(), "MCPCB alu 1,6 mm", 2.40, GROEN, "lag", 1),
    ("D05L", "LED ned 3000K x24", lambda: L.ned_led(), "3030 LED", 1.80, LED_GUL, "kjop", 24),
    ("D06", "Ramme", lambda: L.ramme(), "PC kvit (PETG i prototypen)", 1.20, KVIT, "lag", 1),
    ("D07", "Diffusor ned", lambda: L.diffusor_ned(), "PMMA opal 2 mm", 1.19, OPAL, "lag", 1),
    ("D08", "Diffusor opp", lambda: L.diffusor_opp(), "PMMA opal 1,5 mm", 1.19, OPAL, "lag", 1),
    ("D09", "Hovudkort", lambda: I.hovudkort(), "FR-4 1,6 mm", 1.85, GROEN, "lag", 1),
    ("D09K", "Komponentar hovudkort", lambda: I.hk_komponentar(), "div.", 2.0, SVART, "kjop", 1),
    ("D10", "Luke", lambda: I.luke(), "EN AW-5754 H22 1,5 mm, pulverlakk", 2.67, GRAA, "lag", 1),
    ("D11", "USB-kort", lambda: I.usb_kort(), "FR-4 1,6 mm", 1.85, GROEN, "lag", 1),
    ("D11K", "USB-C hunn", lambda: I.usb_kontakt(), "stål/LCP", 4.0, STAAL, "kjop", 1),
    ("D11J", "JST PH USB-kort", lambda: I.jst_usb(), "PA", 1.1, KVIT, "kjop", 1),
    ("D12F", "Berøringspunkt framme", lambda: I.punkt(-1), "CuZn37 (blyfri), dreia knapp, klarlakk", 8.47, MESSING, "lag", 1),
    ("D12B", "Berøringspunkt bak", lambda: I.punkt(1), "CuZn37 (blyfri), dreia knapp, klarlakk", 8.47, MESSING, "lag", 1),
    ("D13F", "Hylse framme", lambda: I.bossing(-1), "POM, sneppehakar (usynleg under kragen)", 1.41, SVART, "lag", 1),
    ("D13B", "Hylse bak", lambda: I.bossing(1), "POM, sneppehakar (usynleg under kragen)", 1.41, SVART, "lag", 1),
    ("K01", "Celle 21700", lambda: I.celle(), "Samsung INR21700-50E (utan vern, vern på D09)", 2.77, CELLE_BLAA, "kjop", 1),
    ("K02", "Batterihaldar", lambda: I.haldar(), "Keystone 1121 (21700, polarisert)", 1.6, SVART, "kjop", 1),
    ("K03", "Avstand hovudkort M3x25", lambda: I.hk_avstand(), "alu sekskant F-F 5,5 NV", 2.70, ALU, "kjop", 4),
    ("K05", "Nylonavstand M3x28 + 2 nylonskruar M3x6", lambda: L.laas_avstand(), "PA 6.6 kvit", 1.14, KVIT, "kjop", 6),
    ("K06", "Avstand USB SO-M3-3", lambda: I.usb_avstand(), "PEM SO-M3-3", 7.9, STAAL, "kjop", 2),
    ("K07", "PEM-mutrar i chassiset CLS-M3-2", lambda: I.pem_mutrar(), "PEM CLS-M3-2", 7.9, STAAL, "kjop", 10),
    ("K08", "Føter", lambda: I.foter(), "TPE 60 ShA lys grå, sneppar over skruehovudet", 1.10, GRAA, "kjop", 4),
    ("K09", "Skruar kropp ISO 7380 M3x6", lambda: I.kropp_skruar(), "A2", 7.9, STAAL, "kjop", 4),
    ("K10", "Skruar modul ISO 7380 M3x5", lambda: L.modul_skruar(), "A2", 7.9, STAAL, "kjop", 4),
    ("K11", "Skruar opp-kort M3x4", lambda: L.opp_kort_skruar(), "A2", 7.9, STAAL, "kjop", 6),
    ("K12", "Skruar ramme M3x6 ovanfrå", lambda: L.ramme_skruar(), "A2", 7.9, STAAL, "kjop", 4),
    ("K23", "Gjengeinnsats M3 x 5", lambda: L.gjengeinnsats(), "messing, varmepressa", 8.4, MESSING, "kjop", 4),
    ("K22", "Glideputer", lambda: L.glideputer(), "POM kvit, snepp", 1.41, KVIT, "kjop", 4),
    ("K13", "Skruar hovudkort M3x5", lambda: I.hk_skruar(), "A2", 7.9, STAAL, "kjop", 8),
    ("K14", "Myntskruar luke M3x6", lambda: I.luke_skrue(), "A2, fanga, hovud Ø8 x 2, spor 1,2 x 1,0", 7.9, STAAL, "kjop", 2),
    ("K15", "Skruar USB-kort M3x3", lambda: I.usb_skruar(), "A2", 7.9, STAAL, "kjop", 2),
    ("D14", "Berøringskort", lambda: I.beroringskort(), "FR-4 1,6 mm", 1.85, GROEN, "lag", 1),
    ("K19", "Avstand berøringskort SO-M3-3", lambda: I.bk_avstand(), "PEM SO-M3-3 + M3x5", 7.9, STAAL, "kjop", 2),
    ("K20", "Fjørkontaktar", lambda: I.fjorkontakt(), "CuSn6 forgylt, 0,8 mm forspenning, 2 mm slag", 8.8, MESSING, "kjop", 2),
    ("K21", "PEM-mutrar i lysbrettet CLS-M3-2", lambda: L.pem_brett(), "PEM CLS-M3-2", 7.9, STAAL, "kjop", 6),
    ("K18", "JST PH opp-kort", lambda: L.kontaktar_opp(), "PA", 1.1, KVIT, "kjop", 2),
    ("E01", "USB-C-leidning og plugg", lambda: I.plugg_og_leidning(), "TPE/tekstil", 1.2, SVART, "ekstern", 1),
]

# delar som skal ha kontakt (skrue i hol, mutter mot plate): ikkje kollisjon når snittet er lite
KONTAKT_OK = set()


def bygg(berre=None):
    ut = {}
    for d in DELAR:
        if berre and d[0] not in berre:
            continue
        ut[d[0]] = d[2]()
    return ut
