""" 
MENDOCINO REPEATERS PROJECT
This is the all-important definition of repeaters, from criteria on Waveform Similarity and Signal to Noise Ratio. 
Those criteria are defined in the beginning of this script. 
When we define the cutoff = 0.95, we get a few great examples of repeating earthquakes. 
Place your coherence and snr files into a directory named after the station.  Set the station and choose 
your physical parameters.  Then run it!

"""

import numpy as np
import collections
from subprocess import call 
import os 
import make_histograms_plots

Params=collections.namedtuple('Params',[
	'station_name',
	'metric','cutoff','statistic',
	'freq_method',
	'snr_cutoff',
	'Minimum_frequency_width',
	'magnitude_difference_tolerance',
	'min_freq_inst','max_freq_inst',
	'lowest_chosen_frequency','highest_chosen_frequency',
	'plot_arg',
	'data_input_file','snr_input_file',
	'CRE_out_filename','total_out_filename','output_dir',
	'station_coords','raw_sac_dir']);

Candidate_data=collections.namedtuple('Candidate_data',[
	'event1name','event2name',
	'ev1mag','ev1dist',
	'ev2mag','ev2dist',
	'xcorr','coh_array']);

SNR_data=collections.namedtuple('SNR_data',[
	'event1name','event2name',
	'f_axis1','snr1',
	'f_axis2','snr2']);

Results_summary=collections.namedtuple('Results_summary',[
	'name1','name2',
	'xcorr_value','coh_value','min_freq','max_freq',
	'dist1','dist2',
	'mag1','mag2'])


def define_repeaters(station_name, station_location_file, metric, cutoff, statistic='median', freq_method='hard_coded', max_frequency=25.0, snr_cutoff=5.0, Minimum_frequency_width=5.0, plot_all=0):
	MyParams=configure(station_name, station_location_file, metric, cutoff, statistic, freq_method, max_frequency, snr_cutoff, Minimum_frequency_width, plot_all);
	[Candidates_coh, Candidates_snr] = inputs(MyParams);
	[Total_results, CRE_results] = compute(MyParams, Candidates_coh, Candidates_snr);
	outputs(MyParams, Total_results, CRE_results);
	return;


# ------------------ CONFIGURE ------------------- # 

def configure(station_name, station_location_file, metric, cutoff, statistic, freq_method, highest_chosen_frequency, snr_cutoff, Minimum_frequency_width, plot_all):

	# Decisions that you rarely change:
	magnitude_difference_tolerance = 3.0;    # We ignore event pairs that have very disparate magnitudes.  

	# Frequencies we have in the data file, based on sampling frequency (this is used to interpret the coherence in data_input_file, 
	# which does not come with a frequency label)
	min_freq_inst=0.0;
	max_freq_inst=50.0;
	lowest_chosen_frequency=1;    # This is a CHOICE.  Set to 0-50 if you want every frequency. 

	four_char=station_name;
	if len(station_name)==3:
		four_char=station_name+"_"
	
	# This is where we have put the results of the C calculation with all the candidates (xcorr > 0.60). 
	data_input_file = "CRE_Candidates/"+four_char+"-above_cutoff_results.txt"
	snr_input_file = "CRE_Candidates/"+four_char+"-snr_results.txt"	

	# This is where we want to put the CRE detections for each station
	output_dir1="CREs_by_station/"
	output_dir_inner="CREs_by_station/"+station_name+"/";
	CRE_out_filename=output_dir_inner+station_name+"_repeaters_list.txt";
	total_out_filename=output_dir_inner+station_name+"_total_list.txt";

	# If we don't have a directory for this station: 
	call(['mkdir','-p',output_dir1],shell=False);
	call(['mkdir','-p',output_dir_inner],shell=False);

	# Get the station directory and location info. 
	ifile=open(station_location_file,'r');
	for line in ifile:
		temp=line.split();
		if temp[0]==station_name:
			station_coords=[float(temp[1]), float(temp[2])];
			raw_sac_dir=temp[3];
	ifile.close();

	MyParams=Params(station_name=station_name,metric=metric,cutoff=cutoff,statistic=statistic,freq_method=freq_method,snr_cutoff=snr_cutoff,
		Minimum_frequency_width=Minimum_frequency_width,magnitude_difference_tolerance=magnitude_difference_tolerance,
		min_freq_inst=min_freq_inst,max_freq_inst=max_freq_inst,lowest_chosen_frequency=lowest_chosen_frequency,highest_chosen_frequency=highest_chosen_frequency,
		plot_arg=plot_all,data_input_file=data_input_file, snr_input_file=snr_input_file, CRE_out_filename=CRE_out_filename,total_out_filename=total_out_filename,
		output_dir=output_dir_inner,station_coords=station_coords,raw_sac_dir=raw_sac_dir);

	print_out_statements(MyParams);
	return MyParams;


