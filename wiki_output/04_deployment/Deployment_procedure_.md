---
title: "Deployment procedure"
---

# Deployment procedure

  * Build your reportnet3 branch in <https://ci.eionet.europa.eu/view/Github/job/reportnet3-main/job/eea.reportnet3/> by entering the branch and clicking "Build Now" 
  * If new consul properties need to be added or any other changes need to be done in deployment.yaml files etc, create a new branch from main <https://github.com/eea/rn3-deploy-scripts> and apply the new changes.
  * Go to <https://ci.eionet.europa.eu/job/reportnet3-main/job/rn3-deploy-scripts/job/main/>
  * Click "Build with parameters" 
  * In Env, select the environment where you want to deploy your changes
  * In Brn, select the branch you created in step 1 or else select main (master is used for prod)
  * In Ver, write the version that appears in parent-poms -> parent -> pom.xml of your reportnet3 branch that you want to deploy
  * Click build



Once you have tested your changes and the branch that you created in step 1 works, rebase your branch from main and merge it to main.

## Verification notes

The CI URL referenced in step 1 (`https://ci.eionet.europa.eu/view/Github/job/reportnet3-main/job/eea.reportnet3/`) and the deploy-scripts URL in step 3 (`https://ci.eionet.europa.eu/job/reportnet3-main/job/rn3-deploy-scripts/job/main/`) cannot be verified from source code alone, as they refer to Jenkins infrastructure rather than the repository. The `rn3-deploy-scripts` repository (`https://github.com/eea/rn3-deploy-scripts`) is a separate repository not present in the local clone.

The Jenkinsfile.eea at the root of `eea.reportnet3` does not contain stages named after the build parameters described in this wiki (Env, Brn, Ver). Those parameters belong to the `rn3-deploy-scripts` pipeline, which is separate. The Jenkinsfile.eea builds and pushes Docker images to Docker Hub for all services; the deployment step (applying the correct version to a Kubernetes namespace) is handled by the separate deploy-scripts job.

Step 12 notes "master is used for prod" as the Brn value. The confirmed production branch in the repository is `MasterOneVersion`, not `master`. The note may refer to the default branch of the `rn3-deploy-scripts` repository rather than the `eea.reportnet3` source branch; this is ambiguous and could mislead a reader.
