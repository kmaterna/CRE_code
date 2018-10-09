# This script takes "added" files and moves them over to "exist" directory
# So that the output of the generate_xcorr_coh script is all in the 
# most updated directory. 

station=$1 

mv added/*.sac exist/ # moving everything from "added" into "exist"

four_char_base=$station
if [ ${#station} -eq 3 ]; then
     four_char_base+=_
fi

echo $four_char_base
starting_name=$four_char_base
starting_name+=-nearby_30_km.txt

if [ $? -eq 1 ]
     then
     echo "ERROR!  Never got stations_nearby_30_km.txt file!"
     exit 1
fi


sed -i -- 's/added/exist/g' $four_char_base-nearby_30_km.txt # updates the nearby-30km instruction file 
# so that the xcorr_coh program knows all files are inside the "exist" directory 
exit 0;
