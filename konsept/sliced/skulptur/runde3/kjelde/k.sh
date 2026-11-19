#!/bin/bash
# k.sh <design> [modus...] : køyr lag.ts --rask for kvar modusmappe, skriv dom + brot
d=/home/claude/arb2/$1; shift; ms=${@:-$(cd $d && ls -d */ | tr -d /)}
for m in $ms; do [ -f $d/$m/konsept.ts ] || continue
  (cd /home/claude/slicer && npx tsx /home/claude/arb2/verkty/lag.ts $d/$m --rask 2>&1 | grep -E "^[a-zA-Z0-9_-]+ — |BROT|^tal|^klempar|syn feila|rror" | cut -c1-330) &
done; wait
