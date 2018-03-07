extern int get_len_of_time(float mag1, float mag2, float dist1, float dist2);
extern int sanitize_len_of_time(int ts_len);
extern int get_npps(int ts_len);

int get_len_of_time(float mag1, float mag2, float dist1, float dist2){
	/*
	Usually for earthquakes, we want to run coherence on the whole 2048 samples.  But sometimes, when the earthquakes are VERY CLOSE, 
	we want to use less time than that.  The end of the signal is just a bunch of noise.  
	This function tells us how many samples we want to use, as a function of distance and magnitude.  
	*/

	float return_val; 			      // this will be in SAMPLES (max=2048)
	float mean_dist=(dist1+dist2)/2;  // in kilometers
	float mean_mag=(mag1+mag2)/2;

	return_val=150;                             // the time before the p-wave
	return_val += 200*mean_mag;       // the p wave (2 seconds for a Mag 1)
	return_val += 100*(mean_dist/8);  // the p-s time: 1 second per 8 kilometers of distance. 
	return_val += 200*mean_mag;       // the s-wave (2 seconds for a Mag 1)
	return_val += 200;			      // the coda
	if(return_val > 2048)
		return_val = 2048;

	return (int)return_val;
}


int sanitize_len_of_time(int ts_len){
	/*
	This makes sure that we don't accidentally give a length of time-series that breaks the FFT in the coherence code. 
	You don't want a window with only one data point.  
	*/

	// fixing a bug where one fft window ends up with a single datapoint. 
	if(ts_len==1792+1)
		ts_len+=10;  
	if(ts_len==1536+1)
		ts_len+=10;  
	if(ts_len==1280+1)
		ts_len+=10;  
	if(ts_len==1024+1)
		ts_len+=10; 
	if(ts_len==896+1)
		ts_len+=10;  
	if(ts_len==768+1)
		ts_len+=10; 
	if(ts_len==640+1)
		ts_len+=10;  
	if(ts_len==512+1)
		ts_len+=10;  

	return ts_len;
}


int get_npps(int ts_len){
	/*
	This will give us a npps value: shorter npps for shorter time series. 
	It helps the coherence function do the proper windowing and averaging. 
	Must be a power of two for the FFTs to work. 
	*/
	int return_val; 			// this will be in SAMPLES (normally=512)

	if(ts_len > 1024)
		return_val = 512;
	else if(ts_len>512)
		return_val = 256;
	else
		return_val = 128;
	
	//printf("Note: NPPS for coherence will be %d. \n", return_val);
	return return_val;
}

