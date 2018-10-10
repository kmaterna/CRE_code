#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "sacio.h"
#include "sac.h"
#include "determine_ts_len.h"
#define MAXNUM 2048 // THIS is the approximate number of data points per earthquake. 
#define NPS 512  // THIS is the number of points per segment (512 is good for vectors of ~2048 points)
#define FILENAME_SIZE 80  // Maximum number of characters in sac filename

/****************************
This code performs cross-correlation and coherence of sac files.
It reads from a list of nearby event-pairs (e.g. B046_nearby.txt)
and generates coherence and cross-correlation values for each event pair in that file.  
It throws away event pairs that occurred within some nominal time (10 seconds) of each other. 

This script reads unfiltered sac files. 
However, inside this script, we filter from 2-24 Hz using the code from sac.h file. 
We use the filtered waveform for cross-correlating and we save this value.  

When events have a high maximum cross-correlation (for example above 0.6), then we use the 
index of the maximum cross-correlation value to shift the filtered and raw arrays relative to one another.
Then we re-compute the coherence for the optimally-shifted unfiltered waveforms.

We write the summary values for cross-correlation and coherence (0-50Hz) to a single output file. 
We only save the cross-correlation and coherence data for events with xcorr>cutoff.  
We avoid saving mostly garbage that way.  

COMPILE WITH THIS LINE RIGHT HERE!!!
gcc -o major_computation source_name.c -L/$HOME/sac/lib  -lsacio -lsac
On the BSL linux computers:
gcc -o exec_name source_name.c -L/share/apps/sac/lib -lsacio -lsac -lm
****************************/



/* FUNCTION PROTOTYPES. */
int close_events_in_time(char[], char[], int);
double xcorr(float x[], float y[], int, int);
void call_coherence();
void coherence();
int load();
void lremv();
void fft842();  // seems like declaring the types of the arguments here is optional. 
void sample_coherence(double);   // this is where we implement our criteria for summarizing coherence values
int get_len_of_event_names(char[]); // Ex: gets "B045"; returns 45 (since the sac file names are 45 characters long)


// GLOBAL VARIABLES YOU DON'T TOUCH: George Moody's code had a lot of them :(
double *xx, *yy, *gxx, *gyy, *gxyre, *gxyim, *phi, *weight;
int npfft = NPS;	/* points per Fourier transform segment (a power of 2) */
int time_shift = 0;      // This variable is used when time-series arrays need shifting relative to each other. 
FILE * ifile = NULL;    // for reading the two-column input file. 
FILE * output_file = NULL;    // the output file needs to be global so that we can write to it from anywhere. 
char input_file_name[] = "coh_input_temp.txt";                  // file for putting sac data (re-written each time we loop)
char output_file_name[] = "____-above_cutoff_results.txt";
char summary_file_name[] = "____-process_summary.txt";     // the file for summarizing what we're doing



