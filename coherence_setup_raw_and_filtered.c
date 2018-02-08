#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "sacio.h"

/****************************
This code takes a pair of events and generates the input file that we will use to 
calculate coherence. 
If the filtered (2-24Hz) events are highly correlated, we use the cross-correlation 
to shift their relative timing to match the maximum cross-correlation.  
We then set up the coherence of the shifted UNFILTERED waveforms. 

COMPILE WITH THIS LINE RIGHT HERE!!!
gcc -o coherence_setup coherence_setup.c -L/$HOME/sac/lib  -lsacio -lsac

EXAMPLE OF USAGE: 
./coherence_setup -i RAW_B046.PB.EHZ..D.2010.069.035306.71361145.sac $event2_raw $event1_fil $event2_fil

****************************/
#define MAXNUM 2048

// Function prototypes
double xcorr(float x[], float y[], int, int);
int get_len_of_time(float, float, float, float);
int sanitize_len_of_time(int);
int get_npps(int);

// Global variables
int time_shift=0;
int perform_shift=0;
int npfft;   // the points per FFT (a power of two)

int main(int argc, char *argv[]){

	char input_file_name[] = "coh_input_temp.txt";
	char waveform_file_name[] = "two_filtered_waveforms.txt";
	float cross_correlation_cutoff=0.6;
	FILE * input_file = NULL;    // points to the file where we write UNFILTERED waveforms
	FILE * filtered_waveforms = NULL;  // points to the file where we write FILTERED waveforms
	int len_of_event_names;  // the event file names are this many characters long
	double cc_max;
	int maxnum=MAXNUM;

	len_of_event_names=strlen(argv[1])+1;
	printf("Length of event names is: %d\n",len_of_event_names);
	char event1_raw[len_of_event_names];
	char event2_raw[len_of_event_names];
	char event1_fil[len_of_event_names];
	char event2_fil[len_of_event_names];			
	memcpy(event1_raw, argv[1], len_of_event_names);
	memcpy(event2_raw, argv[2], len_of_event_names);
	memcpy(event1_fil, argv[3], len_of_event_names);
	memcpy(event2_fil, argv[4], len_of_event_names); 
	// get the names of the RAW and FIL files you're reading. 
	printf("Event 1 = %s \n", event1_raw);
	printf("Event 2 = %s \n", event2_raw);

	// char event1_raw[len_of_event_names];
	// char event2_raw[len_of_event_names];
	// char event1_fil[len_of_event_names];
	// char event2_fil[len_of_event_names];
	int i, j;
	char * temp;
	
	for (i = 1; i < argc; i++) {
		if (*argv[i] == '-') switch (*(argv[i]+1)) // switch on the character after the dash
		{
			case 's':
				perform_shift=1;
				break;
			case 'n':
				perform_shift=0;
				break;

			default:
				break;
			// leaving this flexible to adding more stuff later.  
		}
	}

	// NOW WE READ THE SAC FILES
	float yarray1_raw[MAXNUM];
	float yarray2_raw[MAXNUM];
	float yarray1_fil[MAXNUM];
	float yarray2_fil[MAXNUM];
	float beg, del;
	int nlen, nerr;
	float mag1, mag2, dist1, dist2;
	int len_of_ts;
	int adjusted_len_of_ts;



	rsac1( event1_raw, yarray1_raw, &nlen, &beg, &del, &maxnum, &nerr, strlen( event1_raw ) ) ;
	if ( nerr != 0 ) {
		printf("%d",nerr);
		printf("Error reading in #1 SAC file: |%s|\n", event1_raw);
		exit ( nerr ) ;
	}
	printf("Success in reading file %s \n",event1_raw);

	getfhv ( "MAG" , & mag1 , & nerr , strlen("MAG") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: mag\n");
		exit(-1);
	}
	getfhv ( "DIST" , & dist1 , & nerr , strlen("DIST") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: dist\n");
		exit(-1);
	}


	rsac1( event2_raw, yarray2_raw, &nlen, &beg, &del, &maxnum, &nerr, strlen( event2_raw ) ) ;
	if ( nerr != 0 ) {
		printf("%d",nerr);
		printf("Error reading in #2 SAC file: |%s|\n", event2_raw);
		exit ( nerr ) ;
	}
	printf("Success in reading file %s \n",event2_raw);

	getfhv ( "MAG" , & mag2 , & nerr , strlen("MAG") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: mag\n");
		exit(-1);
	}
	getfhv ( "DIST" , & dist2 , & nerr , strlen("DIST") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: dist\n");
		exit(-1);
	}


	rsac1( event1_fil, yarray1_fil, &nlen, &beg, &del, &maxnum, &nerr, strlen( event1_fil ) ) ;
	if ( nerr != 0 ) {
		printf("%d",nerr);
		printf("Error reading in #1 SAC file: |%s|\n", event1_fil);
		exit ( nerr ) ;
	}
	printf("Success in reading file %s \n",event1_fil);

	rsac1( event2_fil, yarray2_fil, &nlen, &beg, &del, &maxnum, &nerr, strlen( event2_fil ) ) ;
	if ( nerr != 0 ) {
		printf("%d",nerr);
		printf("Error reading in #2 SAC file: |%s|\n", event2_fil);
		exit ( nerr ) ;
	}
	printf("Success in reading file %s \n",event2_fil);


	cc_max=xcorr(yarray1_fil, yarray2_fil, MAXNUM, MAXNUM/8 - 5);  // get cross-correlation value and index.

	len_of_ts=get_len_of_time(mag1, mag2, dist1, dist2);  // get the appropriate length of time to do coherence (might be less than MAXNUM samples)
	adjusted_len_of_ts=len_of_ts - abs(time_shift);
	adjusted_len_of_ts=sanitize_len_of_time(adjusted_len_of_ts);		// fixing a bug where one fft window ends up with a single datapoint. 
	npfft = get_npps(adjusted_len_of_ts);  // give us number of points per fft window, based on len_of_ts
	// ^^ global variable. 

	if(perform_shift)
	{
	// If the events are highly correlated, we will shift the time-series to get better coherences. 
		if(cc_max>1*cross_correlation_cutoff)
		{
            //time_shift=-27;
			//printf("%d \n", time_shift);
			if(time_shift<-MAXNUM/8 || time_shift>MAXNUM/8)
				printf("ERROR: Invalid time shift.  Double Check this at %s,  %s.  \n", event1_fil, event2_fil);

			// shift arrays around and write the shifted arrays into coh_input file.  
			if(time_shift>=0)  // for a positive time-shift
			{
				input_file = fopen(input_file_name, "w+");    // file with input data
		        for(j=0; j<adjusted_len_of_ts; j++){
		            fprintf(input_file, "%G %G \n", yarray1_raw[j], yarray2_raw[j+abs(time_shift)]);
		        }
		        fclose(input_file);	

				// NOW WE WRITE THE FILTERED WAVEFORM DATA INTO A SEPARATE TEXT FILE FOR PLOTTING LATER
				filtered_waveforms = fopen(waveform_file_name, "w+");    // file with filtered waveform data
				for(j=0;j<adjusted_len_of_ts; j++){
					fprintf(filtered_waveforms,"%G %G\n",yarray1_fil[j], yarray2_fil[j+abs(time_shift)]);
				}
				fclose(filtered_waveforms);
				printf("Printing filtered waveforms out to separate file...\n");		

	    	}
			if(time_shift<0)  // for a negative time-shift
			{
				input_file = fopen(input_file_name, "w+");    // file with input data
		        for(j=0; j<adjusted_len_of_ts; j++){
		            fprintf(input_file, "%G %G \n", yarray1_raw[j+abs(time_shift)], yarray2_raw[j]);
		        }
		        fclose(input_file);	

				// NOW WE WRITE THE FILTERED WAVEFORM DATA INTO A SEPARATE TEXT FILE FOR PLOTTING LATER
				filtered_waveforms = fopen(waveform_file_name, "w+");    // file with filtered waveform data
				for(j=0;j<adjusted_len_of_ts; j++){
					fprintf(filtered_waveforms,"%G %G\n",yarray1_fil[j+abs(time_shift)], yarray2_fil[j]);
				}
				fclose(filtered_waveforms);
				printf("Printing filtered waveforms out to separate file...\n");		        

	    	}
	        printf("Performing time shift of %d hundredths of a second...\n\n", time_shift);
		}

		else { // if the events aren't highly correlated anyway, we don't bother with the shift. 
			// Now we write the data into the coh_input text file (temporary file)
			input_file = fopen(input_file_name, "w+");    // file with input data
			for(j=0;j<adjusted_len_of_ts; j++){
				fprintf(input_file,"%G %G\n",yarray1_raw[j], yarray2_raw[j]);
			}
			fclose(input_file);	
			// NOW WE WRITE THE FILTERED WAVEFORM DATA INTO A SEPARATE TEXT FILE FOR PLOTTING LATER
			filtered_waveforms = fopen(waveform_file_name, "w+");    // file with filtered waveform data
			for(j=0;j<adjusted_len_of_ts; j++){
				fprintf(filtered_waveforms,"%G %G\n",yarray1_fil[j], yarray2_fil[j]);
			}
			fclose(filtered_waveforms);
			printf("Printing filtered waveforms out to separate file...\n");
			printf("Not performing time shift...\n");
		}
	}


	else{
		// NOW WE WRITE THE DATA INTO A TEMPORARY TEXT FILE
		input_file = fopen(input_file_name, "w+");    // file with input data
		for(j=0;j<adjusted_len_of_ts; j++){
			fprintf(input_file,"%G %G\n",yarray1_raw[j], yarray2_raw[j]);
		}
		fclose(input_file);

		// NOW WE WRITE THE FILTERED WAVEFORM DATA INTO A SEPARATE TEXT FILE FOR PLOTTING LATER
		filtered_waveforms = fopen(waveform_file_name, "w+");    // file with filtered waveform data
		for(j=0;j<adjusted_len_of_ts; j++){
			fprintf(filtered_waveforms,"%G %G\n",yarray1_fil[j], yarray2_fil[j]);
		}
		fclose(filtered_waveforms);
		printf("Printing filtered waveforms out to separate file...\n");
		printf("Not performing time shift...\n");
	}


	return(0);
}



