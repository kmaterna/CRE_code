"""
This is my master script to view repeaters.  
It's complicated. It calls C and Bash from Python...
It gives us a graph with five things:
1. Waveform 1 (filtered)
2. Waveform 2 (filtered)
3. Cross correlation (filtered)
4. Coherence (unfiltered)
5. SNR for each waveform
June 9, 2016.
"""
import subprocess
import glob, os, sys
import make_coh_snr_plot

def master_waveform_viewer_snr(station_name, event1,event2,f1=1.0,f2=15.0,snr_cutoff=5.0,raw_sac_dir="",output_dir=""):
	# The events you want to look at
	# print "Arguments should be: station_name, event1, event2, start_frequency, end_frequency, and snr_cutoff.  \n"
	# f1: the frequency where SNR begins to get high.
	# f2: the frequency where SNR is no longer high. 
	# An example of raw_sac_dir: "../B046.EHZ.snr/"
	# An example of event1     : "B045.PB.EHZ..D.2009.094.003131.71203430.sac"

	# Find where the code lives. 
	# Find whether you're on linux (BSL machines) or Mac

	path_to_code=os.path.dirname(os.path.realpath(__file__));
	try:
		am_i_linux=subprocess.check_output(['uname','-a','|','grep','Linux'],shell=False);
		print("I am a linux machine; operating like a BSL computer");
		compiler_arguments="-L/share/apps/sac/lib  -lsacio -lsac -lm";
	except subprocess.CalledProcessError as exc:
		am_i_linux=[];
		print("I am a Mac");
		compiler_arguments=" -L/$HOME/sac/lib -lsacio -lsac";


	event1_base=event1.split('/')[-1];  # something like B045.PB.EHZ..D.2012.127.091831.71776880.sac without the directory
	event2_base=event2.split('/')[-1];  # something like B045.PB.EHZ..D.2012.127.091831.71776880.sac without the directory

	# Setting up file names
	event1_raw="RAW_"+event1_base
	event2_raw="RAW_"+event2_base
	event1_fil="FIL_"+event1_base
	event2_fil="FIL_"+event2_base

	frequency=100.0  # frequency of seismic data (Hz)
	pps_c=512       # points per sample (reading into coherence.c)
	min_freq=f1      # min and max freq for python plotting black bars (0 if we want to compute via corner freq)
	max_freq=f2      # anything other than 0 overrides the Fc option


	# Set up the coherence between the RAW waveforms (based on the xcorr of the filtered waveforms)
	# This will also write a temporary file with the FILTERED waveforms too. 
	subprocess.call("clear");
	print("Gathering Data... Generating Raw and Filtered waveforms from SAC... \n");
	subprocess.call(path_to_code+"/make_a_raw_filtered_waveform.sh "+raw_sac_dir+" "+event1_base,shell=True)
	subprocess.call(path_to_code+"/make_a_raw_filtered_waveform.sh "+raw_sac_dir+" "+event2_base,shell=True)
	print("Reading in data...  \n");
	subprocess.call("gcc -o coherence_setup "+path_to_code+"/coherence_setup_raw_and_filtered.c "+compiler_arguments, shell=True)
	print("./coherence_setup " + event1_raw +" "+ event2_raw);
	subprocess.call(["./coherence_setup",event1_raw,event2_raw,event1_fil,event2_fil,"-s"])
	# -s means "perform shift" if the correlation is high; -n means "don't perform shift".

	# Run the coherence calculation
	print("Running coherence calculation... ");
	pps_c=get_npfft('coh_input_temp.txt');
	subprocess.call("gcc -o coherence "+path_to_code+"/coherence.c -lm",shell=True);
	subprocess.call("./coherence -i coh_input_temp.txt -f "+str(frequency)+" -n "+str(pps_c)+" > coh_output.txt", shell=True)
	print("./coherence -i coh_input_temp.txt -f $frequency -n $pps > coh_output.txt");
	print("Completed coherence calculation. \n");


	# Get the signal to noise ratio for each event
	print("Running SNR calculation on " + event1_base + "... ");
	subprocess.call([path_to_code+"/noise_floor_VS_data.sh",event1_base])
	subprocess.call("gcc -o get_snr "+path_to_code+"/get_snr.c "+compiler_arguments,shell=True)
	subprocess.call(["./get_snr"])
	subprocess.call(["mv","SNR.txt","SNR1.txt"])

	print("Running SNR calculation on " + event2_base + "... ");
	subprocess.call([path_to_code+"/noise_floor_VS_data.sh",event2_base])
	subprocess.call(["./get_snr"])
	subprocess.call(["mv","SNR.txt","SNR2.txt"])

	# Run a python code to plot things.
	# Arguments: event1, event2, waveform_file, c_coherence_file, instrument_frequency, min_frequency, max_frequency, station, show_overlay
	print("Running a Python code to graph coherence...");
	plot_overlay = 0; # make the overlay show up (doesn't save overlay)
	pretty_plot=0;  # how pretty are we making this plot?
	make_coh_snr_plot.make_coh_snr_plot(output_dir,event1_base,event2_base,"two_filtered_waveforms.txt","coh_output.txt",frequency,min_freq,max_freq,snr_cutoff,plot_overlay,pretty_plot);

	print("All done!\n");
	clean_up_files_matching("SNR*.txt");
	clean_up_files_matching("*.sac");
	clean_up_files_matching("*.am");
	clean_up_files_matching("coh_output.txt");
	clean_up_files_matching("coh_input_temp.txt");
	clean_up_files_matching("two_filtered_waveforms.txt");
	clean_up_files_matching("coherence");
	clean_up_files_matching("coherence_setup");
	clean_up_files_matching("get_snr");
	return;

def clean_up_files_matching(match_string):
	clear_list=glob.glob(match_string);
	for item in clear_list:
		subprocess.call(['rm',item],shell=False); 	
	return;	



def get_npfft(myfile):
	"""
	This will give us a npps value: shorter npps for shorter time series. 
	It helps the coherence function do the proper windowing and averaging. 
	Must be a power of two for the FFTs to work. 
	"""
	my_file=open(myfile,'r');
	ts_len=0;
	for line in my_file:
		ts_len+=1
	my_file.close();
	if ts_len > 1024:
		return 512;
	elif ts_len>512:
		return 256;
	else:
		return 128;