int main(int argc, char *argv[]){

	if( argc != 4 ){   // check if you have provided a station name
		printf("Oops! You have provided the wrong number of arguments.\n");
		printf("We want something like ./computation station_name list_file append_mode.\n");
		exit(1);
	}

	// ****** THESE ARE THE PARAMETERS YOU CARE ABOUT AND CHOICES YOU WANT TO MAKE ******* // 	
	int seconds_apart = 10;                  // we don't compare events that are within 10 seconds of each other
	float cross_correlation_cutoff = 0.70;   // if xcorr is greater than this, we care about shifting the arrays and doing coherence that way
	int maxdelay = 250;                      // for cross-correlation, we shift this many hundredths of a second in each direction (NOT MORE THAN 250!).
	int small_number = 0*1000;  // CONTROL PROGRAM FLOW: if you want to start at a certain index value. 
	int big_number = 1000*1000*100;   // CONTROL PROGRAM FLOW: the coherence/xcorr loop won't go more than this many times.	
	double sampfreq = 100.0;  // Defined from the seismic instrument we're using (Hz). 


	// ****** BORING VARIABLES AND PROCEDURES YOU DON'T CARE ABOUT ******* // 

	// Please parse the name of the station (3 characters or 4 characters?). 
	int len_of_station_name;  // this is just for naming the output files correctly. 
	len_of_station_name=strlen(argv[1]);  // the length of a null-terminated string from the user. 	
	char station_name[len_of_station_name+1];  // get the name of the station, which is null-terminated. 
	memcpy(station_name,argv[1],len_of_station_name+1);  // save the name of the argument/station (usually 3 or 4 characters)

	// input file
	int len_of_list_file;                              // this is just for naming the file correctly. 
	len_of_list_file=strlen(argv[2]);                  // the length of a null-terminated string from the user. 
	char list_file_name[len_of_list_file+1];             // get the name of the output_file, which is null-terminated. 
	memcpy(list_file_name,argv[2],len_of_list_file+1);  // save the name of the argument

	// Hard-coded output files
	memcpy(output_file_name,station_name,len_of_station_name);  // change the top 3 or 4 characters on the output_file_name
	memcpy(summary_file_name,station_name,len_of_station_name);	

	FILE * input_file   = NULL;    // points to the same file as ifile, but this is for writing
	FILE * list_file    = NULL;
	FILE * summary_file = NULL;
	list_file    = fopen(list_file_name,"r");  
	if (list_file == NULL){
		printf("ERROR: Error opening: %s\n",list_file_name);
		printf("Exiting the program...\n");
		exit(1);
	}
	else{
		printf("SUCCESS in opening: %s\n",list_file_name);
	}

	// Are we running in append mode, or full-compare mode? 
	// Opens / appends to the output file. 
	// We are almost always running in append mode, but I'm just keeping the functionality in there just in case. 
	char append_flag[11];
	memcpy(append_flag,argv[3],11);
	append_flag[11]=(char)0;   

	if (strcmp(append_flag,"append_mode")==0){
		output_file  = fopen(output_file_name,"a");
		summary_file = fopen(summary_file_name,"a");
		printf("Output files opened in APPEND mode.\n");  // in append mode. 
	}
	else if (strcmp(append_flag,"fullsq_mode")==0){
		output_file  = fopen(output_file_name,"w+");
		summary_file = fopen(summary_file_name,"w+");
		printf("Output files opened in WRITE mode.\n");   // in over-write mode. 
	}
	else{
		printf("Append Flag is %s\n",append_flag);
		printf("Please specify either 'append_mode' or 'fullsq_mode' for the second program option.");
	}


	// Starting the process of opening the input file. 
	if(list_file==NULL){
		printf("Could Not Open List of Nearby Event Pairs\nExiting Program...\n");
		exit(0);       
	}
	time_t rawtime;           // for getting the start-time and end-time of the process
	struct tm * timeinfo;
	float yarray1_cut[MAXNUM];  // for raw sac files, 20.47 seconds long
	float yarray2_cut[MAXNUM];
	float yarray1_filtered[MAXNUM]; // for filtered sac files, 20.47 seconds long
	float yarray2_filtered[MAXNUM];
	float beg, del;
	int nlen, nerr;
	int max = MAXNUM;
	int i, j;
	float mag1, mag2, dist1, dist2;
	int skip_close_events=0;
	int counter = 0;  // the number of event pairs we have compared
	double max_xcorr;
	int number_of_shifts=0; // the number of highly-correlated event pairs we have computed
	int len_of_ts; 
	int adjusted_len_of_ts;
	float * yarray1_subevent, * yarray2_subevent;   // this is used when we shorten the time-series below 20.48 seconds (nearby or small events)

	// starting with noting the time at the beginning, and labeling column headers.  
	fprintf(summary_file,"SUMMARY FILE FOR COMPARISON OF WAVEFORMS\n\n");
	fprintf(summary_file,"Events at station: %s\n\n", station_name);
	fprintf(summary_file,"Column Key: \n");
	fprintf(summary_file,"Event1 Event2 Mag1 Dist1 Mag2 Dist2 X-corr All_Coherence_Values_Between_0_and_50_Hertz \n\n");

	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	fprintf ( summary_file, "Process started at: %s\n\n", asctime (timeinfo) );
	printf ("Process started at: %s\n\n", asctime (timeinfo) );

	


	// ******* THE MEAT OF THE PROGRAM: ******** //
	// LOOP THROUGH EVENT PAIRS TO COHERE THEM.  FIRST GRAB THE NAMES OF EVENTS IN THE LIST FILE.
	char event1[FILENAME_SIZE];    // the array that will hold event1 
	char event2[FILENAME_SIZE];    // the array that will hold event2 
	char event1_cut[FILENAME_SIZE];    // the array that will hold event1 
	char event2_cut[FILENAME_SIZE];    // the array that will hold event2 
	char cut_prefix[]="CUT_";

	// TIME TO TRY filering using C code that comes with SAC. 
    double low, high, attenuation, transition_bandwidth;;
    int order, passes;
    low    = 2.00;
    high   = 24.00;
    passes = 2;
    order  = 4;
    transition_bandwidth = 0.0;
    attenuation = 0.0;


	// LOOPS THROUGH A LOT OF TIMES
	for(i=0; i<big_number; i++){  

		counter+=1;

		if(i<small_number)  // This is part of controlling the flow of the program for debugging. 
		{
			continue;
		}

		if(i==big_number-1)
		{
			printf("OOPS!  WE REACHED %d AND DIDN'T FINISH ALL THE EVENT PAIRS.\n", big_number);
			printf("PLEASE SPECIFY A BETTER BIG_NUMBER!!! \n");
		}

		// Set the program up to see the filtered and raw files
		// Read in the names of sac files from our list_file. Create the cut_sac_file names. 
		fscanf(list_file, "%s %s", &event1, &event2);
		if(feof(list_file)){
			break;
		}

		for( j = 0; j < FILENAME_SIZE; j++){
			if (j<8){
				event1_cut[j] = event1[j];
				event2_cut[j] = event2[j];
			}
			else if (j<12){
				event1_cut[j] = cut_prefix[j-8];
				event2_cut[j] = cut_prefix[j-8];
			}
			else if (j>=12){
				event1_cut[j] = event1[j-4];
				event2_cut[j] = event2[j-4];
			}
		}

		//Debugging code
		// printf("event1:%s\n",event1);
		// printf("event2:%s\n",event2);

		// ARE THE EVENTS VERY CLOSE IN TIME?  IF YES, THEN SKIP THEM.  
		skip_close_events=close_events_in_time(event1,event2,seconds_apart);
		if(skip_close_events)
			continue;

		// NOW WE READ THE SAC FILES FOR DATA AND METADATA (MAGNITUDE AND DISTANCE)
		rsac1( event1_cut, yarray1_cut, &nlen, &beg, &del, &max, &nerr, strlen( event1_cut ) ) ;
		if ( nerr != 0 ) {
			printf("%d",nerr);
			printf("Error reading in #1 SAC file: [%s]\n", event1_cut);
			//continue;
			exit ( nerr ) ;
		}
		//printf("Success in reading file %s, and ",event1);

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

		strtok(event2_cut, "\n");
		rsac1( event2_cut, yarray2_cut, &nlen, &beg, &del, &max, &nerr, strlen( event2_cut ) ) ;
		if ( nerr != 0 ) {
			printf("%d",nerr);
			printf("Error reading in #2 SAC file: [%s]\n", event2_cut);
			//continue;
			exit ( nerr ) ;
		}
		//printf("Success in reading file %s\n",event2);
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


		// MAKING FILTERED VERSIONS OF THE WAVEFORMS. THANK YOU SAC.  
		memcpy(yarray1_filtered,yarray1_cut, MAXNUM * sizeof(float));
		memcpy(yarray2_filtered,yarray2_cut, MAXNUM * sizeof(float));
		xapiir(yarray1_filtered, nlen, SAC_BUTTERWORTH, transition_bandwidth, attenuation, order, SAC_BANDPASS, low, high, del, passes);
		xapiir(yarray2_filtered, nlen, SAC_BUTTERWORTH, transition_bandwidth, attenuation, order, SAC_BANDPASS, low, high, del, passes);


		// FIRST WE PERFORM XCORR AND SEE IF WE NEED TO SHIFT THE TIME SERIES. 
		max_xcorr=xcorr(yarray1_filtered, yarray2_filtered, MAXNUM, maxdelay);
		// printf("Time Shift is : %d\n",time_shift);
		// if we do need to shift around, we've saved time_shift into a global variable. 

		len_of_ts=get_len_of_time(mag1, mag2, dist1, dist2);  // get the appropriate length of time to do coherence (might be less than MAXNUM samples)
		adjusted_len_of_ts=len_of_ts - abs(time_shift);
		adjusted_len_of_ts=sanitize_len_of_time(adjusted_len_of_ts);		// fixing a bug where one fft window ends up with a single datapoint. 
		npfft = get_npps(adjusted_len_of_ts);  // give us number of points per fft window, based on len_of_ts
		// ^^ global variable. 


		// If the events are highly correlated, we will shift the time-series to get better coherences. 
		if(max_xcorr>cross_correlation_cutoff) 
		{
			printf("Time Shift is: %d; TS length is: %d; npfft is %d \n", time_shift, len_of_ts, npfft);
			if(time_shift<-maxdelay || time_shift>maxdelay)
				printf("ERROR: Invalid time shift.  Double Check this at %s,  %s.  \n", event1, event2);


			// shift arrays around and write the SHIFTED RAW arrays into coh_input file.  
			if(time_shift>=0)  // for a positive time-shift
			{
				input_file = fopen(input_file_name, "w+");    // file with input data
				for(j=0; j<adjusted_len_of_ts; j++){
					fprintf(input_file, "%G %G \n", yarray1_cut[j], yarray2_cut[j+abs(time_shift)]);
				}
				fclose(input_file);	
			}
			if(time_shift<0)  // for a negative time-shift
			{
				input_file = fopen(input_file_name, "w+");    // file with input data
				for(j=0; j<adjusted_len_of_ts; j++){
					fprintf(input_file, "%G %G \n", yarray1_cut[j+abs(time_shift)], yarray2_cut[j]);
				}
				fclose(input_file);	
			}

			//This is tricky: recompute max_xcorr for the shorter optimally-shifted array. 
	        yarray1_subevent=(float *)malloc((len_of_ts-abs(time_shift)) * sizeof(float));  
        	yarray2_subevent=(float *)malloc((len_of_ts-abs(time_shift)) * sizeof(float));  

        	if(time_shift>=0)
        	{
	        	yarray1_subevent=memcpy(yarray1_subevent, &yarray1_filtered[0], (len_of_ts-abs(time_shift)) * sizeof(float));
	        	yarray2_subevent=memcpy(yarray2_subevent, &yarray2_filtered[abs(time_shift)], (len_of_ts-abs(time_shift)) * sizeof(float));
        	}
        	if(time_shift<0)
        	{
	        	yarray1_subevent=memcpy(yarray1_subevent, &yarray1_filtered[abs(time_shift)], (len_of_ts-abs(time_shift)) * sizeof(float));
	        	yarray2_subevent=memcpy(yarray2_subevent, &yarray2_filtered[0], (len_of_ts-abs(time_shift)) * sizeof(float));
        	}

        	//printf("Maxcorr: %f ", max_xcorr);
        	max_xcorr=xcorr(yarray1_subevent, yarray2_subevent, len_of_ts-abs(time_shift), 1);
        	//printf("Maxcorr: %f \n", max_xcorr);

        	free (yarray1_subevent);
        	free (yarray2_subevent);


			// FOR THE HIGHLY-CORRELATED EVENT PAIRS: GENERATE COHERENCE; 
			// WRITE CROSS CORRELATION, COHERENCE, AND METADATA TO FILE. 
			fprintf(output_file, "%s %s ", event1, event2);
			fprintf(output_file, "%.2f %.4f %.2f %.4f ", mag1, dist1, mag2, dist2);
			fprintf(output_file, "%.4f ", max_xcorr);


			// Call coherence and write to output file. 
			call_coherence(sampfreq);    // generate coherence values (reads input from two-column file)

			time_shift=0;  // setting this to zero for safety. 
			number_of_shifts+=1;
		}

		// Am I still alive? 
		if((counter % 20000)==0){
			printf("%d...\n",counter);
		} // this piece of the code is here to provide console updates that it's still working. 

	} // end the big coherence loop through event pairs


	
	// WRITE ENDING INFORMATION TO THE SUMMARY FILE AND CONSOLE
	fprintf(summary_file,"Cross-Correlation Cutoff: %.3f\n", cross_correlation_cutoff);
	fprintf(summary_file,"Number of Comparisons: %d\n", counter);
	fprintf(summary_file,"Number of Shifted And Printed Comparisons: %d\n\n", number_of_shifts);
	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	fprintf ( summary_file, "Process ended at: %s\n", asctime (timeinfo) );
	printf ("Process finished at: %s\n", asctime (timeinfo) );
	
	printf("Number of Comparisons: %d.   Bye!\n", counter);
	printf("Number of Shifted And Printed Comparisons: %d\n", number_of_shifts);
	

	fclose(summary_file);
	fclose(list_file);
	fclose(output_file);
	return(0);
}




