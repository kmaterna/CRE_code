#!/bin/bash

raw_sac_dir=$1
f=$2

echo $f

cp $raw_sac_dir$f .

sac <<SACEND
r $f
cut t5 -1.00 19.47
# Make sure these are exactly 20.47 seconds apart. 
r
write RAW_$f
bp co 2 24 p 2
write FIL_$f
exit
SACEND