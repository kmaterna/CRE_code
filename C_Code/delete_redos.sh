#!/bin/bash

# Perform set-up for processing redos. 
# First we delete. Then we send the files to added directory. 

station_name=$1

if [ $(find ./redos/$station_name*.sac | wc -l) -gt 0 ]
	then

	echo "Redo mode: "
	echo "We are going to delete some files from the exist directory. "
	
	# The delete function. 
	# This overwrites the station_name_above_cutoff_results.txt file. 
	python  ../../C_CREs/delete_event_pairs.py $station_name
	
	mv redos/$station_name*.sac added # add files to "added"
	find ./added/$station_name*.sac | wc -l > added/added_file_list.txt  # remake the added_file_list.txt
	find ./added/$station_name*.sac >> added/added_file_list.txt
fi
exit 0; 