/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::    This function tells me whether two events                   :*/
/*::  		are within 10 seconds of each other				        :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
int close_events_in_time(char event1[], char event2[], int seconds_apart)
{
	long event1_time, event2_time;
	char year1[5], year2[5];
	char doy1[4], doy2[4], hour1[3], hour2[3], minute1[3], minute2[3], second1[3], second2[3];
	char * ptr;
	int j;
	int return_value=0;
	int len_of_event_names;

	len_of_event_names=strlen(event1);   // how long are the event names? 

	// IMPORTANT NOTE: I AM ASSUMING THE EVENT NAMES COME IN THE FORM 
	// *.YYYY.DDD.HHMMSS.????????.sac
	// All the magic numbers in this code are because of this assumption. 

	// ARE THE EVENTS MORE THAN 10 SECONDS APART?  
	for(j=0;j<4;j++){  // get the event year. 
		year1[j]=event1[len_of_event_names - 28 + j];
		year2[j]=event2[len_of_event_names - 28 + j];
	}
	year1[4]='\0';
	year2[4]='\0';

	for(j=0;j<3;j++){ // get the event day. 
		doy1[j]=event1[len_of_event_names - 23 + j];
		doy2[j]=event2[len_of_event_names - 23 + j];
	}
	doy1[3]='\0';
	doy2[3]='\0';
	// printf("Day 1 is... %s\n",doy1);
	// printf("Day 2 is... %s\n",doy2);

	for(j=0; j<2; j++){ // get the HHMMSS information
		hour1[j]=event1[len_of_event_names - 19 + j];
		hour2[j]=event2[len_of_event_names - 19 + j];
		minute1[j]=event1[len_of_event_names - 17 + j];
		minute2[j]=event2[len_of_event_names - 17 + j];
		second1[j]=event1[len_of_event_names - 15 + j];
		second2[j]=event2[len_of_event_names - 15 + j];
	}
	hour1[2]='\0';
	hour2[2]='\0';
	minute1[2]='\0';
	minute2[2]='\0';
	second1[2]='\0';
	second2[2]='\0';

	int year1_int, year2_int, year_difference;
	year1_int=strtol(year1,NULL,10);
	year2_int=strtol(year2,NULL,10);
	year_difference=year2_int - year1_int;


	if ( year_difference == 0 ){ // the events are in the same year
		//printf("%s %s %s %s \n", year1, year2, doy1, doy2);

		// Each event time in seconds from the beginning of the year. 
		event1_time=strtol(doy1,&ptr,10)*(3600*24)+strtol(hour1,&ptr,10)*3600+strtol(minute1,&ptr,10)*60+strtol(second1,&ptr,10);
		event2_time=strtol(doy2,&ptr,10)*(3600*24)+strtol(hour2,&ptr,10)*3600+strtol(minute2,&ptr,10)*60+strtol(second2,&ptr,10);
		
		if(abs(event1_time - event2_time) < seconds_apart){
			printf("WE HAVE FOUND TWO VERY CLOSE EVENTS!  ");
			printf("%s %s \n", event1, event2);
			return_value=1;
			// get out of the loop!!!
		}
	}

	if ( year_difference == 1){  // the events are one year apart; Check for the rare case of events occurring over New Years!
		// I can't believe I'm writing this. 

		// Each event time in seconds from the beginning of the year. 
		event1_time=(strtol(doy1,&ptr,10)-1)*(3600*24)+strtol(hour1,&ptr,10)*3600+strtol(minute1,&ptr,10)*60+strtol(second1,&ptr,10);
		event2_time=(strtol(doy2,&ptr,10)-1)*(3600*24)+strtol(hour2,&ptr,10)*3600+strtol(minute2,&ptr,10)*60+strtol(second2,&ptr,10);		

		if (strtol(doy2,&ptr,10)==1){
			if ( year1_int%4 == 0 ){ // for leap years
				if ( strtol(doy1,&ptr,10) == 366 ){
					if (abs((event1_time-366*3600*24) - event2_time) < seconds_apart){ // the events are near in time, but over the new year. 
						return_value=1;
					}
				}
			}
			else { // it's not a leap year. 
				if ( strtol(doy1,&ptr,10) >= 365 ){
					if (abs((event1_time-365*3600*24) - event2_time) < seconds_apart){ // the events are near in time, but over the new year. 
						return_value=1;
					}
				}
			}
		}
	}



	return(return_value);
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
    int delay;
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
    time_shift=best_delay;
    return cc_max;
}







void call_coherence(double sampfreq)
{
    int pps = npfft;
    double sfx = 1.0, sfy = 1.0;
    double coherence_value;

    // Pre-allocating memory for the major arrays:
    if ((xx = (double *)calloc(npfft, sizeof(double))) == NULL ||
	(yy = (double *)calloc(npfft, sizeof(double))) == NULL ||
	(gxx = (double *)calloc(npfft/2 + 1, sizeof(double))) == NULL ||
	(gyy = (double *)calloc(npfft/2 + 1, sizeof(double))) == NULL ||
	(gxyre = (double *)calloc(npfft/2 + 1, sizeof(double))) == NULL ||
	(gxyim = (double *)calloc(npfft/2 + 1, sizeof(double))) == NULL ||
	(phi = (double *)calloc(npfft/2 + 1, sizeof(double))) == NULL ||
	(weight = (double *)calloc(npfft, sizeof(double))) == NULL) {
	(void)fprintf(stderr,
		      "Insufficient memory (try again using -n %d)\n",
		      npfft/2);
	exit(1);
    }

    ifile = fopen(input_file_name,"r");

    if (ifile == NULL) {
	(void)fprintf(stderr, "Unable to Open Input File. \n");
	exit(1);
    }
    
    /* Number of FFT inputs (a power of 2 no less than nnn). */
    for (npfft = 2; npfft < pps; npfft <<= 1)
	;
	
	//printf("pps is: %d\n", pps);
    coherence(pps, sfx, sfy, sampfreq);
    fclose(ifile);
    //printf("Successful Coherence.\n");

    // release memory for next time. 
    free (xx);
    free (yy);
    free (gxx);
    free (gyy); 
    free (gxyre); 
    free (gxyim);
    free (phi);
    free (weight);

    return;

}









