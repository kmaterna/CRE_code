extern int get_len_of_event_names(char station_name[]);

/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
/*::    This function tells me the length of the                    :*/
/*::  		sac files for each station we might use		    :*/
/*::        Update this for each new project.                       :*/
/*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
int get_len_of_event_names(char station_name[])
{
	int len_of_event_names=0;

	if (strcmp(station_name,"B045")==0){ //Mendocino
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
	if (strcmp(station_name,"KMR")==0){
		len_of_event_names=43;
	}
	if (strcmp(station_name,"KMR")==0){
		len_of_event_names=43;
	}
	if (strcmp(station_name,"B081")==0){ //Anza
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B082")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B084")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B086")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B087")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B088")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B093")==0){
		len_of_event_names=44;
	}
	if (strcmp(station_name,"B946")==0){
		len_of_event_names=44;
	}
	if (len_of_event_names==0){
		printf("ERROR: %s is not one of the recognized stations.  Please check get_len_of_event_names.\n",station_name);
	}

	printf("The length of event names is: %d\n",len_of_event_names);
	return len_of_event_names;
}


