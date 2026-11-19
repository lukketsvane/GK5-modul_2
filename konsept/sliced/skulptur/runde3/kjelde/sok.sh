#!/bin/bash
# sok.sh <design/modus> VAR=v1,v2,.. [VAR2=..] : prøv kombinasjonar via miljøvariablar, utan bilete
m=/home/claude/arb2/$1; shift
n1=${1%%=*}; IFS=, read -ra v1 <<< "${1#*=}"; n2=${2%%=*}; IFS=, read -ra v2 <<< "${2#*=}"; [ -z "$2" ] && v2=("")
for x in "${v1[@]}"; do for y in "${v2[@]}"; do
  ( o=$(cd /home/claude/slicer && env UTAN=1 $n1=$x ${n2:+$n2=$y} npx tsx /home/claude/arb2/verkty/lag.ts $m --rask 2>&1)
    echo "$n1=$x $n2=$y | $(echo "$o" | grep -oE '(ALT OK|IKKJE OK)' | head -1) | $(echo "$o" | grep -E '^klempar' | cut -c10-70) | $(echo "$o" | grep -E '^tal' | grep -oE '[0-9]+ delar|[0-9]+ lause|[0-9]+ ark' | tr '\n' ' ') | $(echo "$o" | grep -E 'BROT (kvart|gods|grip|orden|plate)' | cut -c8-60 | tr '\n' ' ')" ) &
done; wait; done