/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  NO NEED TO LOOK BEYOND THIS POINT                             :*/
/*::  Coherence code from George Moody's website (has docs          :*/
/*::  Taken from http://paulbourke.net/miscellaneous/correlate/     :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/


void coherence(nnn, sfx, sfy, sampfreq)
int nnn;	/* number of points per segment */
double sfx, sfy;/* scale factors for input data */
double sampfreq; /*instrument sampling frequency*/
{
    double df, dt, sf, temp1, temp2, temp3, temp4;
    int i, nd2;
    int nffts=0;
    int nloaded=0;

    /* Number of FFT outputs (half of the number of inputs). */
    nd2 = npfft/2;

    /* Compute Hanning window. */
    for (i = 0; i < nnn; i++)
	weight[i] = 0.5*(1 - cos(2.0*M_PI*i/(nnn - 1)));

    /* Read a pair of segments, and compute and sum their spectra. */
    for (nffts = 0; (nloaded = load(xx, yy, nnn, nffts)) > 0; nffts++) {
	    //printf("Hello from insdie the loading loop.  Nloaded=%d\n", nloaded);
		/* Detrend and zero-mean xx[] and yy[]. */
		lremv(xx, nloaded);
		lremv(yy, nloaded);

		/* Apply Hanning window. */
		for (i = 0; i < nloaded; i++) {
		    xx[i] *= weight[i];
		    yy[i] *= weight[i];
		}

		/* Compute forward FFT. */
		fft842(0, npfft, xx, yy);

		/* Compute auto- and cross-spectra. */
		gxx[0] += 4.0 * xx[0] * xx[0];
		gyy[0] += 4.0 * yy[0] * yy[0];
		gxyre[0] += 2.0 * xx[0] * yy[0];
		gxyim[0] = 0.0;
		for (i = 1; i < nd2; i++) {
		    double xi = xx[i], xj = xx[npfft-i],
		           yi = yy[i], yj = yy[npfft-i];

		    gxx[i] += (xi+xj)*(xi+xj) + (yi-yj)*(yi-yj);
		    gyy[i] += (yi+yj)*(yi+yj) + (xi-xj)*(xi-xj);
		    gxyre[i] += xi*yj + xj*yi;
		    gxyim[i] += xj*xj + yj*yj - xi*xi - yi*yi;
		}
    }
    //printf("NFFTS = %d \n",nffts);
    if (nffts == 0) return;
    

    /* Sample interval (seconds). */
    dt = 1.0/sampfreq;

    /* Frequency interval (Hz). */
    df = 1.0/(dt*npfft);

    /* Normalize estimates. */
    temp1 = sfx * dt / (4.0 * nnn * nffts);
    temp2 = sfy * dt / (4.0 * nnn * nffts);
    sf = sqrt(fabs(sfx*sfy));
    temp3 = sf  * dt / (2.0 * nnn * nffts);
    temp4 = sf  * dt / (4.0 * nnn * nffts);

    for (i = 0; i < nd2; i++) {
		gxx[i] *= temp1;
		gyy[i] *= temp2;
		gxyre[i] *= temp3;
		gxyim[i] *= temp4;
		/* Compute and print magnitude squared coherence (dimensionless), and
		   cross- and auto-spectra (in dB). */
		phi[i] = gxyre[i]*gxyre[i] + gxyim[i]*gxyim[i];
		if (gxx[i] == 0.0 || gyy[i] == 0.0) xx[i] = 1.0;
		else xx[i] = phi[i] / (gxx[i]*gyy[i]);

		// THIS IS HOW WE OUTPUT THE COHERENCE VALUES
		// (void)printf("%9.4lf  %9.4lf  %10.4lf  %10.4lf  %10.4lf\n",
		// 	     df*i, xx[i],
		// 	     (phi[i] > 1.0e-10 ? 5.0*log10(phi[i]) : -50.0),
		// 	     (gxx[i] > 1.0e-10 ? 10.0*log10(gxx[i]) : -100.0),
		// 	     (gyy[i] > 1.0e-10 ? 10.0*log10(gyy[i]) : -100.0));

    }
	sample_coherence(sampfreq);
	return;
}




