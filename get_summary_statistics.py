"""
Take a folder full of repeaters_results_files and generate COV and summary statistics of events per family. 
num families
num events per family 
avg_cov
avg_timespan
slip rate in Nth box 
slip rate uncertainty in Nth box
"""

import numpy as np 
import util_general_functions
import util_functions_for_viewing_families
import collections

Family_sum_arrays=collections.namedtuple('Family_sum_arrays',[
	'lon_array','lat_array',
	'dep_array','mag_array',
	'event_times_array',
	'cov','n_events',
	'event_timespan',
	'family_id']);


def get_summary_statistics(families_summaries):
	[output_filename, box_dims, time_window, make_slip_rate_cutoff] = configure();
	MyFamilies = inputs(families_summaries);
	[avg_cov, n_families, avg_n, max_n, mean_timespan, n_short_families, slip_rate_boxes, unc_boxes] = compute(box_dims, time_window, make_slip_rate_cutoff, MyFamilies);
	write_outputs(output_filename, avg_cov, n_families, avg_n, max_n, mean_timespan, n_short_families, make_slip_rate_cutoff, box_dims, slip_rate_boxes, unc_boxes);



def configure():  # You're going to want to change this for different locations (Mendocino, Anza, etc.)
	output_filename="summary_statistics.txt";
	min_lon=-124.75;
	max_lon=-124.25;
	min_lat=40.25;
	max_lat=40.36; # this gets the main cluster in the MTJ
	box_dims=[];  # define as many boxes as you want! 
	box_dims.append([min_lon, max_lon, min_lat, max_lat, 18, 30]);   # the lower cluster
	box_dims.append([min_lon, max_lon, min_lat, max_lat, 0, 18]);    # the upper cluster
	time_window=[2008.7, 2017.7];
	make_slip_rate_cutoff=1.0;  # Years
	return [output_filename, box_dims, time_window, make_slip_rate_cutoff];


def inputs(families_summaries):

	myfile=open(families_summaries,'r');
	cov_array=[]
	n_events_array = [];
	event_times_array=[];
	event_timespan_array = [];
	lon_array=[];
	lat_array=[];
	mag_array=[];
	dep_array=[];
	id_array=[];
	for line in myfile:
		[sing_lon_array, sing_lat_array, sing_time_array, sing_mag_array, sing_dep_array, type_of_loc, mean_lon, mean_lat, mean_depth, slip_rate] = util_general_functions.read_family_line(line);
		event_times_array.append(sing_time_array);
		n_events_array.append(len(sing_lon_array));  # number of events in the family
		id_array.append(int(line.split()[1]))        # the ID number of the family
		cov_array.append(util_functions_for_viewing_families.CVar(sing_time_array));
		event_timespan_array.append(sing_time_array[-1]-sing_time_array[0]);
		lon_array.append(sing_lon_array);
		lat_array.append(sing_lat_array);
		dep_array.append(sing_dep_array);
		mag_array.append(sing_mag_array);
	myfile.close();
	MyFamilies=Family_sum_arrays(lon_array=lon_array,lat_array=lat_array,dep_array=dep_array,mag_array=mag_array,
		event_times_array=event_times_array,cov=cov_array,n_events=n_events_array,event_timespan=event_timespan_array,family_id=id_array);

	return MyFamilies;


def compute(box_dims, time_window, make_slip_rate_cutoff, MyFamilies):

	# Get the basic stats that can be found from families_summaries file 
	n_families=len(MyFamilies.n_events);
	avg_cov = np.mean(MyFamilies.cov);
	avg_n = np.mean(MyFamilies.n_events);
	max_n = np.max(MyFamilies.n_events);
	mean_timespan = np.mean(MyFamilies.event_timespan);

	# n_short_families
	is_long_enough_array=[];
	n_short_families=0;
	for i in MyFamilies.event_timespan:
		if i<make_slip_rate_cutoff:
			n_short_families=n_short_families+1; 
			is_long_enough_array.append(0);
		else:
			is_long_enough_array.append(1);

	slip_rate_boxes=[]; unc_boxes=[];
	for mybox in box_dims:
		[slip_rate1, unc_1] = get_slip_rate_stats(mybox, make_slip_rate_cutoff, time_window, MyFamilies, is_long_enough_array);  # for box 1: the lower region
		slip_rate_boxes.append(slip_rate1);
		unc_boxes.append(unc_1);

	return [avg_cov, n_families, avg_n, max_n, mean_timespan, n_short_families, slip_rate_boxes, unc_boxes]; 



