""" 
MENDOCINO REPEATERS PROJECT
6/12/16

From a list of repeating earthquakes, generate a set of important histograms and maps. 

"""
import numpy as np
import matplotlib.pyplot as plt
from obspy import read
from subprocess import call
import glob, sys

sys.path.append(".");  # add current directory to python path
import master_waveform_viewer_snr


def make_inter_event_time_histogram(station_name, filename, output_dir):
    my_file = open(filename, 'r');

    # Read in lists for event1 and event2
    my_file.readline();  # ignore the first line.
    intervals = []
    for line in my_file:
        temp = line.split()
        ev1 = (temp[0])
        ev2 = (temp[1])

        # Here we make the assumption that the file names are of the format *.YYYY.DDD.HHMMSS.????????.sac
        name1 = ev1[-28:-13]
        name2 = ev2[-28:-13]
        event_time1 = float(name1[0:4]) + float(name1[5:8]) / 365.24 + float(name1[9:11]) / (24 * 365.24) + float(
            name1[11:13]) / (24 * 60 * 365.24) + float(name1[13:15]) / (24 * 60 * 60 * 365.24)
        event_time2 = float(name2[0:4]) + float(name2[5:8]) / 365.24 + float(name2[9:11]) / (24 * 365.24) + float(
            name2[11:13]) / (24 * 60 * 365.24) + float(name2[13:15]) / (24 * 60 * 60 * 365.24)
        intervals.append(event_time2 - event_time1)
    my_file.close();
    print("Making inter event time histogram...\n");

    plt.figure()
    plt.hist(intervals, 30, color='b')
    plt.ylabel('Number of Event Pairs');
    plt.xlabel('Time (years)');
    plt.title('Intervals between Repeating Event Pairs at ' + station_name + "; N_total = " + str(len(intervals)));
    plt.savefig(output_dir + "_intervals_histogram.png");
    plt.close()
    return;


# Shows us the dist/mag distributions of the repeaters we are finding. 
def make_mag_dist_histograms(repeaters_file, directory):
    [mag1, dist1, mag2, dist2] = np.loadtxt(repeaters_file, usecols=(6, 7, 8, 9), unpack=True, skiprows=1)
    dist, Mean_M, Diff_M = [], [], [];

    # Dealing with the one-element case.
    if type(mag1) != type([]):
        mag1 = list([mag1]);
        dist1 = list([dist1]);
        mag2 = list([mag2]);
        dist2 = list([dist2]);

    for i in range(len(dist1)):
        Mean_M.append((mag1[i] + mag2[i]) / 2)  # Record mean magnitude.
        dist.append((dist1[i] + dist2[i]) / 2)  # Record mean magnitude.
        Diff_M.append(abs(mag1[i] - mag2[i]))  # Record magnitude differences.

    print("Making Distances histogram...\n");
    plt.figure();
    plt.hist(dist, color='b');
    plt.xlabel('Mean Distance From Station (km)');
    plt.ylabel('Number of Event Pairs');
    plt.title("Distance of Repeating Event Pairs")
    plt.savefig(directory + "_distances_histogram.png")
    plt.close();

    print("Making Magnitudes histogram...\n");
    plt.figure();
    plt.hist(Mean_M, color='b');
    plt.xlabel('Mean Magnitude');
    plt.ylabel('Number of Event Pairs');
    plt.title("Magnitudes of Repeating Event Pairs")
    plt.savefig(directory + "_magnitudes_histogram.png")
    plt.close()

    print("Making Magnitude Differences histogram...\n");
    plt.figure();
    plt.hist(Diff_M, color='b');
    plt.xlabel('Magnitude Difference');
    plt.ylabel('Number of Event Pairs');
    plt.title("Magnitude Differences of Repeating Event Pairs");
    plt.savefig(directory + "_magnitude_differences_histogram.png");
    plt.close()
    return;


def make_repeater_seismograms(MyParams):
    # station_name, CRE_filename, output_dir, snr_cutoff):
    # For each repeater, call the plotting routines to look at its coherence, xcorr, and SNR.
    clear_list = glob.glob(MyParams.output_dir + "*.pdf");
    for item in clear_list:
        call(['rm', item], shell=False);
    my_file = open(MyParams.CRE_out_filename, 'r');
    my_file.readline();  # skip the first line of headers.
    for line in my_file:
        temp = line.split()
        event1 = temp[0]
        event2 = temp[1]
        f1 = float(temp[4])
        f2 = float(temp[5])  # the frequency range we're talking about for valid SNR.
        master_waveform_viewer_snr.master_waveform_viewer_snr(MyParams.station_name, event1, event2, f1, f2,
                                                              MyParams.snr_cutoff, MyParams.raw_sac_dir,
                                                              MyParams.output_dir);
    my_file.close();
    return;


