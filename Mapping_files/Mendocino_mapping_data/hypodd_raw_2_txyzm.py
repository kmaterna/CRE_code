"""
Python script to prepare useful mapping files from the results of online catalog searches. 

Example: let's make a new-and-updated HYPODD.TXYZM file. 
Go to: http://www.ncedc.org/ncedc/catalog-search.html
Search parameters: 
	double-differenced catalog. 
	start_time=1984/01/01,00:00:00
	end_time=2017/08/31,00:00:00
	minimum_latitude=39.5
	maximum_latitude=41.5
	minimum_longitude=-126.2
	maximum_longitude=-123
	minimum_magnitude=0.0
	maximum_magnitude=10
Copy/pasta the whole results page into hypodd_raw_search.eq, and then run this script. 
"""

from sys import exit

def get_time(year_string, time_string):
	"""
	The purpose of this function is to turn two strings like "2016/11/30 23:18:35.17" and turn them into a decimal year. 
	"""
	year=float(year_string[0:4])
	month=float(year_string[5:7])
	day=float(year_string[8:10])
	hour=float(time_string[0:2])
	minute=float(time_string[3:5])
	second=float(time_string[6:8])
	
	dec_time=year+((month-1.0)/12.0)+((day-1)/365.24)+(hour/(365.24*24))+(minute/(365.24*24*60))+(second/(365.24*24*60*60));
	return dec_time;



if __name__=="__main__":
	input_file="hypodd_raw_search.eq"
	output_file="hypodd.txyzm"
	ifile=open(input_file,'r');
	ofile=open(output_file,'w');

	# The meat of the program 
	for line in ifile:
		temp=line.split();
		test_item=str(temp[0]);
		test_item=test_item[0:4]
		if test_item.isdigit():  # are we looking at an actual data row?  not a header?  
			year_str=temp[0]
			time_str=temp[1]
			lat=temp[2]
			lon=temp[3]
			dep=temp[4]
			mag=temp[5]
			dec_time=get_time(year_str,time_str);
			ofile.write(str(dec_time)+" "+lon+" "+lat+" "+dep+" "+mag+"\n");
	ofile.close();
	ifile.close();
