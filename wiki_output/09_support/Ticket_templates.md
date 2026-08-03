---
title: "Ticket templates"
---

# Ticket templates

When we write comments in a ticket we need to provide some useful information.

If there are code/config changes we can use the following template:

**Deployed on** |  all systems in which the branch has been merged to and deployed   
---|---  
**Branch name** |  branch that contains the code   
**Services affected** |  services that need to be restarted   
**Pull request** |  link to pull request if exists   
**Consul properties** |  consul properties that need to be added/modified with their values. _If the value is sensitive info we only add the consul variable name._  
**Database changes** |  the name of the sql script that was added in the database folder in reportnet3 project   
**POM changes** |  any pom changes that were needed   
  
If something is not needed for the above e.g. there are no consul changes we can leave the second column empty.

We also need to provide a short explanation of the issue and how it was fixed.  
We can also add logs, urls for the dataflows and steps to reproduce this issue (the last one is optional)

After we add this comment we can edit the description and at the end of it, add the url pointing to this specific comment.

## Verification notes

No source code verification applicable — organisational/process content.

The template fields align correctly with the deployment model visible in the source. "Services affected" maps to the Spring Boot microservices (`communication`, `ums`, `dataset-service`, etc.). "Consul properties" correctly identifies Consul KV as the configuration mechanism — all services pull configuration from Consul at startup. "Database changes" correctly identifies the SQL script convention used in the `database` folder of the repository. "Pull request" and "Branch name" match the Git-based development workflow evident in the repository structure. No inaccuracies identified.
