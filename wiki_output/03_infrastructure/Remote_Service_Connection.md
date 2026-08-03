---
title: "Remote Service Connection"
---

# Remote Service Connection

This guide explains how to set up port-forward to connect to services like Mongo or Consul.

[Edit this section](Remote_Service_Connection/edit.md)

##  Installation Guide

Below there are instructions for both Linux and Windows

[Edit this section](Remote_Service_Connection/edit.md)

### Prerequisites

  * `kubectl` is installed and configured on your local machine.



[Edit this section](Remote_Service_Connection/edit.md)

### Installation & Configuration

[Edit this section](Remote_Service_Connection/edit.md)

#### Step 1: Install `kubectl` (skip if installed)

  * Windows: Use [kubectl installation guide](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows)
  * Linux/macOS: Use the [official `kubectl` binary](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-kubectl-binary-with-curl-on-linux) **OR** use the [native package manager](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/#install-using-native-package-management)



Verify installation:
[code] 
    kubectl version --client
    
[/code]

Example output:
[code] 
    $ kubectl version --client
    Client Version: v1.33.3
    Kustomize Version: v5.6.0
    
[/code]

[Edit this section](Remote_Service_Connection/edit.md)

### Step 2: Configure `.kube/config` for the environment, e.g: `01dev` Environment

The `.kube/config` file stores Kubernetes cluster configuration

[Edit this section](Remote_Service_Connection/edit.md)

##### Windows

  * Navigate to: `C:\Users\{USERNAME}\.kube\` (directory is hidden by default)



[Edit this section](Remote_Service_Connection/edit.md)

##### Linux/macOS

  * Navigate to: `~/.kube/config`



[Edit this section](Remote_Service_Connection/edit.md)

##### Edit or merge the configuration

Add the cluster context for `01dev`. Example snippet:
[code] 
    apiVersion: v1
    clusters:
    - cluster:
        server: https://kvm-rancher-s4.eea.europa.eu/r/projects/1a7026/kubernetes:6443
      name: RN3sandbox (Staging)
    contexts:
    - context:
        cluster: RN3sandbox (Staging)
        user: RN3sandbox (Staging)
      name: sandbox
    users:
    - name: RN3sandbox (Staging)
      user:
        token: <YOUR_ACCESS_TOKEN>
    
[/code]

Ask the DevOps team for the `token`.

[Edit this section](Remote_Service_Connection/edit.md)

### Step 3: Verify Connection

Check connectivity to the `01dev` cluster:
[code] 
    kubectl --context sandbox get pods
    
[/code]

You should see a list of pods.

[Edit this section](Remote_Service_Connection/edit.md)

## Connect to a remote service

Now you can port-forward the service:
[code] 
    kubectl --context sandbox port-forward svc/mongo-mongodb-replicaset 27010:27017
    
[/code]

[Edit this section](Remote_Service_Connection/edit.md)

## Service Name per Environment

Environment  | Mongo  | Consul UI   
---|---|---  
AWS NKP Prod |  mongo-mongodb-replicaset  |  consul-ui  
RN3prod |  mongo-mongodb-replicaset  |  consul-ui  
RN3transport |  mongo-mongodb-replicaset  |  consul-ui  
RN3sandbox |  mongo-mongodb-replicaset  |  consul-ui  
RN3test |  mongo-mongodb-replicaset  |  consul-ui  
Rancher2Develop |  rn3-mongo-mongodb-headless  |  consul-ui

## Verification notes

No source code verification applicable — this page is an operational runbook for setting up `kubectl` port-forwards to remote services; it contains no verifiable claims about Reportnet3 application architecture or behaviour. The service names listed in the table (`mongo-mongodb-replicaset`, `consul-ui`) are consistent with the Helm release names used in `Reportnet_Deployment.md` and `AWSNKP_Service_Access.md`.
