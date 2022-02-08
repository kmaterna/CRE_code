#!/bin/bash
set -e

# This script will take any files in the "added" directory and compare them to: 
# 1. the files in the exist directory, and 
# 2. the other files in the added directory. 
# By default, it will APPEND the coherence and SNR results to the end of the results files. 
# It can also handle re-dos that have already been included, but for some reason need to be deleted and re-added. 
# It should be called from B045/ or parallel directory. 

if [[ "$#" -eq 0 ]]; then
  echo ""
  echo "Please provide the name of the station. Ex: c_coh_main_script.sh B045"
  echo ""
  exit 1 
fi

# Defining variables based on inputs and computer system. 
station_name=$1
compare_list_file=$station_name"_nearby_list.txt"  # something like "B045_nearby_list.txt"
where_is_code="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"  # where does the c code live on this machine? 
amilinux=`uname -a | grep 'Linux' || True`  # the True is necessary for grep under set -e
if [ ! -z "$am_i_linux" ]; then # WE ARE ON A LINUX MACHINE 
	compiler_list=" -L/share/apps/sac/lib -lsacio -lsac -lm" # FOR BSL LINUX
	sed_args=("-i" "s/added/exist/g" "$compare_list_file")  # FOR LINUX
else
	compiler_list=" -L/$HOME/sac/lib -lsacio -lsac" # FOR MAC
	sed_args=("-i" "''" "s/added/exist/g" "$compare_list_file")  # FOR MAC
fi

# Initial processing
setup.sh $station_name         # Figure out what data we have; grab names of files, make safe copies of result files. 
delete_redos.sh $station_name  # If we are doing redos, delete existing comparisons before we re-do that station. 

# Compare existing files with everything in the added directory. 
gcc -o add_nearby.o $where_is_code/generate_nearby_add_ons_list.c $compiler_list
./add_nearby.o $station_name $compare_list_file
sed "${sed_args[@]}"
mv added/*.sac exist/

gcc -o major_computation.o $where_is_code/call_xcorr_and_coherence_cfilter.c $compiler_list
./major_computation.o $station_name $compare_list_file append_mode

gcc -o get_snr.o $where_is_code/get_snr.c $compiler_list
echo "Producing SNR solution file"
python $where_is_code/update_solution_file_with_SNR.py $station_name  # only does computation for each "hit" from the last step (cc>value)

cleaning_up.sh $station_name
