from collect_data_in_dirs import *
from csv_utils import *
import csv, inspect, yaml, sys
import matplotlib.pyplot as plt
import numpy as np

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)
os.chdir(this_directory)
architecture_storage_names = ["DRAM", "SMEM", "RF"]
gemm_dataspace_names = ["A", "B", "Z"]
dnn_dataspace_names = ["Inputs", "Weights", "Outputs"]

PROBLEM_SHAPE = "gemm"

def plot_csv(summary):
    
    density_order = ["WD-1.0", "WD-0.5", "WD-0.3333", "WD-0.25"]
    figs = []
    stat_idx = 0
    plt.rcParams['font.size'] = 16 
    plt.rcParams['axes.titlesize'] = 18 
    plt.rcParams['axes.labelsize'] = 16 
    
    for stat_type in ["cycles", "energy"]:
    
        stat_idx = stat_idx + 1
        fig = plt.figure(num=stat_idx, figsize=(10, 6))
        X_ticks = []
        
        DSTC_bars = []
        STC_bars = []
        STC_flexible_bars = []
        STC_flexible_rle_bars = []
        STC_flexible_rle_dualCompress_bars = []
        
        N = 0
        for density_name in density_order :
            wd_density = float(density_name.split("-")[1])
            
            DSTC_bars.append(summary[density_name][stat_type]["DSTC-RF2x-24-bandwidth"])
            STC_bars.append(summary[density_name][stat_type]["STC-RF2x-24-bandwidth"])
            STC_flexible_bars.append(summary[density_name][stat_type]["STC_flexible-RF2x-24-bandwidth"])
            STC_flexible_rle_bars.append(summary[density_name][stat_type]["STC_flexible-RF2x-24-bandwidth-RLE"])
            STC_flexible_rle_dualCompress_bars.append(summary[density_name][stat_type]["STC_flexible_dualCompress-RF2x-24-bandwidth-RLE"])
            
            X_ticks.append(str(wd_density*100) + "%")
            N = N + 1

        bar_width = 0.15
        
        ind = np.arange(N)
        
        plt.bar(ind, DSTC_bars, bar_width, label="DSTC", color = 'firebrick')
        plt.bar(ind + bar_width, STC_bars, bar_width, label="STC", color = 'cornflowerblue')
        plt.bar(ind + 2*bar_width, STC_flexible_bars, bar_width, label="STC-flexible", color='lightslategrey')
        plt.bar(ind + 3*bar_width, STC_flexible_rle_bars, bar_width, label="STC-flexible-rle", color='gold')
        plt.bar(ind + 4*bar_width, STC_flexible_rle_dualCompress_bars, bar_width, label="STC-flexible-rle-dualCompress", color='black')

        title_fontdict = {'fontsize': 16}
        plt.xticks(ind + bar_width*4/2, X_ticks, rotation=0)
        if stat_type == "cycles" :
            plt.ylabel('Normalized Cycles')  
            plt.title("Fig15 Cycles", fontdict = title_fontdict)
        else:
            plt.ylabel('Normalized Energy')    
            plt.title("Fig15 Energy \nbased on 45nm instead of 65nm reported in paper (trends should match)",fontdict = title_fontdict)
        plt.xlabel('Weight Density Degrees')
        plt.legend(loc='best')
        
        fig_name = "fig_" + stat_type + ".png"
        plt.savefig(os.path.join(os.pardir, "outputs", fig_name))
        print("Fig saved to ", os.path.abspath(os.path.join(os.pardir, "outputs", fig_name)))        
        
    #plt.show()


def aggregate_model_stats(summary, verbose):
    
    # pick the best dataflow for each scheme
    for layer_name, layer_stats in summary.items():
        for hw_setup, stats in layer_stats.items():
            summary[layer_name][hw_setup]["edp"] = stats["cycles"] * stats["energy_pJ"]
    
    stats_types = ["cycles", "energy_pJ", "edp"]
    hw_setup_based_summary = {}    
   
    #pprint.pprint(summary)
    for stats_type in stats_types:
        hw_setup_based_summary[stats_type] = {}
        for layer_name, layer_stats in summary.items():
            for hw_setup, stats in layer_stats.items():
                if hw_setup not in hw_setup_based_summary[stats_type]:
                    hw_setup_based_summary[stats_type][hw_setup] = {}
                hw_setup_based_summary[stats_type][hw_setup][layer_name] = stats[stats_type]
        
    processed_summary = {}
    for stats_type, stats in hw_setup_based_summary.items():
        processed_summary[stats_type] = {}
        for hw_setup_name, hw_setup_stats in stats.items():
            processed_summary[stats_type][hw_setup_name] = 0
            for layer_name, val in hw_setup_stats.items():
                processed_summary[stats_type][hw_setup_name] += val
    
    return processed_summary

def dump_csvs(summary, filename_base, revert = True, per_layer = True):

    csv_path = os.path.join(os.pardir, "csv_results", filename_base + ".csv")
    if os.path.exists(csv_path):
        print("Warn: found existing file: ", csv_path, " --- remove")
        os.remove(csv_path)
    print("dummping stats to ", csv_path)
    
    if not revert:
        process_and_dump_limited_bw_stats(summary, csv_path, per_layer)
    
    else: 
        reverse_key_summary = {}
        for WD_degree, WD_stats in summary.items():
            reverse_key_summary[WD_degree] = {}
            for stat_type, hw_setups in WD_stats.items():
                for hw_setup, actual_val in hw_setups.items():
                    if hw_setup not in reverse_key_summary[WD_degree]:
                        reverse_key_summary[WD_degree][hw_setup] = {}
                    reverse_key_summary[WD_degree][hw_setup][stat_type] = actual_val
        
        # pprint.pprint(reverse_key_summary)
        process_and_dump_limited_bw_stats(reverse_key_summary, csv_path, per_layer)

