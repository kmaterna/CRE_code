""" 
MENDOCINO REPEATERS PROJECT
June 9, 2016

This code makes an important plot:

1. filtered waveform1
2. filtered waveform2
3. Shifted xcorr function
4. Coherence 0-50Hz (as calculated by C)
5. SNR for both traces. 

"""
from obspy import read
from obspy.signal.cross_correlation import correlate
import numpy as np
import matplotlib.pyplot as plt


def make_coh_snr_plot(output_dir, event1, event2, waveform_file_name, coh_file_name, inst_freq, min_freq, max_freq,
                      snr_cutoff, show_overlay, pretty_plot):
    # [event1, event2, waveform_file, coh_file, inst_freq, min_freq, max_freq, snr_cutoff, show_overlay]
    # inst_freq = instrument frequency
    # min/max freq = for drawing a black line on the coherence graph.

    # Parameters that don't usually change
    N_xcorr = 256 - 5;  # the number of data points on either side to cross-correlate
    snr1file = "SNR1.txt"
    snr2file = "SNR2.txt"

    # Import the data for plotting
    [waveform1, waveform2] = np.loadtxt(waveform_file_name, unpack=True);
    [c_freq, c_coh] = np.loadtxt(coh_file_name, unpack=True, usecols=(0, 1));  # results of coherence calculation
    [frequency1, snr1] = np.loadtxt(snr1file, unpack=True);  # READ IN signal to noise ratios
    [frequency2, snr2] = np.loadtxt(snr2file, unpack=True);  # READ IN signal to noise ratios

    t = np.arange(0, len(waveform1) / inst_freq, 1.0 / inst_freq)  # 100 Hz data.

    # DOING XCORR JUST FOR KICKS
    if len(waveform1) < 256 / 4 or len(waveform2) < 256 / 4:
        N_xcorr = 256 / 4;  # smaller window for smaller signals
    [index, cc_max, fnct] = correlate(waveform1, waveform2, shift=N_xcorr);  # possible issue with new obspy xcorr API

    # GRABBING EVENT MAGNITUDES, ALSO FOR KICKS
    # Assuming that sacfiles are already copied into working dir
    data_directory = ""
    sacfile1 = data_directory + event1
    sacfile2 = data_directory + event2
    print("Event 1: ");
    [mag1, dist1] = get_mag_dist_from_sac(sacfile1);
    print("Event 2: ");
    [mag2, dist2] = get_mag_dist_from_sac(sacfile2);

    # COMPUTE MEDIAN OF COHERENCE DATA IN SOME FREQUENCY RANGE
    begin = int(len(c_coh) * min_freq / (inst_freq / 2.0))
    finish = int(len(c_coh) * max_freq / (inst_freq / 2.0))
    if finish == len(c_coh):
        finish = finish - 1;  # For python's 0-indexing.
    coherence_val = np.median(c_coh[begin:finish])

    print("Length of C Coherence Vector: %d \n" % len(c_coh));

    if show_overlay:
        g, axarr = plt.subplots(4)
        axarr[0].set_title(event1[15:] + ' Overlaid With ' + event2[15:])
        axarr[0].plot(t[0:len(waveform1)], waveform1)
        axarr[1].plot(t[0:len(waveform2)], waveform2, 'r')
        axarr[2].plot(t[0:len(waveform1)], waveform1)
        axarr[2].plot(t[0:len(waveform2)], waveform2, 'r')
        axarr[3].plot(t[0:len(waveform2)], np.subtract(waveform1, waveform2), 'b')
        plt.show();
        plt.close();

    # PLOTTING WAVEFORMS , XCORR, AND COHERENCE
    fig = plt.figure(dpi=500);
    g, axarr = plt.subplots(5)
    if pretty_plot:
        axarr[0].plot(t[0:len(waveform1)], waveform1 / np.max(waveform1))  # normalizing because it's prettier
        axarr[0].set_ylim([-1, 1])
        axarr[0].set_ylabel('v(t)')
        axarr[1].plot(t[0:len(waveform2)], waveform2 / np.max(waveform2), 'r')  # normalizing because it's prettier
        axarr[1].set_ylim([-1, 1])
        axarr[1].set_ylabel('v(t)')
        axarr[1].set_xlabel('Time (s)')
    else:
        axarr[0].plot(t[0:len(waveform1)], waveform1)
        axarr[1].plot(t[0:len(waveform2)], waveform2, 'r')

    axarr[0].set_xlim([0, 20.48])
    axarr[0].locator_params(axis='y', nbins=3)
    axarr[1].set_xlim([0, 20.48])
    axarr[1].locator_params(axis='y', nbins=3)

    # the cross-correlation where x-axis means time delay (in seconds)
    xcorr_xaxis = np.arange(-N_xcorr / (1.0 * inst_freq), (N_xcorr + 1) / (1.0 * inst_freq), 1.0 / inst_freq)
    if pretty_plot == 0:
        axarr[2].plot(xcorr_xaxis, fnct, 'k')
        max_cc_str = str(max(fnct));
        axarr[2].set_title('Cross-Correlation Function: Maximum = ' + max_cc_str[0:5])
        axarr[2].locator_params(axis='y', nbins=5)
    if pretty_plot == 1:
        axarr[2].axis('off');

    # Now plotting coherence function
    axarr[3].plot(c_freq, c_coh, 'k')
    axarr[3].plot([c_freq[begin], c_freq[begin]], [0, 1], '--k')
    axarr[3].plot([c_freq[finish], c_freq[finish]], [0, 1], '--k')
    plt.ylim((0, 1))
    max_coh_str = str(coherence_val);
    axarr[3].set_title('Coherence Value = ' + max_coh_str[0:5])
    axarr[3].locator_params(axis='y', nbins=4)
    axarr[3].set_ylabel('Coherence')

    axarr[4].plot(frequency1, snr1, 'b')
    axarr[4].plot(frequency2, snr2, 'r')
    axarr[4].plot([0, 50], [1, 1], '--k')
    axarr[4].plot([0, 50], [snr_cutoff, snr_cutoff], '--g')
    axarr[4].set_ylabel('SNR')
    top_number = max(max(snr1), max(snr2))
    plt.ylim((0, top_number))
    axarr[4].locator_params(axis='y', nbins=4)

    plt.xlabel('Frequency (Hertz)')
    plt.subplots_adjust(hspace=1.0)
    # plt.tight_layout()

    # Slightly different formatting if we plan on showing this plot to human beings.
    if pretty_plot:
        x_location_text = 16;
        y_location_text = 0.25;
        axarr[0].text(x_location_text, y_location_text, "Mag " + str(mag1), fontsize=15);
        axarr[1].text(x_location_text, y_location_text, "Mag " + str(mag2), fontsize=15);
        axarr[4].set_title('Signal-to-Noise Ratio');
        event1_short = event1[-28:-20]
        event2_short = event2[-28:-20]
        axarr[0].set_title("Event " + event1_short + ' and Event ' + event2_short, fontsize=16)
    else:
        axarr[4].set_title(
            'SNR. D1=' + str(dist1) + ', M1=' + str(mag1) + '; D2=' + str(dist2) + ', M2=' + str(mag2) + '.')
        event1_short = event1[-28:-13]
        event2_short = event2[-28:-13]
        axarr[0].set_title(event1_short + ' and ' + event2_short, fontsize=16)

    plt.savefig(output_dir + event1_short + "_" + event2_short + ".pdf");

    return;


def get_mag_dist_from_sac(sacfile):
    st1 = read(sacfile)
    tr1 = st1[0]
    temp1 = tr1.stats
    d1 = temp1['sac']
    mag1 = d1['mag']
    dist1 = d1['dist']
    depth1 = d1['evdp']
    print("Magnitude of Event is: %f " % mag1);
    print("Depth of Event is: %f" % depth1);
    print("Distance of Event is: %f \n-------------------------" % dist1);
    mag1 = round(float(mag1), 2)
    dist1 = round(float(dist1), 2)
    return [mag1, dist1];
