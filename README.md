# Real-time Speech translation
This repository contains detailed guidance on how to run a distributed real-time speech translation system. It's structured around 3 parts. The first part describes the AI model we are using in our system with guidance on Installation and containerization with docker. The second part describes how to create the kubernetes cluster which will orchestrate our system in a distributed environment. And the last part will help you setup a client-side script to send audio streams to your running worker node.


## Prerequisites

- [ ] OS Installation: 3 ubuntu 20.04 with 32 GB of RAM, 16 cores CPU and 80 GB of harddisk. (These specifications are maximized due to some latency requirements to consider when running the model. Feel free to adjust based on your needs.)
- [ ] Good understanding of docker, kubernetes, linux command line and container orchestration (if you want to use a different tool than kubernetes).
- [ ] (Not mandatory) Recommend to use Ansible to automate the nodes creation and installation on remote servers.


## Part 1. Whisper model modification

In this project we are implementing to our infrastructure an open-source pre-trained model [openai Whisper](https://github.com/openai/whisper). The model can perform "multilingual speech recognition, speech translation, and language identification". We adapted the format to take as input real-time audio streams in chunks and do the transcription. The base repository to refer to for the updates is the following: https://github.com/kordaniel/hy-net-ai/tree/main/node-whisper.

### Containerization of whisper

- [ ] Option 1: The image is publicly available in docker hub: (This step keeps you from containerizing the model yourself)

```console
foo@bar$ docker pull ssquare/group1-netai:1.0.0

```

- [ ] Option 2: If you reproduce the steps to build the image, follow these steps:
Requirements: You should be able to push the image to docker hub, which requires you to have a github account with a ready repository. (Therefore recommended to follow Option 1)

```console
foo@bar$ sudo apt update
foo@bar$ sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

foo@bar$ git clone <this_repo>
foo@bar$ cd <repo_directory>
foo@bar$ cd node-whisper
foo@bar$ docker build . -t whisper:1.0.0
foo@bar$ docker tag whisper:1.0.0 <your_dockerhub_repo>:1.0.0
foo@bar$ docker push <your_dockerhub_repo>:1.0.0
```

## Part 2. Cluster creation

### Cluster initialization

- Make sure to have your 3 VMs up and running in the same local network. (To use ansible for automation you should be able to ssh between the servers from your master node).
- For this project we have a master node and two worker nodes with similar configurations.
- In the control plane (master), install kubernetes and all required dependencies.

 ```console
 foo@bar$ sudo apt-get update
 foo@bar$ sudo apt install kubeadm kubelet kubectl

 ```
- In the workers, installations

```console
foo@bar$ sudo apt install kubeadm kubelet

```

Once the installation completed, we proceed to initialize the cluster and install Pod network to connect the workers to the control plane.

- In the control plane, make sure you are working on your $HOME directory to make files accessible.

```console
foo@bar$ kubeadm init --pod-network-cidr=10.244.0.0/16 >> cluster_initialized.txt

foo@bar$ mkdir .kube
foo@bar$ cp /etc/kubernetes/amin.conf .kube/config
foo@bar$ export KUBECONFIG=.kube/config

foo@bar$ kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml >> pod_network_setup.txt

```
Run the commands with sudo in case of **Permission Denied** issues.
Run the join command and save the output to be used on the worker nodes.

```console
foo@bar$ kubeadm token create --print-join-command

```

- In the workers, run the output of the previous command

After this step your cluster should be correctly initialized.You can run the following command in the control plane to list the available nodes:

```console
foo@bar$ kubectl get nodes -o wide
```

### Creating Deployment of the whisper model

- Once the cluster is up and running, use the whisper-deployment.yaml file in the repo to deploy the model in the worker nodes.
- Feel free to modify the parameters, change number of replicas, ports, labels, etc.

```console
foo@bar$ kubectl apply -f whisper-deployment.yaml
```

- The control plane then deploys your container to the workers nodes with the number of replicas specified in the file.
- For more information run the following commands in the control plane and learn from each of the outputs:

```console
foo@bar$ kubectl get deploy -o wide

foo@bar$ kubectl get events --sort-by=.metadata.creationTimestamp #for debugging purpose

foo@bar$ kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=<worker_node>
```

- To publicly expose the services use the whisper-service.yaml which relies on NodePort to extend our ClusterIP.

```console
foo@bar$ kubectl apply -f whisper-service.yaml
```

## Part 3. Setting up the client

Use the [node-client](node-client/) directory inside the repo. Follow the instructions in it's README to set up the required environment and instructions on how to run the program.

Once you have the requirements installed and the environment set up correctly, modify the the script main.py by changing the HOST and PORT variables, to bind to the worker endpoint given at the end of Part 2.

## Authors and acknowledgment
This work is a collaboration between Daniel Korpela, Amy Sokhna Sidibé & Anas Temouden for the Network-AI course of University of Helsinki.
