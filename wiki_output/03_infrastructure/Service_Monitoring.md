---
title: "Service Monitoring"
---

# System Monitoring

This guide explains how to set up a local environment to monitor Kubernetes-based systems across multiple environments, run cluster health checks, and view results via a browser interface.

[Edit this section](Service_Monitoring/edit.md)

##  Installation Guide

Below there are instructions for both Linux and Windows

[Edit this section](Service_Monitoring/edit.md)

### Prerequisites

  * `kubectl` is installed and configured on your local machine.



[Edit this section](Service_Monitoring/edit.md)

### Installation & Configuration

[Edit this section](Service_Monitoring/edit.md)

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

[Edit this section](Service_Monitoring/edit.md)

### Step 2: Configure `.kube/config` for `01dev` Environment

The `.kube/config` file stores Kubernetes cluster configuration

[Edit this section](Service_Monitoring/edit.md)

##### Windows

  * Navigate to: `C:\Users\{USERNAME}\.kube\` (directory is hidden by default)



[Edit this section](Service_Monitoring/edit.md)

##### Linux/macOS

  * Navigate to: `~/.kube/config`



[Edit this section](Service_Monitoring/edit.md)

##### Edit or merge the configuration

Add the cluster context for `01dev`. Example snippet:
[code] 
    apiVersion: v1
    clusters:
    - cluster:
        server: https://rancher2develop.eea.europa.eu/k8s/clusters/c-m-9pf4z69b
      name: 01dev
    contexts:
    - context:
        cluster: 01dev
        user: 01dev
      name: 01dev
    users:
    - name: 01dev
      user:
        token: <YOUR_ACCESS_TOKEN>
    
[/code]

Ask the DevOps team for the `token`.  
If there are multiple contexts you will have to set `current-context: 01dev`

[Edit this section](Service_Monitoring/edit.md)

### Step 3: Verify Connection

Check connectivity to the `01dev` cluster:
[code] 
    kubectl --context 01dev get nodes
    # or if 01dev is default context
    kubectl get nodes
    
[/code]

You should see a list of cluster nodes

[Edit this section](Service_Monitoring/edit.md)

## Start System Monitor

Now you can port-forward the system monitor service to your local machine:
[code] 
    kubectl --context 01dev port-forward svc/debian-13-linux-pod 8501:8501
    
[/code]

Then open your browser at <http://localhost:8501>

Press **Run Cluster Checks**

## Verification notes

No source code verification applicable — this page is an operational runbook for setting up local `kubectl` access to the `01dev` cluster and port-forwarding a monitoring service; it contains no verifiable claims about Reportnet3 application architecture or behaviour.
