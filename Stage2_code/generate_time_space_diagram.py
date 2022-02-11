""" 
MENDOCINO REPEATERS PROJECT
8/23/16
From list of repeating earthquake families, generate a few time-space diagrams.
"""
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append(".");  # add current directory to python path
import util_general_functions


def main_program(time_window, family_summaries, mapping_data):
    dont_plot_family = 1.0;  # years between beginning and end of sequence, in case we dont want short-lived sequences
    colorlist = 'brgcmky'
    bg_catalog_file = mapping_data + '/ncsn.txyzm'
    large_event_catalog_file = mapping_data + '/M5up.eq'

    lon_bounds = [-124.63, -124.28];
    lat_bounds = [40.25, 40.36];  # latitude and longitude range for most plots.
    color_change_time = 2015.07;  # the timing of the M5.7 event.

    # Zoomed in, simpler:
    time_space_simpler(family_summaries, lon_bounds, lat_bounds, [0, 18], dont_plot_family, time_window[0],
                       time_window[1], bg_catalog_file, large_event_catalog_file, color_change_time + 10);  # shallow
    time_space_simpler(family_summaries, lon_bounds, lat_bounds, [18, 27], dont_plot_family, time_window[0],
                       time_window[1], bg_catalog_file, large_event_catalog_file, color_change_time);  # deeper cluster
    time_space_simpler(family_summaries, lon_bounds, lat_bounds, [27, 35], 0, time_window[0],
                       time_window[1], bg_catalog_file, large_event_catalog_file, color_change_time);  # deepest

    # More complicated, colored by depth, zoomed in and zoomed out:
    # time_space_colored_by_depth(family_summaries, lon_bounds, lat_bounds, [0, 27], dont_plot_family, time_window[0],
    #                             time_window[1], bg_catalog_file, large_event_catalog_file, colorlist);

    print("Space-Time Diagrams Created!");
    return;


def plot_recent_M5_eqs(ax, mapping_file):  # plot stars for major earthquakes in the time range.
    # record of major >M5 earthquakes in: "latitude longitude depth time magnitude"
    MyCat = util_general_functions.read_humanreadable(mapping_file);
    MyCat = util_general_functions.filter_to_bounding_box(MyCat, [-360, 360, 40.20, 40.50, 0, 50]);
    for item in MyCat:
        ax.plot(item.lon, item.decdate, 'D', markersize=item.mag * 2, c='red');
    return ax;


def plot_M6p8_eq(ax):  # M6.8 Earthquake on 2014-069
    ax.plot([-127, -121], [2014.0 + 69 / 365.24, 2014.0 + 69 / 365.24], '--k');
    return ax;


def plot_M5p7_eq(ax):  # M5.7 rupture patch
    # Rupture patch is approx.
    # double-differenced hypocenter at 40.31, -124.56, 20.24
    hypocenter_x = -124.56;
    multiplier = 110 * np.cos(np.deg2rad(40.3));  # the east-west distance of a degree up at Mendocino
    rupture_length = 8.5;  # km total.
    rupture_start = hypocenter_x - (rupture_length / multiplier) / 2.0;  # the western edge of rupture
    rupture_end = hypocenter_x + (rupture_length / multiplier) / 2.0;  # the eastern edge of rupture
    print(rupture_start);
    print(rupture_end);
    ax.plot([rupture_start, rupture_end], [2015.07, 2015.07], 'k', linewidth=3.5);
    return ax;


def plot_M6p5_eq(ax):  # M6.5 Earthquake in 2010
    ax.plot([-127, -121], [2010.027, 2010.027], '--k');
    return ax;


def plot_eq_cloud(ax, dep_min, dep_max, lat_min, lat_max, eq_file):
    bg_cat = util_general_functions.read_txyzm(eq_file);
    filt_cat = util_general_functions.filter_to_bounding_box(bg_cat, [-360, 360, lat_min, lat_max, dep_min, dep_max]);
    ax.plot([x.lon for x in filt_cat], [x.decdate for x in filt_cat], '.', color='gray');
    return ax;


def plot_eq_cloud_afterM5p7(ax, dep_min, dep_max, lat_min, lat_max, time_start, dot_color, eq_file):
    bg_cat = util_general_functions.read_txyzm(eq_file);
    filt_cat = util_general_functions.filter_to_bounding_box(bg_cat, [-360, 360, lat_min, lat_max, dep_min, dep_max]);
    filt_cat = util_general_functions.filter_to_starttime_endtime(filt_cat, time_start, 2030.0);
    ax.plot([x.lon for x in filt_cat], [x.decdate for x in filt_cat], '.', color=dot_color);
    return ax;


def axis_format(ax, start_time, end_time):  # useful formatting for the axis of the plot.
    ax.grid();
    ax.set_ylim([start_time - 0.2, end_time + 0.2])
    ax.get_yaxis().get_major_formatter().set_useOffset(False)
    ax.get_xaxis().get_major_formatter().set_useOffset(False)  # keeps the labels in regular (not engineering) notation
    ax.set_xlabel("Longitude", fontsize=16);
    ax.set_ylabel("Year", fontsize=16);
    return ax;


# ********************************** #  
# The plots themselves 
# ********************************** # 


