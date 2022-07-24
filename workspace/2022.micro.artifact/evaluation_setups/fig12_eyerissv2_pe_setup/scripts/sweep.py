import yaml, inspect, os, sys, subprocess, pprint, shutil, argparse
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt

OVERWRITE = True

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)

# setup directory and file paths
curr_dir_path = os.path.dirname(os.path.realpath(__file__)) 
hw_dir_path = os.path.join(curr_dir_path, '..', 'hardware-specs')
config_dir_path = os.path.join(hw_dir_path, 'configurations') 
mapping_dir_path = os.path.join(curr_dir_path, '..', 'mappings')
wl_dir_path = os.path.join(curr_dir_path, '..', 'workload')
rt_dir_path = os.path.join(curr_dir_path, '..', 'ert_art')

arch_file_path = os.path.join(hw_dir_path, 'designs', 'arch.yaml')
pe_ert_file_path = os.path.join(rt_dir_path, 'ERT.yaml')
pe_art_file_path = os.path.join(rt_dir_path, 'ART.yaml')


def main(design_points_file_path, base_output_dir, max_layers):

    timeloop_exe = "timeloop-model"
    print("running design_points_file_path ", design_points_file_path)

    abs_design_points_file_path = os.path.abspath(design_points_file_path)
    design_points = yaml.load(open(abs_design_points_file_path), Loader = yaml.SafeLoader)

    cur_num_layer = 0
    for dpt in design_points:
        wl_name = dpt["workloadID"]
        layer_name = dpt["layerID"]
        config_name = dpt["configID"]
        density_name = dpt["densityID"]
       
        output_dir = os.path.join(base_output_dir,  layer_name, density_name)
        if ( not os.path.exists(output_dir)):
            os.makedirs(output_dir, exist_ok = True)
        
        print("output directory: %s ", output_dir)

        wl_spec_path       = os.path.join(wl_dir_path, wl_name, density_name, layer_name + '.yaml')
        config_spec_path   = os.path.join(config_dir_path, config_name + '.yaml')
        mapping_spec_path  = os.path.join(mapping_dir_path, wl_name, layer_name + '-perfect_factor.yaml')
        
        # process absolute path for data masks
        if "actual_data" == density_name:
            wl_spec = yaml.load(open(wl_spec_path), Loader = yaml.SafeLoader)
            iact_datamasks_path = os.path.join(this_directory, "..", "workload", wl_name, density_name, "actual_data_masks", layer_name + "_iacts.txt")  
            wl_spec["problem"]["instance"]["densities"]["Inputs"]["data_file_path"] = iact_datamasks_path
            
            weights_datamasks_path = os.path.join(this_directory, "..", "workload", wl_name, density_name, "actual_data_masks", layer_name + "_weights.txt")  
            wl_spec["problem"]["instance"]["densities"]["Weights"]["data_file_path"] = weights_datamasks_path

            with open(wl_spec_path, 'w') as f:
                yaml.dump(wl_spec, f)

        # create and perform operations at the output directory    
        if (not os.path.exists(os.path.join(output_dir, "output"))):
            os.makedirs(os.path.join(output_dir, "output"), exist_ok = True)
        os.chdir(os.path.join(output_dir, "output"))
        
        # collect all input files
        lst_of_input_files = []
        lst_of_input_files.append(wl_spec_path)
        lst_of_input_files.append(arch_file_path)
        lst_of_input_files.append(config_spec_path)
        lst_of_input_files.append(pe_ert_file_path)
        lst_of_input_files.append(pe_art_file_path)
        lst_of_input_files.append(mapping_spec_path)


        logfile_path = os.path.join(output_dir, "timeloop.log")
        subprocess_cmd = [timeloop_exe, *lst_of_input_files]
       
        outfile = open(logfile_path, "w")    
        status = subprocess.call(subprocess_cmd) 
        outfile.close()
           
        os.chdir(curr_dir_path)
        
        # reset path for data masks
        if "actual_data" == density_name:
            wl_spec = yaml.load(open(wl_spec_path), Loader = yaml.SafeLoader)
            iact_datamasks_path = os.path.join("actual_data_masks", layer_name + "_iacts.txt")  
            wl_spec["problem"]["instance"]["densities"]["Inputs"]["data_file_path"] = iact_datamasks_path
            
            weights_datamasks_path = os.path.join("actual_data_masks", layer_name + "_weights.txt")  
            wl_spec["problem"]["instance"]["densities"]["Weights"]["data_file_path"] = weights_datamasks_path

            with open(wl_spec_path, 'w') as f:
                yaml.dump(wl_spec, f)
        cur_num_layer = cur_num_layer + 1
        
        if cur_num_layer == max_layers:
            break

if __name__ == "__main__":


    parser = argparse.ArgumentParser(""" sweep various mobilenet layers with different density distribution options """)
    parser.add_argument('--max_layers', type=int, default=8, help='max number of layers to run')
    parser.add_argument('--include_actual', action="store_true", help="explore mappings instead of use the mappings already found")
    options = parser.parse_args()

    if options.include_actual:
        design_points_file = "mobilenet0.5-sparse_with_actual.yaml"
        max_layers = options.max_layers * 2 # include a pair for each layer: uniform and actual
        base_dir_name = "uniform_actual"
    else:
        design_points_file = "mobilenet0.5-sparse.yaml"
        max_layers = options.max_layers 
        base_dir_name = "uniform_only"
    
    design_points_file_path = os.path.join(this_directory, "..", "design-points", design_points_file)
    base_output_dir = os.path.join(this_directory, "..", "outputs", base_dir_name)
    main(design_points_file_path, base_output_dir, max_layers)

    
