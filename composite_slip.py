"""
MENDOCINO REPEATERS PROJECT
September 29, 2016

This script takes a series of repeating earthquake families and makes a composite time-series of slip. 

"""

import numpy as np 
import matplotlib.pyplot as plt
import util_general_functions


def main_program(time_window,Family_Summaries, mapping_data):
	min_lon=-124.75;
	max_lon=-124.25;
	min_lat=40.25;
	max_lat=40.36; # this gets the main cluster in the MTJ
	no_slip_rates_cutoff=1.0; # If the family spans less than this # of years, we don't consider it for slip rates. 

	start_time=time_window[0]
	end_time=time_window[1]

	[lat, lon, dep, timing, mag, n_seq]=read_file(Family_Summaries, no_slip_rates_cutoff);  # read the locations of the repeating earthquake families
	make_composite_plot(min_lon, max_lon, min_lat, max_lat, 18, 30, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, "Integrated Repeater Slip History Below 18 km",1);
	# make_map(min_lon, max_lon, min_lat, max_lat, 18, 30, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, "Integrated Repeater Slip History Below 18 km");
	make_composite_plot(min_lon, max_lon, min_lat, max_lat, 00, 18, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, "Integrated Repeater Slip History Above 18 km",0);
	# make_map(min_lon, max_lon, min_lat, max_lat, 00, 18, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, "Integrated Repeater Slip History Above 18 km");
	
	make_composite_plot(min_lon, max_lon, min_lat, max_lat, 0, 30, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, "Integrated Repeater Slip History All Depths",0);
	# make_map(min_lon, max_lon, min_lat, max_lat, 0, 30, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, "Integrated Repeater Slip History All Depths");

	print "Composite Slip Diagrams created!"
	return;



def read_file(families_summary, no_slip_rates_cutoff):
	# Starts with "Family_Summaries.txt"
	# Makes a list of latitude, longitude, depth, timing, magnitude, and family_number for each event in the family files. 
	input_file1=open(families_summary,'r')
	total_lat=[]; total_lon=[]; total_dep=[]; total_timing=[]; total_mag=[]; n_seq=[] # initialize arrays to zero. 
	
	for line in input_file1:
		# get timing and metadata for each family. 
		number_of_sequence=int(line.split()[1]);
		[fam_lon, fam_lat, fam_time, fam_mag, fam_depth, fam_loctype, mean_lon, mean_lat, mean_depth, slip_rate] = util_general_functions.read_family_line(line);

		if (fam_time[-1]-fam_time[0])>no_slip_rates_cutoff:  # if the family from start-to-finish 
		# spans more than some number of years, then we count it. 

			for i in range(len(fam_time)):
				total_lat.append(mean_lat)
				total_lon.append(mean_lon)
				total_dep.append(mean_depth)
				total_timing.append(fam_time[i])
				total_mag.append(fam_mag[i]);
				n_seq.append(number_of_sequence);

	input_file1.close();
	return [total_lat, total_lon, total_dep, total_timing, total_mag, n_seq]


def add_fancy_labels(axarr):

	# For the faster-slip period of time:
	starttime=2014.5;
	endtime=2015.03;
	level=100;
	axarr[1].plot([starttime, endtime],[level, level], color='black');
	axarr[1].plot([starttime, starttime],[level-10, level+10],color='black')
	axarr[1].plot([endtime, endtime],[level-10, level+10],color='black')
	axarr[1].text(2014.35,level-50," More\nActive")

	# For the slower-slip period of time: 
	starttime=2015.25;
	endtime=2016.89;
	level=100;
	axarr[1].plot([starttime, endtime], [level, level], color='black');
	axarr[1].plot([starttime, starttime],[level-10, level+10],color='black')
	axarr[1].plot([endtime, endtime],[level-10, level+10],color='black')
	axarr[1].text(starttime+0.2,level-20,"Less Active")

	return axarr;



def add_large_events(axarr, max_slip, start_time, end_time, mapping_data, min_mag):
	ax1=axarr[1];
	source_file=open(mapping_data+"/M5up.eq",'r')
	for line in source_file:
		temp=line.split()
		if temp[0]=='#':
			continue;
		time=float(temp[1]);
		mag=float(temp[-2])
		if (time>start_time) and (time<end_time):
			if mag>=min_mag:

				if temp[1]=="2010.09589041":
					plotting_epsilon=0.58;  # we need to offset the label because of two closely spaced events. 
					plotting_end="";
				elif temp[1]=="2010.02739726":
					plotting_epsilon=0.06;
					plotting_end=",";
				else:
					plotting_epsilon=0.04; # the label-plotting offset from the black line. 
					plotting_end="";
				
				ax1.plot([time,time],[0,max_slip],'--k')
				mag_str=str(temp[5])
				ax1.text(time+plotting_epsilon,0.3,"M"+mag_str[0:3]+plotting_end)
	source_file.close();

	return axarr;




