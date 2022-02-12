# Takes in: metric, cutoff, mean/median, Max-frequency, SNR cutoff, minimum_span, 

from subprocess import call
import glob, sys

sys.path.append(".");  # add current directory to python path
import define_repeaters, find_network_repeaters, connected_component_analysis
import make_family_summaries, gmt_plotting, mag_interval_histogram, view_families
import composite_slip, generate_time_space_diagram, get_summary_statistics, util_general_functions


def full_CRE_analysis(MyParams, metric, cutoff, statistic='median', freq_method='hard_coded', max_frequency=25.0,
                      SNR_cutoff=5.0, Minimum_frequency_width=5.0):
    output_dir = setup_output_dir(MyParams, metric, cutoff, freq_method, max_frequency, statistic);  # config step
    station_tuple_list = util_general_functions.get_dirs_for_station(MyParams.station_locations);  # read step
    # define_repeaters_each_station(MyParams, station_tuple_list, metric, cutoff, statistic, freq_method, max_frequency,
    #                               SNR_cutoff, Minimum_frequency_width);  # define repeaters
    CRE_post_analysis(MyParams, output_dir);  # do CRE family analysis
    cleaning_up(output_dir);  # Move everything to output directory
    return;


def CRE_post_analysis(MyParams, output_dir):
    # Generate CREs and families, and summarize the useful things about the families (lat,lon,depth,mag,sliprate)
    find_network_repeaters.network_repeaters_two_more_stations(MyParams.Network_repeaters_list,
                                                               MyParams.stage2_results);
    connected_component_analysis.connected_components(MyParams.time_window, MyParams.Network_repeaters_list,
                                                      MyParams.families_list);
    make_family_summaries.main_program(MyParams.time_window, MyParams.families_list, MyParams.families_summaries,
                                       MyParams.station_locations);
    get_summary_statistics.get_summary_statistics(MyParams.families_summaries);  # CHANGES PER EXPERIMENT

    # # OPTIONAL IN ANY SEQUENCE:
    # HISTOGRAMS
    # mag_interval_histogram.generate_histograms(MyParams.Network_repeaters_list, MyParams.station_locations);
    #
    # view_families.view_families(MyParams.time_window, MyParams.families_summaries,
    #                             MyParams.station_locations, MyParams.mapping_data_general, output_dir,
    #                             families=(-1,));  # 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17

    # These two are right now very specific to Mendocino.
    generate_time_space_diagram.main_program(MyParams.time_window, MyParams.families_summaries,
                                             MyParams.mapping_data_specific);
    # composite_slip.main_program(MyParams.time_window, MyParams.families_summaries, MyParams.mapping_data_specific);
    #
    # # GMT CROSS-SECTIONS: specific to Mendocino; changes necessary for other areas.
    # gmt_plotting.mendocino_main_program(MyParams.Network_repeaters_list, MyParams.families_summaries,
    #                                     MyParams.station_locations, MyParams.mapping_code,
    #                                     MyParams.mapping_data_general, MyParams.mapping_data_specific);
    return;


# ----------- NOT LIKELY TO CHANGE BELOW THIS POINT ----------------- # 

def setup_output_dir(MyParams, metric, cutoff, freq_method, max_frequency, statistic):
    # Place outputs in specific folder
    print("Setting up output directories...");
    if metric == "corr":
        directory_name = MyParams.stage2_results + "/" + metric + "_" + str(cutoff) + "/";
    else:
        directory_name = MyParams.stage2_results + "/" + metric + "_" + str(cutoff) + "_" + freq_method + "_" + str(
            max_frequency) + "_" + statistic + "/";
    print("Directory name is %s " % directory_name);
    call(['mkdir', '-p', directory_name], shell=False);  # For the result directory
    call(['mkdir', '-p', directory_name + "Image_Families/"], shell=False);  # For the image directory
    delete_files_matching(directory_name + "*");
    delete_files_matching(directory_name + "Image_Families/*");
    return directory_name;


def define_repeaters_each_station(MyParams, station_tuple_list, metric, cutoff, statistic, freq_method, max_frequency,
                                  SNR_cutoff, Minimum_frequency_width):
    for station in station_tuple_list:
        given_station = station[0];  # extract name
        print("Defining repeaters for station: %s" % given_station);
        define_repeaters.define_repeaters(given_station, MyParams, metric, cutoff, statistic, freq_method,
                                          max_frequency, SNR_cutoff, Minimum_frequency_width, 0);  # bool = 'plot_all'
        # break;  # only do one station for now.
    return;


def cleaning_up(output_dir):
    delete_files_matching("???*_total_list.txt");
    delete_files_matching("???*_repeaters_list.txt");
    delete_files_matching("slip_curve_*depth.txt");
    delete_files_matching("*.pyc");
    delete_files_matching("filtfile.sac");
    move_files_matching('*.ps', output_dir);
    move_files_matching('*.png', output_dir);
    move_files_matching('*.jpg', output_dir);
    move_files_matching('*.eps', output_dir);
    move_files_matching('*_list.txt', output_dir);
    move_files_matching('*_Summaries.txt', output_dir);
    move_files_matching('summary*.txt', output_dir);
    move_files_matching('Families*.txt', output_dir);
    copy_files_matching('CREs_by_station/B046/*.eps', output_dir);
    copy_files_matching('CREs_by_station/B046/*.png', output_dir);
    return;


def delete_files_matching(match_string):
    clear_list = glob.glob(match_string);
    for item in clear_list:
        call(['rm', item], shell=False);
    return;


def move_files_matching(match_string, new_dir):
    move_list = glob.glob(match_string);
    for item in move_list:
        call(['mv', item, new_dir], shell=False);
    return;


def copy_files_matching(match_string, new_dir):
    copy_list = glob.glob(match_string);
    for item in copy_list:
        call(['cp', item, new_dir], shell=False);
    return;