void sample_coherence(double sampfreq)
// written by K. Materna.  This function write the entire coherence function between two waveforms. 
// The entire function is written out for further analysis later. 
{	
	// print the entire range of coherence values from min_freq to max_freq hertz (for analysis later)

	double min_freq=0; // Hz
	double max_freq=sampfreq/2.0;

	double freq_interval = (sampfreq)/(npfft);   // the interval of frequencies in the coherence function x-axis	
	int first_index = round(min_freq / freq_interval);
	int last_index = round(max_freq / freq_interval);   // the first and last pieces of the coherence function we will look at

	int i;
	for(i=first_index; i<last_index; i++){
		fprintf(output_file, "%f ", xx[i]);   
	}

	fprintf(output_file, "\n");
	return;

}



/* This function loads the data arrays. */
int load(xx, yy, nnn, nffts)
double *xx, *yy;/* arrays to be filled */
int nnn;	/* number of values to be loaded into each array (<= npfft) */
int nffts;  /* a way to avoid a stupid static long problem */
{
    int i, nloaded, nd2 = nnn/2;
    static long pos;
    if(nffts==0) pos = 0 ;

    (void)fseek(ifile, pos, 0);
    //printf("fseek ifile...\n");
    //printf("pos = %ld...\n", pos);
    for (i = 0; i < nnn; i++) {
	if (i == nd2) pos = ftell(ifile);
	if (fscanf(ifile, "%lf%lf", xx+i, yy+i) != 2) break;
    }
    nloaded = i;
    if (i < npfft) {
	if (i < nd2) pos = ftell(ifile);
	for ( ; i < npfft; i++)
	    *(xx+i) = *(yy+i) = 0.0;
    }
    return (nloaded);
}