/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  This function cross-correlates two signals                    :*/
/*::  Taken from http://paulbourke.net/miscellaneous/correlate/     :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
// This program returns the maximum cross-correlation found between two signals. 
// IT PLACES THE TIME SHIFT AT WHICH THE CROSS-CORRELATION OCCURS IN A GLOBAL VARIABLE. 
// n is the length of the x and y arrays
double xcorr(float x[], float y[], int n, int maxdelay){

    int i,j;
    double mx,my,sx,sy,sxy,denom,r;
    time_shift=0;   // re-setting time-shift for safety. 

    // Calculate the mean of the two series x[], y[] 
    mx = 0;
    my = 0;   
    for (i=0;i<n;i++) 
    {
        mx += x[i];
        my += y[i];
    }
    mx /= n;
    my /= n;

    // Calculate the denominator
    sx = 0;
    sy = 0;
    for (i=0;i<n;i++) 
    {
        sx += (x[i] - mx) * (x[i] - mx);
        sy += (y[i] - my) * (y[i] - my);
    }
    denom = sqrt(sx*sy);

    // Calculate the correlation series
    double cc_max=0;
    int best_delay=0;
    int delay=0;
    for (delay=-maxdelay;delay<maxdelay;delay++) 
    {
        sxy = 0;
        for (i=0;i<n;i++) 
        {
            j = i + delay;
            if (j < 0 || j >= n)
                continue;
            else
                sxy += (x[i] - mx) * (y[j] - my);
        }   
        r = sxy / denom;
        // r is the correlation coefficient at "delay" */
        if (r > cc_max)
        {
            cc_max=r;  // replace the coefficient with the biggest one we've found yet. 
            best_delay=delay;
        }
    }
    time_shift=best_delay;  // the global variable
    return cc_max;
}



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
