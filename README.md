# CRE_detection

Steps to using this repo:
1. Clone the github repo. 
2. Put the Stage1_code and Stage2_code onto your shell path

3. Set up a new experiment directory (My_Expt):

    Make directories for B045, all stations, etc., each with an added/ subdirectory that contains sac files. 

    Make station_locations.txt (text file with name, lon, lat, name/exist/ for each station). Put in your experiment directory.

4. Run Stage1: 
    Call shell script c_coh_main_script.sh (stage1) from each of the B045-type directories. 
    
    The code assumes that you have added/ directories full of sac files created by Taka, with T5 header variable as the picked p-wave arrival time. 
These probably contain 30s of noise before the arrival time, and some amount of signal (at least 20.48s) after the arrival time. 
Don't make the SAC files too much longer than they need to be. 
Stage1 will generate a list of candidate CRE pairs that pass xcorr>threshold. 
See parameters in the tops of generate_nearby_add_ons_list.c and call_xcorr_and_coherence_cfilter.c for details. 


5. Run Stage2: 
Run python Stage2_code/drive_comparison.py **from your experiment directory** that contains the data directories. Stage2 will create a new folder called Stage2_results or similar. Inside, CREs_by_station will be created and rewritten. 
A new directory for each criterion is made. 

6. Update your background catalog for detailed plots.  For Mendocino, see "hypodd_raw_2_txyzm.py" in mapping data folder 


WHAT WILL BE CREATED: 

--"CREs_by_station"

    --Station_DIRs

        --repeaters_list.txt
        --Maps, Histograms, and (optionally) waveform plots
	
--Results

    --A bunch of maps, histograms, slip histories, and (optionally) family images. 
    --Easy summary for tradeoffs
    
--Tradeoffs
