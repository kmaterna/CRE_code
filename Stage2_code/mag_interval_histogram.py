""" 
MENDOCINO REPEATERS PROJECT
2/4/16

From a list of repeating earthquakes, generate histograms of magnitudes and intervals between repeating events. 

"""

import matplotlib.pyplot as plt
import sys

sys.path.append(".");  # add current directory to python path
import util_general_functions


def generate_histograms(repeaters_file, station_location_file):
    my_file = open(repeaters_file, 'r');

    # Read in lists for event1 and event2
    mean_mag, intervals, M = [], [], []

    station_tuple_list = util_general_functions.get_dirs_for_station(station_location_file);
    stations = [x[0] for x in station_tuple_list];
    station_paths = [x[3] for x in station_tuple_list];

    my_file.readline();
    for line in my_file:
        temp = line.split()
        name1, name2 = temp[0], temp[1];
        use_station = temp[2]  # read use_station from the list in network_repeaters_list.txt
        if use_station[-1] == "_":
            use_station = use_station[0:-1];
        # print(use_station);
        event_time1 = util_general_functions.get_float_time_from_name(name1);
        event_time2 = util_general_functions.get_float_time_from_name(name2);
        intervals.append(event_time2 - event_time1)

        # Now that we know which station recorded these events, get metadata.
        mydirectory = station_paths[stations.index(use_station)];
        file1 = mydirectory + use_station + "*" + name1;
        [_, _, _, mag1, _] = util_general_functions.get_info_from_sac(file1);
        file2 = mydirectory + use_station + "*" + name2;
        [_, _, _, mag2, _] = util_general_functions.get_info_from_sac(file2);
        mean_mag.append((mag1 + mag2) / 2);
        M.append(abs(mag1 - mag2));

    my_file.close();

    plt.figure()
    plt.hist(intervals, 30, color='b');
    plt.ylabel('Number of Event Pairs', fontsize=18);
    plt.xlabel('Time (years)', fontsize=18);
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)
    plt.title('Intervals between Repeating Event Pairs', fontsize=18);
    plt.savefig('interval_histogram.eps');
    plt.close();
    print("Histogram of Inter-Event Times Plotted!");

    plt.figure()
    plt.hist(mean_mag, 15, color='b');
    plt.ylabel('Number of Event Pairs', fontsize=18);
    plt.xlabel('Mean Event Magnitudes', fontsize=18);
    plt.xticks(fontsize=18);
    plt.yticks(fontsize=18);
    plt.title('Mean Magnitues of Repeating Event Pairs', fontsize=18);
    plt.savefig('magnitude_histogram.eps');
    plt.close();
    print("Histogram of Magnitudes Plotted!");

    plt.figure();
    plt.hist(M, 15, color='b');
    plt.xlabel('Magnitude Difference', fontsize=18);
    plt.ylabel('Number of Event Pairs', fontsize=18);
    plt.xticks(fontsize=18);
    plt.yticks(fontsize=18);
    plt.title("Magnitude Differences of Repeating Event Pairs", fontsize=18);
    plt.savefig("magnitude_differences_histogram.eps");
    plt.close()
    print("Histogram of Magnitude Differences Plotted!");

    return;
