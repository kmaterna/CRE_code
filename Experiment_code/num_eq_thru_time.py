#!/usr/bin/env python

import datetime as dt
import glob
import matplotlib.pyplot as plt
import numpy as np

def configure(station_name):
    exist_file_dir = station_name + "/exist/";
    total_pair_candidates = "Stage2_Results/CREs_by_station/"+station_name+"/"+station_name+"_total_list.txt";
    repeaters_file = "Stage2_Results/CREs_by_station/" + station_name + "/" + station_name + "_repeaters_list.txt";
    return exist_file_dir, total_pair_candidates, repeaters_file;

def read_pairs(filename):
    pair_event_times = [];
    [ev1, ev2] = np.loadtxt(filename, usecols=(0, 1), unpack=True, skiprows=1,
                            dtype={'names': ('a', 'b'), 'formats': ('U55', 'U55')});
    if np.size(ev1) == 1:
        pair_events = [str(ev1), str(ev2)];
    elif np.size(ev1) == 0:
        pair_events = [];
    else:
        pair_events = list(ev1) + list(ev2);
    for event in pair_events:
        specname = event.split('/')[-1];
        yrstr, daystr = specname[-28:-24], specname[-23:-20];
        pair_event_times.append(dt.datetime.strptime(yrstr + " " + daystr, "%Y %j"));
    return sorted(pair_event_times);

def read_all_evtimes(dirname):
    sac_files = glob.glob(dirname + "*.sac");
    all_evtimes = [];
    for item in sac_files:
        specname = item.split('/')[-1];
        yrstr, daystr = specname[-28:-24], specname[-23:-20];
        all_evtimes.append(dt.datetime.strptime(yrstr+" "+daystr, "%Y %j"));
    return sorted(all_evtimes);

def make_cumulative_ts(event_dts, normalize=False):
    """Assumes the events come in ordered"""
    n_total, total_ts = [], []
    total_ts.append(event_dts[0]);
    n_cumulative = 0;
    n_total.append(0)
    n_total.append(0)
    for i in range(len(event_dts)):
        n_cumulative += 1;
        total_ts.append(event_dts[i])
        total_ts.append(event_dts[i])
        n_total.append(n_cumulative)
        n_total.append(n_cumulative)
    total_ts.append(event_dts[-1]);
    if normalize:
        n_total = np.divide(n_total, n_total[-1]);
    return total_ts, n_total;

def make_plot(all_evtimes, pair_events, cre_events, station_name):
    zoom_start = dt.datetime.strptime("20210601", "%Y%m%d");
    zoom_end = dt.datetime.strptime("20220331", "%Y%m%d");
    eq_time = dt.datetime.strptime("20211220", "%Y%m%d");
    last_eq_time = dt.datetime.strptime("20220308", "%Y%m%d");

    ts1, n_total = make_cumulative_ts(all_evtimes, normalize=True);
    ts2, n_pair_candidates = make_cumulative_ts(pair_events, normalize=True);
    ts3, n_cres = make_cumulative_ts(cre_events, normalize=True);
    f = plt.figure(figsize=(14, 7), dpi=300);
    plt.plot(ts1, n_total, linewidth=2, color='black', label='all sac files, n='+str(len(all_evtimes)));
    plt.plot(ts2, n_pair_candidates, linewidth=2, color='red',
             label='candidate pairs (cc>0.7), n='+str(len(pair_events)));
    plt.plot(ts3, n_cres, linewidth=2, color='blue', label='CRE pairs (coh>0.97), n='+str(len(cre_events)));
    plt.title("CRE/Earthquake occurrence at %s" % station_name, fontsize=20);
    plt.ylabel('Normalized Event Count', fontsize=15);
    plt.gca().grid(True)
    plt.plot([eq_time, eq_time], [0.5, 1.5], linestyle='dashed', color='teal');
    plt.ylim([0, 1.01]);
    plt.legend();
    ax = f.add_axes([0.53, 0.2, 0.35, 0.2]);
    ax.plot(ts1, n_total, linewidth=2, color='black');
    ax.plot(ts2, n_pair_candidates, linewidth=2, color='red');
    ax.plot(ts3, n_cres, linewidth=2, color='blue');
    ax.tick_params(axis='x', rotation=45)
    ax.text(dt.datetime.strptime("20210603", "%Y%m%d"), 1.0, "2021-22", fontsize=15);
    ax.plot([eq_time, eq_time], [0.5, 1.5], linestyle='dashed', color='teal');
    ax.text(eq_time, 0.85, "M6.0, M6.1", fontsize=10, color='teal');
    ax.text(last_eq_time, 0.85, "End", fontsize=10, color='black');
    ax.plot([last_eq_time, last_eq_time], [0.5, 1.5], linestyle='dashed', color='black');
    ax.set_xlim([zoom_start, zoom_end]);
    ax.set_ylim([0.84, 1.03]);
    plt.savefig(station_name+"_CREs_with_time.png");
    print("Saving figure %s " % station_name+"_CREs_with_time.png");
    return;


if __name__ == "__main__":
    sta_names = ["B045", "B046", "B047", "B049", "B932", "B933", "B935", "JCC", "KCT", "KHMB", "KMPB", "KMR"];
    for station_name in sta_names:
        exist_file_dir, total_pair_candidates, repeaters_file = configure(station_name);
        all_evtimes = read_all_evtimes(exist_file_dir);
        pair_events = read_pairs(total_pair_candidates);
        cre_events = read_pairs(repeaters_file);
        make_plot(all_evtimes, pair_events, cre_events, station_name);
