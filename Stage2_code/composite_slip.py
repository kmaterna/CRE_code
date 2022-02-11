"""
MENDOCINO REPEATERS PROJECT
September 29, 2016
This script takes a series of repeating earthquake families and makes a composite time-series of slip.
"""

import matplotlib.pyplot as plt
import sys

sys.path.append(".");  # add current directory to python path
import util_general_functions


def main_program(time_window, Family_Summaries, mapping_data):
    min_lon, max_lon = -124.75, -124.25;
    min_lat, max_lat = 40.25, 40.36;  # this gets the main cluster in the MTJ
    no_slip_rates_cutoff = 1.0;  # If the family spans less than this # of years, we don't consider it for slip rates.
    bg_catalog_file = mapping_data + '/ncsn.txyzm'
    big_events_file = mapping_data + '/M5up.eq'

    [lat, lon, dep, timing, mag, n_seq] = read_file(Family_Summaries, no_slip_rates_cutoff);  # read family locations

    make_composite_plot([min_lon, max_lon, min_lat, max_lat, 18, 27], lat, lon, dep, timing, mag, n_seq, time_window,
                        bg_catalog_file, big_events_file, "Integrated Repeater Slip History Below 18 km", 1);
    make_map(min_lon, max_lon, min_lat, max_lat, 18, 27, lat, lon, dep, timing, n_seq, time_window,
             big_events_file, "Integrated Repeater Slip History Below 18 km");
    make_composite_plot([min_lon, max_lon, min_lat, max_lat, 0, 18], lat, lon, dep, timing, mag, n_seq, time_window,
                        bg_catalog_file, big_events_file, "Integrated Repeater Slip History Above 18 km", 0);
    make_map(min_lon, max_lon, min_lat, max_lat, 00, 18, lat, lon, dep, timing, n_seq, time_window,
             big_events_file, "Integrated Repeater Slip History Above 18 km");

    make_composite_plot([min_lon, max_lon, min_lat, max_lat, 0, 27], lat, lon, dep, timing, mag, n_seq, time_window,
                        bg_catalog_file, big_events_file, "Integrated Repeater Slip History All Depths", 0);
    make_map(min_lon, max_lon, min_lat, max_lat, 0, 30, lat, lon, dep, timing, n_seq, time_window,
             big_events_file, "Integrated Repeater Slip History All Depths");

    print("Composite Slip Diagrams created!");
    return;


def read_file(families_summary, no_slip_rates_cutoff):
    # Starts with "Family_Summaries.txt"
    # Makes a list of latitude, longitude, depth, timing, magnitude, and family_number for each event in family file.
    input_file1 = open(families_summary, 'r')
    total_lat, total_lon, total_dep, total_timing, total_mag, n_seq = [], [], [], [], [], [];

    for line in input_file1:
        # get timing and metadata for each family.
        number_of_sequence = int(line.split()[1]);
        [_, _, fam_time, fam_mag, _, _, avg_lon, avg_lat, avg_dep, _] = util_general_functions.read_family_line(line);

        if (fam_time[-1] - fam_time[0]) > no_slip_rates_cutoff:  # if the family from start-to-finish
            # spans more than some number of years, then we count it.

            for i in range(len(fam_time)):
                total_lat.append(avg_lat)
                total_lon.append(avg_lon)
                total_dep.append(avg_dep)
                total_timing.append(fam_time[i])
                total_mag.append(fam_mag[i]);
                n_seq.append(number_of_sequence);

    input_file1.close();
    return [total_lat, total_lon, total_dep, total_timing, total_mag, n_seq]


def add_fancy_labels(axarr):
    # For the faster-slip period of time:
    starttime, endtime = 2014.5, 2015.03;
    level = 100;
    axarr[1].plot([starttime, endtime], [level, level], color='black');
    axarr[1].plot([starttime, starttime], [level - 10, level + 10], color='black')
    axarr[1].plot([endtime, endtime], [level - 10, level + 10], color='black')
    axarr[1].text(2014.35, level - 50, " More\nActive")

    # For the slower-slip period of time:
    starttime, endtime = 2015.25, 2016.89;
    level = 100;
    axarr[1].plot([starttime, endtime], [level, level], color='black');
    axarr[1].plot([starttime, starttime], [level - 10, level + 10], color='black')
    axarr[1].plot([endtime, endtime], [level - 10, level + 10], color='black')
    axarr[1].text(starttime + 0.2, level - 20, "Less Active")
    return axarr;