def print_out_statements(MyParams):
	if MyParams.metric=="coh":
		print "\n-------------------------------------"
		print "DEFINING REPEATING EARTHQUAKES FOR STATION "+MyParams.station_name
		print "\nYou have chosen to define repeaters as: "
		print "The "+MyParams.statistic.upper()+" of all coherence values where SNR > "+str(MyParams.snr_cutoff)+"."
		print "Coherence cutoff = "+str(MyParams.cutoff)+"."
		print "Available frequencies = "+str(MyParams.lowest_chosen_frequency)+" to "+str(MyParams.highest_chosen_frequency)+" Hz."
		print "Repeaters must have magnitudes less than "+str(MyParams.magnitude_difference_tolerance)+" magnitude units apart."
		if MyParams.plot_arg==1:
			print "You have chosen to view plots of all of your repeaters.  "
		print "-------------------------------------\n"
	elif MyParams.metric=="corr":
		print "\n-------------------------------------"
		print "DEFINING REPEATING EARTHQUAKES FOR STATION "+MyParams.station_name
		print "\nYou have chosen to define repeaters as: "
		print "XCorr cutoff = "+str(MyParams.cutoff)+"."
		if MyParams.plot_arg==1:
			print "You have chosen to view plots of all of your repeaters.  "
		print "-------------------------------------\n"
	else:
		print "\n-------------------------------------"
		print "ERROR!  Your metric is not valid.  Please choose metric from the choices: "
		print "[corr, coh]"
		print "-------------------------------------\n"
	return;



# ------------------ INPUTS ------------------- # 

def inputs(MyParams):

	Candidates_coh = read_data_input_file(MyParams.data_input_file);
	Candidates_snr = read_snr_input_file(MyParams.snr_input_file);
	return [Candidates_coh, Candidates_snr];


def read_data_input_file(filename):
	ifile=open(filename,'r');
	event1name=[]; event2name=[]; ev1mag=[]; ev2mag=[]; ev1dist=[]; ev2dist=[]; xcorr=[]; coh_collection=[];
	for line in ifile:
		coh=[];
		temp=line.split();
		event1name.append(temp[0]); 
		event2name.append(temp[1]);
		ev1mag.append(float(temp[2]));
		ev1dist.append(float(temp[3]));
		ev2mag.append(float(temp[4]));
		ev2dist.append(float(temp[5]));
		xcorr.append(float(temp[6]));
		for i in range(7, len(temp)):
			coh.append(float(temp[i]))
		coh_collection.append(coh);
	ifile.close();
	Candidates_coh = Candidate_data(event1name=event1name, event2name=event2name, ev1mag=ev1mag, ev1dist=ev1dist, ev2mag=ev2mag, ev2dist=ev2dist, xcorr=xcorr, coh_array=coh_collection);
	return Candidates_coh;

