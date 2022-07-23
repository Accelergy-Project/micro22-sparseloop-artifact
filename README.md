# MICRO22 Sparseloop Artifact

This repository provides the evaluation setups for MICRO22 artifact evaluation for the paper *Sparseloop: An Analytical Modeling Approach to Sparse Tensor Accelerators*. We provide a docker environment and a jupyter notebook for the artifect evlauation. 

## Perform artifact evaluation

### Clone repo

```
git clone git@github.com:nellie-wu/micro22-sparseloop-artifact.git
```

### Using Docker

- Make a copy of the provided template docker compose file: `cp docker-compose.yaml.template docker-compose.yaml`
- Examine the instructions in `docker-compose.yaml` to setup the docker correctly, e.g., setup the correct `UID` and `GID`.
- Pull the newest docker image: `docker-compose pull`
- Run docker: `docker-compose up`. You should see the docker being setup.
- This docker uses Jupyter notebooks, and you will see an URL once the docker is up. Please copy and paste the 127.0.0.1 URL
to a web browser of your choice to access the workspace. 
- If the webpage does not work, please try the tourble shooting notes in `docker-compose.yaml`.

### Running Experiments

We provide a jupyter notebook for the experiments.  Please navigate to `workspace/2022.micro.artifact/notebook` and follow the instructions in the notebook to run the experiments. 

For each experiment, we give a ***very conservative estiamtion of how long the sweeping will take***. The input specifications and related scripts can be found in workspace/2022.micro.artifact/evaluation_setups. The easiest way to validate the outputs is to compare the generated figure/table to the figure/table in the paper, but we do provide a `ref_outputs` folder for each evaluation for more detailed comparison of results if necessary.
