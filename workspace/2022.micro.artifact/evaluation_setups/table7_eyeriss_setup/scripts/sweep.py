import os, inspect, sys, subprocess, yaml, pprint, math, pickle, shutil, signal, math, time, argparse
from copy import deepcopy

# static paths
this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)
os.chdir(this_directory)

# paths to important input specs
arch_file_path = os.path.join(this_directory, "..", "arch", "arch.yaml")
components_file_path = os.path.join(this_directory, "..", "arch", "components.yaml")
sparse_iact_opt_file_path = os.path.join(this_directory, "..", "sparse_opt", "sparse_iact_opt.yaml")
dense_iact_opt_file_path = os.path.join(this_directory, "..", "sparse_opt", "dense_iact_opt.yaml")
workload_dir_path = os.path.join(this_directory, "..", "workload")
ert_path = os.path.join(this_directory, "..", "ert_art", "ERT.yaml")
art_path = os.path.join(this_directory, "..", "ert_art", "ART.yaml")
mappings_dir = os.path.join(this_directory, "..", "mappings_found")
dataflow_file_path = os.path.join(this_directory, "..", "dataflow", "row_stationary.yaml")
mapper_file_path = os.path.join(this_directory, "..", "mapper", "mapper.yaml")


def run_timeloop(job_name, input_dict, ert_path, art_path, base_dir):
    
    print("Running job: ", job_name)
    output_dir = os.path.join(base_dir, "output")
    
    if not os.path.exists(output_dir) \
       and not os.path.exists(os.path.join(output_dir, "timeloop-mapper.map+stats.xml")) \
       and not os.path.exists(os.path.join(output_dir, "timeloop-model.map+stats.xml")):
       os.makedirs(output_dir)
    else:
        if not OVERWRITE:
            print("Found existing results: ", output_dir)
            return True
        else:
            print("Found and overwrite existing results: ", output_dir)
    
    input_file_path = os.path.join(base_dir, "aggregated_input.yaml")
    shutil.copy(ert_path, os.path.join(base_dir, "ERT.yaml"))
    shutil.copy(art_path, os.path.join(base_dir, "ART.yaml"))
    
    if not USE_MODEL: 
        input_dict.pop("mapping")
        yaml.dump(input_dict, open(input_file_path, "w"), default_flow_style=False)
        os.chdir(output_dir)
        subprocess_cmd = ["timeloop-mapper", input_file_path, os.path.join(base_dir, "ERT.yaml"), os.path.join(base_dir, "ART.yaml")]

        print("\tRunning test: ", job_name)

        p = subprocess.Popen(subprocess_cmd)
        try:
            p.communicate(timeout=1200) # wait for at most 20 min
        except KeyboardInterrupt:
           p = 0
           while p <= 60 and not os.path.exists(os.path.join(output_dir, "timeloop-mapper.map+stats.xml")):
               time.sleep(1)
               p = p + 1        
        except subprocess.TimeoutExpired:
           print(job_name,  " reaches timeout limit")
           os.kill(p.pid, signal.SIGINT)
        
        return True
    
    else:
        model_input_dict = deepcopy(input_dict)
        model_input_dict.pop("architecture_constraints")
        model_input_dict.pop("mapspace_constraints")
        model_input_dict.pop("mapper")
        yaml.dump(model_input_dict, open(input_file_path, "w"), default_flow_style=False)
        
        os.chdir(output_dir)
        subprocess_cmd = ["timeloop-model", input_file_path, os.path.join(base_dir, "ERT.yaml"), os.path.join(base_dir, "ART.yaml"), os.path.join(base_dir, "map.yaml")]
        p = subprocess.Popen(subprocess_cmd)


def main():
    
    arch_spec = yaml.load(open(arch_file_path), Loader = yaml.SafeLoader)
    component_spec = yaml.load(open(components_file_path), Loader = yaml.SafeLoader)
    constraints_spec = yaml.load(open(dataflow_file_path), Loader = yaml.SafeLoader)
    mapper_spec = yaml.load(open(mapper_file_path), Loader = yaml.SafeLoader)

    stats_collector = {}

    for layer in os.listdir(workload_dir_path):
        aggregated_input = {}
        workload_spec = yaml.load(open(os.path.join(workload_dir_path, layer)), Loader = yaml.SafeLoader)
        
        dense_iact = workload_spec["problem"]["instance"]["densities"]["Inputs"] > 0.9

        if not dense_iact:             
            sparse_opt_spec = yaml.load (open(sparse_iact_opt_file_path), Loader = yaml.SafeLoader)
        else:
            sparse_opt_spec = yaml.load (open(dense_iact_opt_file_path), Loader = yaml.SafeLoader)
       
        mapping_file_path = os.path.join(mappings_dir, layer)
        mapping_spec = yaml.load(open(mapping_file_path), Loader = yaml.SafeLoader)
        
        aggregated_input.update(arch_spec)
        aggregated_input.update(component_spec)
        aggregated_input.update(sparse_opt_spec)
        aggregated_input.update(workload_spec)
        aggregated_input.update(mapping_spec)
        aggregated_input.update(constraints_spec)
        aggregated_input.update(mapper_spec)

        job_name = layer.split('.')[0]
        base_output_dir = os.path.join(OUT_DIR, job_name)

        # run evaluation 
        run_timeloop(job_name, aggregated_input, ert_path, art_path, base_output_dir)
    
  
if __name__ == "__main__":

    parser = argparse.ArgumentParser("sweep alexnet conv layers to get DRAM compression ratio for Eyeriss. Usage: python3 run_alexnet_conv.py")
    parser.add_argument('-o', '--output_dir', type=str, default=os.path.join(this_directory, "..", "outputs"), help='abs path to top level output directory' )
    parser.add_argument('--max_layers', type=int, default=100, help='max number of layers to run')
    parser.add_argument('--no_overwrite', action="store_true", help='skip job there is already some previous results in the output folder')
    parser.add_argument('--search_mapping', action="store_true", help='search for optimal mapping instead of using the provided mappings, this option will make the experiment run much slower')
    options = parser.parse_args()
   
    OUT_DIR = options.output_dir
    OVERWRITE = not options.no_overwrite 
    USE_MODEL = not options.search_mapping 
    
    main()



