"""
MENDOCINO REPEATERS PROJECT
Jan 17, 2015

# This script identifies families of repeaters: 
# 1. Takes in a pre-existing list of event-pairs that are considered repeaters, based on some agreed-upon criterion
# 2. Identifies a set of unique events
# 3. Produces an MxM connectivity matrix of zeros and ones to represent how those M events are related (similar = 1, dissimilar=0)
# 4. Runs connected component anlysis to identify families (in the scipy libraries)
# 5. Writes the resulting SORTED families into a separate file. 

"""

import numpy as np
import scipy as sp
import scipy.sparse as ssp
import matplotlib.pyplot as plt



# ----------- THE MAIN PROGRAM ---------- # 
def connected_components(time_window,Network_repeaters_list,families_list):
	[event1, event2] = inputs(Network_repeaters_list);
	[unique_events, integer, labels] = compute(time_window, event1, event2);
	outputs(unique_events, integer, labels, families_list); 
	return;	

# ----------- THE GUTS ---------- # 

def inputs(inputfile):
	event1=[]; event2=[];
	ifile=open(inputfile,'r');
	for line in ifile:
		temp=line.split();
		event1.append(temp[0])
		event2.append(temp[1])
	return [event1, event2];


def compute(time_window, event1, event2):
	start_time=time_window[0];
	end_time=time_window[1];
	print "Starting time and ending time are: "
	print start_time
	print end_time

	# Cut the arrays to the appropriate time window. 
	event1_cut=[]; event2_cut=[];
	for i in range(len(event1)):
		time1=float(event1[i][0:4])+float(event1[i][5:8])/365.0;
		time2=float(event2[i][0:4])+float(event2[i][5:8])/365.0;
		if time1>start_time and time1<end_time:
			if time1>start_time and time1<end_time:
				event1_cut.append(event1[i]);
				event2_cut.append(event2[i]);


	unique_events = make_unique_events_list(event1_cut, event2_cut);
	M = make_connectivity_matrix(event1_cut, event2_cut, unique_events);
	integer, labels = connected_component_analysis(M);
	return [unique_events, integer, labels];


def make_unique_events_list(event1, event2):
	"""Takes a pre-existing set of event-pairs that are considered repeaters, and generates a set of unique events"""
	unique_events=[]  # the list of unique events
	counter=0;
	for i in range(len(event1)):
		if event1[i] not in unique_events:
			unique_events.append(event1[i]);
		if event2[i] not in unique_events:
			unique_events.append(event2[i]);
		counter+=1
	print "Length of Event Pairs Vector is: " + str(counter);
	print "Length of Unique Events Vector is: " + str(len(unique_events));
	return unique_events;

def make_connectivity_matrix(event1, event2, unique_events):
	matrix_size=len(unique_events);
	M = np.zeros([matrix_size,matrix_size]);
	for i in range(len(event1)):
		index0=unique_events.index(event1[i])
		index1=unique_events.index(event2[i])
		M[index0, index1] = 1;
		M[index1, index0] = 1;
	return M;

def connected_component_analysis(M):
	integer, labels=ssp.csgraph.connected_components(M, directed=False, connection='weak', return_labels=True)
	print labels;
	print "The " + str(len(M)) + " unique events fall into " + str(integer) + " connected components."
	return integer, labels;


# ------------ OUTPUTS ------------ # 
def outputs(unique_events, integer, labels, output_file):
	outfile=open(output_file,"w");
	for i in range(integer):  # will be range(integer)
		unique_index = np.where(labels==i)   # this "index" will be an array of variable length
		outfile.write("Family " + str(i)+ " With " + str(np.size(unique_index)) + " Events: ");
		# print unique_index
		unsorted_events=[];   # sort the events in the family chronologically. 
		for j in range(np.size(unique_index)):
			unsorted_events.append(unique_events[unique_index[0][j]])
		unsorted_events.sort(); # chronological sorting. 
		for j in range(np.size(unique_index)):
			outfile.write(unsorted_events[j])  # at this point it's actually sorted already. 
			outfile.write(" ")
		outfile.write("\n")
		del unique_index
	outfile.close()
	return;





