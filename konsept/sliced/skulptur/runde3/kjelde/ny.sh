#!/bin/bash
# ny.sh <design> <modus> <uttrykk> : lag modusmappe med konsept.ts som kallar lampe(<uttrykk>)
mkdir -p /home/claude/arb2/$1/$2 && printf 'import { lampe } from "../lampe"\nconst x = lampe(%s)\nexport const { namn, kropp, bag, plan, utstyr } = x\n' "$3" > /home/claude/arb2/$1/$2/konsept.ts
