#!/bin/bash

sacfile=$1

rm noise.sac
rm waveform.sac
rm noisefft.am noisefft.ph
rm waveformfft.am waveformfft.ph

# Write the noise and waveform segments into separate files:
# A few seconds of each
sac << SACEND
cut t5 -17 -2
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

# # Make a plot that shows the noise and waveform spectra
# sac << SACEND
# r waveform_fft.am noise_fft.am
# smooth mean halfwidth 9
# loglog
# color on increment on
# xlim 0.5 50
# ylabel "Amplitude"
# xlabel "Frequency (Hz)"

# # WHOO! We can put distance and magnitude header info into the titles!
# evaluate to d &1,dist
# evaluate to m &1,mag
# title '$sacfile: Distance = %d km; mag = %m'

# p2
# saveimg $sacfile.signal_vs_noise.pdf
# exit
# SACEND

#rm waveform_fft.am
#rm noise_fft.am

