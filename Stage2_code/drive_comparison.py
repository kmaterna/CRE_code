#!/usr/bin/env python

"""
MAIN PYTHON SCRIPT 
that compares CRE results under different cutoffs for coherence and cross-correlation. 
Documentation of Options:
Metric = ['coh', 'corr'] # how to determine repeaters: coherence or xcorr? 
Cutoff = [0.95, 0.98]  # all-important cutoff
Statistic = ['mean', 'median']  # how to summarize range of frequencies of coherence calculation
max_freq_options=[8, 15, 25]  # maximum frequency ever touched.
freq_method = ['snr-based', 'hard-coded', 'magnitude-based'];
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
                                                     'station_location_file', 'time_window', 'stage2_results_dir',
                                                     'mapping_code', 'mapping_data_general', 'mapping_data_specific',
                                                     'metric', 'cutoff', 'statistic', 'max_freq_allowed',
                                                     'freq_method', 'SNR_cutoff', 'Minimum_freq_width',
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
                           station_location_file=fileconfig["station_location_file"],
                           time_window=ast.literal_eval(techconfig["time_window"]),
                           stage2_results_dir=fileconfig["stage2_results_dir"],
                           mapping_code=fileconfig["mapping_code"],
                           mapping_data_general=fileconfig["mapping_data_general"],
                           mapping_data_specific=fileconfig["mapping_data_specific"],
                           metric=techconfig["metric"],
                           cutoff=float(techconfig["cutoff"]),
                           statistic=techconfig["Statistic"],
                           max_freq_allowed=float(techconfig["max_freq_allowed"]),
                           freq_method=techconfig["freq_method"],
                           SNR_cutoff=float(techconfig["SNR_cutoff"]),
                           Minimum_freq_width=float(techconfig["Minimum_freq_width"]),
                           config_filename=configfile);
    return MyParams;


if __name__ == "__main__":
    configfile = sys.argv[1];
    MyParams = parse_config(configfile);
    def_rep_each_station.full_CRE_analysis(MyParams);
