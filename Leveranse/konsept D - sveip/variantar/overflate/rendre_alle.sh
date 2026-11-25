#!/bin/sh
# Rendrar alle fem overflatevariantane i full kvalitet. Køyr frå overflate/.
for v in v1_plate v2_gore v3_felt v4_straum v5_duk; do
  python3 sveip_hud.py "$v" 2>&1 | grep -E "nett|SKREIV|Error|Traceback"
done
