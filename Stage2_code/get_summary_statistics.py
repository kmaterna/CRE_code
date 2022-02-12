"""
Take a folder full of repeaters_results_files and generate COV and summary statistics of events per family. 
num families
num events per family 
avg_cov
avg_timespan
slip rate in Nth box 
slip rate uncertainty in Nth box
"""

import numpy as np
import sys

sys.path.append(".");  # add current directory to python path
import util_general_functions, util_functions_for_viewing_families


def get_summary_statistics(families_summaries):
    [output_filename, bboxes, time_window, make_slip_rate_cutoff] = configure();
    MyFamilies = util_general_functions.read_families_into_structure(families_summaries);
    [avg_cov, n_families, avg_n, max_n, avg_time, n_short_fams, slip_rates, uncs] = compute(bboxes, time_window,
                                                                                            make_slip_rate_cutoff,
                                                                                            MyFamilies);
    write_outputs(output_filename, avg_cov, n_families, avg_n, max_n, avg_time, n_short_fams,
                  make_slip_rate_cutoff, bboxes, slip_rates, uncs);


def configure():  # You're going to want to change this for different locations (Mendocino, Anza, etc.)
    output_filename = "summary_statistics.txt";
    min_lon, max_lon = -124.75, -124.25;
    min_lat, max_lat = 40.25, 40.36;  # this gets the main cluster in the MTJ
    bboxes = [];  # define as many boxes as you want!
    bboxes.append([min_lon, max_lon, min_lat, max_lat, 18, 30]);  # the lower cluster
    bboxes.append([min_lon, max_lon, min_lat, max_lat, 0, 18]);  # the upper cluster
    time_window = [2008.7, 2022.1];
    make_slip_rate_cutoff = 1.0;  # Years
    return [output_filename, bboxes, time_window, make_slip_rate_cutoff];


def compute(box_dims, time_window, make_slip_rate_cutoff, MyFamilies):
    # Get the basic stats that can be found from families_summaries file
    cov_array = [util_functions_for_viewing_families.CVar(x.ev_time) for x in MyFamilies];
    num_events_array = [len(item.ev_time) for item in MyFamilies];
    timespan_array = [item.ev_time[-1]-item.ev_time[0] for item in MyFamilies];
    n_families = len(MyFamilies);
    avg_cov = np.mean(cov_array);
    avg_n = np.mean(num_events_array);
    max_n = np.max(num_events_array);
    mean_timespan = np.mean(timespan_array);

    # n_short_families: how many of them are there?
    n_short_families = 0;
    for item in MyFamilies:
        if item.ev_time[-1]-item.ev_time[0] < make_slip_rate_cutoff:
            n_short_families = n_short_families + 1;

    slip_rate_boxes, unc_boxes = [], [];
    for bbox in box_dims:
        [slip_rate1, unc_1] = get_slip_rate_stats(bbox, make_slip_rate_cutoff, time_window, MyFamilies);
        slip_rate_boxes.append(slip_rate1);
        unc_boxes.append(unc_1);

    return [avg_cov, n_families, avg_n, max_n, mean_timespan, n_short_families, slip_rate_boxes, unc_boxes];


def get_slip_rate_stats(bbox, make_slip_rate_cutoff, time_window, MyFamilies):
    """
    Compute the slip rates (and uncertainties) inside of the box of interest.
    """
    # Get events that are within the box and time range of interest.
    event_timing, event_magnitude, family_code_number = [], [], [];
    MyFamilies = util_general_functions.filter_to_bounding_box(MyFamilies, bbox);

    for family in MyFamilies:
        if family.ev_time[-1] - family.ev_time[0] < make_slip_rate_cutoff:
            continue;
        for i in range(len(family.ev_depth)):
            if time_window[0] < family.ev_time[i] < time_window[1]:
                event_timing.append(family.ev_time[i]);
                event_magnitude.append(family.ev_mag[i]);
                family_code_number.append(family.family_id)  # an array, [0 0 0 0 1 1 2 2 ...] for each event by family.
    number_of_families = len(set(family_code_number));  # the unique number of families that we observed in the blob.

    slip_rate = get_slip_rate(event_timing, event_magnitude, time_window, number_of_families);  # total slip rate
    unc = get_uncertainty(MyFamilies, time_window, make_slip_rate_cutoff);
    return [slip_rate, unc];


def get_slip_rate(event_timing, event_magnitude, time_window, number_of_families):
    """ number of families is just an int. Events in event_timing and event_magnitude are used to compute slip rate. """
    d_total = 0.0;
    for i in range(len(event_timing)):
        d_total += util_general_functions.event_slip(event_magnitude[i]);  # from Nadeau and Johnson, 1998.
    if number_of_families > 0:
        d_normalized = d_total / number_of_families;
        slip_rate = round(100 * d_normalized / (time_window[1] - time_window[0])) / 100;  # cm/year
    else:
        slip_rate = np.NaN;
    return slip_rate;


def get_uncertainty(MyFamilies, time_window, make_slip_rate_cutoff):
    # Use simple standard deviation of the slip rate distribution.
    slip_rate_distribution = [];  # this is the array that we build of slip rate estimates.
    for family in MyFamilies:
        if family.ev_time[-1] - family.ev_time[0] < make_slip_rate_cutoff:
            continue;
        test_event_timing, test_event_magnitude = [], [];
        for i in range(len(family.ev_depth)):
            test_event_timing.append(family.ev_time[i]);
            test_event_magnitude.append(family.ev_mag[i]);
            test_slip_rate = get_slip_rate(test_event_timing, test_event_magnitude, time_window, 1.0);
            slip_rate_distribution.append(test_slip_rate);
    slip_rate_uncertainty = np.std(slip_rate_distribution);
    return slip_rate_uncertainty;


def write_outputs(filename, avg_cov, n_families, avg_n, max_n, mean_timespan, n_short_families, slip_rate_cutoff,
                  bboxes, slip_rate_boxes, unc_boxes):
    myfile = open(filename, 'w');
    myfile.write("Number of families shorter than %.3f years = %d\n\n" % (slip_rate_cutoff, n_short_families));

    myfile.write("N_ALL_FAM = %d\n" % n_families);
    myfile.write("AVG_Events_per_family = %f events\n" % avg_n);
    myfile.write("MAX_Events_per_family = %.2f events\n" % max_n);
    myfile.write("AVG_COV = %f\n" % avg_cov);
    myfile.write("MEAN_Timespan = %f years\n\n\n" % mean_timespan);

    for i in range(len(bboxes)):
        box = bboxes[i];
        myfile.write("Box [%.2f,%.2f,%.2f,%.2f,%.2f,%.2f] slip rate = %f cm/year \n" % (
        box[0], box[1], box[2], box[3], box[4], box[5], slip_rate_boxes[i]));
        myfile.write("Box [%.2f,%.2f,%.2f,%.2f,%.2f,%.2f] slip_rate_unc = %f cm/year \n" % (
        box[0], box[1], box[2], box[3], box[4], box[5], unc_boxes[i]));
    myfile.close();
    return;
