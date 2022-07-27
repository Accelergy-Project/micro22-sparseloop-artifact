import yaml, inspect, os, sys, subprocess, pprint, shutil, argparse
from copy import deepcopy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

OVERWRITE = True

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)

sys.path.append(os.path.join(this_directory, "..", "..", "utils"))
from parse_timeloop_output import parse_timeloop_stats

def plot(stats, X_ticks, base_output_dir):
    
    plt.rcParams['font.size'] = 16 
    plt.rcParams['axes.titlesize'] = 16 
    plt.rcParams['axes.labelsize'] = 16   
    title_fontdict = {'fontsize' : 18 }
    bar_width = 0.2
    colors = {"baseline": "cornflowerblue", "uniform": "firebrick", "actual_data": "pink"} 
    #fig = plt.figure(num=0, figsize=(7, 4))
    fig, ax = plt.subplots()
    
    num_series = len(stats.keys())
    num_groups = len(stats[list(stats.keys())[0]])
    ind = np.arange(num_groups)
    
    for idx in range(num_series):
        series_name = list(stats.keys())[idx]
        plt.bar(ind + idx * bar_width, stats[series_name], bar_width, label = series_name, color = colors[series_name])
        
    plt.xticks (ind + bar_width * num_series/2, X_ticks, rotation=0)    
    plt.xlabel('Layers')
    plt.ylabel("Number of Cycles")
    plt.yscale("log")
    
    plt.ylim(300000, 30000000)
    plt.title("Fig12 Processing Latency")
    plt.legend(loc = 'best')
    
    fig.tight_layout()
    plt.savefig(os.path.join(base_output_dir, "fig.png"))
    print("Fig saved to ", os.path.abspath(os.path.join(base_output_dir, "fig.png")))
    plt.show()

def main(base_output_dir):
    
    gt_results = yaml.load(open(os.path.join(".", "ground_truth_cycles.yaml")), Loader = yaml.SafeLoader)
    stats = {"baseline": []}
    X_ticks = []
    
    # go through layers
    layer_order = ["L07", "L27", "L21", "L13", "L19", "L25", "L23", "L09"]
    for layer_name in layer_order:
        if not os.path.exists(os.path.join(base_output_dir, layer_name)):
            break
        stats["baseline"].append(gt_results[layer_name]) 
        X_ticks.append(layer_name)
        for density_model in os.listdir(os.path.join(base_output_dir, layer_name)):
            if density_model not in stats:
                stats[density_model] = []
            parsed_stats = parse_timeloop_stats(os.path.join(base_output_dir, layer_name, density_model, "output", "timeloop-model.map+stats.xml" ))
            stats[density_model].append(parsed_stats["cycles"])
    
    plot(stats, X_ticks, base_output_dir)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(""" sweep various mobilenet layers with different density distribution options """)
    parser.add_argument('--include_actual', action="store_true", help="explore mappings instead of use the mappings already found")
    options = parser.parse_args()

    if options.include_actual:
        base_dir_name = "uniform_actual"
    else:
        base_dir_name = "uniform_only"
    
    base_output_dir = os.path.join(this_directory, "..", "outputs", base_dir_name)
    main(base_output_dir)
 