def read_snr_input_file(filename):
	# Read in the SNR information. 
	
	ifile=open(filename,'r');
	f_axis1=[]; snr1=[]; 
	f_axis2=[]; snr2=[];
	event1name=[]; event2name=[];

	# Get SNR for that same event pair from the snr file
	for line in ifile:
		temp=line.split();
		event1name.append(temp[0])
		event2name.append(temp[1])
	
		counter = 2
		event1snr_freq, counter = read_array_from_tokens(temp, counter)
		event1snr, counter 		= read_array_from_tokens(temp, counter)
		event2snr_freq, counter = read_array_from_tokens(temp, counter)
		event2snr, counter 		= read_array_from_tokens(temp, counter)
		f_axis1.append(event1snr_freq);
		snr1.append(event1snr);
		f_axis2.append(event2snr_freq);
		snr2.append(event2snr);

	ifile.close();
	Candidates_snr = SNR_data(event1name=event1name, event2name=event2name, f_axis1=f_axis1, snr1=snr1, f_axis2=f_axis2, snr2=snr2);
	return Candidates_snr;

# Get the frequencies and SNR values into memory
def read_array_from_tokens(tokens, start):
	output = []
	counter = start
	for x in range(counter,len(tokens)):
		item=tokens[x]
		counter+=1
		if item=="[]":
			break;
		if item[0]=='[':
			output.append(float(item[1:-1]))
		elif item[-1]==']':
			output.append(float(item[0:-1]))
			break
		else:
			output.append(float(item[0:-1]))
	return (output, counter)


# ------------------ COMPUTE ------------------- # 

