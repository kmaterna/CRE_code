"""
MAIN PYTHON SCRIPT 
that compares CRE results under different cutoffs for coherence and cross-correlation. 
Preferred recipe for Mendocino:
'coh', 0.97, 'mean', 'snr_based', 15, SNR_cutoff=5.0, Minimum_freq_width=5.0.
"""

import collections;
import def_rep_each_station

TotalParams=collections.namedtuple('TotalParams',[
	'Network_repeaters_list',
	'families_list',
	'families_summaries',
	'station_locations',
	'time_window',
        'stage1_results',
        'stage2_results'])


# Definition of types of parameters I want to loop through. 
Metric = ['coh', 'corr']
Cutoff = [0.95, 0.98]
Statistic = ['mean', 'median']
max_freq_options=[8, 15, 25]
Define_freq = ['snr-based', 'hard-coded', 'magnitude-based'];
SNR_cutoff = [5.0];
Minimum_freq_width = [5.0];

# Parameters that aren't likely to change between experiments
time_window=[2008.7, 2017.60]; # start time and end time for repeater search, etc. 
Network_repeaters_list='Network_CRE_pairs_list.txt';
families_list="families_list.txt";
families_summaries="Families_Summaries.txt";
stage1_results="Stage1_Results"
stage2_results="Stage2_Results"
station_locations="station_locations.txt"
MyParams=TotalParams(Network_repeaters_list=Network_repeaters_list, families_list=families_list, families_summaries=families_summaries,
	station_locations=station_locations,time_window=time_window, stage1_results=stage1_results, stage2_results=stage2_results);


# # Preferred
def_rep_each_station.full_CRE_analysis(MyParams,'coh', 0.97, 'mean', 'snr_based', 15, SNR_cutoff[0], Minimum_freq_width[0]);
# def_rep_each_station.full_CRE_analysis(MyParams,"corr", 0.97);

# COHERENCE
# for limit in Cutoff:  # try different cutoffs
	# def_rep_each_station.full_CRE_analysis(MyParams,'coh', limit, 'mean', 'snr_based', 15, SNR_cutoff[0], Minimum_freq_width[0]);

