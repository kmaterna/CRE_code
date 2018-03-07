# CRE_detection

WHAT YOU NEED:

--Raw Data Dirs (for each station)

--Code Dir

	--Code (python, bash, c)
	--"CRE_Candidates" (inputs to this process)
		--*_above_cutoff_results.txt
		--*_snr_results.txt
		--station_locations.txt (file that contains NAME LON LAT data_dir, for each station)
	—“Mapping_files”
		--Faults, seismicity, etc. 
	—“GMT_Scripts”
		--just GMT code



WHAT WILL BE CREATED: 
	--"CREs_by_station"
		--Station_DIRs
			--repeaters_list.txt
			--Maps, Histograms, and (optionally) waveform plots
	--Results
		—-A bunch of maps, histograms, slip histories, and (optionally) family images. 
		—-Easy summary for tradeoffs
	--Tradeoffs
