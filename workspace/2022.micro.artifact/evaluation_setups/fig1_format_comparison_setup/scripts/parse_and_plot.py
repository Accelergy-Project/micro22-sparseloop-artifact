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

# paths to important input specs
base_output_dir = os.path.join(this_directory, "..", "outputs")


def main():

    sparse_opts = ["coordinate_list", "bitmask"]
    stat_types = ["cycles", "energy_pJ"]
    plot_metrics = ["Normalized Processing Speed", "Normalized Energy Efficiency"]
    colors = ["firebrick", "cornflowerblue"]
    bar_width = 0.2
    
    stat_idx = 0
    for stat_type in stat_types:
        N = 0
        bars = {}
        X_ticks = []
        
        fig = plt.figure(num=stat_idx, figsize=(5, 4))

        for sparse_opt in sparse_opts :
            bars[sparse_opt] = []
        for d in [0.01, 0.02, 0.04, 0.08, 0.1, 0.2, 0.4, 0.8]:
            X_ticks.append(str(d * 100) + "%")
            N = N + 1 
            for sparse_opt in sparse_opts:
                output_file_path = os.path.join(base_output_dir, "output_" + str(d) + "_" + sparse_opt, "timeloop-mapper.map+stats.xml")
                corresponding_coo_file_path = os.path.join(base_output_dir, "output_" + str(d) + "_coordinate_list", "timeloop-mapper.map+stats.xml")
                job_output_stats = parse_timeloop_stats(output_file_path)
                coo_output_stats = parse_timeloop_stats(corresponding_coo_file_path)
                bars[sparse_opt].append(coo_output_stats[stat_type]/job_output_stats[stat_type])
                
        
        ind = np.arange(N)

        for idx in range(len(sparse_opts)):
            sparse_opt = sparse_opts[idx]
            plt.bar(ind + idx * bar_width, bars[sparse_opt], bar_width, label = sparse_opt, color = colors[idx])
            
        plt.xticks (ind + bar_width * len(sparse_opts)/2, X_ticks, rotation=0)    
        plt.xlabel('Tensor density')
        plt.ylabel(plot_metrics[stat_idx].capitalize())
        plt.ylim([0, 2.5])

        title_fontdict = {'fontsize' : 18 }
        plt.title("Fig1 " + plot_metrics[stat_idx].capitalize())
        plt.legend(loc = 'best')
        fig.tight_layout()
        plt.savefig("../outputs/fig_" + str(stat_type) + ".png")
        print("Fig for ", stat_type, " saved to ", os.path.abspath("../outputs/fig_" + str(stat_type) + ".png"))
        stat_idx = stat_idx + 1

if __name__ == "__main__":
    main()
