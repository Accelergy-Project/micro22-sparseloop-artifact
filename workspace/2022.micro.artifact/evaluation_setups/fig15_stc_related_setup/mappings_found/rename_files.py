import os, inspect, sys, subprocess, yaml, pprint, math, pickle, shutil, signal, math, time, datetime
from copy import deepcopy

this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)
os.chdir(this_directory)

path_to_WD_based_mappings = os.path.join(this_directory, "int8", "resnet50_selected")
for wd_dir in os.listdir(path_to_WD_based_mappings):
    print(wd_dir)
    wd = wd_dir.split('-')[-1]
    
    for wk_dir in os.listdir(os.path.join(path_to_WD_based_mappings, wd_dir)):
        wk_dir_path = os.path.join(path_to_WD_based_mappings, wd_dir,  wk_dir)
        
        if not wk_dir[0]  == "0":
            shutil.rmtree(wk_dir_path)
        
    for wk_dir in os.listdir(os.path.join(path_to_WD_based_mappings, wd_dir)):
        wk_dir_path = os.path.join(path_to_WD_based_mappings, wd_dir,  wk_dir)
        
        new_wk_dir = wk_dir[3:]
        print(wk_dir, new_wk_dir)
        
        
        if "01-" in wk_dir:
            shutil.rmtree(wk_dir_path)
        else:
            new_wk_dir_path = os.path.join(path_to_WD_based_mappings, wd_dir,  new_wk_dir)
            os.rename(wk_dir_path, new_wk_dir_path)

