# HY-Net-Ai
Template for a group project

## Repository
This repository contains the [Oakestra](https://github.com/oakestra/oakestra) framework as a submodule. Submodules needs to be cloned and initialized when cloning the repository, which can be achieved by following the following instructions:

### Clone
```console
foo@bar:$ git clone --recurse-submodules git@github.com:kordaniel/hy-net-ai.git
```

Pull new changes including commits from submodules:
### Pull new commits including submodules
```console
foo@bar:$ git pull --recurse-submodules
```

### Pull submodule new commits
```console
foo@bar:$ cd oakestra
foo@bar: oakestra$ git submodule update --remote --recursive --init
```

## Run Oakestra
First set the required environment variables. This can be done by sourcing the `envs-set` file. Do note that it might not work on all machines, depending on the network stack and how it's configured.
```console
foo@bar:$ source envs-set
foo@bar:$ cd oakestra
foo@bar:oakestra$ docker compose -f run-a-cluster/1-DOC.yaml -f run-a-cluster/override-alpha-versions.yaml up
```
After stopping the system you can clear the environment variables with
```console
foo@bar:$ source envs-unset
```