/* This function computes and removes the DC component and the slope of an
   array. */
void lremv(xx, nnn)
double *xx;	/* input data array */
int nnn;	/* number of values in data array */
{
    int i;
    double fln;
    double dc;		/* DC component of data */
    double slope;	/* slope of data */

    dc = slope = 0.0;
    for (i = 0; i < nnn; i++) {
	dc += xx[i];
	slope += xx[i]*(i+1);
    }
    dc /= (double)nnn;
    slope *= 12.0/(nnn*(nnn*(double)nnn-1.0));
    slope -= 6.0*dc/(nnn-1.0);
    fln = dc - 0.5*(nnn+1.0)*slope;
    for (i = 0; i < nnn; i++)
	xx[i] -= (i+1)*slope + fln;
}

void r2tx(nthpo, cr0, cr1, ci0, ci1)
int nthpo;
double *cr0, *cr1, *ci0, *ci1;
{
    int i;
    double temp;

    for (i = 0; i < nthpo; i += 2) {
	temp = cr0[i] + cr1[i];	cr1[i] = cr0[i] - cr1[i]; cr0[i] = temp;
	temp = ci0[i] + ci1[i];	ci1[i] = ci0[i] - ci1[i]; ci0[i] = temp;
    }
}

void r4tx(nthpo, cr0, cr1, cr2, cr3, ci0, ci1, ci2, ci3)
int nthpo;
double *cr0, *cr1, *cr2, *cr3, *ci0, *ci1, *ci2, *ci3;
{
    int i;
    double i1, i2, i3, i4, r1, r2, r3, r4;

    for (i = 0; i < nthpo; i += 4) {
	r1 = cr0[i] + cr2[i];
	r2 = cr0[i] - cr2[i];
	r3 = cr1[i] + cr3[i];
	r4 = cr1[i] - cr3[i];
	i1 = ci0[i] + ci2[i];
	i2 = ci0[i] - ci2[i];
        i3 = ci1[i] + ci3[i];
	i4 = ci1[i] - ci3[i];
	cr0[i] = r1 + r3;
	ci0[i] = i1 + i3;
	cr1[i] = r1 - r3;
	ci1[i] = i1 - i3;
	cr2[i] = r2 - i4;
	ci2[i] = i2 + r4;
	cr3[i] = r2 + i4;
	ci3[i] = i2 - r4;
    }
}

