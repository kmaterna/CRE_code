"""
MENDOCINO REPEATERS PROJECT
March 1, 2016
Script that makes a handful of plots about waveforms and metadata.
"""

import numpy as np
import matplotlib.pyplot as plt
import os, sys

sys.path.append(".");  # add current directory to python path
import util_functions_for_viewing_families
import util_general_functions


def view_families(time_window, families_summaries, station_locations, mapping_data, output_dir, families=(-1,)):
    """
    Note: families='-1' is the default state, and means do all families.
    Alternately: families = [0, 1, 2, 3] means only do a few families
    """
    [summary_array, stations, station_paths, ca_coords, plate_coords] = overall_inputs(families_summaries,
                                                                                       station_locations, mapping_data);
    if families[0] == -1:
        families = np.arange(0, len(summary_array));  # do all families
    cwd = os.getcwd();
    output_dir = cwd + "/" + output_dir + "Image_Families/";
    for i, myline in enumerate(summary_array):
        if i in families:  # do select families
            major_plots(myline, stations, station_paths, output_dir, ca_coords, plate_coords, time_window);
    return;


# -------- INPUT PARAMETERS ------ #

def overall_inputs(families_summaries, station_locations_file, mapping_data):
    # Mapping Files
    [ca_lon, ca_lat] = np.loadtxt(mapping_data + "/CA_bdr", unpack=True);
    ca_coords = [ca_lon, ca_lat];
    plates_file = mapping_data + "/nuvel1_plates_mod.txt";
    input_plates = open(plates_file, 'r');
    # for drawing the plate boundaries
    plate_lat, plate_lon = [], [];
    for line in input_plates:
        temp = line.split()
        if len(temp) > 0:
            if temp[0] == '>':
                plate_lat.append(np.nan)
                plate_lon.append(np.nan)
            else:
                plate_lat.append(float(temp[0]))
                plate_lon.append(float(temp[1]) - 360.0)
    input_plates.close();
    plate_coords = [plate_lon, plate_lat];

    # opening families summaries
    summaryfile = open(families_summaries, 'r');
    summary_array = [];
    for line in summaryfile:
        summary_array.append(line);
    summaryfile.close();

    station_tuple_list = util_general_functions.get_dirs_for_station(station_locations_file);
    stations = [x[0] for x in station_tuple_list];
    station_paths = [x[3] for x in station_tuple_list];

    return [summary_array, stations, station_paths, ca_coords, plate_coords];


# ------------- THE MAIN PROGRAM ----------- #
# MAKE WAVEFORM PLOTS AND METADATA PLOTS FOR EACH FAMILY

