---
title: "Access containers with kubectl"
---

# Access containers with kubectl

The usual way to access a container running in Kubernetes is through Rancher, but it is also possible to get access from the terminal.

To do so, here are the steps: 

  1. Install kubectl (<https://kubernetes.io/docs/tasks/tools/#kubectl>) on your local machine.
  2. Create a kube config file that looks like this (this one is for Prod env, make the necessary changes for the env you need to access)  

[code]    apiVersion: v1
    kind: Config
    clusters:
    - cluster:
        api-version: v1
        server: https://kvm-rancher-s2.eea.europa.eu/r/projects/1a4420/kubernetes:6443
      name: "RN3Prod" 
    contexts:
    - context:
        cluster: "RN3Prod" 
        user: "RN3Prod" 
      name: "RN3Prod" 
    current-context: "RN3Prod" 
    users:
    - name: "RN3Prod" 
      user:
        token: "<reducted - ask your team to get you one>" 
    
[/code]

  3. List all the active containers in the pod using   

[code]    kubectl get pod --kubeconfig=<path to config file>/config -n reportnet
    
[/code]

  
The output will look similar to this:   

[code]    NAME                                                          READY   STATUS    RESTARTS   AGE
    api-gateway-577d7bf898-58qbd                                  1/1     Running   0          67d
    api-gateway-577d7bf898-ff9p4                                  1/1     Running   0          67d
    bootstrap-kafka-0                                             1/1     Running   0          376d
    bootstrap-kafka-1                                             1/1     Running   0          3d
    bootstrap-kafka-2                                             1/1     Running   0          522d
    bootstrap-kafka-exporter-584d5f59d-jrktv                      1/1     Running   0          223d
    citus-datasets-manager-bcc6878f8-sfvfr                        1/1     Running   0          3d
    citus-metrics-prometheus-postgres-exporter-6c85946b86-mjmtt   1/1     Running   0          466d
    collaboration-6b6b677b74-64kr8                                1/1     Running   0          67d
    communication-56b7c77646-wzmtc                                1/1     Running   0          67d
    consul-0                                                      1/1     Running   1          557d
    consul-1                                                      1/1     Running   4          377d
    consul-2                                                      1/1     Running   1          557d
    dataflow-54878b6db7-98k2x                                     1/1     Running   1          67d
    dataflow-54878b6db7-j6hzr                                     1/1     Running   1          67d
    dataflow-54878b6db7-krrbh                                     1/1     Running   0          3d
    dataflow-54878b6db7-lhwkr                                     1/1     Running   0          67d
    dataset-5bd7ff757f-646vt                                      1/1     Running   0          5d20h
    dataset-5bd7ff757f-hbfmq                                      1/1     Running   0          5d20h
    ...
    
[/code]



  1. Select the container you need to access, _**i.e. dataset-5bd7ff757f-646vt**_ and execute the following command  

[code]    kubectl --kubeconfig=<path to config file>/config -n reportnet exec -it dataset-5bd7ff757f-646vt -- ./bin/sh
    
[/code]

## Verification notes

No source code verification applicable — operational runbook. The namespace `-n reportnet` and the Rancher API server URL (`kvm-rancher-s2.eea.europa.eu`) and project ID (`1a4420`) should be verified against the current cluster configuration, as these are environment-specific values that may have changed since this runbook was written. Pod name hashes (e.g. `dataset-5bd7ff757f-646vt`) are illustrative and will differ in practice. The shell path `./bin/sh` is non-standard; most containers use `/bin/sh` or `/bin/bash` — if the command fails, try `-- /bin/sh` instead.