def make_coherence_histogram(coh_all, coh_keepers, station_name, save_path):
    plt.figure();
    plt.hist(coh_all, bins=50, histtype='stepfilled', color='b', label='All')
    plt.hist(coh_keepers, bins=8, histtype='stepfilled', color='r', alpha=0.5, label='Repeaters')
    plt.title('Coherence Values for Station ' + station_name);
    plt.legend();
    plt.savefig(save_path + station_name + '_coherence_hist.eps');
    plt.close();
    return;


def make_xcorr_histogram(xcorr_all, xcorr_keepers, station_name, save_path):
    # Make a histogram of cross correlation values
    plt.figure();
    plt.hist(xcorr_all, bins=40, histtype='stepfilled', color='b', label='All');
    plt.hist(xcorr_keepers, bins=40, histtype='stepfilled', color='r', label='CREs');
    plt.xlim([0.6, 1]);
    plt.title('Cross Correlation Values for Station ' + station_name);
    plt.legend();
    plt.savefig(save_path + station_name + '_xcorr_hist.eps');
    plt.close();
    return;


def make_scatter_coh_xcorr(xcorr_all, coh_all, xcorr_keepers, coh_keepers, distance_all, station_name, save_path):
    # Make a plot that shows cross-correlation vs. coherence
    plt.figure();
    for x in range(len(distance_all)):
        if distance_all[x] > 100:
            distance_all[x] = 100;  # this is for forcing the color bar to show us nearby events.
    plt.scatter(xcorr_all, coh_all, c=distance_all);
    plt.colorbar();
    plt.plot(xcorr_keepers, coh_keepers, '.m');
    plt.xlabel('Cross-Correlation')
    plt.ylabel('Coherence')
    plt.ylim([0, 1])
    plt.xlim([0.6, 1])
    plt.savefig(save_path + station_name + '_xcorr_vs_coh.eps');
    plt.close();
    return;


def get_event_location(sacfile):
    st1 = read(sacfile, debug_headers=True);
    evla = st1[0].stats.sac.evla;
    evlo = st1[0].stats.sac.evlo;
    return [evlo, evla];


# Make a gmt map of the repeaters distribution
def make_repeaters_map(MyParams, mapping_data_general, mapping_data_specific, mapping_code):
    ifile = open(MyParams.CRE_out_filename, 'r')
    evfile1 = open('event_locations_first_hypodd.txt', 'w')
    evfile2 = open('event_locations_second_hypodd.txt', 'w')
    connectors = open('event_connectors.txt', 'w')

    print("Making GMT map of repeaters... \n");
    ifile.readline();  # skip the first line.
    for line in ifile:
        temp = line.split()
        event1 = temp[0]
        event1_base = event1.split('/')[
            -1];  # something like B045.PB.EHZ..D.2012.127.091831.71776880.sac without the directory
        [evlo1, evla1] = get_event_location(MyParams.raw_sac_dir + event1_base);
        evfile1.write(str(evlo1) + " " + str(evla1) + " 0.20\n");  # write longitude, latitude, marker size

        event2 = temp[1]
        event2_base = event2.split('/')[-1];
        [evlo2, evla2] = get_event_location(MyParams.raw_sac_dir + event2_base);
        evfile2.write(str(evlo2) + " " + str(evla2) + " 0.20\n");  # write longitude, latitude, marker size

        connectors.write(str(evlo1) + " " + str(evla1) + "\n" + str(evlo2) + " " + str(
            evla2) + "\n>\n");  # write ev1, ev2, > (for white lines between events)

    ifile.close();
    evfile1.close();
    evfile2.close();
    connectors.close();

    call([mapping_code + '/map_view_repeaters.gmt', str(MyParams.station_coords[0]), str(MyParams.station_coords[1]),
          MyParams.station_name, mapping_data_general, mapping_data_specific]);
    call(['mv', 'Repeater_Locations.ps', MyParams.output_dir + 'Repeater_Locations.ps'], shell=False);
    call(['rm', 'event_connectors.txt', 'event_locations_first_hypodd.txt', 'event_locations_second_hypodd.txt',
          'gmt.history']);
    return;
