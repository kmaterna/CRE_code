#!/bin/bash

# Perform set-up for processing in add-on mode. 

station_name=$1

# Making necessary directories. 
echo "Making necessary directories for $station_name"
mkdir -p exist
mkdir -p redos

# Create file_list.txts
echo "Making exist_file_list.txt, added_file_list.txt, and redos_file_list.txt"
num_exist=`find ./exist -maxdepth 2 -name "$station_name*.sac" | wc -l`
echo $num_exist > exist/exist_file_list.txt
find ./exist -maxdepth 2 -name "$station_name*.sac" >> exist/exist_file_list.txt
echo "Files in exist dir: " $num_exist
num_added=`find ./added -maxdepth 2 -name "$station_name*.sac" | wc -l`
echo $num_added > added/added_file_list.txt
find ./added -maxdepth 2 -name "$station_name*.sac" >> added/added_file_list.txt
echo "Files in added dir: " $num_added
num_redos=`find ./redos -maxdepth 2 -name "$station_name*.sac" | wc -l`
echo $num_redos > redos/redos_file_list.txt
find ./redos -maxdepth 2 -name "$station_name*.sac" >> redos/redos_file_list.txt
echo "Files in redos dir: " $num_redos

# Do we have any data to process? We probably should. 
if [ $num_added -eq 0 ] && [ $num_redos -eq 0 ]
       then
       echo "ERROR!  No new sac files in the 'added' or the 'redos' directory!  "
       echo "ERROR!  I have nothing to do.  Exiting now..."
       exit 1
fi

# are we starting with no existing files? then start from the top.
if [ $num_exist -eq 0 ] 
	then
	echo "Starting from the top!  Beginning with empty result files and performing all computations..."
fi
exit 0