def convert_to_per_hw_setup_based(summary):
    # get the various hw setups

    layers = list(summary.keys())
    unique_hw_setups = summary[layers[0]].keys()

    hw_setup_based_stats = {}
    for unique_hw_setup in unique_hw_setups:
        hw_setup_based_stats[unique_hw_setup] = {}
        for layer in layers:
            if unique_hw_setup not in summary[layer]:
                print("ERROR: ", unique_hw_setup, " not found for layer: ", layer)
                print("Available setups: ", summary[layer].keys())
                sys.exit(1)
            hw_setup_based_stats[unique_hw_setup][layer] = deepcopy(summary[layer][unique_hw_setup])
    return hw_setup_based_stats

def process_normalization(all_models_summary, norm_to):

    if norm_to == []:
        return all_models_summary

    base_WD_name = norm_to[0]
    base_hw_setup = norm_to[1]
    
    for WD_name, WD_stats in all_models_summary.items():
        for stat_type, stats in WD_stats.items():
            if base_WD_name == "":
                baseline_stats = stats[base_hw_setup]
            else:
                baseline_stats = all_models_summary[base_WD_name][stat_type][base_hw_setup]
            
            for hw_setup, stat_value in stats.items():
                all_models_summary[WD_name][stat_type][hw_setup] = round(stat_value/baseline_stats,4)
    
    return all_models_summary 


def main():
    parser = argparse.ArgumentParser( description= " Parse sweeping results generated by sweep.py. Usage: python3 parse_sweep_results.py --raw ../outputs/resnet_selected/*" )
    parser.add_argument('--raw', nargs='*', required=True, type=str, help = "path to directory with outputs")
    parser.add_argument('--stats_prefix', type=str, default='timeloop-model')
    parser.add_argument('--norm_to', type=str, nargs = "*", default=["WD-1.0", "TC-RF2x-24-bandwidth"], 
                        help='normalize all output to a specific output, default to no norm to return abs vlaue,if need to norm to ampere dense base line, set to "FlexibleGH, Ms, dense_U" ')
    parser.add_argument('--overwrite', action="store_true")
    parser.add_argument('--num_layers', type=int, default=1000, help="max number of layers to process")
    parser.add_argument('-w', '--workload', type=str, default='resnet50_selected', help='model to aggregate to')
    parser.add_argument('-v', '--verbose', action="store_true")
    parser.add_argument('--use_model', action="store_true")
    parser.add_argument('-o', '--outfile_name', default='csv_summary', type=str,
                        help='output file path')
    parser.add_argument('--plot_csv', type=str, default=None, help="csv base name for data loading and plotting, e.g., resnet50") 
    args = parser.parse_args()
    
    include = ["cycles", "energy_pJ", "utilization"] 
    
    if args.plot_csv is None:
        # step 1: general summary stats for each layer, each hw setup 
        all_models_summary = {} 
        first_weight_density_degree = True
        for weight_density_degree_dir in args.raw:
            weight_density_name = weight_density_degree_dir.split(os.sep)[-1]
            all_models_summary[weight_density_name] = {}
            
            all_layers_summary = {}
            layer_id = 1
            num_layers = len(os.listdir(weight_density_degree_dir))
            # print("number of processed layers: ", num_layers)
            for layer_shape_dir in sorted(os.listdir(weight_density_degree_dir)):
                
                if layer_id > args.num_layers:
                    break
                layer_shape_name = layer_shape_dir.split(os.sep)[-1]
                #print("Layer ", layer_shape_name)
                
                per_shape_dirs = [os.path.join(weight_density_degree_dir, layer_shape_dir, d) \
                        for d in os.listdir(os.path.join(weight_density_degree_dir,layer_shape_dir))]
                summary = top(per_shape_dirs, args.stats_prefix, include, "none") 
               
                # explicit indication of STC not supporting certain ratio (instead of using 2:4 values for all other ratioes)
                weight_density_degree = float(weight_density_name.split('-')[-1])
                if weight_density_degree < 0.5:
                    for key, stat in summary.items():
                        if "STC-" in key and "DSTC" not in key:
                            for stat_type, val in stat.items():
                                summary[key][stat_type] = 0
                # collect per layer result 
                all_layers_summary[layer_shape_name] = deepcopy(summary)
                layer_id = layer_id + 1

            model_summary = aggregate_model_stats(all_layers_summary, args.verbose) 
            #pprint.pprint(model_summary)
            all_models_summary[weight_density_name] = deepcopy(model_summary)
            
            # Sanity check on number of layers processed
            # should be the same across all density cases
            if first_weight_density_degree:
                num_layers = len(all_layers_summary.keys())
                first_weight_density_degree = False
        
  
        norm_to = args.norm_to 
        #pprint.pprint(all_models_summary)
        normed_all_models_summary = process_normalization(all_models_summary, args.norm_to)
        #pprint.pprint(normed_all_models_summary)
    
        if norm_to == []:
            norm_to = ["", ""]
        csv_file_name = args.workload + "-normed-" + norm_to[0] + "-" + norm_to[1]
        dump_csvs(normed_all_models_summary, csv_file_name, per_layer = True) 
    
    
    # step 4: generate plots
    norm_to = args.norm_to 
    if args.norm_to == []:
        norm_to = ["", ""]
    csv_file_name = args.workload + "-normed-" + norm_to[0] + "-" + norm_to[1] + ".csv"
    csv_path = os.path.join('..', 'csv_results', csv_file_name) if args.plot_csv is None else args.plot_csv
    summary = load_csv_into_dict_WD_based(csv_path)
    plot_csv(summary)

if __name__ == '__main__':
    main()


