#!/bin/bash

station_name=$1
input_filename=$2

cd exist

number_of_existing_events=`find . -name "$station_name*.sac" | wc -l`
number_of_comparisons=`cat ../$input_filename | wc -l`

if [ "$number_of_existing_events" -gt "$number_of_comparisons" ]; then # the shortest way to do this is by reading the nearby_30_km file:
	echo "Processing only the sac files in the nearby list!"
	for WORD in `cat ../*-nearby_30_km.txt`
	do
		echo $WORD
		short_word=${WORD:8:48} # cutting off the ./exist/ part of the string
		echo $short_word
		long_word=$short_word
		long_word+=CUT_
		if [ ! -f $long_word ]; then
			sac <<-SACEND
			cut t5 -1.00 19.47
			# Make sure these are exactly 20.47 seconds apart.
			r $short_word
			write CUT_$short_word
			exit
			SACEND
		fi 
	done

else # the shortest way to do this is by processing every single file in the exist directory:
	echo "Processing every sac file!"
	for f in $station_name*.sac 
	do
		sac <<-SACEND
		cut t5 -1.00 19.47
		# Make sure these are exactly 20.47 seconds apart.
		r $f
		write CUT_$f
		exit
		SACEND
	done	
        uncutfiles=$(find exist -name "$station_name*.sac" | wc -l)
        cut_files=$(find exist -name "CUT_*.sac" | wc -l)
        if [ $uncutfiles -eq $cut_files ]
            then
            echo "Success cutting all files!"
        else
            echo "PROBLEM! Not all files were successfully cut. "
            cd ../
            exit 1
        fi

fi

echo "Number of raw sac files: "
find . -name "$station_name*.sac" | wc -l
echo "Number of cut sac files: "
find . -name "CUT*.sac" | wc -l
cd ../

exit 0