def compute(MyParams, Candidates_coh, Candidates_snr):

	coh_all=[];     xcorr_all=[];
	name1_all=[];   name2_all=[];
	dist1_all=[];   mag1_all=[];
	dist2_all=[];   mag2_all=[];
	min_freq_all=[]; max_freq_all=[];
	coh_cre=[];     xcorr_cre=[];
	name1_cre=[];   name2_cre=[];
	dist1_cre=[];   mag1_cre=[];
	dist2_cre=[];   mag2_cre=[];
	min_freq_cre=[]; max_freq_cre=[];
	repeater_nflag=0;
	low_signal_counter=0;
		
	for i in range(len(Candidates_coh.event1name)):

		# CHECKS AND BALANCES:
		if Candidates_coh.event1name[i] != Candidates_snr.event1name[i]:
			print("We have a problem! "+Candidates_coh.event1name[i]+" and "+Candidates_snr.event1name[i]+" do not match. Go check the input files!\n")
			continue
		if Candidates_coh.event2name[i] != Candidates_snr.event2name[i]:
			print("We have a problem! "+Candidates_coh.event2name[i]+" and "+Candidates_snr.event2name[i]+" do not match. Go check the input files!\n")
			continue
		distance=(Candidates_coh.ev1dist[i]+Candidates_coh.ev2dist[i])/2   # mean distance
		if Candidates_coh.ev1dist[i]>3000:
			distance=Candidates_coh.ev2dist[i];
		if Candidates_coh.ev2dist[i]>3000:
			distance=Candidates_coh.ev1dist[i];
		if Candidates_coh.ev1dist[i]>3000 and Candidates_coh.ev2dist[i]>3000:
			print("We have a problem!  "+Candidates_coh.event1name[i]+" and "+Candidates_coh.event2name[i]+" are both located too far away.\n");
			distance=25;   # THIS IS A TOTAL GUESS.  WE FOUND ONE EVENT WHERE THIS IS NEEDED.  


		# Determined the maximum frequency we're looking at for a pair of events (Mean magnitude only, nothing to do with SNR);
		if MyParams.metric=="corr":  # these parameters are set to default values if using corr, because they don't matter. 
			min_freq=MyParams.min_freq_inst;
			max_freq=MyParams.max_freq_inst;
		elif MyParams.freq_method=="hard_coded":
			min_freq=1;
			max_freq=MyParams.highest_chosen_frequency;
		elif MyParams.freq_method=="snr_based":  # Now determine the available frequencies based on SNR. 
			min_freq, max_freq = determine_freqs_by_SNR(Candidates_snr.f_axis1[i], Candidates_snr.snr1[i], Candidates_snr.f_axis2[i], Candidates_snr.snr2[i], MyParams.snr_cutoff, MyParams.highest_chosen_frequency, MyParams.lowest_chosen_frequency);
			#print "Minimum and maximum frequencies = %f Hz, %f Hz" %(min_freq, max_freq)
		elif MyParams.freq_method=="magnitude_based":
			min_freq=1; 
			max_freq = determine_freqs_by_magnitude(M, MyParams.highest_chosen_frequency); 

		# Cut to the range of useful frequencies.  	
		coh=Candidates_coh.coh_array[i];
		index_1=int(np.round(len(coh)*(min_freq-MyParams.min_freq_inst)/(MyParams.max_freq_inst-MyParams.min_freq_inst)));
		index_top=int(np.round(len(coh)*(max_freq-MyParams.min_freq_inst)/(MyParams.max_freq_inst-MyParams.min_freq_inst)));
		# pathological case in which the two indeces are the same:
		if index_1==index_top:
			index_top+=1;

		# !!!!!! Define the measure of coherence (usually mean or median)
		if MyParams.statistic=='mean':
			coh_statistic=np.mean(coh[index_1:index_top])
		if MyParams.statistic=='median':
			coh_statistic=np.median(coh[index_1:index_top])
		if str(coh_statistic)=='nan':
			print "OMG NAN!!!"		


		if (max_freq - min_freq) <=MyParams.Minimum_frequency_width:  # these are events where there's very little usable signal anyway
			low_signal_counter+=1; 
			continue;
		else:
			# Summary statistics for all comparisons (for making plots)
			name1_all.append(Candidates_coh.event1name[i])
			name2_all.append(Candidates_coh.event2name[i])
			coh_all.append(coh_statistic)
			xcorr_all.append(Candidates_coh.xcorr[i])
			dist1_all.append(Candidates_coh.ev1dist[i])
			dist2_all.append(Candidates_coh.ev2dist[i])
			mag1_all.append(Candidates_coh.ev1mag[i])
			mag2_all.append(Candidates_coh.ev2mag[i])
			min_freq_all.append(min_freq);
			max_freq_all.append(max_freq);			
			
			if abs(Candidates_coh.ev1mag[i]-Candidates_coh.ev2mag[i])<=MyParams.magnitude_difference_tolerance:  # if we have similar magnitudes
				if MyParams.metric=="coh":
					similarity_value=coh_statistic;
				elif MyParams.metric=="corr":
					similarity_value=Candidates_coh.xcorr[i]
			
				# WE HAVE A REPEATER!!!  WRITE IT DOWN!!! 
				if similarity_value>MyParams.cutoff:
					name1_cre.append(Candidates_coh.event1name[i])
					name2_cre.append(Candidates_coh.event2name[i])
					coh_cre.append(coh_statistic)
					xcorr_cre.append(Candidates_coh.xcorr[i])
					dist1_cre.append(Candidates_coh.ev1dist[i])
					dist2_cre.append(Candidates_coh.ev2dist[i])
					mag1_cre.append(Candidates_coh.ev1mag[i])
					mag2_cre.append(Candidates_coh.ev2mag[i])
					min_freq_cre.append(min_freq);
					max_freq_cre.append(max_freq);
					repeater_nflag += 1;
				# if coh_statistic>0.90 and xcorr<0.80:
					# print "Anomaly: "+event1_data+ " "+event2_data;
	
	Total_results=Results_summary(name1=name1_all, name2=name2_all, xcorr_value=xcorr_all, coh_value=coh_all, min_freq=min_freq_all, max_freq=max_freq_all, dist1=dist1_all, dist2=dist2_all, mag1=mag1_all, mag2=mag2_all);
	CRE_results=Results_summary(name1=name1_cre, name2=name2_cre, xcorr_value=xcorr_cre, coh_value=coh_cre, min_freq=min_freq_cre, max_freq=max_freq_cre, dist1=dist1_cre, dist2=dist2_cre, mag1=mag1_cre, mag2=mag2_cre);

	print "\nSTATION "+MyParams.station_name+":\n"
	print str(len(CRE_results.name1))+" Repeaters Found"
	print "Out of " + str(len(Total_results.name1))+" possible event pairs."
	print str(low_signal_counter)+" event pairs had low SNR (below SNR="+str(MyParams.snr_cutoff)+").\n"

	return [Total_results, CRE_results];