void r8tx(nx, nthpo, length, cr0, cr1, cr2, cr3, cr4, cr5, cr6, cr7, ci0, ci1,
	  ci2, ci3, ci4, ci5, ci6, ci7)
int nx, nthpo, length;
double *cr0, *cr1, *cr2, *cr3, *cr4, *cr5, *cr6, *cr7;
double *ci0, *ci1, *ci2, *ci3, *ci4, *ci5, *ci6, *ci7;
{
    double scale = 2.0*M_PI/length, arg, tr, ti;
    double c1, c2, c3, c4, c5, c6, c7;
    double s1, s2, s3, s4, s5, s6, s7;
    double ar0, ar1, ar2, ar3, ar4, ar5, ar6, ar7;
    double ai0, ai1, ai2, ai3, ai4, ai5, ai6, ai7;
    double br0, br1, br2, br3, br4, br5, br6, br7;
    double bi0, bi1, bi2, bi3, bi4, bi5, bi6, bi7;
    int j, k;

    for (j = 0; j < nx; j++) {
	arg = j*scale;
	c1 = cos(arg);
	s1 = sin(arg);
	c2 = c1*c1 - s1*s1;
	s2 = 2.0*c1*s1;
	c3 = c1*c2 - s1*s2;
	s3 = c2*s1 + s2*c1;
	c4 = c2*c2 - s2*s2;
	s4 = 2.0*c2*s2;
	c5 = c2*c3 - s2*s3;
	s5 = c3*s2 + s3*c2;
	c6 = c3*c3 - s3*s3;
	s6 = 2.0*c3*s3;
	c7 = c3*c4 - s3*s4;
	s7 = c4*s3 + s4*c3;
	for (k = j; k < nthpo; k += length) {
	    ar0 = cr0[k] + cr4[k];	ar4 = cr0[k] - cr4[k];
	    ar1 = cr1[k] + cr5[k];	ar5 = cr1[k] - cr5[k];
	    ar2 = cr2[k] + cr6[k];	ar6 = cr2[k] - cr6[k];
	    ar3 = cr3[k] + cr7[k];	ar7 = cr3[k] - cr7[k];

	    ai0 = ci0[k] + ci4[k];	ai4 = ci0[k] - ci4[k];
	    ai1 = ci1[k] + ci5[k];	ai5 = ci1[k] - ci5[k];
	    ai2 = ci2[k] + ci6[k];	ai6 = ci2[k] - ci6[k];
	    ai3 = ci3[k] + ci7[k];	ai7 = ci3[k] - ci7[k];

	    br0 = ar0 + ar2;		br2 = ar0 - ar2;
	    br1 = ar1 + ar3;		br3 = ar1 - ar3;

	    br4 = ar4 - ai6;		br6 = ar4 + ai6;
	    br5 = ar5 - ai7;		br7 = ar5 + ai7;

	    bi0 = ai0 + ai2;		bi2 = ai0 - ai2;
	    bi1 = ai1 + ai3;		bi3 = ai1 - ai3;

	    bi4 = ai4 + ar6;		bi6 = ai4 - ar6;
	    bi5 = ai5 + ar7;		bi7 = ai5 - ar7;

	    cr0[k] = br0 + br1;
	    ci0[k] = bi0 + bi1;
	    if (j > 0) {
		cr1[k] = c4*(br0-br1) - s4*(bi0-bi1);
		ci1[k] = c4*(bi0-bi1) + s4*(br0-br1);
		cr2[k] = c2*(br2-bi3) - s2*(bi2+br3);
		ci2[k] = c2*(bi2+br3) + s2*(br2-bi3);
		cr3[k] = c6*(br2+bi3) - s6*(bi2-br3);
		ci3[k] = c6*(bi2-br3) + s6*(br2+bi3);
		tr = M_SQRT1_2*(br5-bi5);
		ti = M_SQRT1_2*(br5+bi5);
		cr4[k] = c1*(br4+tr) - s1*(bi4+ti);
		ci4[k] = c1*(bi4+ti) + s1*(br4+tr);
		cr5[k] = c5*(br4-tr) - s5*(bi4-ti);
		ci5[k] = c5*(bi4-ti) + s5*(br4-tr);
		tr = -M_SQRT1_2*(br7+bi7);
		ti =  M_SQRT1_2*(br7-bi7);
		cr6[k] = c3*(br6+tr) - s3*(bi6+ti);
		ci6[k] = c3*(bi6+ti) + s3*(br6+tr);
		cr7[k] = c7*(br6-tr) - s7*(bi6-ti);
		ci7[k] = c7*(bi6-ti) + s7*(br6-tr);
	    }
	    else {
		cr1[k] = br0 - br1;
		ci1[k] = bi0 - bi1;
		cr2[k] = br2 - bi3;
		ci2[k] = bi2 + br3;
		cr3[k] = br2 + bi3;
		ci3[k] = bi2 - br3;
		tr = M_SQRT1_2*(br5 - bi5);
		ti = M_SQRT1_2*(br5 + bi5);
		cr4[k] = br4 + tr;
		ci4[k] = bi4 + ti;
		cr5[k] = br4 - tr;
		ci5[k] = bi4 - ti;
		tr = -M_SQRT1_2*(br7 + bi7);
		ti =  M_SQRT1_2*(br7 - bi7);
		cr6[k] = br6 + tr;
		ci6[k] = bi6 + ti;
		cr7[k] = br6 - tr;
		ci7[k] = bi6 - ti;
	    }
	}
    }
}

