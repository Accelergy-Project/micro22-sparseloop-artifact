import yaml, inspect, os, sys, subprocess, pprint, shutil
from copy import deepcopy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

OVERWRITE = True

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)

sys.path.append(os.path.join(this_directory, "..", "..", "utils"))
from parse_timeloop_output import parse_timeloop_stats

def plot(my_data, gt_data):
    
    plt.rcParams['font.size'] = 16 
    plt.rcParams['axes.titlesize'] = 16 
    plt.rcParams['axes.labelsize'] = 16   
    dense_gt = gt_data[1.0][1.0]
    dense_mine = my_data[1.0][1.0]

    X_ticks = []
    my_bars = []
    gt_bars = []
    
    N = 0
    total_gt = 0
    total_mine = 0
    for A_density, val in my_data.items():
        for B_density, cycles in val.items():
            if A_density == 1 and B_density == 1:
                continue
            if A_density != 1 or (A_density == 1 and B_density == 1):
                my_bars.append(round(cycles/dense_mine,2))
                gt_bars.append(round(gt_data[A_density][B_density]/dense_gt,2))
                X_ticks.append(str(A_density) + "_" + str(B_density))
                total_gt = total_gt + round(gt_data[A_density][B_density]/dense_gt,2)
                total_mine = total_mine + round(cycles/dense_mine)
                N = N + 1

    bar_width = 0.3
    ind = np.arange(N)
    fig = plt.figure(figsize=(14, 8))
    plt.bar(ind, gt_bars, bar_width, label="baseline", color='cornflowerblue')
    plt.bar(ind + bar_width, my_bars, bar_width, label="our work (uniform density model)", color='firebrick')

    plt.xticks(ind + bar_width/2, X_ticks, rotation=0)
    plt.xlabel('A-density_B-density')
    plt.ylabel('Latency (normalized to dense)')
    plt.ylim([0, 1])

    title_fontdict = {'fontsize': 18}
    plt.title("Fig13 DSTC Validation ", fontdict = title_fontdict)
    plt.legend(loc='best')
   
    accu = 0
    average_across = 0
    for i in range(len(X_ticks)):
        if gt_bars[i] != 1.0:
            accu = accu + 1 - abs(gt_bars[i] - my_bars[i])/gt_bars[i]
            average_across = average_across + 1
    avg_accu = round(accu / average_across, 3) 
    fig.tight_layout()
    
    fig_name = "fig.png"
    plt.savefig(os.path.join("..", "outputs", fig_name))
    print("Fig saved to ", os.path.abspath(os.path.join("..", "outputs", fig_name)))
    print("average accuracy: ", avg_accu) 
    #plt.show()

def main():
    
    # load all yaml input specs
    
    output_base_dir = os.path.join(this_directory, "..", "outputs")
    stats = {}
    # go through density combinations
    for A_density in [1.0, 0.9, 0.7, 0.5, 0.3]:
        for B_density in [1.0,  0.4]:
            job_name  = "B_" + str(B_density) + "-A_" + str(A_density)
            if A_density not in stats:
                stats[A_density] = {}
            # Get data 
            output_dir = os.path.join(output_base_dir, job_name, "outputs")
            raw_stats = parse_timeloop_stats(os.path.join(output_dir, "timeloop-model.map+stats.xml"))
            cycles = raw_stats["cycles"]
            stats[A_density][B_density] = cycles

    ground_truth_data = yaml.load(open(os.path.join(this_directory, "baseline.yaml")), Loader = yaml.SafeLoader)
    plot(stats, ground_truth_data)


if __name__ == "__main__":
    main()
        
