#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "sacio.h"

// Define the maximum length of the data array */
#define MAXIMUM 11200   // This was 2048 before; now with the noisy data it's longer. 
#define pi 3.14159265358979323846

// COMPILE WITH THIS LINE RIGHT HERE!!!
// gcc -o exec_name source_name.c -L/$HOME/sac/lib  -lsacio -lsac
// gcc -o exec_name source_name.c -L/share/apps/sac/lib -lsacio -lsac -lm 
// This script takes the list of existing and add-on files, and generates a list of 
// event pairs that need comparing.  Add-on-to-existing and Add-on-to-add-on will be listed. 

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  Function prototypes                                           :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
float coord2distance(float, float, float, float);
double deg2rad(double);
double rad2deg(double);
int get_len_of_event_names(char[]);
void compare_two_events(char[], char[], float, float);



/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::  Major parameters                                              :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/

// Global variables. 
FILE * outptr;  // the output file will be accessible from functions as well. 
int comparisons = 0;      // the number of inter-event distances we compute
int hits = 0;             // the number of nearby pairs

int main(int argc, char *argv[]){

	if( argc != 2 ){   // check if you have provided a station name
		printf("Oops! You have provided the wrong number of arguments.\n");
		printf("We want something like ./nearby station_name (Ex: ./nearby B046). \n");
		exit(1);
	}

	// CHOICES OF PARAMETERS FOR EVENT COMPARISON
	float distance_cutoff = 30.0; // kilometers (above this event distance and we don't cross-correlate)
	float eastern_cutoff = -110;  // We are less interested in events in Nevada and farther east. 
        // we use -123.3. for Mendocino, since we don't want to look at events in Nevada and east. 
        // we don't use this value for Anza. 


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


	// Please sanitize the name of the station (3 characters or 4 characters?). 
	int len_of_station_name;                             // this is just for naming the output files correctly. 
	len_of_station_name=strlen(argv[1]);                 // the length of a null-terminated string from the user. 
	char station_name[len_of_station_name+1];            // get the name of the station, which is null-terminated. 
	memcpy(station_name,argv[1],len_of_station_name+1);  // save the name of the argument/station (usually 3 or 4 characters)

	// Please open an output file
	char output_name[] = "____-nearby_30_km.txt";          // template file name for nearby event pairs
	memcpy(output_name,station_name,len_of_station_name);  // create the name of a file that starts with the argument of argv[1]
	outptr = fopen(output_name,"w");                       // detailed output file
	printf("Station name is: %s\n",station_name);
	printf("Output_filename is: %s\n",output_name);

	// Please declare strings of the right length to hold our file name data. 
	int len_of_event_names = 0;  // the event file names are 44-48 characters long, depending on which station you use. 
	int len_of_event_names_long=0;
	len_of_event_names=get_len_of_event_names(station_name);
	len_of_event_names_long=len_of_event_names+8;   // includes the directory name. 
	char event1[len_of_event_names_long]; // getting ready to hold names of files during the computations. 
	char event2[len_of_event_names_long];
	
	// DECLARING VARIABLES
	time_t rawtime;           // for getting the start-time and end-time of the process
	struct tm * timeinfo;
	int i, j, k, n;
	int num_exist_events;
	int num_added_events;
	
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
	char exist_event_names[num_exist_events][len_of_event_names_long];  // 2D char array of existing file names
	for( i=0; i< num_exist_events; i++){
		linesize = getline(&buffer, &bufsize, exist_flist);
		for( j = 0; j < len_of_event_names_long; j++){
			exist_event_names[i][j] = buffer[j];
			//printf("%c",exist_event_names[i][j]);
		}
	}


	// Get NEW FILES information (list of files). 
	linesize = getline(&buffer, &bufsize, added_flist);  // get the first line of the list file
	printf("The number of added events is: %s \n", buffer);
	num_added_events = strtol(buffer,&token,10);  // First line tells us the number of events in the exist directory
	// Populate a 2D char array for file names
	char added_event_names[num_added_events][len_of_event_names_long];  // 2D char array of existing file names
	for( i=0; i< num_added_events; i++){
		linesize = getline(&buffer, &bufsize, added_flist);
		for( j = 0; j < len_of_event_names_long; j++){
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
		for( k=0; k< len_of_event_names_long; k++){
			event1[k]=added_event_names[i][k];
		}
		strtok(event1, "\n");
		//printf("event1 is: %s",event1);

		for( j=0; j < num_exist_events; j++){  
			for( k=0; k < len_of_event_names_long; k++){
				event2[k]=exist_event_names[j][k];
			}
			strtok(event2, "\n");

			compare_two_events(event1,event2, distance_cutoff, eastern_cutoff);  // will you write them to the file?  
		}
	}


	// DOING THIS A SECOND TIME: FOR ADDED VS ADDED EVENTS
	for( i=0; i < num_added_events; i++){ 
		
		// READ FIRST ADDED EVENT AND ITS LAT/LONG METADATA
		for( k=0; k< len_of_event_names_long; k++){
			event1[k]=added_event_names[i][k];
		}
		strtok(event1, "\n");
		//printf("event1 is: %s",event1);

		// LOOP THROUGH CHOICES FOR SECOND EVENT
		for( j=i+1; j < num_added_events; j++){  
			for( k=0; k < len_of_event_names_long; k++){
				event2[k]=added_event_names[j][k];
			}
			strtok(event2, "\n");

			compare_two_events(event1,event2,distance_cutoff,eastern_cutoff);
		}
	}


    fprintf(outptr,"BREAKFILE\n");

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
void compare_two_events(char event1[], char event2[], float distance_cutoff, float eastern_cutoff)
{
	// We write to events to the intermediate file if both are west of the eastern_cutoff
	// (we don't care about events in Nevada);
	// and if they are less than 30 km apart. 

	int latflag;
	float yarray1[MAXIMUM];
	float yarray2[MAXIMUM];
	float beg, del;
	int nlen, nerr;
	int max = MAXIMUM;
	float evla1, evlo1, evla2, evlo2;
	float distance;


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

	if(evlo1<eastern_cutoff || fabs(evla1)<0.01){
		// we have some events where the longitude is 0.0000.
		// Since I don't trust the locations, I'm giong to check 
		//them for repeater status anyway. 

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

		latflag=0;

		if(evlo2<eastern_cutoff || fabs(evla2)<0.01){
			if(fabs(evla1)<0.01 || fabs(evla2)<0.01){
				latflag=1;
			}

			// CHECK IF LESS THAN 30 KM
			distance = coord2distance(evla1, evlo1, evla2, evlo2);
			//if(distance>1000 || latflag==1){
			//	printf("DISTANCE BETWEEN EVENTS: %f KILOMETERS\n", distance);
				//printf("%s %s \n", event1, event2);
				//printf("%f %f %f %f\n", evla1, evlo1, evla2, evlo2);
			//}

			comparisons += 1;  // How many distances did we compute?

			if(distance<distance_cutoff || latflag==1){
				// for(n=0; n<len_of_event_names_long;n++){
				// 	short_name1[n]=event1[n];
				// 	short_name2[n]=event2[n];
				// }
				hits += 1;    // We've found a nearby pair
				// WRITE VALUE TO OUTPUT FILE
				fprintf(outptr,"%s %s\n", event1, event2);
			} // end less-than-30-km if statement
		}// end east-condition if-statement
	}// end east-condition if-statement
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

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::    This function tells me the length of the                    :*/
/*::  		sac files for each station we might use			        :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
int get_len_of_event_names(char station_name[])
{
	int len_of_event_names=0;

	if (strcmp(station_name,"B045")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B046")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B047")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B049")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B932")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B933")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B934")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B935")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"KCT")==0){
		len_of_event_names=43;
	}
	if (strcmp(station_name,"JCC")==0){
		len_of_event_names=45;
	}
	if (strcmp(station_name,"KHMB")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"KMPB")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"KMR")==0){
		len_of_event_names=43;
	}
	if (strcmp(station_name,"B081")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B082")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B084")==0){
		len_of_event_names=44;
	}
	if (len_of_event_names==0){
		printf("ERROR: %s is not one of the recognized stations.  Please check get_len_of_event_names.\n",station_name);
	}

	printf("The length of event names is: %d\n",len_of_event_names);
	return len_of_event_names;
}


