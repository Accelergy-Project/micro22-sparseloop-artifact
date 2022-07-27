import os, inspect, sys, subprocess, yaml, pprint, math, pickle, shutil, signal, math, time, argparse
from copy import deepcopy

# static paths
this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)
os.chdir(this_directory)

# import timeloop result parser
sys.path.append(os.path.join(this_directory, "..", "..", "utils"))
from parse_timeloop_output import parse_timeloop_stats
from sweep import workload_dir_path

def main(stats_prefix):
    
    stats_collector = {}
    job_names = ["alexnet_conv1", "alexnet_conv2", "alexnet_conv3", "alexnet_conv4", "alexnet_conv5"]
    
    # collect all the static job information
    for layer in os.listdir(workload_dir_path):
        job_name = layer.split('.')[0]
        base_output_dir = os.path.join(OUT_DIR, job_name)
        
        workload_spec = yaml.load(open(os.path.join(workload_dir_path, layer)), Loader = yaml.SafeLoader)
        dense_iact = workload_spec["problem"]["instance"]["densities"]["Inputs"] > 0.9
        stats_collector[job_name] = {"path": base_output_dir, "dense_iact": dense_iact}
    
    # find output files and parse based on the collected information
    print("Eyeriss DRAM Compression Ratioes (read + write)")
    for job_name in job_names:
        job_info = stats_collector[job_name]
        
        baseline_dense_path = job_info["path"].replace("outputs", "dense_outputs")
        baseline_dense_output_stats = parse_timeloop_stats(os.path.join(baseline_dense_path, "output", stats_prefix + ".map+stats.xml"))
        baseline_DRAM_accesses = sum(j for j in baseline_dense_output_stats["energy_breakdown_pJ"]["DRAM"]["actual_accesses_per_instance"])
        
        job_output_stats = parse_timeloop_stats(os.path.join(job_info["path"], "output", stats_prefix + ".map+stats.xml"))
        job_DRAM_weight_accesses =  job_output_stats["energy_breakdown_pJ"]["DRAM"]["actual_accesses_per_instance"][0]
        job_DRAM_iact_accesses =  job_output_stats["energy_breakdown_pJ"]["DRAM"]["actual_accesses_per_instance"][1]
        job_DRAM_oact_accesses =  job_output_stats["energy_breakdown_pJ"]["DRAM"]["actual_accesses_per_instance"][2]
       
        # ~0.76 captures the overhead and is obtained from the stats files as metadata overhead ratio
        # Please look into the timeloop.stats.txt files in the outputs folder for information
        if job_info["dense_iact"]: 
            eyeriss_DRAM_accesses = job_DRAM_weight_accesses + job_DRAM_iact_accesses + job_DRAM_oact_accesses/0.76
        else:
            eyeriss_DRAM_accesses = job_DRAM_weight_accesses + job_DRAM_iact_accesses/0.76 + job_DRAM_oact_accesses/0.76
        
        print(job_name, ": ",  round(baseline_DRAM_accesses/eyeriss_DRAM_accesses, 1))

  
if __name__ == "__main__":

    parser = argparse.ArgumentParser("parse result to get DRAM compression ratio for Eyeriss. Usage: python3 parse_and_plot.py")
    parser.add_argument('--stats_prefix', type=str, default="timeloop-model", help='the output prefix that the parser to be looking for' )
    parser.add_argument('-o', '--output_dir', type=str, default=os.path.join(this_directory, "..", "outputs"), help='abs path to top level output directory that needs to be parsed' )
    options = parser.parse_args()
    OUT_DIR = options.output_dir
    
    main(options.stats_prefix)



