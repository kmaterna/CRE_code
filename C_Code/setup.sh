#!/bin/bash

# Perform set-up for processing in add-on mode. 

station_name=$1

# Create file_list.txts
echo "Making exist_file_list.txt, added_file_list.txt, and redos_file_list.txt"
find ./exist/$station_name*.sac | wc -l > exist/exist_file_list.txt
find ./exist/$station_name*.sac >> exist/exist_file_list.txt
find ./added/$station_name*.sac | wc -l > added/added_file_list.txt
find ./added/$station_name*.sac >> added/added_file_list.txt
find ./redos/$station_name*.sac | wc -l > redos/redos_file_list.txt
find ./redos/$station_name*.sac >> redos/redos_file_list.txt

# Do we have any data to process? We probably should. 
if [ $(find ./added/$station_name*.sac | wc -l) -eq 0 ] && [ $(find ./redos/$station_name*.sac | wc -l) -eq 0 ]
       then
       echo "ERROR!  No new sac files in the 'added' or the 'redos' directory!  "
       echo "ERROR!  I have nothing to do.  Exiting now..."
       exit 1
fi


# are we starting with no existing files? then delete any obsolete result files. 
if [ $(find ./exist/$station_name*.sac | wc -l) -eq 0 ] 
	then
	echo "Starting from the top!  Beginning with empty result files and performing all computations..."
	rm $station_name*.txt
	exit 0
fi
exit 0
