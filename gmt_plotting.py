"""
MENDOCINO REPEATERS PROJECT
Feb 2015

This code takes the families from Family_Summaries with longitudes, latitudes, and slip rates.
Then it calls GMT to make a variety of plots of families and individual repeater pairs. 
Makes about 10 GMT plots. 

"""

from subprocess import call
import glob
import util_general_functions



def main_program(Network_repeaters_list, families_summaries, station_locations, mapping_code, mapping_data):
	pairwise_gmt(Network_repeaters_list, station_locations, mapping_code, mapping_data);
	#familywise_gmt(families_summaries, mapping_code, mapping_data);  # right now this isn't working, since I haven't fixed all the GMT scripts to use relative paths yet. 
	cleaning_up();
	return;


def pairwise_gmt(repeaters_file,station_location_file, mapping_code, mapping_data):
	hypodd_file1="event_locations_first_hypodd.txt"
	hypodd_file2="event_locations_second_hypodd.txt"
	ncss_file1="event_locations_first_ncss.txt"
	ncss_file2="event_locations_second_ncss.txt"
	xyzm_file_hypodd="repeaters_xyzm_hypodd.txt"
	xyzm_file_ncss="repeaters_xyzm_ncss.txt"
	connectors_file="event_connectors.txt"

	my_file=open(repeaters_file,'r');
	pos_file_1=open(hypodd_file1,'w+');
	pos_file_2=open(hypodd_file2,'w+');
	worse_pos_file_1=open(ncss_file1,'w+');
	worse_pos_file_2=open(ncss_file2,'w+');
	connectors_file=open(connectors_file,'w+');
	xyzm_hypodd=open(xyzm_file_hypodd,'w+');
	xyzm_ncss=open(xyzm_file_ncss,'w+');
	
	# size of event dots on GMT:
	size1=0.20
	size2=0.10

	[stations,station_paths]=util_general_functions.get_dirs_for_station(station_location_file);

	# Read in lists for event1 and event2
	event1=[]
	event2=[]
	station=[]
	my_file.readline();
	for line in my_file:
			temp=line.split()
			event1.append(temp[0])
			event2.append(temp[1])
			temp_station=temp[2];
			if temp_station[-1]=='_':
				temp_station=temp_station[0:3]; # Remove the trailing underscore. 
			station.append(temp_station)


	# Read in position data for event1 and event2
	for i in range(len(event1)):
		mydirectory=station_paths[stations.index(station[i])];
		event1_name=mydirectory+"*"+event1[i];
		[longitude1, latitude1, depth, magnitude, loc_type] = util_general_functions.get_info_from_sac(event1_name);

		if loc_type[0:6]=="hypodd":
			pos_file_1.write(str(longitude1)+" "+str(latitude1)+" "+str(size1)+"\n");
			xyzm_hypodd.write(str(longitude1)+" "+str(latitude1)+" "+str(depth)+" "+str(magnitude)+"\n");
		else:
			worse_pos_file_1.write(str(longitude1)+" "+str(latitude1)+" "+str(size1+0.03)+"\n");
			xyzm_ncss.write(str(longitude1)+" "+str(latitude1)+" "+str(depth)+" "+str(magnitude)+"\n");
			# For these non-hypoDD events, I'm making the size larger because it's going to be plotted in a square, 
			# which is naturally smaller.

		event2_name=mydirectory+"*"+event2[i];
		[longitude2, latitude2, depth, magnitude, loc_type] = util_general_functions.get_info_from_sac(event2_name);
		if loc_type[0:6]=="hypodd":
			pos_file_2.write(str(longitude2)+" "+str(latitude2)+" "+str(size2)+"\n");
			xyzm_hypodd.write(str(longitude2)+" "+str(latitude2)+" "+str(depth)+" "+str(magnitude)+"\n");
		else:
			worse_pos_file_2.write(str(longitude2)+" "+str(latitude2)+" "+str(size2+0.05)+"\n");
			xyzm_ncss.write(str(longitude2)+" "+str(latitude2)+" "+str(depth)+" "+str(magnitude)+"\n");

		# write the connector file
		connectors_file.write(str(longitude1)+" "+str(latitude1)+"\n");
		connectors_file.write(str(longitude2)+" "+str(latitude2)+"\n");
		connectors_file.write("\n>\n");

	my_file.close()
	pos_file_1.close()
	pos_file_2.close()
	worse_pos_file_1.close()
	worse_pos_file_2.close()
	connectors_file.close()
	xyzm_hypodd.close();
	xyzm_ncss.close();

	call(mapping_code+'/map_view_repeaters.gmt 0 0 0 '+mapping_data,shell=True)  # this is to allow the script to handle both single-station and multi-station files. 
	call(mapping_code+'/xyzm_repeaters.gmt '+mapping_data,shell=True)

	print "Maps of repeating earthquakes generated!"
	return;




