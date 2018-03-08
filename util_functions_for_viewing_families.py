"""
MENDOCINO REPEATERS PROJECT
March 1, 2016

These are some utility functions for viewing families of repeaters. 

"""
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from obspy.core.stream import Stream
from obspy import read
from subprocess import call
import os



# ------- COEFFICIENT OF VARIATION ------- #
def CVar(event_times):
	""" The coefficient of Variation: IF CV = 0 , the events are periodic.  IF CV > 0, the events are random.  """
	Tr=[]   # recurrence times
	for i in range(len(event_times)-1):
		Tr.append(event_times[i+1]-event_times[i]);
	cv=np.std(Tr)/np.mean(Tr)
	return cv;


# ------- MAKE A MATRIX OF XCORR/COH VALUES FOR A FAMILY (NOT ALL EVENTS ARE REPEATERS) ----- #
def make_similarity_matrix(number_of_events, event_names,ev1_non_repeaters,ev2_non_repeaters,similarity_values_non_repeaters):
	z=np.zeros([number_of_events, number_of_events]);

	for i in range(number_of_events):
		for j in range(i+1,number_of_events):
			ev1=event_names[i];
			ev2=event_names[j];
			set1 = [k for k, n in enumerate(ev1_non_repeaters) if n == ev1]
			set2 = [k for k, n in enumerate(ev2_non_repeaters) if n == ev2]

			place_in_coh_list=np.intersect1d(set1,set2);
			if len(place_in_coh_list)>0:
				keep_value=similarity_values_non_repeaters[place_in_coh_list];
				z[i,j]=keep_value;
				z[j,i]=keep_value;
				del keep_value;
			else:
				z[i,j]=0;
				z[j,i]=0;
			del set1, set2, place_in_coh_list;
	# Drawing the diagonal
	for i in range(number_of_events):
		z[i,i]=1;
	return z;


# -------- MAKING THE FIRST SAVED FIGURE (WAVEFORMS) ----- #
def make_waveform_plot(family_of_interest, event_names, magnitude, station, sac_directory, save_path):
	""" Plotting all the waveforms in a given family. """
        
        path_to_python=os.path.dirname(os.path.realpath(__file__));

	x=np.arange(0,20.48,0.01)
	number_of_events=len(event_names);
	plt.figure()
	g, axarr = plt.subplots(number_of_events, sharex=True)
	for i in range(number_of_events):
		name=event_names[i]

		sacfile=sac_directory+'*.'+name
		print sacfile
		call([path_to_python+"/filter_sac.sh",sacfile])

		st1 = read('filtfile.sac')
		tr1 = st1[0]
		array1 = tr1.data

		axarr[i].plot(x, array1)
		axarr[i].get_yaxis().set_ticks([])
		caption=event_names[i][0:15]
		plt.text(0.8, 0.8,caption,
	     horizontalalignment='center',
	     verticalalignment='center',
	     transform = axarr[i].transAxes,
	     fontsize=14)
		caption2="M="+str(magnitude[i]);
		plt.text(0.8, 0.25,'M=%.2f' % (magnitude[i]) ,
	     horizontalalignment='center',
	     verticalalignment='center',
	     transform = axarr[i].transAxes,
	     fontsize=14)
		plt.xlabel('Time (s)',fontsize=14)
		if i==0:
			axarr[i].set_title("Family "+str(family_of_interest)+" at "+station)
	plt.xticks(fontsize=14)
	plt.savefig(save_path+"Family_"+str(family_of_interest)+".jpg");
	plt.close();



