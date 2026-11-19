#!/bin/bash
# full.sh <design> <modus> : full bygging med produksjonsfiler
cd /home/claude/slicer && npx tsx /home/claude/arb2/verkty/lag.ts /home/claude/arb2/$1/$2 > /home/claude/arb2/$1/$2/full.log 2>&1; echo "$1/$2 exit $? $(head -1 /home/claude/arb2/$1/$2/full.log | cut -c1-110)"
