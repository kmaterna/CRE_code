"""
Mendocino Repeaters Project
6/8/2016

This script takes a "solution file" (which has sac file, sac file, distance, magnitude, 
	cross-correlation, and coherence information)
and makes another parallel file with information about which frequencies have good signal-to-noise ratios. 

"""

from subprocess import call
import numpy as np
from sys import argv

station_name=argv[1]
if len(station_name)==3:
	station_name=station_name+'_';
input_file=open(station_name+"-above_cutoff_results.txt",'r');
output_file=open(station_name+"-snr_results.txt",'w+');
snr_file="SNR.txt";  # intermediate file

for line in input_file:
	f1=[]; f2=[]; snr1=[]; snr2=[];

	sacfile1=line.split()[0];
	sacfile2=line.split()[1];

	# Call to compute SNR for sac file #1: splits up the noise from the data, does FFTs, writes noise_fft.am, waveform_fft.am
	call(["noise_floor_VS_data.sh",sacfile1],shell=False); 
	call("./get_snr.o",shell=False)
	for oneline in open(snr_file):
		f1.append(float(oneline.split()[0]));
		snr1.append(float(oneline.split()[1]));

	# Call to compute SNR for sac file #2
	call(["noise_floor_VS_data.sh",sacfile2],shell=False); 
	call("./get_snr.o",shell=False)
	for oneline in open(snr_file):
		f2.append(float(oneline.split()[0]));
		snr2.append(float(oneline.split()[1]));

	output_string=sacfile1+' '+sacfile2+' '+str(f1) + ' ' + str(snr1) + ' ' + str(f2) + ' ' + str(snr2)+'\n'
	output_file.write(output_string);


