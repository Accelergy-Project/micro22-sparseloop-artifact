

# run sparse cases
for d in 0.01 0.02 0.04 0.08 0.1 0.2 0.4 0.8 
do
  prob_file_name="spmspm.prob.${d}.yaml"
  for sparse_setup in  "coordinate_list" "bitmask"  
  do
    out_dir_name="output_${d}_${sparse_setup}"
    if [[ ! -d ../outputs/${out_dir_name} ]]
    then
      mkdir ../outputs/${out_dir_name}
    fi
    timeloop-mapper ../arch/*.yaml ../dataflow/*.yaml ../sparse-opt/${sparse_setup}.yaml  ../mapper/*.yaml  ../workload/${prob_file_name} ../ert_art/*.yaml -o ../outputs/${out_dir_name}/
  done
done


