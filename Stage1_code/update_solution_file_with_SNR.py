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
code_dir=argv[2]
if len(station_name)==3:
	station_name=station_name+'_';
input_file=open(station_name+"-above_cutoff_results.txt",'r');
output_file=open(station_name+"-snr_results.txt",'w+');
snr_file="SNR.txt";  # intermediate file

for line in input_file:
	f1=[]
	f2=[]
	snr1=[]
	snr2=[]
	temp=line.split()

	sacfile1=temp[0]
	sacfile2=temp[1]

	# Call to compute SNR for sac file #1
	call("gcc -o get_snr.o "+code_dir+"/get_snr.c -L/share/apps/sac/lib  -lsacio -lsac -lm", shell=True)
	calling="noise_floor_VS_data.sh "+sacfile1
	call(calling,shell=True);  
	# Sac splits up the noise from the data and FFTs them both
	# writes noise_fft.am, waveform_fft.am

	call("./get_snr.o",shell=True)
	snr_handle=open(snr_file,'r')
	for line in snr_handle:
		temp=line.split()
		f1.append(float(temp[0]))
		snr1.append(float(temp[1]))
	snr_handle.close();

	# Call to compute SNR for sac file #2
	calling="noise_floor_VS_data.sh "+sacfile2
	call(calling,shell=True);  
	# Sac splits up the noise from the data and FFTs them both
	call("./get_snr.o",shell=True)

	snr_handle=open(snr_file,'r')
	for line in snr_handle:
		temp=line.split()
		f2.append(float(temp[0]))
		snr2.append(float(temp[1]))
	snr_handle.close();

	output_string=sacfile1+' '+sacfile2+' '+str(f1) + ' ' + str(snr1) + ' ' + str(f2) + ' ' + str(snr2)+'\n'
	output_file.write(output_string);


