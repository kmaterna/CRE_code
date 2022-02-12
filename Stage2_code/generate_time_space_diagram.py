""" 
MENDOCINO REPEATERS PROJECT
8/23/16
From list of repeating earthquake families, generate a few time-space diagrams.
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
import pygmt

sys.path.append(".");  # add current directory to python path
import util_general_functions as utils


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
    time_space_colored_by_depth(family_summaries, lon_bounds, lat_bounds, [0, 27], dont_plot_family, time_window[0],
                                time_window[1], bg_catalog_file, large_event_catalog_file, colorlist);

    map_bbox = [-124.8, -124.20, 40.15, 40.46];
    map_by_timing_of_last_event(family_summaries, map_bbox, large_event_catalog_file);

    print("Space-Time Diagrams Created!");
    return;


def plot_recent_M5_eqs(ax, mapping_file):  # plot stars for major earthquakes in the time range.
    # record of major >M5 earthquakes in: "latitude longitude depth time magnitude"
    MyCat = utils.read_humanreadable(mapping_file);
    MyCat = utils.filter_to_bounding_box(MyCat, [-360, 360, 40.20, 40.50, 0, 50]);
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
    bg_cat = utils.read_txyzm(eq_file);
    filt_cat = utils.filter_to_bounding_box(bg_cat, [-360, 360, lat_min, lat_max, dep_min, dep_max]);
    ax.plot([x.lon for x in filt_cat], [x.decdate for x in filt_cat], '.', color='gray');
    return ax;


def plot_eq_cloud_afterM5p7(ax, dep_min, dep_max, lat_min, lat_max, time_start, dot_color, eq_file):
    bg_cat = utils.read_txyzm(eq_file);
    filt_cat = utils.filter_to_bounding_box(bg_cat, [-360, 360, lat_min, lat_max, dep_min, dep_max]);
    filt_cat = utils.filter_to_starttime_endtime(filt_cat, time_start, 2030.0);
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
    _fig = plt.figure();
    ax = plt.gca();

    myfamilies = utils.read_families_into_structure(family_summaries);
    myfamilies = utils.filter_to_bounding_box(myfamilies, [-360, 360, lat_bounds[0], lat_bounds[1], 0, 50])

    lon_mapping, time_mapping, mag_mapping, depth_mapping = [], [], [], []
    for j, family in enumerate(myfamilies):  # for each family
        # Please plot something for each family
        if family.ev_time[-1] - family.ev_time[0] > dont_plot_family:
            # DON'T PLOT THE EVENTS WITH SHORT SEQUENCE (likely not repeaters anyway)
            magsq = [x * x * 10 for x in family.ev_mag];
            for i in range(len(family.ev_depth)):
                lon_mapping.append(family.lon);
                time_mapping.append(family.ev_time[i]);
                mag_mapping.append(magsq[i]);
                depth_mapping.append(family.ev_depth[i]);
            ax.plot([family.lon, family.lon], [family.ev_time[0], family.ev_time[-1]],
                    color=colorlist[(j % 7)]);  # blue line with dots

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
    return;


def time_space_simpler(family_summaries, lon_bounds, lat_bounds, dep_bounds, dont_plot_family, start_time, end_time,
                       bg_eq_file, large_event_file, color_change_time):
    """
    Simplified Zoomed in on the active region.
    Adding the stars for M5 earthquakes.
    """

    _fig = plt.figure(figsize=(8, 4), dpi=300);
    ax = plt.gca();
    times0, times1, lons0, lons1 = [], [], [], [];

    myfamilies = utils.read_families_into_structure(family_summaries);
    myfamilies = utils.filter_to_bounding_box(myfamilies, [-360, 360, lat_bounds[0], lat_bounds[1], dep_bounds[0],
                                                           dep_bounds[1]])
    for family in myfamilies:  # for each family
        if family.ev_time[-1] - family.ev_time[0] > dont_plot_family:
            # DON'T PLOT THE EVENTS WITH SHORT SEQUENCE (not likely repeaters anyway)
            ax.plot([family.lon, family.lon], [family.ev_time[0], family.ev_time[-1]], color='b');  # line
            for i in range(len(family.ev_depth)):
                times0.append(family.ev_time[i]);
                lons0.append(family.lon);
                if family.ev_time[i] > color_change_time:
                    times1.append(family.ev_time[i]);
                    lons1.append(family.lon);

    # the dots for each CRE event.
    ax.plot(lons0, times0, marker='.', markersize=10.0, color='b', linestyle='None')
    ax.plot(lons1, times1, marker='.', markersize=10.0, color='r', linestyle='None')

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
    return;


def map_by_timing_of_last_event(family_summaries, region, large_event_cat_file):
    myfamilies = utils.read_families_into_structure(family_summaries);
    myfamilies = utils.filter_to_bounding_box(myfamilies, [-360, 360, region[2], region[3], 0, 50])

    big_events = utils.read_humanreadable(large_event_cat_file);
    big_events = utils.filter_to_bounding_box(big_events, [-360, 360, 40.20, 40.50, 0, 50]);
    big_events = utils.filter_to_starttime_endtime(big_events, 2010.0, 2023.0);

    proj = 'M4i'
    pygmt.makecpt(cmap="roma", series="2015/2022/0.1", background="o", output="mycpt.cpt", reverse=True);

    fig = pygmt.Figure();
    fig.basemap(region=region, projection=proj, frame="+t\"CRE families by most recent event\"");
    fig.coast(region=region, projection=proj, borders='1', shorelines='1.0p,black', water='lightblue',
              map_scale="n0.4/0.06+c" + str(region[2]) + "+w20", frame="0.1");
    for event in big_events:
        fig.plot([event.lon], [event.lat], style='a0.4c', color=[event.decdate], cmap='mycpt.cpt', pen="thin,black");

    for family in myfamilies:
        fig.plot([family.lon], [family.lat], style='c0.2c', color=[family.ev_time[-1]], cmap='mycpt.cpt',
                 pen="thin,black");
    fig.colorbar(position="JCR+w4.0i+v+o0.7i/0i", cmap="mycpt.cpt", frame=["x1.0", "y+L\"Year\""]);
    fig.savefig("Recent_CREs.png");
    return;
