#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include "sacio.h"

/****************************
This code takes an evevnt and generates the list of frequencies that have high SNR.
It uses a small bash script to generate noise_fft.am and waveform_fft.am files. 

It reads the spectral information.
It writes a file with frequencies (left column, Hz) that have high SNR (right column). 

COMPILE WITH THIS LINE RIGHT HERE!!!
gcc -o get_snr get_snr.c -L/$HOME/sac/lib  -lsacio -lsac

EXAMPLE OF USAGE: 
./get_snr

****************************/
#define MAXNUM 1025

// Function prototypes

// Global variables

// Main function
int main(int argc, char *argv[]){

	// Important numbers and files
	int maxnum=MAXNUM;
	char noise_file[]="noise_fft.am";
	char waveform_file[]="waveform_fft.am";

	char output_file_name[] = "SNR.txt";
	FILE * output_file = NULL;
	output_file = fopen(output_file_name,"w+");

	int i,j;
	float start_frequency=0.0;
	float end_frequency=50.0; // in Hz
	int boxcar_width=9;       // for filtering the spectra. 
	float SNR_cutoff=2;       // we keep signal when SNR > this number
	

	// NOW WE READ THE SAC FILES
	float noise_xvals[MAXNUM];
	float noise_yvals[MAXNUM];
	float noise_filtered[MAXNUM];
	float waveform_xvals[MAXNUM];
	float waveform_yvals[MAXNUM];
	float waveform_filtered[MAXNUM];
	float snr[100];  // we have 50Hz as the max frequency, and I'm saving SNR twice per Hz.
	int npts1, npts2, nerr;  // the number of points in the spectral file
	float beg, del;
	float delta1, delta2;  // the frequency spacing of the spectral file
	int index1, index2;

	// READING THE NOISE
	rsac1(noise_file, noise_yvals, &npts1, &beg, &del, &maxnum, &nerr, strlen( noise_file )) ;
	if ( nerr > 0 ) {
		printf("%d",nerr);
		printf("Error reading in noise_fft.sac file: %s\n", noise_file);
		exit(nerr) ;
	}
	printf("Success in reading file %s \n",noise_file);

	getfhv ( "DELTA" , & delta1 , & nerr , strlen("DELTA") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: delta\n");
		exit(-1);
	}


	// READING THE WAVEFORM
	rsac1(waveform_file, waveform_yvals, &npts2, &beg, &del, &maxnum, &nerr, strlen( waveform_file )) ;
	if ( nerr > 0 ) {
		printf("%d",nerr);
		printf("Error reading in noise_fft.sac file: %s\n", waveform_file);
		exit(nerr) ;
	}
	printf("Success in reading file %s \n",waveform_file);
	getfhv ( "DELTA" , & delta2 , & nerr , strlen("DELTA") ) ;
	// Check the Return Value 
	if ( nerr != 0 ) {
		fprintf(stderr, "Error getting header variable: delta\n");
		exit(-1);
	}

	// Making the list of frequencies in the spectrum (might be different). 
	for (i = 0; i<npts1; i++)
	{
		noise_xvals[i]=i*delta1;
	}
	for (i = 0; i<npts2; i++)
	{
		waveform_xvals[i]=i*delta2;
	}

	// FILTERING THE NOISE SPECTRUM (SIMPLE AVERAGING BOXCAR WITH WIDTH OF NINE)
	int count;
	float sum;
	for (i = 0; i<=npts1; i++)
	{
		count=0;
		sum=0;
		if (i <= boxcar_width) // the very lower end of the spectrum 
		{
			for (j=0;j<=i+boxcar_width;j++)
			{
				count+=1;
				sum+=noise_yvals[j];
			}
			noise_filtered[i]=sum/(float)count;
		}
		else if (i >= npts1-boxcar_width)  // the very upper end of the spectrum
		{
			for (j=i-boxcar_width;j<=npts1;j++)
			{
				count+=1;
				sum+=noise_yvals[j];
			}
			noise_filtered[i]=sum/(float)count;
		}
		else // the normal cases (middle of the spectrum)
		{
			for (j=i-boxcar_width;j<=i+boxcar_width;j++)
			{
				sum+=noise_yvals[j];
			}
			noise_filtered[i]=sum/(float)(boxcar_width+boxcar_width+1);
		}
	}

	for (i = 0; i<=npts2; i++)
	{
		count=0;
		sum=0;
		if (i <= boxcar_width) // the very lower end of the spectrum 
		{
			for (j=0;j<=i+boxcar_width;j++)
			{
				count+=1;
				sum+=waveform_yvals[j];
			}
			waveform_filtered[i]=sum/(float)count;
		}
		else if (i >= npts2-boxcar_width)  // the very upper end of the spectrum
		{
			for (j=i-boxcar_width;j<=npts2;j++)
			{
				count+=1;
				sum+=waveform_yvals[j];
			}
			waveform_filtered[i]=sum/(float)count;
		}
		else // the normal cases (middle of the spectrum)
		{
			for (j=i-boxcar_width;j<=i+boxcar_width;j++)
			{
				sum+=waveform_yvals[j];
			}
			waveform_filtered[i]=sum/(float)(boxcar_width+boxcar_width+1);
		}
	}


	// Signal to noise ratio!  Twice per Hz, from zero to 50. [0, 0.5, 1.0, 1.5, 2.0, ...]
	float placement_in_array;
	for (i=0; i<=2*(int)end_frequency; i++)
	{
		placement_in_array=(float)i;
		index1=(int)((placement_in_array/2.0)/delta1);  // where in the noise array you want to look
		index2=(int)((placement_in_array/2.0)/delta2);  // where in the waveform array you want to look
		// the 2.0 is because we're doing two steps per Hz. 
		
		snr[i]=waveform_filtered[index2]/noise_filtered[index1];
		if(snr[i]>=SNR_cutoff)
		{
			fprintf(output_file,"%f %f\n",placement_in_array/2.0,snr[i]);
		}
	}
	fclose(output_file);
	printf("Output file written.\n");


	return(0);

}

