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
        print(wk_dir)
        if os.path.exists(os.path.join(path_to_WD_based_mappings, wd_dir, wk_dir, "FlexibleGH-RF2x-24-bandwidth-RLE-CompressAB")):
            shutil.rmtree(os.path.join(path_to_WD_based_mappings, wd_dir, wk_dir, "FlexibleGH-RF2x-24-bandwidth-RLE-CompressAB"))
        
        for design_dir in os.listdir(os.path.join(path_to_WD_based_mappings, wd_dir, wk_dir)):
            
            rename = False
            if "DSTC" in design_dir:
                pass
            elif "Ampere" in design_dir:
                new_dir_name = "STC-RF2x-24-bandwidth"
                rename = True
            elif "FlexibleGHCompressAB" in design_dir and "RLE" in design_dir:
                new_dir_name = "STC_flexible_dualCompress-RF2x-24-bandwidth-RLE"
                rename = True
            elif "FlexibleGH" in design_dir and "RLE" in design_dir:
                new_dir_name = "STC_flexible-RF2x-24-bandwidth-RLE"
                rename = True
            elif "FlexibleGH" in design_dir:
                new_dir_name = "STC_flexible-RF2x-24-bandwidth"
                rename = True
            elif "TC" in design_dir and "STC" not in design_dir and not "24" in design_dir and "DSTC" not in design_dir:
                new_dir_name = "TC-RF2x-24-bandwidth"
                rename = True
            else:
                rename = False
            
            if rename:
                design_dir_path = os.path.join(path_to_WD_based_mappings, wd_dir, wk_dir, design_dir)
                new_design_dir_path = os.path.join(path_to_WD_based_mappings, wd_dir, wk_dir, new_dir_name)
                print("renmaing: " , design_dir , "to: " , new_dir_name)
                os.rename(design_dir_path, new_design_dir_path)
            
        if wd_dir != "WD-1.0" and \
           not os.path.exists(os.path.join(path_to_WD_based_mappings,  wd_dir , wk_dir, "TC-RF2x-24-bandwidth")): 
            wk_dir_src = wk_dir 
            wk_dir_src = wk_dir_src.replace("WD" + wd, "WD1.0")
            print(wk_dir_src)
            shutil.copytree(os.path.join(path_to_WD_based_mappings, "WD-1.0", wk_dir_src, "TC-RF2x-24-bandwidth"),
                            os.path.join(path_to_WD_based_mappings,  wd_dir , wk_dir, "TC-RF2x-24-bandwidth"))




