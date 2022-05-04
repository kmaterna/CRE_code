#!/usr/bin/env python

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
Run from a Pygmt conda environment.
"""

import collections, sys, os, configparser, ast

sys.path.append(".");  # add current directory to python path
import def_rep_each_station

# The main parameter object. 
TotalParams = collections.namedtuple('TotalParams', ['Network_repeaters_list', 'families_list', 'families_summaries',
                                                     'station_locations', 'time_window', 'stage2_results',
                                                     'mapping_code', 'mapping_data_general', 'mapping_data_specific',
                                                     'config_filename']);

def parse_config(configfile):
    assert(os.path.isfile(configfile)), FileNotFoundError("config file "+configfile+" not found.");
    configobj = configparser.ConfigParser();
    configobj.read(configfile);
    fileconfig = configobj["filepaths_config"];
    techconfig = configobj["cre_config"]
    MyParams = TotalParams(Network_repeaters_list=fileconfig["Network_repeaters_list"],
                           families_list=fileconfig["families_list"],
                           families_summaries=fileconfig["families_summaries"],
                           station_locations=fileconfig["station_locations_file"],
                           time_window=ast.literal_eval(techconfig["time_window"]),
                           stage2_results=fileconfig["stage2_results"],
                           mapping_code=fileconfig["mapping_code"],
                           mapping_data_general=fileconfig["mapping_data_general"],
                           mapping_data_specific=fileconfig["mapping_data_specific"],
                           config_filename=configfile);
    metric = techconfig["metric"];
    cutoff = float(techconfig["cutoff"]);
    statistic = techconfig["Statistic"];
    max_freq_options = float(techconfig["max_freq_options"]);
    Define_freq = techconfig["Define_freq"];
    SNR_cutoff = float(techconfig["SNR_cutoff"]);
    Minimum_freq_width = float(techconfig["Minimum_freq_width"])
    return MyParams, metric, cutoff, statistic, max_freq_options, Define_freq, Minimum_freq_width, SNR_cutoff;

if __name__ == "__main__":
    configfile = sys.argv[1];
    MyParams, metric, cutoff, statistic, max_freq, Define_freq, min_freq_width, SNR_cutoff = parse_config(configfile);
    # # Preferred
    def_rep_each_station.full_CRE_analysis(MyParams, metric, cutoff, statistic, Define_freq, max_freq, SNR_cutoff,
                                           min_freq_width);  # example with coherence
    # def_rep_each_station.full_CRE_analysis(MyParams, 'corr', 0.90);   # example with cross correlation
