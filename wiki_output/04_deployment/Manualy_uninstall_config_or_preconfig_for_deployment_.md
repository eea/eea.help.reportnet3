---
title: "Manualy uninstall config or preconfig for deployment"
---

# Manualy uninstall config or preconfig for deployment

If the deployment fails while trying to uninstall config or preconfig for a service, we should manually uninstall it and build with parameters again. We do the following:

1\. In jenkins build console output we find the error that shows in what step jenkins failed e.g.  

[code]
    + helm uninstall application-config -n reportnet --kubeconfig=****
    Error: Kubernetes cluster unreachable: unable to parse the server version: unexpected end of JSON input
    
[/code]

  
2\. In our local file .kube/config we paste the rancher configuration for the environment that the deployment failed   
3\. We enter project rn3-deploy-scripts and in helm directory we run the uninstall command that failed in jenkins using the path for our local kube config file  
e.g. helm uninstall application-config -n reportnet --kubeconfig=/yourPath/.kube/config  
3\. In jenkins <https://ci.eionet.europa.eu/job/reportnet/job/rn3-deploy-scripts> we run again build with parameters

## Verification notes

The procedure references the `rn3-deploy-scripts` repository and its `helm/` directory, which is a separate repository not present in the local clone and therefore cannot be fully verified. The Helm release names `application-config` and the Kubernetes namespace `reportnet` cannot be confirmed from the `eea.reportnet3` source alone.

The Jenkins URL given here (`https://ci.eionet.europa.eu/job/reportnet/job/rn3-deploy-scripts`) differs from the URL given in `Deployment_procedure_.md` (`https://ci.eionet.europa.eu/job/reportnet3-main/job/rn3-deploy-scripts/job/main/`). One of these is likely outdated; the path structure suggests the `reportnet3-main` form is the more recent one.

The described error pattern (`Kubernetes cluster unreachable: unable to parse the server version`) is an infrastructure-level Kubernetes connectivity issue, not a code issue. The step numbers contain a duplication: both the second and third steps are numbered "3". This is a minor editorial error in the original document.
