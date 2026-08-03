---
title: "Check And Fix Database Errors"
---

# Check And Fix Database Errors

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

## Postgress

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

### Fig Pgpool

You might see an error in the pods regarding pgpool and passwords   
(e.g. dataset does not have a dataflow entry for the pgpool password or sth)

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

#### Manually

  * Go to Kubernetes -> Deployments -> rn3-pg-helm-pgpool -> open **each** pod with exec
  * execute command: **cat /opt/bitnami/pgpool/conf/pool_passwd**
  * We should see entries for postgress, dataflow, testUser, dataset, recordstore and validation (we need to have 6 records)
  * Go to another environment which is working correctly and execute inside a rn3-pghelm-pgpool pod the command **cat /opt/bitnami/pgpool/conf/pool_passwd**
  * Copy everything and set it up to the rn3-pg-helm-pgpool pod that has the issue  

[code]    You can execute cat > /opt/bitnami/pgpool/conf/pool_passwd
    then paste the records
    hit enter
    then Ctrl + Shift + C
    
[/code]




[Edit this section](Check_And_Fix_Database_Errors/edit.md)

#### Use script

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

### Check that databases pods are working correctly

  * Every day someone needs to go to Kubernetes -> Stateful Sets -> rn3-pg-helm-postgresql go to one pod
  * execute **/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh repmgr -f /opt/bitnami/repmgr/conf/repmgr.conf cluster show** and check that:
    1. There is one primary and the rest are stand by
    2. All have status RUNNING
    3. All standby have upstream that points to the primary


  * Execute command **exit**
  * Delete the problematic pod from rn3-pg-helm-postgresql so that it's restarted



[Edit this section](Check_And_Fix_Database_Errors/edit.md)

## MongoDb

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

### Check that mongodb pods are working correctly

  * Go to Kubernetes -> Stateful sets -> mongodb-replicaset -> exec 
  * execute **mongo**
  * execute **rs.status()**
  * Check that there is one master and two secondary and that all secondary are synced to the master



[Edit this section](Check_And_Fix_Database_Errors/edit.md)

#### Secondary pod is not synced to master one

Restart the secondary pod and check again.

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

### Mongo db duplicate records

<https://taskman.eionet.europa.eu/projects/reportnet-3/wiki/Locate_mongo_record_duplicates>

[Edit this section](Check_And_Fix_Database_Errors/edit.md)

### Find new master host and port

  * Go to Kubernetes -> Stateful sets -> mongodb-replicaset -> exec 
  * execute **mongo**
  * execute **rs.status()**
  * Find the primary 
  * Go to kubernetes cli (initial page)
  * execute **kubectl -n reportnet get services**
  * You can see mongo-db-replica-{primary} -> You can get the port from there (Not the host because it's an internal ip)
  * Get the ip from the hosts tab in Rancher or from the url that you use to connect to Consul



[Edit this section](Check_And_Fix_Database_Errors/edit.md)

### Mongo DB cluster desynched

  * In Master mongo host (master status can be seen in rs.status() hosts list)
  * When you open a mongo exec shell in Rancher 
  * Type mongo and hit Enter 
  * Now you are in mongo DB shell. Type rs.status() and enter 
  * **You will get a list of mongo hosts participating in the cluster. Should be 3 of them. If you see 4 and the mongo complains about duplicates then**
  * Type: cfg = rs.conf()
  * If for example the member you want to remove is the second on the rs.status() list then you have to splice (position, number of hosts) = splice(1,1). If the host is the first one its (0,1) 
  * Lets say that the problematic host is the first one. To remove the first host type: cfg.members.splice(0,1)
  * Then apply the change by typing: rs.reconfig(cfg, {force:true})

## Verification notes

**PostgreSQL component names.** The deployment names `rn3-pg-helm-pgpool` (Deployments) and `rn3-pg-helm-postgresql` (StatefulSets) are consistent across this document, `Postgres_daily_backup.md`, and `Postgres_recovery_in_kubernetes.md`. The `pool_passwd` file path `/opt/bitnami/pgpool/conf/pool_passwd` is specific to the Bitnami PgPool image and cannot be verified from Java source, but is consistent with Bitnami's standard paths.

**PgPool expected users.** The document states that `pool_passwd` should contain entries for `postgres, dataflow, testUser, dataset, recordstore, and validation` — six records. The Consul key `config/recordstore/dataset.users` in `Operation_guidelines.md` lists `recordstore,validation,dataset` as the dataset-facing users; the presence of `postgres`, `dataflow`, and `testUser` is plausible for a full cluster but cannot be confirmed from source code.

**repmgr command path.** The path `/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh` and the repmgr command `repmgr -f /opt/bitnami/repmgr/conf/repmgr.conf cluster show` are consistent with `Postgres_recovery_in_kubernetes.md` and reflect the Bitnami PostgreSQL-repmgr image layout.

**MongoDB replica set.** The procedure describes a three-node MongoDB replica set (`mongodb-replicaset` StatefulSet) with one primary and two secondaries. This is consistent with the MongoDB setup documented in `mongodb.md` (three-node replica set). The `rs.status()`, `rs.conf()`, and `rs.reconfig()` commands are standard MongoDB shell commands. The StatefulSet name `mongodb-replicaset` matches the metrics endpoint reference in `Operation_guidelines.md` (`mongo-mongodb-replicaset-0`). The `mongo` shell command used to enter the MongoDB shell has been superseded by `mongosh` in MongoDB 5.0+; if the cluster has been upgraded beyond 4.x this command may not be available.