def add_large_events(axarr, max_slip, start_time, end_time, mapping_file, min_mag):
    ax1 = axarr[1];
    MyCat = util_general_functions.read_humanreadable(mapping_file);
    MyCat = util_general_functions.filter_to_starttime_endtime(MyCat, start_time, end_time);
    MyCat = util_general_functions.filter_to_mag_range(MyCat, min_mag, 10);
    for item in MyCat:
        if item.decdate == 2010.09589041:
            plotting_epsilon = 0.58;  # we need to offset the label because of two closely spaced events.
            plotting_end = "";
        elif item.decdate == 2010.02739726:
            plotting_epsilon = 0.06;
            plotting_end = ",";
        else:
            plotting_epsilon = 0.04;  # the label-plotting offset from the black line.
            plotting_end = "";
        ax1.plot([item.decdate, item.decdate], [0, max_slip], '--k')
        ax1.text(item.decdate + plotting_epsilon, 0.3, "M" + str(item.mag) + plotting_end)
    return axarr;


def add_cumulative_seismicity(bbox, start_time, end_time, eq_file, axarr):
    # Get seismicity from the rest of the newtork in this box.
    MINIMUM_MAG = 0.5;
    MyCat = util_general_functions.read_txyzm(eq_file);
    MyCat = util_general_functions.filter_to_bounding_box(MyCat, bbox);
    MyCat = util_general_functions.filter_to_starttime_endtime(MyCat, start_time, end_time);
    MyCat = util_general_functions.filter_to_mag_range(MyCat, MINIMUM_MAG, 10);
    network_time = [x.decdate for x in MyCat];  # the time series of when events happen in the box.

    # Making the seismicity time series; this is the staircase time series
    n_total_eq, total_eq_ts = [], []
    total_eq_ts.append(start_time);
    n_cumulative = 0;
    n_total_eq.append(0)
    n_total_eq.append(0)
    for i in range(len(network_time)):
        n_cumulative += 1;
        total_eq_ts.append(network_time[i])
        total_eq_ts.append(network_time[i])
        n_total_eq.append(n_cumulative)
        n_total_eq.append(n_cumulative)
    total_eq_ts.append(end_time);

    a1 = axarr[1];  # go plot the cumulative seismicity on a different axis.
    # Make the y-axis label and tick labels match the line color.
    for tl in a1.get_yticklabels():
        tl.set_color('b')
    a1.set_ylabel("Averaged Repeater Slip (mm)", color='b');

    a2 = a1.twinx()
    a2.plot(total_eq_ts, n_total_eq, 'r')
    a2.set_ylabel('Total Earthquakes', color='r')
    for tl in a2.get_yticklabels():
        tl.set_color('r')
    a1.set_xlim([start_time, end_time + 0.5])
    a2.set_xlim([start_time, end_time + 0.5])

    return axarr;


