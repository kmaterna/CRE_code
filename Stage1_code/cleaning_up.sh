#!/bin/bash


station_name=$1

echo "Cleaning up now."

cd exist
echo "Number of raw sac files: "
find . -name "$station_name*.sac" | wc -l
cd ../

# Get the time stamp 
todaysdate=$(date +"%Y-%m-%d_%H-%M-%S")  ## BASH IS AMAZING
name_len=${#station_name}

# apply the time stamp to a safe copy of the result file. 
starting_name=$station_name
if [ $name_len -eq 3 ]  # 3 letter names: add an extra underscore. 
	then
	starting_name+=_	
fi
starting_name+=-above_cutoff_results.txt
final_name=$station_name
final_name+=-above_cutoff_results_
final_name+=$todaysdate
final_name+=.txt
cp $starting_name $final_name

rm SNR.txt coh_input_temp.txt
rm *.am waveform.sac noise.sac
rm *.o

echo "Lines in above_cutoff_results.txt:"
cat $station_name*above_cutoff_results.txt | wc -l
echo "Lines in snr_results.txt:"
cat $station_name*snr_results.txt | wc -l

exit 0;
