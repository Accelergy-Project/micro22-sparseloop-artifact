import csv, inspect, yaml, sys, os, pickle, pprint, yaml, argparse
from copy import deepcopy


this_file_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
this_directory = os.path.dirname(this_file_path)

sys.path.append(os.path.join(this_directory, "..", "..", "utils"))
from parse_timeloop_output import parse_timeloop_stats

def collect_data_in_dirs(directories, stats_prefix, keys_to_include):
    summary = {}
    for d in directories:
        # print("INFO: looking for stats file in :", d)
        if not os.path.isdir(d):
            print("WARN: provided path is not directory: ", d)
            raw_stats_path = os.path.join(d)
            dirname = os.path.dirname(d).split(os.sep)[-1]
        else:
            raw_stats_path = os.path.join(d, "output", stats_prefix + ".map+stats.xml")
            if not os.path.exists(raw_stats_path):
                #print("WARN: cannot find stats file in provided directory: ", raw_stats_path)
                raw_stats_path = os.path.join(os.path.join(d,"output"), stats_prefix + ".map+stats.xml")
                alternative_prefix = "timeloop-mapper" if stats_prefix == "timeloop-model" else "timeloop-model"
                raw_stats_path = os.path.join(d, "output",  alternative_prefix + ".map+stats.xml")
            
            dirname = os.path.dirname(raw_stats_path).split(os.sep)[-2] 
        
        if not os.path.exists(raw_stats_path):
            print("ERROR: cannot find any stats file in provided directory: ", raw_stats_path)
            exit(1)
            continue
        
        file_stats = parse_timeloop_stats(raw_stats_path)
        if keys_to_include[0] == 'all':
            summary[dirname] = file_stats
        else:
            useful_stats = {}
            for key in keys_to_include:
                useful_stats[key] = deepcopy(file_stats[key])
            summary[dirname] = useful_stats
    return summary

def normalize(baseline_name, summary):
    norm_to_key = "none"
    for key in summary.keys():
        if baseline_name == key:
            norm_to_key = key

    if norm_to_key != "none":
        #print("INFO: normalizing to ", norm_to_key)
        pass
    else:
        print("Warn: cannot find the design to norm to: ", baseline_name)
        return summary
    
    normalized_summary = {}
    for run_key, run_stats in summary.items():
        normalized_summary[run_key] = {}
        for stat_name, stat_entry in run_stats.items():
            run_stats_type = type(stat_entry)
            if (run_stats_type == dict or run_stats_type == list):
                print("Warn: cannot normalize dictionary or list stats: ", run_key, ": ", stat_name)
                normalized_summary[run_key][stat_name] = deepcopy(stat_entry)
                continue
            normalized_stat_entry = stat_entry/summary[norm_to_key][stat_name]
            normalized_summary[run_key][stat_name] = normalized_stat_entry
    return normalized_summary

def top(directories, stats_prefix, include, norm_to):
    
    summary = collect_data_in_dirs(directories, stats_prefix, include)
    if norm_to != "none":
        summary = normalize(norm_to, summary)
    #pprint.pprint(summary)
    return summary


def main():
    parser = argparse.ArgumentParser( description='A simple tool for generating pickle files from directories of timeloop outputs.')
    parser.add_argument('dirs', nargs='*', default=[], type=str,
                        help='raw parsed pkl output file')
    parser.add_argument('--stats_prefix', type=str, default='timeloop-mapper')
    parser.add_argument('--include', type=str, nargs='+', default=['all'], 
                        help='set of stats keys to include, default to all')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose prints')
    parser.add_argument('--norm_to', type=str, default='none', 
                        help='normalize all output to a specific output')
    parser.add_argument('-o', '--outname', default='component_break_down', type=str,
                        help='output file name')
    args = parser.parse_args()
    
    summary = top(args.dirs, args.stats_prefix, args.include, args.norm_to)   
    pickle.dump(summary, open(args.outname +".pkl", "wb"))
    if args.verbose:
        pprint.pprint(summary)
    print("INFO: component breakdown dumped at: ", args.outname +'.pkl')

if __name__ == '__main__':
    main()
