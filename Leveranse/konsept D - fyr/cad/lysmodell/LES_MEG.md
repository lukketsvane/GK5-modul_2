# Lysmodell for FYR

Monte Carlo-modellen som `kontroll/fyr_lys.json` kjem frå. Han reknar luminansen du ser i spaltene, lyset på bordet og lysstraumen ut. Lyskontrollen på dei faktiske CAD-netta (`cad/fyr_lyskontroll.py`) er ein eigen, uavhengig kontroll.

| Fil | Innhald |
|---|---|
| `fyrlys.py` | Strålefylgjaren for sidelyset (numpy): lamellar, tak, sideveggar, stav og stripe, hylse med port og mantel med spalter |
| `run_side.py` | Køyrer éin geometri og skriv `res_<namn>.json` |
| `cfg_serie.json` | Geometrien for den endelege rista, skriven av frå `FyrParams` for hand |
| `samle.py` | Samlar resultatet til `kontroll/fyr_lys.json` |
| `kjor.py` | Køyrer heile kjeda: `py -3 cad/lysmodell/kjor.py` (om lag eitt minutt) |
| `topp.py`, `topp_out.json` | Toppkammeret under loket. `topp_out.json` er resultatet tala i `samle.py` byggjer på |

Føresetnader: 100 lm/W for stripa (ikkje publisert av produsenten), 7 W/m, kvit rist med refleksjon 0,8 og loket PLEXIGLAS Satinice WH02 med transmisjon 0,44 (datablad). Alt er rekna, ingenting er målt.

Endrar du rista, stripa eller hylsa i `cad/fyr_geometri.py`, må `cfg_serie.json` endrast tilsvarande før du køyrer `kjor.py` på nytt.