def add_cumulative_seismicity(min_lon, max_lon, min_lat, max_lat, min_dep, max_dep, start_time, end_time, mapping_data, axarr):

	# Get seismicity from the rest of the newtork in this box. 
	network_time=[]  # the time series of when events happen in the box. 
	MINIMUM_MAG=0.5;
	input_file=open(mapping_data+"/hypodd.txyzm",'r');
	for line in input_file:
		temp=line.split();
		test_lon=float(temp[1]);
		test_lat=float(temp[2]);
		test_dep=float(temp[3]);
		test_mag=float(temp[4]);
		test_timing=float(temp[0]);
		if (test_lat<max_lat) and (test_lat>min_lat):
			if (test_lon<max_lon) and (test_lon>min_lon):
				if (test_dep<max_dep) and (test_dep>min_dep):
					if (test_mag>=MINIMUM_MAG):
						if (test_timing<end_time) and (test_timing>start_time):
							# Now we have an event in our region of interest; let's add it to the plot. 
							network_time.append(test_timing)
							#print test_timing;
	
	# Making the seismicity time series; this is the crazy staircase time series
	n_total_eq=[]
	total_eq_ts=[]
	total_eq_ts.append(start_time);
	n_cumulative=0;
	n_total_eq.append(0)
	n_total_eq.append(0)
	for i in range(len(network_time)):
		n_cumulative+=1;
		total_eq_ts.append(network_time[i])
		total_eq_ts.append(network_time[i])
		n_total_eq.append(n_cumulative)
		n_total_eq.append(n_cumulative)
	total_eq_ts.append(end_time);

	a1=axarr[1];  # go plot the cumulative seismicity on a different axis. 
	# Make the y-axis label and tick labels match the line color.
	for tl in a1.get_yticklabels():
	    tl.set_color('b')
	a1.set_ylabel("Averaged Repeater Slip (mm)",color='b');

	a2 = a1.twinx()
	a2.plot(total_eq_ts, n_total_eq, 'r')
	a2.set_ylabel('Total Earthquakes', color='r')
	for tl in a2.get_yticklabels():
	    tl.set_color('r')
	a1.set_xlim([start_time,end_time+0.5])
	a2.set_xlim([start_time,end_time+0.5])

	return axarr;



def make_composite_plot(min_lon, max_lon, min_lat, max_lat, min_dep, max_dep, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, plot_name, fancy_labels):

	plt.figure();
	g, axarr = plt.subplots(2, sharex=True)

	plot_timing=[]
	plot_mag=[]
	ts=[]
	slip=[]
	n_families=[]
	ts.append(start_time)
	slip_keep_level=0
	slip.append(0)
	slip.append(0)  # initializing things for the slip history. 

	# Get events that are within the box and time range of interest. 
	for i in range(len(lat)):
		if (lat[i]<max_lat) and (lat[i]>min_lat):
			if (lon[i]<max_lon) and (lon[i]>min_lon):
				if (dep[i]<max_dep) and (dep[i]>min_dep):
					if (timing[i]<end_time) and (timing[i]>start_time):
						# Now we have an event in our region and time of interest; let's add its slip to the plot. 
						plot_timing.append(timing[i])
						plot_mag.append(mag[i])
						n_families.append(n_seq[i])
						#if timing[i]>2015.07:
							#print n_seq[i];  # tell me which families were active after the M5.7 event. 

	number_of_families=len(set(n_families));  # the unique number of families that we observed in the blob.
	ordered_mag=[x for (y,x) in sorted(zip(plot_timing,plot_mag))]  # magnitude in an ordered list. 
	plot_timing.sort();

	# plot the slip associated with each event (Nadeau and Johnson, 1998); this is the crazy staircase
	for i in range(len(plot_timing)):
		d=util_general_functions.event_slip(ordered_mag[i]);  
		slip_keep_level+=(d*10.0) / number_of_families;  # *10 means millimeters
		ts.append(plot_timing[i])
		ts.append(plot_timing[i])
		slip.append(slip_keep_level)
		slip.append(slip_keep_level)
	ts.append(end_time);
	max_slip=max(slip);
	slip_rate = round(10*max(slip)/(end_time-start_time))/10;
	print number_of_families;

	# Writing output so that we can make an estimate of slip rate slope and uncertainty.
	# going to use scipy curve fitting. 
	outfile=open("slip_curve_"+str(min_dep)+"_"+str(max_dep)+"_km_depth.txt",'w');
	cumulative_slip=0;
	for i in range(len(plot_timing)):
		cumulative_slip+=util_general_functions.event_slip(ordered_mag[i])*10.0/number_of_families;  # *10 means millimeters
		outfile.write("%f %f \n" % (plot_timing[i],cumulative_slip) );
	outfile.close();


	# # GET THE SLIP RATE

	# Plot the lollipop diagram 
	a1=axarr[0];
	for i in range(len(plot_timing)):
		a1.plot([plot_timing[i], plot_timing[i]],[0,ordered_mag[i]-0.1],'k')
		a1.scatter(plot_timing[i], ordered_mag[i],c='black');
	a1.get_xaxis().get_major_formatter().set_useOffset(False)
	a1.set_xlim([start_time-0.2,end_time+0.2])
	a1.set_ylabel("Magnitude");
	a1.set_ylim([0,5]);		
	a1.set_title(plot_name);

	# Plot the slip histories. 
	a1=axarr[1];
	a1.plot(ts, slip,'b')
	a1.get_xaxis().get_major_formatter().set_useOffset(False)
	a1.set_xlim([start_time,end_time+0.5])
	a1.set_title("Slip History: Averaged Slip Rate = "+ str(slip_rate)+" mm / yr ["+str(number_of_families)+" sequences]");
	a1.set_ylim([-2.2, max(slip)+0.2]);

	axarr=add_cumulative_seismicity(min_lon, max_lon, min_lat, max_lat, min_dep, max_dep, start_time, end_time, mapping_data, axarr);
	axarr=add_large_events(axarr,max_slip, start_time, end_time, mapping_data, 5.5);  # min_mag is where we start notating events. 

	if fancy_labels==1:
		axarr=add_fancy_labels(axarr);

	#plt.xlim([2013.7, 2015.0])
	plt.savefig(plot_name+".jpg")
	plt.close()
	return;


