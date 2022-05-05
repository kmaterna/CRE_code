# Takes in: metric, cutoff, mean/median, Max-frequency, SNR cutoff, minimum_span, 

from subprocess import call
import glob, sys

sys.path.append(".");  # add current directory to python path
import define_repeaters, find_network_repeaters, connected_component_analysis
import make_family_summaries, gmt_plotting, mag_interval_histogram, view_families
import composite_slip, generate_time_space_diagram, get_summary_statistics, util_general_functions


def full_CRE_analysis(MyParams):
    output_dir = setup_output_dir(MyParams);  # config step
    define_repeaters_each_station(MyParams);  # define repeaters for each station
    CRE_post_analysis(MyParams, output_dir);  # do CRE family analysis
    cleaning_up(output_dir);  # Move everything to output directory
    return;


def CRE_post_analysis(MyParams, output_dir):
    # Generate CREs and families, and summarize useful things about families (lat,lon,depth,mag,sliprate)
    find_network_repeaters.network_repeaters_two_more_stations(MyParams.stage2_results_dir,
                                                               output_dir+MyParams.Network_repeaters_list);
    connected_component_analysis.connected_components(MyParams.time_window, output_dir+MyParams.Network_repeaters_list,
                                                      output_dir+MyParams.families_list);
    make_family_summaries.main_program(MyParams.time_window, output_dir+MyParams.families_list,
                                       MyParams.station_location_file,
                                       output_dir+MyParams.families_summaries);
    get_summary_statistics.get_summary_statistics(output_dir+MyParams.families_summaries, output_dir);

    # # OPTIONAL IN ANY SEQUENCE:
    mag_interval_histogram.plot_histograms(output_dir+MyParams.Network_repeaters_list, MyParams.station_location_file,
                                           output_dir);
    view_families.view_families(MyParams.time_window, output_dir+MyParams.families_summaries,
                                output_dir + MyParams.Network_repeaters_list,
                                MyParams.station_location_file, MyParams.mapping_data_general, output_dir,
                                families=(-1,));  # 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17

    # These two are right now very specific to Mendocino.
    generate_time_space_diagram.main_program(MyParams.time_window, output_dir+MyParams.families_summaries,
                                             MyParams.mapping_data_specific, output_dir);
    composite_slip.main_program(MyParams.time_window, output_dir+MyParams.families_summaries,
                                MyParams.mapping_data_specific, output_dir);

    # # GMT CROSS-SECTIONS: specific to Mendocino; changes necessary for other areas.
    gmt_plotting.mendocino_main_program(MyParams.Network_repeaters_list, MyParams.families_summaries,
                                        MyParams.station_location_file, MyParams.mapping_code,
                                        MyParams.mapping_data_general, MyParams.mapping_data_specific);
    return;


def setup_output_dir(MyParams):
    # Place outputs in specific folder
    print("Setting up output directories...");
    if MyParams.metric == "corr":
        directory_name = MyParams.stage2_results_dir + "/" + MyParams.metric + "_" + str(MyParams.cutoff) + "/";
    else:
        directory_name = MyParams.stage2_results_dir + "/" + MyParams.metric + "_" + str(MyParams.cutoff) + "_" + \
                         MyParams.freq_method + "_" + str(MyParams.max_freq_allowed) + "_" + MyParams.statistic + "/";
    print("Directory name is %s " % directory_name);
    call(['mkdir', '-p', directory_name], shell=False);  # For the result directory
    call(['mkdir', '-p', directory_name + "Image_Families/"], shell=False);  # For the image directory
    delete_files_matching([directory_name + "Image_Families/*"]);
    call(['cp', MyParams.config_filename, directory_name + 'cre_config.txt'], shell=False);
    return directory_name;


def define_repeaters_each_station(MyParams):
    station_tuple_list = util_general_functions.get_dirs_for_station(MyParams.station_location_file);  # read step
    for station_tuple in station_tuple_list:
        print("Defining repeaters for station name: %s" % station_tuple[0]);
        define_repeaters.define_repeaters(station_tuple, MyParams, MyParams.metric, MyParams.cutoff, MyParams.statistic,
                                          MyParams.freq_method, MyParams.max_freq_allowed, MyParams.SNR_cutoff,
                                          MyParams.Minimum_freq_width, plot_all=0);
    return;


def cleaning_up(output_dir):
    delete_files_matching(["*_total_list.txt", "*_repeaters_list.txt", "filt*.sac"]);
    move_files_matching(['*.ps'], output_dir);
    copy_files_matching('CREs_by_station/B046/*.eps', output_dir);
    copy_files_matching('CREs_by_station/B046/*.png', output_dir);
    return;


def delete_files_matching(match_strings):
    if isinstance(match_strings, list):
        for filetype in match_strings:
            clear_list = glob.glob(filetype);
            for item in clear_list:
                call(['rm', item], shell=False);
    else:
        print("You did not give me a list. Not deleting files.");
    return;


def move_files_matching(match_strings, new_dir):
    if isinstance(match_strings, list):
        for filetype in match_strings:
            move_list = glob.glob(filetype);
            for item in move_list:
                call(['mv', item, new_dir], shell=False);
    else:
        print("You did not give me a list. Not moving files.");
    return;


def copy_files_matching(match_string, new_dir):
    copy_list = glob.glob(match_string);
    for item in copy_list:
        call(['cp', item, new_dir], shell=False);
    return;
