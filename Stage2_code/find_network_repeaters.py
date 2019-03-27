"""
This file will take a series of individual-station repeater pair files and condense it into a list of 
repeater pairs detected by 2 or more stations. 
It writes an output file with elements like: 
2010.063.190428.71358400.sac 2017.114.161621.72793316.sac B045 B046 B047 (all the stations that were used to observe this pair)
"""


import glob as glob
import sys
from subprocess import call
import collections

Indv_station_repeaters = collections.namedtuple('Indv_station_repeaters',[
	'station_names',
	'station_data']);
# The station_data field is full of arrays with elements like "2010.241.010956.71447890.sac 2017.175.203253.72820756.sac".


def network_repeaters_two_more_stations(Network_repeaters_list,stage2_results):
	[filelist,outfile] = configure(Network_repeaters_list,stage2_results);   # Get all the individual-station CRE files. 
	Individual_station_repeaters = inputs(filelist);  # read them into an array
	[evpairs,stations]      =compute(Individual_station_repeaters);  # compute the unique repeaters and where they were observed
	outputs(evpairs,stations,outfile);  # write a file. 
	return;



# --------------------- GUTS -------------------- # 
def configure(Network_repeaters_list,stage2_results):
	call(['rm',Network_repeaters_list],shell=False);
	copy_list=glob.glob(stage2_results+'/CREs_by_station/*/*_*_list.txt');
        #print(copy_list);
	for item in copy_list:
		call(['cp',item,'.'],shell=False); 
	filelist=glob.glob("*_repeaters_list.txt");
	outfile=Network_repeaters_list;
	print("Available files are..."+str(filelist))
	return [filelist, outfile];

def inputs(filelist):
	station_names=[];
	station_data=[];
	for i in filelist:
		datalist=[];
		infile=open(i,'r')
		station_names.append(i[0:4]);
		infile.readline();
		for line in infile:
			temp=line.split()
			datalist.append(temp[0][-28:] + " " + temp[1][-28:]);
		infile.close()
		station_data.append(datalist);
	Individual_station_repeaters=Indv_station_repeaters(station_names=station_names, station_data=station_data);
	return Individual_station_repeaters;

def compute(Individual_station_reps):
	winners=[]; recorded_stations=[];  # has the intersections of repeaters found at two stations

	# Find intersections. 
	for i in range(len(Individual_station_reps.station_data)):
		myarray1=Individual_station_reps.station_data[i];
		for j in range(i+1, len(Individual_station_reps.station_data)):
			myarray2=Individual_station_reps.station_data[j];
			print("Comparing "+Individual_station_reps.station_names[i] + " with " + Individual_station_reps.station_names[j]+"...");

			for val in myarray1:  # Find event pairs that were detected as repeaters in both stations
				if val in myarray2:
					winners.append(val);
					recorded_stations.append([Individual_station_reps.station_names[i], Individual_station_reps.station_names[j]]);

	# # Read the intersections of repeating earthquakes (VERY nonunique list)
	# # Thankfully they are all in one convenient place.  They just need to be "uniqued".  
	unique_winners = list(set(winners))  # find unique list. 
	unique_stations=[];
	for x in unique_winners:
		temp_stations=[];
		for i in range(len(winners)):
			if winners[i]==x:
				if recorded_stations[i][0] not in temp_stations:
					temp_stations.append(recorded_stations[i][0])
				if recorded_stations[i][1] not in temp_stations:
					temp_stations.append(recorded_stations[i][1])
		unique_stations.append(temp_stations);
	print("\nFound "+str(len(unique_winners))+" unique repeating event pairs.");
	return [unique_winners, unique_stations];


def outputs(unique_evpairs, unique_stations,outfile):

	ofile=open(outfile,'w');
	for i in range(len(unique_evpairs)):
		ofile.write(unique_evpairs[i]) # Write the unique event pairs
		for item in unique_stations[i]:
			ofile.write(" "+item);
		ofile.write("\n")
	ofile.close();
	return;



