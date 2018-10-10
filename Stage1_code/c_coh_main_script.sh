#!/bin/bash
set -e

# This script will take additional files in the "added" directory and compare them to: 
# 1. the files in the exist directory, and 
# 2. the other files in the added directory. 
# It will APPEND the coherence and SNR results to the end of the results files. 
# It can also handle re-dos that have already been included, but for some reason need to be deleted and re-added. 
# It should be called from B045/ or parallel directory. 

if [[ "$#" -eq 0 ]]; then
  echo ""
  echo "Please provide the name of the station. Ex: c_coh_main_script.sh B045"
  echo ""
  exit 1 
fi

# Defining variables
station_name=$1
compare_list_file=$station_name"_nearby_list.txt"  # something like "B045_nearby_list.txt"
where_is_code="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # where does the c code live on this machine? 

# Initial processing
# setup.sh $station_name         # Figure out what data we have; grab names of files, make safe copies of result files. 
# delete_redos.sh $station_name  # If we are doing redos, delete existing comparisons before we re-do that station. 

# Compare existing files with everything in the added directory. 
# flags are -L/$HOME/sac/lib -lsacio -lsac for personal machine (not BSL network)
# gcc -o add_nearby.o $where_is_code/generate_nearby_add_ons_list.c -L/share/apps/sac/lib -lsacio -lsac -lm # BSL linux
# gcc -o add_nearby.o $where_is_code/generate_nearby_add_ons_list.c -L/$HOME/sac/lib -lsacio -lsac  
# ./add_nearby.o $station_name $compare_list_file
# mv added/*.sac exist/

# make_cut_files.sh $station_name  $compare_list_file # makes cut files for files in exist directory that we're comparing (saves time). 
# Will kill this. 

gcc -o major_computation.o $where_is_code/call_xcorr_and_coherence_cfilter.c -L/$HOME/sac/lib -lsacio -lsac
# gcc -o major_computation.o $where_is_code/call_xcorr_and_coherence_cfilter.c -L/share/apps/sac/lib -lsacio -lsac -lm
./major_computation.o $station_name $compare_list_file append_mode

echo "Producing SNR solution file"
python $where_is_code/update_solution_file_with_SNR.py $station_name $where_is_code  # only does computation for each "hit" from the last step (cc>0.6)

cleaning_up.sh $station_name
