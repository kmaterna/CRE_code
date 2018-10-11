"""
MAIN PYTHON SCRIPT 
that compares CRE results under different cutoffs for coherence and cross-correlation. 
You can put this into a loop if you'd like. 
Example Options:
Metric = ['coh', 'corr'] # how to determine repeaters: coherence or xcorr? 
Cutoff = [0.95, 0.98]  # all-important cutoff
Statistic = ['mean', 'median'] # how to summarize range of frequencies of coherence calculation
max_freq_options=[8, 15, 25]  # maximum frequency ever touched.
Define_freq = ['snr-based', 'hard-coded', 'magnitude-based'];
SNR_cutoff = [5.0];
Minimum_freq_width = [5.0];
Preferred recipe for Mendocino:
'coh', 0.97, 'mean', 'snr_based', 15, SNR_cutoff=5.0, Minimum_freq_width=5.0.
"""

import collections;
import def_rep_each_station

# The main parameter object. 
TotalParams=collections.namedtuple('TotalParams',['Network_repeaters_list','families_list','families_summaries','station_locations','time_window','stage2_results','mapping_code','mapping_data']); 

# Definition of types of parameters you want to play with. 
Metric = 'corr';
Cutoff = 0.97;
Statistic = 'mean';
max_freq_options=20;
Define_freq = 'snr-based';
SNR_cutoff = 5.0;
Minimum_freq_width = 5.0;

# Parameters that aren't likely to change between experiments
time_window=[2006.7, 2016.20]; # start time and end time for repeater search, etc. You may want to change this. 
families_list="families_list.txt";
families_summaries="Families_Summaries.txt";
stage2_results="Stage2_Results";
station_locations="station_locations.txt";
Network_repeaters_list='Network_CRE_pairs_list.txt';
mapping_code='/work/seismo85/kmaterna/CRE_detection/Mapping_files/Anza_mapping_code';  # you will want to change this if you're interested in a different place, like Mendocino, Anza, etc. 
mapping_data='/work/seismo85/kmaterna/CRE_detection/Mapping_files/Anza_mapping_data';
MyParams=TotalParams(Network_repeaters_list=Network_repeaters_list, families_list=families_list, families_summaries=families_summaries,station_locations=station_locations,time_window=time_window, stage2_results=stage2_results, mapping_code=mapping_code, mapping_data=mapping_data);


# # Preferred
#def_rep_each_station.full_CRE_analysis(MyParams,'coh', 0.98, 'mean', 'snr_based', 20, SNR_cutoff, Minimum_freq_width);  # example with coherence
def_rep_each_station.full_CRE_analysis(MyParams, Metric, Cutoff);   # example with cross correlation


