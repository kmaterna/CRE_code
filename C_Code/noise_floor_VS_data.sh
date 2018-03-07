#!/bin/bash

sacfile=$1

rm noise.sac
rm waveform.sac
rm noisefft.am noisefft.ph
rm waveformfft.am waveformfft.ph

# Write the noise and waveform segments into separate files:
# A few seconds of each
sac << SACEND
cut t5 -32 -2
r $sacfile
write noise.sac
cut t5 -0.2 10
r $sacfile
write waveform.sac
exit
SACEND

# Write the fft's of noise and waveform
sac << SACEND
r noise.sac
fft
writesp am noise_fft
r waveform.sac
fft
writesp am waveform_fft
exit
SACEND

# rm waveform_fft.am
# rm noise_fft.am
# rm waveform.sac
# rm noise.sac
