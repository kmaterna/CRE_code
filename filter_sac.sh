#!/bin/bash

# This file actually helps python plot the filtered waveforms when you image families. 
# You shouldn't delete it.  I did that once.  It was bad.  

sacfile=$1

sac << SACEND
cut t5 -1 19.47
r $sacfile
bp co 2 24 p 2
write filtfile.sac
exit
SACEND