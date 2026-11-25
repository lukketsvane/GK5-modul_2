# -*- coding: utf-8 -*-
"""Samlar resultatet frå run_side.py til kontroll/fyr_lys.json. Køyrt av kjor.py:
    py -3 cad/lysmodell/samle.py <mappe med res_FYR_final.json> <ut.json>
Tala for toppkammeret (lok) kjem frå topp.py (ring av fire 25 mm stripebitar på r 22, WH02, kvitt skjørt), skalert
med straumdelen gjennom R1 og R3; dei står her som tal fordi topp.py ikkje blir køyrd kvar gong."""
import json
import os
import sys

mappe, ut = sys.argv[1], sys.argv[2]
final = json.load(open(os.path.join(mappe, "res_FYR_final.json"), encoding="utf-8"))
eyes = final["eyes"]
samla = {
  "skildring": "FYR lysmotor, endeleg geometri (rist r 10..32, 55°, deling 16, kile ±45°, inga ribbe). Monte Carlo 250 000 strålar, seriemateriale (børsta messing, pulverlakk inni mantelen).",
  "føresetnader": {"stripe": "BTF DC5V FCOB 8 mm 320 LED/m RA90, 7 W/m (produsent), 158 mm", "lysutbytte_lm_per_W": "100 (ANTAKING, ikkje publisert)",
                   "stripe_lm": final["flux_src"], "refleksjon_kvit_rist": 0.8, "lok": "PLEXIGLAS Satinice WH02 3 mm, T 0,44 (datablad)"},
  "avskjering_direkte_maks_elevasjon_grader": round(final["esc_direct_max_el"], 2),
  "lm_ut_gjennom_spaltene": round(final["esc_total"], 2), "lm_ut_ned": round(final["esc_down"], 2), "lm_ut_opp": round(final["esc_up"], 2),
  "verknadsgrad_sidelys": round(final["esc_total"] / final["flux_src"], 4),
  "bord_lux": {k: final[k] for k in ("arc_100", "arc_150", "arc_200", "arc_300", "arc_500")},
  "felt_0_6x0_4_middel_lux": final["field_mean_lux"], "felt_maks_lux_50mm": final["field_max_lux_50mm"],
  "luminans_sett_frå_augo_cd_m2": {k: {"maks": v["max"], "p99": v["p99"], "middel": v["mean"], "stripe_sett": v["strip_seen"]} for k, v in eyes.items()},
  "luminans_maks_alle_augo_cd_m2": max(v["max"] for v in eyes.values()),
  "stripe_luminans_cd_m2": final["L_strip"],
  "toppkammer_frå_lysanalysen": {"merknad": "modell med lukka kvitt golv; FYR har ope loft mot toppkammeret, så loket får litt mindre lys og øvre del av spaltene litt meir",
                                 "full": {"lm_frå_loket": 14.4, "lok_middel_cd_m2": 1010, "lok_maks_cd_m2": 1240, "straum_av_nominell": 0.37},
                                 "glød": {"lm_frå_loket": 5.5, "lok_middel_cd_m2": 390, "lok_maks_cd_m2": 480, "straum_av_nominell": 0.15},
                                 "jamnheit_senter_kant": 1.11},
  "krav": {"F1_ingen_kjelde_synleg_ingen_flate_over_3000": "OPPFYLT (modell + strålekasting på CAD-netta)",
           "F5_under_1500_cd_m2": "OPPFYLT for spaltene (maks %d); loket ca 1010-1240 ved full glød" % max(v["max"] for v in eyes.values()),
           "F3_350_lx_arbeidslys": "IKKJE OPPFYLT: middel %.1f lx på 0,6 x 0,4 m. FYR er stemnings- og aksentlys (ca 18 lm)." % final["field_mean_lux"]},
  "kjelde": {"sporar": "cad/lysmodell/kjor.py: fyrlys.py + run_side.py med cfg_serie.json (250 000 strålar, frø 11); toppkammeret frå topp.py; samla med samle.py", "rå_resultat": final},
}
json.dump(samla, open(ut, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok", ut)