def make_map(min_lon, max_lon, min_lat, max_lat, min_dep, max_dep, lat, lon, dep, timing, mag, n_seq, start_time, end_time, mapping_data, plot_name):
	
	# Getting the large events. 
	source_file=open(mapping_data+"/M5up.eq",'r')
	xmin=-125.6
	xmax=-123.4
	ymin=39.4
	ymax=41.4
	big_time=[]
	big_mag=[]
	big_lon=[]
	big_lat=[]
	big_dep=[]
	for line in source_file:
		temp=line.split()
		if temp[0]=='#':
			break;
		test_time=float(temp[1]);
		test_mag=float(temp[-2]);
		if (test_time>start_time) and (test_time<end_time):
		#if (test_time>1984.0) and (test_time<end_time):
			if test_mag>5.5:
				big_time.append(float(temp[1]));
				big_mag.append(float(temp[-2]));
				big_lon.append(float(temp[3]));
				big_lat.append(float(temp[2]));
				big_dep.append(float(temp[4]));
	source_file.close();

	fig=plt.figure();
	ax0 = plt.subplot2grid((4,1), (0,0), rowspan=3)
	ax1 = plt.subplot2grid((4,1), (3,0), rowspan=1)  # 3 rows, 1 column. Second coordinates are top left corner position.


	# Making map view. 
	ax0.plot(lon,lat,'.')
	for x in range(len(lon)):
		ax0.text(lon[x],lat[x],str(n_seq[x]),fontsize=8);
	ax0.plot([min_lon,max_lon,max_lon,min_lon,min_lon],[min_lat,min_lat,max_lat,max_lat,min_lat],'r'); # draw a rectangle 
	for i in range(len(big_lon)):
		if (big_lon[i]>xmin) and (big_lon[i]<xmax):
			ax0.text(big_lon[i],big_lat[i],str(big_time[i])[0:4]+'M'+str(big_mag[i]));
			if (big_lon[i]>min_lon) and (big_lon[i]<max_lon) and (big_lat[i]>min_lat) and (big_lat[i]<max_lat) and (big_dep[i]>min_dep) and (big_dep[i]<max_dep):
				ax0.scatter(big_lon[i],big_lat[i],c='b');
			else:
				ax0.scatter(big_lon[i],big_lat[i],c='c');
	[ca_lon,ca_lat]=np.loadtxt(mapping_data+"/CA_bdr",unpack=True);
	ax0.plot(ca_lon,ca_lat,'k');
	ax0.set_title("Map of Repeaters and Background Events");
	ax0.set_xlim([xmin, xmax])
	ax0.set_ylim([ymin, ymax])
	ax0.set_ylabel("Latitude")
	
	# Making depth view. 
	ax1.plot(lon,dep,'.')
	ax1.plot([min_lon,min_lon,max_lon,max_lon,min_lon],[min_dep,max_dep,max_dep,min_dep,min_dep],'r')
	plt.scatter(big_lon,big_dep,c='m');
	for i in range(len(big_lon)):
		if (big_lon[i]>xmin) and (big_lon[i]<xmax):
			ax1.text(big_lon[i],big_dep[i],str(big_time[i])[0:6]+'M'+str(big_mag[i]));
			if (big_lon[i]>min_lon) and (big_lon[i]<max_lon) and (big_dep[i]>min_dep) and (big_dep[i]<max_dep) and (big_lat[i]>min_lat) and (big_lat[i]<max_lat):
				ax1.scatter(big_lon[i],big_dep[i],c='b');
			else:
				ax1.scatter(big_lon[i],big_dep[i],c='c');
	plt.gca().invert_yaxis();
	ax1.set_xlabel("Longitude")
	ax1.set_ylabel("Depth (km)")
	ax1.set_xlim([xmin, xmax])
	plt.savefig("Map_View_"+plot_name+".jpg");
	plt.close();








