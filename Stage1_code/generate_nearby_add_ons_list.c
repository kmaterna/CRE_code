#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "sacio.h"

// User defined values
#define MAXIMUM 11200   // Maximum length of the data array. 
#define FILENAME_SIZE 60  // Maximum number of characters in a sac filename
#define pi 3.14159265358979323846 

// COMPILE WITH THIS LINE RIGHT HERE!!!
// gcc -o exec_name source_name.c -L/$HOME/sac/lib  -lsacio -lsac (mac machines)
// gcc -o exec_name source_name.c -L/share/apps/sac/lib -lsacio -lsac -lm (linux machines)
// This script takes the list of existing and add-on files, and generates a list of 
// event pairs that need comparing.  Added-to-exist and Added-to-added will be compared. 

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  Function prototypes                                           :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
float coord2distance(float, float, float, float);
double deg2rad(double);
double rad2deg(double);
int get_len_of_event_names(char[]);
float compare_two_events(char[], char[], float);
int within_box(char[], float, float);

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  Main Program                                                  :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/

int main(int argc, char *argv[]){

	// PARAMETERS CHANGED BY THE USER
	float distance_cutoff = 10.0; // kilometers (above this event distance and we don't cross-correlate)
    // we use a smaller distance cutoff (1-2km instead of 30km) for Anza.
       float eastern_cutoff = -123.3;
       float western_cutoff = -127.0; 

	// PARSING PROGRAM ARGUMENTS
	if( argc != 3 ){   // check if you have provided a station name
		printf("Oops! You have provided the wrong number of arguments.\n");
		printf("We want something like ./nearby station_name list_file (Ex: ./nearby B046 B046_nearby_list.txt). \n");
		exit(1);
	}

	// LIST OF USEFUL INPUT FILES
	FILE * exist_flist;
	FILE * added_flist;
	exist_flist = fopen("exist/exist_file_list.txt", "r");    // file with list of existing events
	if (exist_flist == NULL){
		printf("ERROR: Error opening: exist_file_list.txt\n");
		printf("Exiting the program...\n");
		exit(1);
	}
	added_flist = fopen("added/added_file_list.txt", "r");    // file with list of existing events
	if (exist_flist == NULL){
		printf("ERROR: Error opening: added_file_list.txt\n");
		printf("Exiting the program...\n");
		exit(1);
	}


	// Please parse the name of the station 
	int len_of_station_name;                             // this is just for naming the output files correctly. 
	len_of_station_name=strlen(argv[1]);                 // the length of a null-terminated string from the user. 
	char station_name[len_of_station_name+1];            // get the name of the station, which is null-terminated. 
	memcpy(station_name,argv[1],len_of_station_name+1);  // save the name of the argument/station (usually 3 or 4 characters)

	// Please parse the name of the output file
	int len_of_output_file;                              // this is just for naming the output files correctly. 
	len_of_output_file=strlen(argv[2]);                  // the length of a null-terminated string from the user. 
	char output_name[len_of_output_file+1];             // get the name of the output_file, which is null-terminated. 
	memcpy(output_name,argv[2],len_of_output_file+1);  // save the name of the argument

	// Please open the output file
	FILE * outptr;  // the output file pointer
	outptr = fopen(output_name,"w");                       // detailed output file
	printf("\nStarting the generate_nearby_add_ons calculation.\n");
	printf("Station name is: %s\n",station_name);
	printf("Output_filename is: %s\n",output_name);

	

	// DECLARING INTERNAL VARIABLES
	time_t rawtime;           // for getting the start-time and end-time of the process
	struct tm * timeinfo;
	int i, j, k, n;
	int num_exist_events;
	int num_added_events;
	int comparisons = 0;      // the number of inter-event distances we compute
	int hits = 0;             // the number of nearby pairs	
	float distance;
	int len_of_event_names=FILENAME_SIZE;
        int within_box_flag1 = 1;
        int within_box_flag2 = 1;

	// Please declare strings of the right length to hold our file name data. 
	char event1[len_of_event_names]; // getting ready to hold names of files during the computations. 
	char event2[len_of_event_names];
	char event1_exist[len_of_event_names]; // getting ready to hold names of files during the computations. 
	char event2_exist[len_of_event_names];
	
	// GRAB THE NAMES AND NUMBER OF EVENTS IN THE LIST FILES
	char * buffer;
	char * token; 
	size_t bufsize=64;
	size_t linesize;
	buffer = (char *)malloc(bufsize * sizeof(char));
	if( buffer == NULL)
	{
		perror("Unable to allocate buffer");
		exit(1);
	}  //checking for an unusual error in allocating memory. 


	// Get EXISTING FILES information (list of files). 
	linesize = getline(&buffer, &bufsize, exist_flist);  // get the first line of the list file
	printf("The number of existing events is: %s \n", buffer);
	num_exist_events = strtol(buffer,&token,10);  // First line tells us the number of events in the exist directory
	// This performs a string-to-long, in base 10. 
	// Populate a 2D char array for file names
	char exist_event_names[num_exist_events][len_of_event_names];  // 2D char array of existing file names
	for( i=0; i< num_exist_events; i++){
		linesize = getline(&buffer, &bufsize, exist_flist);
		for( j = 0; j < len_of_event_names; j++){
			exist_event_names[i][j] = buffer[j];
			//printf("%c",exist_event_names[i][j]);
		}
	}


	// Get NEW FILES information (list of files). 
	linesize = getline(&buffer, &bufsize, added_flist);  // get the first line of the list file
	printf("The number of added events is: %s \n", buffer);
	num_added_events = strtol(buffer,&token,10);  // First line tells us the number of events in the exist directory
	// Populate a 2D char array for file names
	char added_event_names[num_added_events][len_of_event_names];  // 2D char array of existing file names
	for( i=0; i< num_added_events; i++){
		linesize = getline(&buffer, &bufsize, added_flist);
		for( j = 0; j < len_of_event_names; j++){
			added_event_names[i][j] = buffer[j];
			//printf("%c",added_event_names[i][j]);
		}

	} // SET-UP COMPLETE


	// BEGIN PROCESSING
	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	printf ("Process started at: %s\n\n", asctime (timeinfo) );


	// BEGIN SAC READING LOOP: ADDED EVENTS VS EXISTING EVENTS
	for( i=0; i < num_added_events; i++){ 
		
		// READ FIRST ADDED EVENT AND ITS LAT/LONG METADATA
		for( k=0; k< len_of_event_names; k++){
			event1[k]=added_event_names[i][k];
		}
		strtok(event1, "\n");
		//printf("event1 is: %s",event1);

		for( j=0; j < num_exist_events; j++){  
			for( k=0; k < len_of_event_names; k++){
				event2[k]=exist_event_names[j][k];
			}
			strtok(event2, "\n");

			distance=compare_two_events(event1,event2, distance_cutoff);  // will you write them to the file? 
			comparisons += 1;  // How many distances did we compute?
                        within_box_flag1=within_box(event1, eastern_cutoff, western_cutoff);
                        within_box_flag2=within_box(event2, eastern_cutoff, western_cutoff);
                        if(within_box_flag1==0 || within_box_flag2==0){
                            continue;
                        }
			if(distance>=0 && distance<distance_cutoff){
				hits += 1;    // We've found a nearby pair
				strcpy(event1_exist,event1);
				strcpy(event2_exist,event2);
				memcpy(event1_exist,"./exist/",8);  // save the name of the file in the exist directory
				memcpy(event2_exist,"./exist/",8);  // save the name of the file in the exist directory
				fprintf(outptr,"%s %s\n", event1, event2);
			} // end less-than-cutoff-km if statement

		}
	}


	// DOING THIS A SECOND TIME: FOR ADDED VS ADDED EVENTS
	for( i=0; i < num_added_events; i++){ 
		
		// READ FIRST ADDED EVENT AND ITS LAT/LONG METADATA
		for( k=0; k< len_of_event_names; k++){
			event1[k]=added_event_names[i][k];
		}
		strtok(event1, "\n");
		//printf("event1 is: %s",event1);

		// LOOP THROUGH CHOICES FOR SECOND EVENT
		for( j=i+1; j < num_added_events; j++){  
			for( k=0; k < len_of_event_names; k++){
				event2[k]=added_event_names[j][k];
			}
			strtok(event2, "\n");

			distance=compare_two_events(event1,event2,distance_cutoff);
			comparisons += 1;  // How many distances did we compute?
                        within_box_flag1=within_box(event1, eastern_cutoff, western_cutoff);
                        within_box_flag2=within_box(event2, eastern_cutoff, western_cutoff);
                        if(within_box_flag1==0 || within_box_flag2==0){
                            continue;
                        }
			if(distance>=0 && distance<distance_cutoff){
				hits += 1; // We've found a nearby pair				
				strcpy(event1_exist,event1);
				strcpy(event2_exist,event2);
				memcpy(event1_exist,"./exist/",8);  // save the name of the file in the exist directory
				memcpy(event2_exist,"./exist/",8);  // save the name of the file in the exist directory
				fprintf(outptr,"%s %s\n", event1_exist, event2_exist);
			} // end less-than-cutoff-km if statement
		}
	}


	// WRITE ENDING INFORMATION TO THE SCREEN
	printf("Number of Existing Waveforms: %d\n", num_exist_events);
	printf("Number of New Waveforms: %d\n", num_added_events);
	printf("Number of Comparisons: %d\n", comparisons);
	printf("Number of Hits: %d\n", hits);
	time ( &rawtime );
	timeinfo = localtime ( &rawtime );
	printf ("Process ended at: %s\n", asctime (timeinfo) );

	// CLOSE EVERYTHING UP
	fclose(exist_flist);
	fclose(added_flist);
	fclose(outptr);
	return(0);
} // end main

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  This function takes two events and decides to compare         :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
int within_box(char event1[], float eastern_cutoff, float western_cutoff)
{
       int flag = 0;
       float evla1, evlo1;
       float beg, del;
       int nlen, nerr; 
       int max = MAXIMUM;
       float yarray1[MAXIMUM];
       // Read the file and their latitudes/longitudes
       rsac1( event1, yarray1, &nlen, &beg, &del, &max, &nerr, strlen( event1 ) ) ;
       if ( nerr != 0 ) {
              printf("%d",nerr);
              printf("Error reading in SAC file: %s\n", event1);
              exit ( nerr ) ;
        }
        getfhv ( "EVLA" , & evla1 , & nerr , strlen("EVLA") ) ;
        if ( nerr != 0 ) {
              fprintf(stderr, "Error getting header variable: evla\n");
              exit(-1);
         }
        getfhv ( "EVLO" , & evlo1 , & nerr , strlen("EVLO") ) ;
        if ( nerr != 0 ) {
              fprintf(stderr, "Error getting header variable: evlo\n");
              exit(-1);
        }
        if(evlo1<=eastern_cutoff && evlo1>=western_cutoff){
              flag=1;
        }
        return(flag);
}	