def determine_freqs_by_magnitude(mag, highest_chosen_frequency):
	""" This determines the maximum frequency we would ever look at, based on the mean magnitude of the events. 
	Returns frequency in Hz. """
	highest_frequency=highest_chosen_frequency;
	if mag > 2:
		highest_frequency = 16; # Hz
	if mag > 3:
		highest_frequency = 10; # Hz
	if mag > 4:
		highest_frequency = 8; # Hz
	return highest_frequency;



def determine_freqs_by_SNR(freq1, snr1, freq2, snr2, cutoff, max_frequency, lowest_chosen_frequency):
	# Based on where both SNR values are high, this function defines the range of frequencies we're looking over. 
	# Returns frequencies in Hz.  
	# The max_frequency may be magnitude-dependent. 
	gt_cutoff1=[freq1[i] for i in range(len(snr1)) if snr1[i]>cutoff and freq1[i]<max_frequency]
	gt_cutoff2=[freq2[i] for i in range(len(snr2)) if snr2[i]>cutoff and freq2[i]<max_frequency]
	overlap = np.intersect1d(gt_cutoff1, gt_cutoff2)
	if len(overlap)<=1:  # If we have events with little usable signal
		minimum = lowest_chosen_frequency;
		maximum = lowest_chosen_frequency;
	else:
		minimum=min(overlap)
		maximum=max(overlap)
	if minimum<lowest_chosen_frequency:
		minimum=lowest_chosen_frequency;
	if maximum<lowest_chosen_frequency:
		maximum=lowest_chosen_frequency;

	return minimum, maximum;   # these will probably be different, but may be the same number. 



# ------------------ OUTPUTS ------------------- # 