void fft842(in, n, x, y)
int in;		/* 0: forward FFT; non-zero: inverse FFT */
int n;		/* number of points */
double *x, *y;	/* arrays of points */
{
    double temp;
    int i, j, ij, j1, j2, j3, j4, j5, j6, j7, j8, j9, j10, j11, j12, j13, j14,
        ji, l[15], nt, nx, n2pow, n8pow;

    for (n2pow = nt = 1; n2pow <= 15 && n > nt; n2pow++)
	nt <<= 1;
    n2pow--;
    if (n != nt) {
	(void)fprintf(stderr, "fft842: %d is not a power of 2\n", n);
	exit(2);
    }
    n8pow = n2pow/3;
    if (in == 0) {
	for (i = 0; i < n; i++)
	    y[i] = -y[i];
    }

    /* Do radix 8 passes, if any. */
    for (i = 1; i <= n8pow; i++) {
	nx = 1 << (n2pow - 3*i);
	r8tx(nx, n, 8*nx,
	     x, x+nx, x+2*nx, x+3*nx, x+4*nx, x+5*nx, x+6*nx, x+7*nx,
	     y, y+nx, y+2*nx, y+3*nx, y+4*nx, y+5*nx, y+6*nx, y+7*nx);
    }

    /* Do final radix 2 or radix 4 pass. */
    switch (n2pow - 3*n8pow) {
      case 0:	break;
      case 1:	r2tx(n, x, x+1, y, y+1); break;
      case 2:	r4tx(n, x, x+1, x+2, x+3, y, y+1, y+2, y+3); break;
    }

    for (j = 0; j < 15; j++) {
	if (j <= n2pow) l[j] = 1 << (n2pow - j);
	else l[j] = 1;
    }	
    ij = 0;
    for (j1 = 0; j1 < l[14]; j1++)
     for (j2 = j1; j2 < l[13]; j2 += l[14])
      for (j3 = j2; j3 < l[12]; j3 += l[13])
       for (j4 = j3; j4 < l[11]; j4 += l[12])
	for (j5 = j4; j5 < l[10]; j5 += l[11])
	 for (j6 = j5; j6 < l[9]; j6 += l[10])
	  for (j7 = j6; j7 < l[8]; j7 += l[9])
	   for (j8 = j7; j8 < l[7]; j8 += l[8])
	    for (j9 = j8; j9 < l[6]; j9 += l[7])
	     for (j10 = j9; j10 < l[5]; j10 += l[6])
	      for (j11 = j10; j11 < l[4]; j11 += l[5])
	       for (j12 = j11; j12 < l[3]; j12 += l[4])
		for (j13 = j12; j13 < l[2]; j13 += l[3])
		 for (j14 = j13; j14 < l[1]; j14 += l[2])
		  for (ji = j14; ji < l[0]; ji += l[1]) {
		      if (ij < ji) {
			  temp = x[ij]; x[ij] = x[ji]; x[ji] = temp;
			  temp = y[ij]; y[ij] = y[ji]; y[ji] = temp;
		      }
		      ij++;
		  }
    if (in == 0) {
	for (i = 0; i < n; i++)
	    y[i] = -y[i];
    }
    else {
	for (i = 0; i < n; i++) {
	    x[i] /= (double)n;
	    y[i] /= (double)n;
	}
    }
}
