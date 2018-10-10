"""
The purpose of this script to go into an existing results file and remove any event pairs that 
need to be redone.  The result will be a results file (with the same name) that has fewer event pairs, 
because some have been deleted.  
"""

from subprocess import call
import numpy as np
from sys import argv

station_name=argv[1];
if len(station_name)==3:
	station_name=station_name+'_';

existing_results_file=station_name+"-above_cutoff_results.txt";           # just a placeholder
copy_of_results_file =station_name+"-before_del_results_file.txt";        # This is a copy that you don't touch. 
working_results_file =station_name+"-working_deleting_results_file.txt";  # This one you keep reading, then writing over the next time
write_to_results_file=station_name+"-above_cutoff_results.txt";           # This one you keep writing each time. 

call(["cp",existing_results_file,copy_of_results_file], shell=False);   # just a copy; don't touch. 
call(["cp",existing_results_file,working_results_file], shell=False);   # this one's gonna keep getting smaller and smaller. 

filelist=open("redos/redos_file_list.txt",'r');
filelist.readline()

for line in filelist:
	temp=line.split();
	redo_event=temp[0];  # We've got a file to replace. Want to delete it.  
	
	readfile=open(working_results_file,'r');
	writefile=open(write_to_results_file,'w+');

	for line in readfile:
		temp2=line.split();
		ev1=temp2[0];  # event1 
		ev2=temp2[1];  # event2 

		if ev1 != redo_event and ev2 != redo_event:
			writefile.write(line);   # write the line as long as it DOESN'T contain the redos. 

	readfile.close();
	writefile.close();

	call(["cp",write_to_results_file,working_results_file], shell=False);   # for each re-do, create a new slightly-smaller results file. 

call(["rm",working_results_file], shell=False);   # want to clean up?
call(["rm",copy_of_results_file], shell=False);   # want to clean up?