/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  This function takes two events and decides to compare         :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
float compare_two_events(char event1[], char event2[], float distance_cutoff)
{
	// We write to events to the intermediate file if they are less than x km apart. 

	float yarray1[MAXIMUM];
	float yarray2[MAXIMUM];
	float beg, del;
	int nlen, nerr;
	int max = MAXIMUM;
	float evla1, evlo1, evla2, evlo2;
	float distance;

	// Read the two files and their latitudes/longitudes
	rsac1( event1, yarray1, &nlen, &beg, &del, &max, &nerr, strlen( event1 ) ) ;
	if ( nerr != 0 ) {
		printf("%d",nerr);
		printf("Error reading in SAC file: %s\n", event1);
		exit ( nerr ) ;
	}
	//printf("Success in reading file %s\n",event1);

	getfhv ( "EVLA" , & evla1 , & nerr , strlen("EVLA") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: evla\n");
		exit(-1);
	}
	//printf("EVENT LATITUDE IS: %f\n", evla1);
	getfhv ( "EVLO" , & evlo1 , & nerr , strlen("EVLO") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: evlo\n");
		exit(-1);
	}
	//printf("EVENT LONGITUDE IS: %f\n", evlo1);

	rsac1( event2, yarray2, &nlen, &beg, &del, &max, &nerr, strlen( event2 ) ) ;
	if ( nerr != 0 ) {
		printf("%d",nerr);
		printf("Error reading in SAC file: %s\n", event2);
		exit ( nerr ) ;
	}
	//printf("Success in reading file %s\n",event2);

	// Can we see the latitude and longitude of event 2? 
	getfhv ( "EVLA" , & evla2 , & nerr , strlen("EVLA") ) ;
	if ( nerr != 0 ) {  // Check the Return Value
		fprintf(stderr, "Error getting header variable: evla\n");
		exit(-1);
	}
	//printf("EVENT LATITUDE IS: %f\n", evla2);
	getfhv ( "EVLO" , & evlo2 , & nerr , strlen("EVLO") ) ;
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: evlo\n");
		exit(-1);
	}
	//printf("EVENT LONGITUDE IS: %f\n", evlo2);
	
	// Throwing out some bad comparisons: I don't want if latitude is 0.0000 (I've found a few that exist)
	if(fabs(evla1)<0.01 || fabs(evla2)<0.01){
		// I have found some events where the longitude is 0.0000. I don't want them. 
		distance=-1;
	    // printf("DISTANCE BETWEEN EVENTS: %f KILOMETERS\n", distance);
		// printf("%s %s \n", event1, event2);
		// printf("%f %f %f %f\n", evla1, evlo1, evla2, evlo2);		
	}
	else{
		// CHECK IF LESS THAN CUTOFF VALUE
		distance = coord2distance(evla1, evlo1, evla2, evlo2);
	}
	return (distance);
}




/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  This function goes from coords to kilometer distances         :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
float coord2distance(float lat1, float lon1, float lat2, float lon2){
    float theta, dist;
    theta = lon1 - lon2;
    dist = sin(deg2rad(lat1)) * sin(deg2rad(lat2)) + cos(deg2rad(lat1)) * cos(deg2rad(lat2)) * cos(deg2rad(theta));
    dist = acos(dist);
    dist = rad2deg(dist);
    dist = dist * 60 * 1.1515;
    dist = dist * 1.609344;
    return (dist);
}

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  This function converts decimal degrees to radians             :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
double deg2rad(double deg) {
  return (deg * pi / 180);
}

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  This function converts radians to decimal degrees             :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
double rad2deg(double rad) {
  return (rad * 180 / pi);
}


