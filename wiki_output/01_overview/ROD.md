---
title: "ROD"
---

# ROD

[Draft, need to be checked and edited]

[Edit this section](ROD/edit.md)

## 1\. Access to ROD-test

Go to rancherdev click on dabase service  
container tab --> click on button with three vertical points

view in API   
this url can be used as well: <https://rancherdev.eea.europa.eu/v2-beta/projects/1a78729/containers/1i1225681>

cntrl + F to find password  
database, user, password will be shown on the web page

once we have the data, go back to the container tab in rancher and click again on three vertical points button and execute shell

then run mysql --user=<RodUser> \--password

type the password and you are in

then type use rod3; and you are in the database of rod3

Further information on ROD: [Reporting obligations database](/projects/infrastructure/wiki/Reporting_obligations_database)

## Verification notes

This page is a draft and is visibly incomplete ("Draft, need to be checked and edited"). The instructions reference Rancher v1/v2 and a MySQL CLI — both suggest the content was written for the Reportnet 2 era. The Reportnet 3 ROD integration runs via `rod-service`, a Feign client that reads obligations from the ROD REST API; there is no direct MySQL access in R3. This page should either be rewritten to describe the `rod-service` integration or marked as deprecated.
