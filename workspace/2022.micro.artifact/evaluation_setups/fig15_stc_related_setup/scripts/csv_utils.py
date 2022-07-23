import csv, inspect, yaml, pprint
def generate_column_names(summary):

    column_names = [" "]
    example_layer_name = list(summary.keys())[0]
    for example_layer, stats in summary.items():
        layer_stat_keys = sorted(stats)
        for key in layer_stat_keys:
            if key not in column_names:
                column_names.append(key)
    column_names = sorted(column_names)
    
    #print("column names: ", column_names)
    return column_names

def process_and_dump_limited_bw_stats(summary, csv_filepath, per_layer=True):
    
    with open(csv_filepath, 'a') as csv_file:   
       
        if not per_layer:
            processed_summary = {"all layers": summary}
        else:
            processed_summary = summary
        
        column_names = generate_column_names(processed_summary)     
        csv_dict_writer = csv.DictWriter(csv_file, fieldnames = column_names)
        
        for layer_name, layer_stats in processed_summary.items():
            # print("INFO: processing csv stats for ", layer_name)
            csv_file.write("\n")
            csv_file.write(layer_name + "\n")
            speedup_dict = {" ": "speedup"}
            energy_dict = {" ": "energy"}
            cycles_dict = {" ": "cycles"}
            edp_dict = {" ": "edp"}
            
            csv_dict_writer.writeheader()
            for entry_name, entry_stats in layer_stats.items():
                # speedup_dict[entry_name] = round(1/entry_stats["cycles"], 4)
                energy_dict[entry_name] = entry_stats["energy_pJ"]
                cycles_dict[entry_name] = entry_stats["cycles"]
                if "edp" in entry_stats:
                    edp_dict[entry_name] = entry_stats["edp"]
                else:
                    edp_dict[entry_name] = cycles_dict[entry_name] * energy_dict[entry_name]
            # csv_dict_writer.writerow(speedup_dict)
            csv_dict_writer.writerow(energy_dict)
            csv_dict_writer.writerow(cycles_dict)
            csv_dict_writer.writerow(edp_dict)
    

def process_and_dump_unlimited_bw_stats(summary, csv_filepath):

    column_names = generate_column_names(summary) 
    with open(csv_filepath, 'a') as csv_file:   
        csv_dict_writer = csv.DictWriter(csv_file, fieldnames = column_names)
        for layer_name, layer_stats in summary.items():
            # print("INFO: processing csv stats for ", layer_name)
            csv_file.write("\n")
            csv_file.write(layer_name + "\n")
            speedup_dict = {" ": "speedup"}
            energy_dict = {" ": "energy"}
            cycles_dict = {" ": "cycles"}
            csv_dict_writer.writeheader()
            per_storage_bandwidth_stats = {}
            dataspace_names = gemm_dataspace_names if PROBLEM_SHAPE == "gemm" else dnn_dataspace_names
            for storage_name in architecture_storage_names:
                per_storage_bandwidth_stats[storage_name] = {}
                for dspace_name in dataspace_names:
                    per_storage_bandwidth_stats[storage_name][dspace_name] = {}
            
            for entry_name, entry_stats in layer_stats.items():
                speedup_dict[entry_name] = round(1/entry_stats["cycles"], 4)
                energy_dict[entry_name] = entry_stats["energy_pJ"] 
                cycles_dict[entry_name] = entry_stats["cycles"]
                
                bandwidth_and_cycles_stats = deepcopy(entry_stats["bandwidth_and_cycles"])
                for storage_name in architecture_storage_names:
                    if storage_name in bandwidth_and_cycles_stats:
                        storage_stats = bandwidth_and_cycles_stats[storage_name]
                        for dspace_idx in range(len(dataspace_names)):
                            total_bandwidth = storage_stats['read_bandwidth'][dspace_idx] + \
                            storage_stats["write_bandwidth"][dspace_idx]
                            dspace_name = dataspace_names[dspace_idx]
                            per_storage_bandwidth_stats[storage_name][dspace_name][entry_name] = total_bandwidth 
           
            csv_dict_writer.writerow(speedup_dict)
            csv_dict_writer.writerow(energy_dict)

            for storage_name in architecture_storage_names:
                if storage_name in per_storage_bandwidth_stats:
                    storage_bw_stats = per_storage_bandwidth_stats[storage_name]
                    sep = "\n" +  storage_name + " bandwidth requirement\n"
                    csv_file.write(sep)                    
                    csv_file.write(layer_name + "/n") # for the ease of plotting
                    csv_dict_writer.writeheader()
                    row_dict = {}
                    for dspace_name in dataspace_names:
                        row_dict[" "] = dspace_name
                        for entry_name in storage_bw_stats[dspace_name].keys():
                            row_dict[entry_name] = storage_bw_stats[dspace_name][entry_name]
                            
                        csv_dict_writer.writerow(row_dict)    


def load_csv_into_dict(csv_path, header_row, end_row):
    
    dict_from_csv = {}

    with open(csv_path, mode='r') as fcsv:
        reader = csv.reader(fcsv)
        rows = []
        for row in reader:
            rows.append(row)
        headers = rows[header_row][1:]
        
        for i in range(1, end_row - header_row + 1):
            row = rows[header_row + i]
            row_type = row[0]
            dict_from_csv[row_type] = {}
            for hw_setup_idx in range(len(headers)):
                dict_from_csv[row_type][headers[hw_setup_idx]] = float(row[hw_setup_idx + 1])

    pprint.pprint(dict_from_csv)
    
    return dict_from_csv

            

def load_csv_into_dict_WD_based(csv_path):
    
    dict_from_csv = {}

    with open(csv_path, mode='r') as fcsv:
        reader = csv.reader(fcsv)
        rows = []
        for row in reader:
            rows.append(row)
        
        density_degree = -1
        next_row_is_header = False
        for row in rows:
            if len(row) == 0:
                continue
            if "WD-" in row[0]:
                # detect a new density degree, create a new entry in dict
                density_degree = row[0]
                dict_from_csv[density_degree] = {}
                next_row_is_header = True
            else:
                assert(density_degree != -1)
                if (next_row_is_header):
                    headers = row[1:]
                    next_row_is_header = False
                else:
                    stat_type = row[0]
                    dict_from_csv[density_degree][stat_type] = {}
                    for hw_setup_idx in range(len(headers)):
                        dict_from_csv[density_degree][stat_type][headers[hw_setup_idx]] = float(row[hw_setup_idx + 1])

    #pprint.pprint(dict_from_csv)
    
    return dict_from_csv
