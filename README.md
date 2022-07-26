# MICRO22 Sparseloop Artifact

This repository provides the evaluation setups for MICRO22 artifact evaluation for the paper *Sparseloop: An Analytical Modeling Approach to Sparse Tensor Accelerators*. We provide a docker environment and a jupyter notebook for the artifect evlauation. Please contact nelliewu@mit.edu if there are any questions.

## System requirement
---------------------
- Please install [docker app](https://www.docker.com/products/docker-desktop/)

## Perform artifact evaluation

### **Recursively** clone repo and prepare your docker compose

```
git clone --recurse-submodules git@github.com:nellie-wu/micro22-sparseloop-artifact.git
cd <cloned repo>
ls docker/
```

You should see the subdirectories in `docker/` populated with actual source code instead of submodule pointers.



### Step 0: Prepare your docker compose
-------------------------

- Create a docker compose file by making a copy of the docker compose tempalte file `cp docker-compose.yaml.template docker-compose.yaml` 
- Examine the instructions in `docker-compose.yaml` to setup the docker correctly, i.e., setup the correct `UID` and `GID`.


### Step 1: Get the docker
---------------------

We provide two options for obtaining the docker image. Please choose one of the methods listed below.

#### Option 1. Pull built image from docker hub
- We provide a pre-built image on dockerhub
  ```
  docker-compose pull
  ```
#### Option 2. Build docker image from source
  
- Build the timeloop-accelergy infrastructure docker
  ```
  cd docker/accelergy-timeloop-infrastructure
  make
  ```
  
- Build the pytorch docker (which uses the timeloop-accelergy infrastructure as a basis)
  ```
  cd ../timeloop-accelergy-pytorch
  make
  ```

To check if the image is obtained successfully, please do `docker image ls` and you should see `mitdlh/timeloop-accelergy-pytorch` with a tag name `micro22-artifact` listed. 

### Step 2: Start the docker
--------------------

- Run `docker-compose up`. You should see the docker being setup.
- This docker uses Jupyter notebooks, and you will see an URL once the docker is up. Please copy and paste the `127.0.0.1 URL`
to a web browser of your choice to access the workspace. 
- If the webpage does not work, please try the tourble shooting notes in `docker-compose.yaml`.

### Step 3: Run experiments in the docker
--------------------

We provide a jupyter notebook for the experiments.  Please navigate to `workspace/2022.micro.artifact/notebook` to run the experiments. Each cell in the notebook provides the background, instructions, and commands to run each evaluation with provided scripts.

For each experiment, we give a ***very conservative estiamtion of how long the sweeping will take***. The input specifications and related scripts can be found in `workspace/2022.micro.artifact/evaluation_setups`. The easiest way to validate the outputs is to compare the generated figure/table to the figure/table in the paper, but we do provide a `ref_outputs` folder for each evaluation for more detailed comparison of results if necessary.
