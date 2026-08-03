---
title: "BackupRestore HotSwitch proposed"
---

# BackupRestore HotSwitch proposed

This is a proposed plan for Hot-Fixing a service using a full database replacement restore.

[Edit this section](BackupRestore_HotSwitch_proposed_/edit.md)

## Brief outlook

Risk factors that can extend backup and restore time: 

  * Database size 
  * Number of records per table 
  * Database lock during backup 
  * Needs the database server running

Target databases: 
  * Keycloak 
  * Orchestrator_db (?) 
  * Metabase (?)

When to use: 
  * Case of corrupted DB 
  * Case of upgrade errors
  * Case of data migration



[Edit this section](BackupRestore_HotSwitch_proposed_/edit.md)

## Example case

Need to recover keycloak from an accidental database change command.

[Edit this section](BackupRestore_HotSwitch_proposed_/edit.md)

### Recurring every day

Login to the database master pod   

[code]
    mkdir -p /bitnami/postgresql/bck_25042024
    pg_dump -U postgres -Fc keycloak > /bitnami/postgresql/bck_25042024/keycloak_ori.dmp
    
[/code]

bck_25042024 is the bck_{DDMMYYY} new directory every day in the /bitnami/postgresql/ root folder   
The folder is persisted in PV thus always available and retained through restarts.   
Also daily snapshots in filesystem level exists for this folder.

Example of Kubernetes CronJob to automate the [Postgres daily backup](Postgres_daily_backup.md).

[Edit this section](BackupRestore_HotSwitch_proposed_/edit.md)

### When we need to restore a clone from backup

Login to the database master pod   

[code]
    psql -U postgres  -c 'create database keycloak1;'
    pg_restore -d keycloak1 -U postgres /bitnami/postgresql/bck_25042024/keycloak_ori.dmp
    
[/code]

Create a new database named keycloak{new instance}  
Restore the dump in the new instance

[Edit this section](BackupRestore_HotSwitch_proposed_/edit.md)

### Connect to the new database in K8s keycloak service

The new keycloak database is going to be keycloak1

In Ranchers statefull services select keycloak   
In the right top corner click edit   
Change the value from "keycloak" to "keycloak1"   
Save the deployment file

{  
"name": "DB_PORT",  
"value": "5432"   
}, {  
"name": "DB_DATABASE",  
"value": " **keycloak** "   
}, {  
"name": "DB_USER",  
"value": "testuser"   
},

K8s will restart keycloak (scale down to 0 and scale up) and it will be attached to the restored database.

[Edit this section](BackupRestore_HotSwitch_proposed_/edit.md)

### Work in the old keycloak database to fix the issue and roll back

When the issue at the original database is fixed.   
Replace the "keycloak1" with "keycloak" at the database name and save the yaml file.   
Keycloak will restart and attach to the original fixed database   
Any change on the data in the new database will be discarded when rolling back to the original database.

## Verification notes

No source code verification applicable — operational runbook; accuracy depends on current infrastructure configuration, not source code.

The target database list mentions `Orchestrator_db (?)` and `Metabase (?)` with question marks, indicating uncertainty at the time of writing. Both databases are confirmed to exist: the Orchestrator DB holds the `jobs`, `job_history`, and `job_process` tables, and the Metabase DB holds all platform metadata. The hot-switch procedure (clone database, point service to clone, roll back when fixed) is generic and would apply equally to either.

The `pg_dump -Fc` and `pg_restore` commands, and the use of the Bitnami PostgreSQL `rn3-pg-helm-postgresql` service name, are consistent with the Bitnami-based PostgreSQL deployment described in `postgresql_db.md` and confirmed by the `Postgres_daily_backup.md` CronJob manifest which also references `rn3-pg-helm-postgresql`.