def time_space_colored_by_depth(family_summaries, lon_bounds, lat_bounds, dep_bounds, dont_plot_family, start_time,
                                end_time, bg_eq_file, large_event_file, colorlist):
    """
    Zoomed out and Zoomed in color-coded by depth.
    """
    input_file1 = open(family_summaries, 'r');

    _fig = plt.figure();
    ax = plt.gca();

    lon_mapping, time_mapping, mag_mapping, depth_mapping = [], [], [], []

    for line1 in input_file1:  # for each family
        [_, _, time, mag, depth, _, mean_lon, mean_lat, _, _] = util_general_functions.read_family_line(line1)
        magsq = [x * x * 10 for x in mag];
        # Please plot something for each family
        if time[-1] - time[0] > dont_plot_family:
            # DON'T PLOT THE EVENTS WITH SHORT SEQUENCE (not likely repeaters anyway)
            if lat_bounds[0] < mean_lat < lat_bounds[1]:
                for i in range(len(depth)):
                    lon_mapping.append(mean_lon);
                    time_mapping.append(time[i]);
                    mag_mapping.append(magsq[i]);
                    depth_mapping.append(depth[i]);
                ax.plot([mean_lon, mean_lon], [time[0], time[-1]], color=colorlist[(i % 7)]);  # blue line with dots

    ax1 = ax.scatter(lon_mapping, time_mapping, s=mag_mapping, c=depth_mapping);  # one dot for each event

    cbar = plt.colorbar(ax1);
    cbar.set_label('Depth (km)')

    # For the cloud of microseismicity:
    ax = plot_eq_cloud(ax, dep_bounds[0], dep_bounds[1], lat_bounds[0], lat_bounds[1], bg_eq_file);
    ax = axis_format(ax, start_time, end_time);
    ax = plot_recent_M5_eqs(ax, large_event_file);
    ax = plot_M6p8_eq(ax);
    # ax = plot_M6p5_eq(ax);

    # Make the zoomed-in version
    ax.set_xlim([lon_bounds[0], lon_bounds[1]]);
    ax.set_title("Longitude of Repeating Earthquake Families")
    plt.savefig("Time_Space_Diagram_zoomed_in.eps")

    # Make the zoomed-out version
    ax.set_xlim([-125.5, -123.8])
    plt.savefig("Time_Space_Diagram.eps")
    plt.close();
    input_file1.close()
    return;


def time_space_simpler(family_summaries, lon_bounds, lat_bounds, dep_bounds, dont_plot_family, start_time, end_time,
                       bg_eq_file, large_event_file, color_change_time):
    """
    Simplified Zoomed in on the active region.
    Adding the stars for M5 earthquakes.
    """
    input_file1 = open(family_summaries, 'r');

    _fig = plt.figure(figsize=(8, 4), dpi=300);
    ax = plt.gca();

    first_segment_times, second_segment_times = [], [];
    first_segment_lons, second_segment_lons = [], [];

    for line1 in input_file1:  # for each family

        [_, _, time, _mag, depth, _, mean_lon, mean_lat, mean_depth, _] = util_general_functions.read_family_line(line1)

        # Please plot something for each family
        if time[-1] - time[0] > dont_plot_family:
            # DON'T PLOT THE EVENTS WITH SHORT SEQUENCE (not likely repeaters anyway)
            if dep_bounds[0] < mean_depth < dep_bounds[1]:
                if lat_bounds[0] < mean_lat < lat_bounds[1]:
                    ax.plot([mean_lon, mean_lon], [time[0], time[-1]],
                            color='b');  # looks like it's gonna be a blue line with dots
                    for i in range(len(depth)):
                        first_segment_times.append(time[i]);
                        first_segment_lons.append(mean_lon);
                        if time[i] > color_change_time:
                            second_segment_times.append(time[i]);
                            second_segment_lons.append(mean_lon);

    # the dots for each CRE event.
    ax.plot(first_segment_lons, first_segment_times, marker='.', markersize=10.0, color='b', linestyle='None')
    ax.plot(second_segment_lons, second_segment_times, marker='.', markersize=10.0, color='r', linestyle='None')

    # For the cloud of microseismicity and other annotations:
    ax = axis_format(ax, start_time, end_time);
    ax = plot_eq_cloud(ax, dep_bounds[0], dep_bounds[1], lat_bounds[0], lat_bounds[1], bg_eq_file);
    ax = plot_eq_cloud_afterM5p7(ax, dep_bounds[0], dep_bounds[1], lat_bounds[0], lat_bounds[1], color_change_time,
                                 'salmon', bg_eq_file);
    ax = plot_M6p8_eq(ax);
    ax = plot_M5p7_eq(ax);
    ax = plot_recent_M5_eqs(ax, large_event_file);
    # ax = plot_M6p5_eq(ax);

    ax.set_xlim([lon_bounds[0], lon_bounds[1]]);
    # ax.set_title("Repeating Earthquake Families "+str(dep_bounds[0])+" to " +str(dep_bounds[1])+" km Depth")
    plt.tight_layout()
    plt.savefig("Time_Space_Diagram_zoomed_in_" + str(dep_bounds[0]) + "_" + str(dep_bounds[1]) + "_depth.eps", dpi=500)

    input_file1.close()
    return;