def get_slip_rate_stats(box, make_slip_rate_cutoff, time_window, MyFamilies, is_long_enough_array): 
	"""
	Compute the slip rates (and uncertainties) inside of the box of interest. 
	"""

	event_times_array=MyFamilies.event_times_array;
	lon_array=MyFamilies.lon_array;
	lat_array=MyFamilies.lat_array;
	dep_array=MyFamilies.dep_array;
	mag_array=MyFamilies.mag_array;
	id_array=MyFamilies.family_id;

	min_lon=box[0];
	max_lon=box[1];
	min_lat=box[2];
	max_lat=box[3];
	min_dep=box[4];
	max_dep=box[5];

	# Get events that are within the box and time range of interest. 
	event_timing=[];
	event_magnitude=[];
	family_code_number=[];

	for i in range(len(lat_array)):
		for j in range(len(lat_array[i])):
			if (lat_array[i][j]<max_lat) and (lat_array[i][j]>min_lat):
				if (lon_array[i][j]<max_lon) and (lon_array[i][j]>min_lon):
					if (dep_array[i][j]<max_dep) and (dep_array[i][j]>min_dep):
						if (event_times_array[i][j]<time_window[1]) and (event_times_array[i][j]>time_window[0]):
							if is_long_enough_array[i]==1:
								event_timing.append(event_times_array[i][j]);
								event_magnitude.append(mag_array[i][j]);
								family_code_number.append(id_array[i])  # an array like [0 0 0 0 1 1 2 2 ...] for coding each event by family. 
	number_of_families=len(set(family_code_number));  # the unique number of families that we observed in the blob.

	slip_rate = get_slip_rate(event_timing, event_magnitude, time_window, number_of_families);   # slip rate from the full dataset
	unc = get_uncertainty(MyFamilies, time_window, family_code_number); 
	return [slip_rate, unc];


def get_slip_rate(event_timing, event_magnitude, time_window, number_of_families):
	""" number of families is just an int. Events in event_timing and event_magnitude are used to compute slip rate. """
	d_total = 0.0;
	for i in range(len(event_timing)):
		d_total += util_general_functions.event_slip(event_magnitude[i]);   # from Nadeau and Johnson, 1998.
	if number_of_families>0:
		d_normalized = d_total / number_of_families; 
		slip_rate = round(100*d_normalized/(time_window[1]-time_window[0]))/100;  # cm/year
	else:
		slip_rate = np.NaN;
	return slip_rate;



def get_uncertainty(MyFamilies, time_window, family_code_number):
	# Use simple standard deviation of the slip rate distribution. 
	n_families_total = len(set(family_code_number));   # the unique number of families that we observed in the blob.
	slip_rate_distribution = [];  # this is the array that we build of slip rate estimates. 

	for k in range(len(MyFamilies.lon_array)):
	
		test_event_timing = [];
		test_event_magnitude = [];
		if k in family_code_number:
			for j in range(len(MyFamilies.event_times_array[k])):
				test_event_timing.append(MyFamilies.event_times_array[k][j]);
				test_event_magnitude.append(MyFamilies.mag_array[k][j]);	
			test_slip_rate = get_slip_rate(test_event_timing, test_event_magnitude, time_window, 1.0);		
			slip_rate_distribution.append(test_slip_rate);

	slip_rate_uncertainty = np.std(slip_rate_distribution);
	return slip_rate_uncertainty; 



def write_outputs(filename, avg_cov, n_families, avg_n, max_n, mean_timespan, n_short_families, slip_rate_cutoff, box_dims, slip_rate_boxes, unc_boxes):
	myfile=open(filename,'w');
	myfile.write("Number of families shorter than %.3f years = %d\n\n" % (slip_rate_cutoff, n_short_families));

	myfile.write("N_LONG_FAM = %d\n" % n_families);
	myfile.write("AVG_Events_per_family = %f events\n" % avg_n);
	myfile.write("MAX_Events_per_family = %.2f events\n" % max_n);
	myfile.write("AVG_COV = %f\n" % avg_cov);
	myfile.write("MEAN_Timespan = %f years\n\n\n" % mean_timespan);
	
	for i in range(len(box_dims)):
		box=box_dims[i];
		myfile.write("Box [%.2f,%.2f,%.2f,%.2f,%.2f,%.2f] slip rate = %f cm/year \n" % (box[0], box[1], box[2], box[3], box[4], box[5], slip_rate_boxes[i]));
		myfile.write("Box [%.2f,%.2f,%.2f,%.2f,%.2f,%.2f] slip_rate_unc = %f cm/year \n" % (box[0], box[1], box[2], box[3], box[4], box[5], unc_boxes[i]));
	myfile.close();
	return;



