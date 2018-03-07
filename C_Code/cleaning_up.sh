#!/bin/bash


station_name=$1

echo "Cleaning up now."

cd exist
echo "Number of raw sac files: "
find . -name "$station_name*.sac" | wc -l
echo "Number of cut sac files: "
find . -name "CUT*.sac" | wc -l
cd ../

echo "Lines in above_cutoff_results.txt:"
cat $station_name*above_cutoff_results.txt | wc -l
echo "Lines in snr_results.txt:"
cat $station_name*snr_results.txt | wc -l


# Get the time stamp 
todaysdate=$(date +"%Y-%m-%d_%H-%M-%S")  ## BASH IS AMAZING
name_len=${#station_name}

# apply the time stamp to a safe copy of the result file. 
if [ $name_len -eq 3 ]  # 3 letter names. 
	then
	starting_name=$station_name
	starting_name+=_-above_cutoff_results.txt
	final_name=$station_name
	final_name+=_-above_cutoff_results_
	final_name+=$todaysdate
	final_name+=.txt
	cp $starting_name $final_name
fi
if [ $name_len -eq 4 ] # 4 letter names. 
	then
	starting_name=$station_name
	starting_name+=-above_cutoff_results.txt
	final_name=$station_name
	final_name+=-above_cutoff_results_
	final_name+=$todaysdate
	final_name+=.txt
	cp $starting_name $final_name
fi

rm SNR.txt coh_input_temp.txt
rm add_nearby major_computation get_snr
rm *.am waveform.sac noise.sac
rm exist/CUT_*.sac
rm *.o

exit 0;
