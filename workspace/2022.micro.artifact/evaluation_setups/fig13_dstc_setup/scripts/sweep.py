import yaml, inspect, os, sys, subprocess, pprint, shutil
from copy import deepcopy
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

OVERWRITE = True

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)

# paths to important input specs
problem_template_path = os.path.join(this_directory, "..", "input_specs", "prob.yaml")
arch_path = os.path.join(this_directory, "..", "input_specs", "architecture.yaml")
component_path = os.path.join(this_directory, "..", "input_specs", "compound_components.yaml")
mapping_path = os.path.join(this_directory, "..", "input_specs", "Os-mapping.yaml")
sparse_opt_path = os.path.join(this_directory, "..",  "input_specs", "sparse-opt.yaml")



def run_timeloop(job_name, input_dict, base_dir, ert_path, art_path):
    output_dir = os.path.join(base_dir +"/outputs")
   
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        if not OVERWRITE:
            print("Found existing results: ", output_dir)
            return
        else:
            print("Found and overwrite existing results: ", output_dir)

    # reuse generated ERT and ART files
    shutil.copy(ert_path, os.path.join(base_dir, "ERT.yaml"))
    shutil.copy(art_path, os.path.join(base_dir, "ART.yaml"))
    
    input_file_path = os.path.join(base_dir, "aggregated_input.yaml")
    ert_file_path = os.path.join(base_dir, "ERT.yaml")
    art_file_path = os.path.join(base_dir, "ART.yaml")
    logfile_path = os.path.join(output_dir, "timeloop.log")
    
    yaml.dump(input_dict, open(input_file_path, "w"), default_flow_style=False)
    os.chdir(output_dir)
    subprocess_cmd = ["timeloop-model", input_file_path, ert_path, art_path]
    print("\tRunning test: ", job_name)

    p = subprocess.Popen(subprocess_cmd)
    p.communicate(timeout=None) 

def main():
    
    ert_path = os.path.join(this_directory, "..",  "input_specs", "ERT.yaml")
    art_path = os.path.join(this_directory, "..",  "input_specs", "ART.yaml")
    print(ert_path)
    
    # load all yaml input specs
    problem_template = yaml.load(open(problem_template_path), Loader = yaml.SafeLoader)
    arch = yaml.load(open(arch_path), Loader = yaml.SafeLoader)
    components = yaml.load(open(component_path), Loader = yaml.SafeLoader)
    mapping = yaml.load(open(mapping_path), Loader = yaml.SafeLoader)
    sparse_opt = yaml.load(open(sparse_opt_path), Loader = yaml.SafeLoader)
    
    output_base_dir = os.path.join(this_directory, "..", "outputs")
    stats = {}
    
    # go through density combinations
    for A_density in [1.0, 0.9, 0.7, 0.5, 0.3]:
        for B_density in [1.0,  0.4]:
            
            if A_density not in stats:
                stats[A_density] = {}
            
            new_problem = deepcopy(problem_template)

            new_problem["problem"]["instance"]["densities"]["A"]["density"] = A_density
            new_problem["problem"]["instance"]["densities"]["B"]["density"] = B_density

            aggregated_input = {}
            aggregated_input.update(arch)
            aggregated_input.update(new_problem)
            aggregated_input.update(components)
            aggregated_input.update(mapping)
            aggregated_input.update(sparse_opt)
            
            job_name  = "B_" + str(B_density) + "-A_" + str(A_density)
            
            run_timeloop(job_name, aggregated_input, os.path.join(output_base_dir, job_name), ert_path, art_path)
            
if __name__ == "__main__":
    main()
        