def major_plots(myline, stations, station_paths, output_dir, ca_coords, plate_coords, time_window):
    # Major plots for just a single line.
    # Line Format: Family 1 with n events: (lon)*n (lat)*n (dep)*n (mag)*n best_station (loc_type)*n + slip_rate.

    temp = myline.split()
    family_number = int(temp[1]);
    number_of_events = int(temp[3])
    [longitude, latitude, event_time, magnitude, depth, _type_of_loc, mean_lon, mean_lat, _mean_depth,
     slip_rate, _] = util_general_functions.read_family_line(myline);

    # Get the names and metadata of the files in the family.
    event_names = []
    for i in range(5, 5 + number_of_events):
        event_names.append(temp[i]);
    best_station = temp[-(2 + number_of_events)]
    print("\nPrinting Family # %d" % family_number);

    # # READ IN NON-REPEATERS DATA AT THE BEST STATION
    [ev1_non_repeaters, ev2_non_repeaters, xcorr_non_repeaters, coherence_non_repeaters] = read_event_comparison(
        best_station + '_total_list.txt');
    [network_repeaters] = read_network_repeaters('Network_CRE_pairs_list.txt');

    # -------- MAKING THE FIRST SAVED FIGURE (WAVEFORMS) ----- #
    sac_directory = station_paths[stations.index(best_station)];
    util_functions_for_viewing_families.make_waveform_plot(family_number, event_names, magnitude, best_station,
                                                           sac_directory, output_dir);

    # --------- MAKING THE SECOND PLOT (METADATA) ----- #
    plt.figure()
    g, axarr = plt.subplots(2, 2)

    # *:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # *:: 				 		Subplot 0,0						        :*/
    # *:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # WHERE ARE THE EVENTS LOCATED ALONG THE PLATE BOUNDARY?
    a1 = axarr[0, 0]
    a1.set_ylim([39, 42])  # MENDOCINO
    a1.set_xlim([-127, -122])
    # a1.set_ylim([31, 35.5])  # ANZA
    # a1.set_xlim([-119, -114.9])
    a1.set(adjustable='box', aspect='equal')
    a1.set_xlabel("Longitude")
    a1.set_ylabel("Latitude")
    if len(event_names) > 2:
        cv = util_functions_for_viewing_families.CVar(event_time);
        a1.set_title("Family " + str(family_number) + ": CV=" + str(cv));
    else:
        a1.set_title("Family " + str(family_number));

    a1.plot(plate_coords[0], plate_coords[1], 'r')
    a1.plot(ca_coords[0], ca_coords[1], 'k')
    a1.plot(mean_lon, mean_lat, '.b')

    # *:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # *:: 				 		Subplot 0,1						        :*/
    # *:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # TIMING AND MAGNITUDE INFORMATION OF FAMILIES
    a1 = axarr[0, 1];
    color = 'bgrcmyk'
    dmin = np.min(depth);
    dmax = np.max(depth);
    for i in range(number_of_events):
        a1.plot([event_time[i], event_time[i]], [0, magnitude[i] - 0.1], color[i % len(color)])
        a1.get_xaxis().get_major_formatter().set_useOffset(False)
        a1.set_xlim([time_window[0] - 0.2, time_window[1] + 0.2])
    a1.set_ylabel("Magnitude");
    a1.set_ylim([0, 5]);
    a1.scatter(event_time, magnitude, c=depth, cmap=plt.cm.cool)

    cbar_ax = g.add_axes([0.92, 0.62, 0.02, 0.25])
    sm = plt.cm.ScalarMappable(cmap='cool', norm=plt.Normalize(dmin, dmax))
    sm.set_array(depth)
    cbar = plt.colorbar(sm, cbar_ax)
    cbar.set_label('Depth (km)', rotation=270, labelpad=15.5)

    # #*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # #*:: 				 		Subplot 1,0						        :*/
    # #*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # WHERE ARE THE EVENTS LOCATED ON A CLOSE-UP MAP?
    a1 = axarr[1, 0];
    # plot the connections between events.
    pairs_counter = 0;
    for i in range(len(event_names)):
        for j in range(i, len(event_names)):
            if event_names[i] + " " + event_names[j] in network_repeaters or event_names[j] + " " + event_names[i] in network_repeaters:
                pairs_counter += 1;
                a1.plot([longitude[i], longitude[j]], [latitude[i], latitude[j]], 'k')

    # Plot the events and everything else about them.
    for i in range(number_of_events):
        a1.plot(longitude[i], latitude[i], "." + color[i % len(color)]);
    a1.set_xlim([np.min(longitude) - 0.01, np.max(longitude) + 0.01])
    a1.set_ylim([np.min(latitude) - 0.01, np.max(latitude) + 0.01])
    a1.get_xaxis().get_major_formatter().set_useOffset(False)
    a1.get_yaxis().get_major_formatter().set_useOffset(False)
    a1.set_xlabel("Longitude")
    a1.set_ylabel("Latitude")
    a1.set(adjustable='box', aspect='equal')
    a1.text(0.6, 0.15, "n_events=" + str(number_of_events) + "; n_pairs=" + str(pairs_counter),
            horizontalalignment='center',
            verticalalignment='center',
            transform=a1.transAxes)

    # #*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # #*:: 				 		Subplot 1,1						        :*/
    # #*:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # # PLOT THE CROSS-CORRELATIONS IN MATRIX FORM
    a1 = axarr[1, 1]

    x = np.array(range(number_of_events));
    y = np.array(range(number_of_events));
    xx, yy = np.meshgrid(x, y)

    # Collecting the matrix of coherence and cross-correlation values between each event pair
    coh_array = util_functions_for_viewing_families.make_similarity_matrix(number_of_events, event_names,
                                                                           ev1_non_repeaters, ev2_non_repeaters,
                                                                           coherence_non_repeaters);
    xcorr_array = util_functions_for_viewing_families.make_similarity_matrix(number_of_events, event_names,
                                                                             ev1_non_repeaters, ev2_non_repeaters,
                                                                             xcorr_non_repeaters)

    # Plotting arrays of cross-correlation and coherence
    a1.scatter(xx, yy, c=coh_array, s=round(30000 / (number_of_events * number_of_events)), marker='s', cmap='jet',
               vmin=0.5, vmax=1);
    a1.scatter(xx, yy, c=xcorr_array, s=30, marker='o', cmap='jet', vmin=0.5, vmax=1);

    a1.set_xlim([-0.50, number_of_events - 0.5])
    a1.set_ylim([-0.50, number_of_events - 0.5])
    a1.set_yticks(y)
    a1.set_xticks(x)
    a1.set(adjustable='box', aspect='equal')
    a1.set_title(best_station + ' Correlations')

    # Coloring the boxes and circles
    cbar_ax = g.add_axes([0.90, 0.12, 0.02, 0.20])
    sm = plt.cm.ScalarMappable(norm=plt.Normalize(0.5, 1), cmap='jet')
    sm.set_array(np.array([0, 1, 2, 3, 4]))
    _cbar = plt.colorbar(sm, cbar_ax)

    plt.savefig(output_dir + "Family_" + str(family_number) + "_Metadata.png")
    plt.close()

    # MAKING THE THIRD FIGURE: SLIP RATES
    # *:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    # *:: 				 		Make Slip History				        :*/
    # *:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::*/
    if slip_rate > -1:
        plt.figure()
        g, axarr = plt.subplots(2, sharex=True)

        a1 = axarr[0];
        color = 'bgrcmyk'
        dmin = np.min(depth);
        dmax = np.max(depth);
        for i in range(number_of_events):
            a1.plot([event_time[i], event_time[i]], [0, magnitude[i] - 0.1], color[i % len(color)])
            # a1.plot([event_time[i], event_time[i]],[0,magnitude[i]-0.1],color[6])
            a1.get_xaxis().get_major_formatter().set_useOffset(False)
            a1.set_xlim([time_window[0] - 0.2, time_window[1] + 0.2])
        a1.set_ylabel("Magnitude", fontsize=14);
        a1.set_ylim([0, 4]);
        a1.scatter(event_time, magnitude, c=depth, cmap=plt.cm.cool)
        # a1.scatter(event_time, magnitude,c='k')
        a1.set_title("Family " + str(family_number));

        cbar_ax = g.add_axes([0.92, 0.62, 0.02, 0.25])
        sm = plt.cm.ScalarMappable(cmap='cool', norm=plt.Normalize(dmin, dmax))
        sm.set_array(depth)
        cbar = plt.colorbar(sm, cbar_ax)
        cbar.set_label('Depth (km)', rotation=270, labelpad=15.5)

        # GET THE SLIP FOR EACH EVENT
        a1 = axarr[1];
        ts, slip = [], []
        ts.append(time_window[0])
        slip.append(0)
        slip.append(0)

        slip_keep_level = 0
        for i in range(number_of_events):
            d = util_general_functions.event_slip(magnitude[i]);  # get slip associated with each event
            slip_keep_level += d;
            ts.append(event_time[i])
            ts.append(event_time[i])
            slip.append(slip_keep_level)
            slip.append(slip_keep_level)
        ts.append(time_window[1]);
        slip_rate_compute = round(100 * max(slip) / (time_window[1] - time_window[0])) / 100;

        a1.plot(ts, slip, 'k')
        a1.get_xaxis().get_major_formatter().set_useOffset(False)
        a1.set_xlim([time_window[0], time_window[1] + 0.5])
        a1.set_ylabel("Slip (cm)", fontsize=14);
        # a1.set_title("Slip History");
        a1.set_title("Slip History: Average Slip Rate = " + str(slip_rate_compute) + " cm / year");
        a1.set_ylim([-0.2, max(slip) + 0.2]);
        plt.xticks(fontsize=14)

        plt.savefig(output_dir + "Family_" + str(family_number) + "_Slip_History.png")
        plt.close()

    return;


def read_event_comparison(filename):
    # Reads the files of the form B045_total_list.txt
    ifile = open(filename, 'r')
    ifile.readline();  # ignoring the header
    ev1_field, ev2_field, xcorr_field, coherence_field = [], [], [], []
    for line in ifile:
        temp = line.split()
        ev1_field.append(temp[0][-28:])
        ev2_field.append(temp[1][-28:])
        xcorr_field.append(float(temp[2]))
        coherence_field.append(float(temp[3]))
    ifile.close();
    return [ev1_field, ev2_field, xcorr_field, coherence_field];


def read_network_repeaters(filename):
    ifile = open(filename, 'r');
    network_repeaters = [];
    for line in ifile:
        temp = line.split();
        network_repeaters.append(temp[0] + " " + temp[1]);
    ifile.close();
    return [network_repeaters];