def familywise_gmt(families_summaries):
	input_file=open(families_summaries,'r');
	outputfile1=open("Families_xy_hypodd.txt",'w');
	outputfile2=open("Families_xy_ncss.txt",'w');
	depthfile1=open("Families_xz_hypodd.txt",'w');
	depthfile2=open("Families_xz_ncss.txt",'w');
	outputfile3=open("Families_xyz_hypodd.txt",'w');
	outputfile4=open("Families_xyz_ncss.txt",'w');
	output_nums=open("Families_number_of_events.txt",'w');

	for line in input_file:

		[fam_lon, fam_lat, fam_time, fam_mag, fam_depth, fam_loctype, mean_lon, mean_lat, mean_depth, slip_rate] = util_general_functions.read_family_line(line);
		
		if slip_rate>-1.0:
			if "hypodd" in fam_loctype:
				# Writing to output file if we have a good slip rate: 
				outputfile1.write(str(mean_lon)+" "+str(mean_lat)+" "+str(slip_rate)+" \n");
				depthfile1.write(str(mean_lon)+" -"+str(mean_depth)+" "+str(slip_rate)+"\n");
				outputfile3.write(str(mean_lon)+" "+str(mean_lat)+" -"+str(mean_depth)+" "+str(slip_rate)+"\n");	
			else:	
				outputfile2.write(str(mean_lon)+" "+str(mean_lat)+" "+str(slip_rate)+" \n");
				depthfile2.write(str(mean_lon)+" -"+str(mean_depth)+" "+str(slip_rate)+"\n");
				outputfile4.write(str(mean_lon)+" "+str(mean_lat)+" -"+str(mean_depth)+" "+str(slip_rate)+"\n");				
			output_nums.write(str(mean_lon)+" "+str(mean_lat)+" "+str(mean_depth)+" "+str(len(fam_lon))+" \n");

	depthfile1.close();
	outputfile1.close();
	depthfile2.close();
	outputfile2.close();
	outputfile3.close();
	outputfile4.close();
	output_nums.close();
	input_file.close();

	call(mapping_code+'/microseismicity_map.gmt')   # makes the depth profile of red dots for repeaters. 
	call(mapping_code+'/zoomed_in_slip_depth.gmt')  # makes the depth profile with colored dots for slip rate
	call(mapping_code+'/zoomed_in_num_depth.gmt')  # makes the depth profile with colored dots for slip rate
	call(mapping_code+'/very_zoomed_in_slip_depth.gmt')  # makes the depth profile with colored dots for slip rate. 
	call(mapping_code+'/cross_section_plus_historical.gmt')  # makes the depth profile and adds recent M5 events. 
	call(mapping_code+'/very_zoomed_in_plus_historical.gmt')  # makes the zoomed in graph with M5s. 
	call(mapping_code+'/slip_rates.gmt')
	call(mapping_code+'zoomed_in_slip_rates.gmt')

	return;


def cleaning_up():
	clean_up_files_matching("Topo*");
	clean_up_files_matching("*.cpt");
	clean_up_files_matching("!*.tmp");
	clean_up_files_matching("*.history");
	clean_up_files_matching("Families*_ncss.txt");
	clean_up_files_matching("Families*_hypodd.txt");
	clean_up_files_matching("event_locations_*_hypodd.txt");
	clean_up_files_matching("event_locations_*_ncss.txt");
	clean_up_files_matching("repeaters_xyzm_*.txt");
	clean_up_files_matching("Families_number_of_events.txt");
	clean_up_files_matching("event_connectors.txt");
	return;

def clean_up_files_matching(match_string):
	clear_list=glob.glob(match_string);
	for item in clear_list:
		call(['rm',item],shell=False); 	
	return;	
