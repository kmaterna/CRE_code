"""
This is code to take a list of families, and generate a related text file
that shows the depth, location, etc. of each event in each family. 
It's useful for plotting later. 
Sept 5, 2016
"""

import glob
import os
import util_general_functions

def main_program(time_window,families_list,families_summaries,station_location_file):

	family_infile=open(families_list,'r');
	outfile=open(families_summaries,'w');
	make_slip_rate_cutoff=1.5;  # years

	# Read a look-up table for directories	
	available_filelist=glob.glob("*_repeaters_list.txt");
	[stations,station_paths]=util_general_functions.get_dirs_for_station(station_location_file);

	# DOING THE MAJOR LOOP THROUGH REPEATER FAMILIES
	family_of_interest=0;
	start_time=time_window[0];
	end_time=time_window[1];


	# for each family...
	for line in family_infile:

		# --------- GRABBING DATA -------- #
		temp_event_names=[]
		event_names=[]
		temp=line.split()
		number_of_events=int(temp[3])
		for i in range(number_of_events):
			temp_event_names.append(temp[i+5]);
		
		event_names=util_general_functions.reorder_chronologically(temp_event_names);
		best_station= get_best_station_for_family(event_names,available_filelist);

		# grabbing useful information like time, magnitude, location
		magnitude=[]; depth=[]; event_time=[]; latitude=[]; longitude=[]; loc_type=[]; 

		# Get metadata for each event in the family. 
		for i in range(number_of_events):
			name=event_names[i]
			event_time.append(util_general_functions.get_float_time_from_name(name));
			
			# Go find the event file in the directories, searching in prescribed order, starting with best_station. 
			use_station=best_station;
			mydirectory=station_paths[stations.index(use_station)];

			foundfiles=glob.glob(mydirectory+use_station+".*."+name);
			if len(foundfiles) == 0:  # if we didn't find my sac file in best_station: 
				for station in stations:  # search around through other stations for that sac file. 
					mydirectory=station_paths[stations.index(station)];
					foundfiles=glob.glob(mydirectory+station+".*."+name);
					if len(foundfiles)==1:
						use_station=station;
						break;

			# Now that we know which station recorded this event, get its metadata. 
			filename=mydirectory+use_station+"*"+name;
			[lonx, latx, depx, magx, loc_typex] = util_general_functions.get_info_from_sac(filename);
			latitude.append(latx)
			longitude.append(lonx)
			loc_type.append(loc_typex)
			depth.append(depx)
			magnitude.append(magx)

		# GET THE SLIP FOR EACH EVENT
		ts=[]; slip=[]; 
		ts.append(start_time)
		slip.append(0)
		slip.append(0)

		slip_keep_level=0
		for i in range(number_of_events):
			d=util_general_functions.event_slip(magnitude[i]);  # get slip associated with each event
			slip_keep_level+=d;
			ts.append(event_time[i])
			ts.append(event_time[i])
			slip.append(slip_keep_level)
			slip.append(slip_keep_level)
		ts.append(end_time);
		slip_rate = round(100*max(slip)/(end_time-start_time))/100;


	    # WRITE RELEVANT INFORMATION FOR EACH FAMILY INTO SUMMARY FILE

		outfile.write("Family "+str(family_of_interest)+" with "+str(number_of_events)+" events: ");
		for i in range(number_of_events):
			outfile.write(event_names[i]);
			outfile.write(" ")
		for i in range(number_of_events):
			outfile.write(str(latitude[i]));
			outfile.write(" ")
		for i in range(number_of_events):
			outfile.write(str(longitude[i]));
			outfile.write(" ")
		for i in range(number_of_events):
			outfile.write(str(depth[i]));
			outfile.write(" ")
		for i in range(number_of_events):
			outfile.write(str(magnitude[i]));
			outfile.write(" ")
		outfile.write(str(best_station));
		outfile.write(" ");
		for i in range(number_of_events):
			outfile.write(str(loc_type[i]));   # does the location come from hypoDD?  ncss?  other?  
			outfile.write(" ")
		if event_time[number_of_events-1]-event_time[0] > make_slip_rate_cutoff:
			outfile.write(str(slip_rate));
		else:
			outfile.write("-1.0");  # -1.0 slip rate is an error code: we didn't compute a slip rate for that family. 
		outfile.write("\n")

		family_of_interest+=1;

	print "Summary of families made\n";
	family_infile.close();
	outfile.close();
	return;


def get_best_station_for_family(event_names,available_filelist):
	# FIGURE OUT WHICH STATION BEST RECORDED (MOST REPEATERS FOR) THIS FAMILY
	best_number_recorded=0;
	for x in available_filelist:   # once for each station 
		repeating_ev1=[];
		repeating_ev2=[];
		number_recorded=0;
		fileid=open(x,'r');
		fileid.readline()
		for line in fileid:
			temp=line.split()
			repeating_ev1.append(temp[0][-28:])
			repeating_ev2.append(temp[1][-28:])
		for y in event_names:
			if (y in repeating_ev1) or (y in repeating_ev2):
				number_recorded+=1;  # if we have recorded this event as a repeater at that station. 
		if number_recorded==len(event_names):
			best_station=x;
			fileid.close();
			break;
		elif number_recorded>best_number_recorded:
			best_station=x;	
		fileid.close();

	best_station=best_station.split("_")[0];
	return best_station; 