def make_composite_plot(bbox, lat, lon, dep, timing, mag, n_seq, time_window, bg_eq_file, big_events_file,
                        plot_name, fancy_labels):
    start_time, end_time = time_window[0], time_window[1]
    plt.figure();
    g, axarr = plt.subplots(2, sharex=True, figsize=(10, 7), dpi=300)

    plot_timing, plot_mag, ts, slip, n_families = [], [], [], [], []
    ts.append(start_time)
    slip_keep_level = 0
    slip.append(0)
    slip.append(0)  # initializing things for the slip history.

    # Get events that are within the box and time range of interest.
    for i in range(len(lat)):
        if bbox[2] < lat[i] < bbox[3]:
            if bbox[0] < lon[i] < bbox[1]:
                if bbox[4] < dep[i] < bbox[5]:
                    if time_window[0] < timing[i] < time_window[1]:
                        # Now we have an event in our region and time of interest; let's add its slip to the plot.
                        plot_timing.append(timing[i])
                        plot_mag.append(mag[i])
                        n_families.append(n_seq[i])

    number_of_families = len(set(n_families));  # the unique number of families that we observed in the blob.
    ordered_mag = [x for (y, x) in sorted(zip(plot_timing, plot_mag))]  # magnitude in an ordered list.
    plot_timing.sort();

    # plot the slip associated with each event (Nadeau and Johnson, 1998); this is the crazy staircase
    for i in range(len(plot_timing)):
        d = util_general_functions.event_slip(ordered_mag[i]);
        slip_keep_level += (d * 10.0) / number_of_families;  # *10 means millimeters
        ts.append(plot_timing[i])
        ts.append(plot_timing[i])
        slip.append(slip_keep_level)
        slip.append(slip_keep_level)
    ts.append(end_time);
    max_slip = max(slip);
    slip_rate = round(10 * max(slip) / (end_time - start_time)) / 10;
    print(number_of_families);

    # Writing output so that we can make an estimate of slip rate slope and uncertainty.
    # going to use scipy curve fitting.
    outfile = open("slip_curve_" + str(bbox[4]) + "_" + str(bbox[5]) + "_km_depth.txt", 'w');
    cumulative_slip = 0;
    for i in range(len(plot_timing)):
        cumulative_slip += util_general_functions.event_slip(
            ordered_mag[i]) * 10.0 / number_of_families;  # *10 means millimeters
        outfile.write("%f %f \n" % (plot_timing[i], cumulative_slip));
    outfile.close();

    # # GET THE SLIP RATE
    # Plot the lollipop diagram
    a1 = axarr[0];
    for i in range(len(plot_timing)):
        a1.plot([plot_timing[i], plot_timing[i]], [0, ordered_mag[i] - 0.1], 'k')
        a1.scatter(plot_timing[i], ordered_mag[i], c='black');
    a1.get_xaxis().get_major_formatter().set_useOffset(False)
    a1.set_xlim([start_time - 0.2, end_time + 0.2])
    a1.set_ylabel("Magnitude");
    a1.set_ylim([0, 5]);
    a1.set_title(plot_name);

    # Plot the slip histories.
    a1 = axarr[1];
    a1.plot(ts, slip, 'b')
    a1.get_xaxis().get_major_formatter().set_useOffset(False)
    a1.set_xlim([start_time, end_time + 0.5])
    a1.set_title("Slip History: Averaged Slip Rate = " + str(slip_rate) + " mm / yr [" + str(
        number_of_families) + " sequences]");
    a1.set_ylim([-2.2, max(slip) + 0.2]);

    axarr = add_cumulative_seismicity(bbox, start_time, end_time, bg_eq_file, axarr);
    axarr = add_large_events(axarr, max_slip, start_time, end_time, big_events_file, min_mag=5.5);  # min_mag for events

    if fancy_labels == 1:
        _axarr = add_fancy_labels(axarr);

    plt.savefig(plot_name + ".png")
    plt.close()
    return;


def make_map(min_lon, max_lon, min_lat, max_lat, min_dep, max_dep, lat, lon, dep, timing, n_seq, time_window,
             big_eq_file, plot_name):
    # Getting the large events.
    start_time, end_time = time_window[0], time_window[1]
    MyCat = util_general_functions.read_humanreadable(big_eq_file);
    MyCat = util_general_functions.filter_to_starttime_endtime(MyCat, start_time, end_time);
    MyCat = util_general_functions.filter_to_mag_range(MyCat, 5.5, 10);
    MyCat = util_general_functions.filter_to_bounding_box(MyCat, [-125.6, -123.4, 39.4, 41.4, 0, 40]);

    _fig = plt.figure();
    ax0 = plt.subplot2grid((4, 1), (0, 0), rowspan=3)
    ax1 = plt.subplot2grid((4, 1), (3, 0), rowspan=1)  # 3 rows, 1 column. Second coordinates are top left corner.

    # Making map view.
    ax0.plot(lon, lat, '.')
    for x in range(len(lon)):
        ax0.text(lon[x], lat[x], str(n_seq[x]), fontsize=8);
    # draw rectangle
    ax0.plot([min_lon, max_lon, max_lon, min_lon, min_lon], [min_lat, min_lat, max_lat, max_lat, min_lat], 'r');
    for item in MyCat:
        ax0.text(item.lon, item.lat, str(item.decdate)[0:4] + 'M' + str(item.mag));
        ax0.scatter(item.lon, item.lat, c='b');
    ax0.set_title("Map of Repeaters and Background Events");
    ax0.set_xlim([min_lon, max_lon])
    ax0.set_ylim([min_lat, max_lat])
    ax0.set_ylabel("Latitude")

    # Making depth view.
    ax1.plot(lon, dep, '.')
    ax1.plot([min_lon, min_lon, max_lon, max_lon, min_lon], [min_dep, max_dep, max_dep, min_dep, min_dep], 'r')
    for item in MyCat:
        ax0.text(item.lon, item.depth, str(item.decdate)[0:4] + 'M' + str(item.mag));
        ax0.scatter(item.lon, item.depth, c='b');
    plt.gca().invert_yaxis();
    ax1.set_xlabel("Longitude")
    ax1.set_ylabel("Depth (km)")
    ax1.set_xlim([min_lon, max_lon])
    plt.savefig("Map_View_" + plot_name + ".png");
    plt.close();