def outputs(MyParams, Total_results, CRE_results):

	Header_string="Choices and Parameters: cutoff="+str(MyParams.cutoff)+"; snr_cutoff="+str(MyParams.snr_cutoff)+"; magnitude_difference="+str(MyParams.magnitude_difference_tolerance)+"; statistic = "+MyParams.statistic+"; Available frequencies = "+str(MyParams.lowest_chosen_frequency)+" to "+str(MyParams.highest_chosen_frequency)+".\n"
	ofile=open(MyParams.total_out_filename,'w');
	ofile.write(Header_string);
	for i in range(len(Total_results.name1)):
		# write to "total_list" file no matter what.  	
		time_ev1=get_time(Total_results.name1[i]);
		time_ev2=get_time(Total_results.name2[i]);
		if time_ev2>=time_ev1:  # the case where event2 is later in time. 
			ofile.write("%s %s %f %f %f %f %f %f %f %f \n" % (Total_results.name1[i],Total_results.name2[i],Total_results.xcorr_value[i],Total_results.coh_value[i],
				Total_results.min_freq[i],Total_results.max_freq[i], Total_results.mag1[i], Total_results.dist1[i], Total_results.mag2[i], Total_results.dist2[i]));
		if time_ev1>time_ev2:   # the case where event1 is later in time (unusual one)
			ofile.write("%s %s %f %f %f %f %f %f %f %f \n" % (Total_results.name2[i],Total_results.name1[i],Total_results.xcorr_value[i],Total_results.coh_value[i],
				Total_results.min_freq[i],Total_results.max_freq[i], Total_results.mag2[i], Total_results.dist2[i], Total_results.mag1[i], Total_results.dist1[i]));
	ofile.close();

	ofile=open(MyParams.CRE_out_filename,'w');
	ofile.write(Header_string);
	for i in range(len(CRE_results.name1)):
		# write to "total_list" file no matter what.  	
		time_ev1=get_time(CRE_results.name1[i]);
		time_ev2=get_time(CRE_results.name2[i]);
		if time_ev2>=time_ev1:  # the case where event2 is later in time. 
			ofile.write("%s %s %f %f %f %f %f %f %f %f \n" % (CRE_results.name1[i],CRE_results.name2[i],CRE_results.xcorr_value[i],CRE_results.coh_value[i],
				CRE_results.min_freq[i],CRE_results.max_freq[i], CRE_results.mag1[i], CRE_results.dist1[i], CRE_results.mag2[i], CRE_results.dist2[i]));
		if time_ev1>time_ev2:   # the case where event1 is later in time (unusual one)
			ofile.write("%s %s %f %f %f %f %f %f %f %f \n" % (CRE_results.name2[i],CRE_results.name1[i],CRE_results.xcorr_value[i],CRE_results.coh_value[i],
				CRE_results.min_freq[i],CRE_results.max_freq[i], CRE_results.mag2[i], CRE_results.dist2[i], CRE_results.mag1[i], CRE_results.dist1[i]));
	ofile.close();

	
	# # ------------- PLOTTING ------------ #
	if len(CRE_results.name1)>0:

		make_histograms_plots.make_repeaters_map(MyParams);   # making a gmt plot of repeating event locations. 
		
		if MyParams.plot_arg:
			make_histograms_plots.make_repeater_seismograms(MyParams);

		if len(CRE_results.name1)>1:
			# Make histograms and scatter plots of coherence values / cross correlation values
			make_histograms_plots.make_coherence_histogram(Total_results.coh_value, CRE_results.coh_value, MyParams.station_name,MyParams.output_dir);
			make_histograms_plots.make_xcorr_histogram(Total_results.xcorr_value, CRE_results.xcorr_value,MyParams.station_name,MyParams.output_dir);
			make_histograms_plots.make_scatter_coh_xcorr(Total_results.xcorr_value, Total_results.coh_value, CRE_results.xcorr_value, CRE_results.coh_value, Total_results.dist1, MyParams.station_name,MyParams.output_dir);

			# Make summary histograms of the repeaters we've found. 
			make_histograms_plots.make_inter_event_time_histogram(MyParams.station_name,MyParams.CRE_out_filename,MyParams.output_dir);   # making inter-event time histogram. 
			make_histograms_plots.make_mag_dist_histograms(MyParams.station_name,MyParams.CRE_out_filename,MyParams.output_dir);   # making magnitudes histogram. 
		
		elif len(CRE_results.name1)==0:
			print("No Repeaters Found: Cannot Make Plots!")
	return; 


	# ------------ UTILITY FUNCTIONS ---------- #
def get_time(evname):
	# event name is formatted like: B046.PB.EHZ..D.2016.238.040926.72684751.sac
	# we want its decimal year. 
	year=float(evname[-28:-24])
	day=float(evname[-23:-20])
	hour=float(evname[-19:-17])
	minute=float(evname[-17:-15])
	second=float(evname[-15:-13])
	decimal_time=year+(day/365.24)+((60*60*hour+60*minute+second)/(60*60*24*365.24));
	return decimal_time;

def get_time_doy(evname):
	# event name is formatted like: B046.PB.EHZ..D.2016.238.040926.72684751.sac.  We want YYYYDDD. 
	year=evname[-28:-24];
	day=evname[-23:-20];
	return year+day;

