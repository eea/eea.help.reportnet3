---
title: "BackupRestore plan"
---

# BackupRestore plan

It is highly important to keep in mind that in Reportnet there are 4 databases: 

  * Datasets: is the database containing all the schemas where reporters report their data
  * Metabase: is the database where Reports metadata are stored: Dataflows, contributors, Dataset metadata ...
  * Keycloak: is the database where Keycloak stores user information and access rights
  * MongoDb: is the database where information related to Dataset schema definition is stored. Here we will find Tables, fields, Rules and constraints. Also Documents to help reporters with the reporting are stored here



There is also one information repository: the pvc called reportnet-data, where Snapshots created by users are stored

The process to create a System backup must include these four databases plus the files stored in reportnet-data folder

Though the reporting activity is different depending on the reporting period it has been agreed that there will be a periodic backup process (TBD what periodicity). Also, backups on demand can be launched

[Edit this section](BackupRestore_plan/edit.md)

## Backup policy

The EEA backup policy can be found [here](https://taskman.eionet.europa.eu/projects/infrastructure/wiki/Netapp_Backup_Info)

With one exception (RN3Prod), Reportnet 3 is following the backup policy of _Backup_rancher_nfs_ : 

  * 8hourly - 2:15, 10:15, 18:15 - retention 3
  * daily - mon-saturday 22:45 - retention 18
  * weekly - every sunday 0:15 - retention 8

In order to reduce the potential for data loss and increase the snapshots' relevance, the RN3Prod data volume is backed up using the _bck_rn3prod_ snapshot policy: 

  * 4-hourly-minus-1 - snapshots at 4 hour intervals for 48h (at 05:15 AM, 09:15 AM, 01:15 PM, 05:15 PM and 09:15 PM, every day) - retention 12
  * daily-01-15 - daily snapshots (at 01:15 AM, every day) - retention 7



[Edit this section](BackupRestore_plan/edit.md)

## Restore policy

[Edit this section](BackupRestore_plan/edit.md)

### Postgres restore from snapshot procedure

**Important note:**  
Many of the described action can be performed via kubernetes CLI requiring minimal sysadmin involvement, mainly on exposing the snapshots and cleaning up after the restore.   
This is the way sysadmins did it, not the best way, and not a devops optimized procedure.

The restore procedure is composed by several actions that will be described below:  
\- access and prepare NetApp snapshot  
\- create a standalone postgres container in the host of the primary node of the damaged primary postgres instance  
\- map and export data from snapshot using the standalone container  
\- import the data in the target primary postgres instance

**Access and prepare NetApp snapshot**

The NetApp snapshots are locate physically in the same NetApp volume as the ones used for the environment.  
The snapshots aren't visibible to the environment's machine, you will need to ask the sysdamin to do that for you.

Find the primary postgres instance's host, and pass it to sysadmin  

[code]
    kubectl --kubeconfig ./.kube/configrn3test -n reportnet get pods
    
[/code]

sysdamin will ssh to that host and create a directory where temporarily will mount the snapshost:  

[code]
    mkdir /mnt/test/
    
[/code]

then mount the snapshot:  

[code]
    mount 10.2.200.1:/rkube /mnt/test/
    
[/code]

Sysdamin will prepare the directory structure for the temporary postgresql instance:  

[code]
    mkdir -p /mnt/test/pgdata/pgdata/dump
    make the directories writable:
    chmod -R 777 /mnt/test/pgdata
    
[/code]

**Create a standalone postgres container in the host of the primary node of the damaged primary postgres instance**

The sysadmin will create a standalone postgres container in the host of the primary node of the damaged primary postgres instance  
\- create a yaml file for the new container  
\- start the container

create the docker-compose yaml file:  
cd /mnt/test/pgdata  
touch docker-compose.yml

Insert this into the file:
[code] 
    version: '2'
    
    services:
    
      db:
        image: postgis/postgis:11-2.5
        restart: always
        environment:
          POSTGRES_PASSWORD: password
        volumes:
            - ./pgdata:/var/lib/postgresql/data
    
[/code]

Note: the version of the postgres in the postgis image MUST MATCH EXACTLY to the one in kubernetes!

Sysadmin will start the new container:  

[code]
    /usr/local/bin/docker-compose up -d
    
[/code]

Then will obtain the container's id:  

[code]
    docker ps
    
[/code]

Then stop the container:  

[code]
    docker stop <container's id>
    
[/code]

**Map the snapshot and export data using the standalone container**  
The new postgresql container created a new database and placed it on several directories created on /mnt/test/pgdata/pgdata/ directories.  
All the newly created sub-directories by this container will be deleted, except the directory dump created earlyer.

The directories from the snapshot will be now copied in their proper locations  
When started again the container will not overwrite the directories just copied.  
The conainer's log will complain that the database wasn't shot down properly and it's proceeding automatically with consistency restore from WAL files, that's normal.

When the copy process is finished, the new container will be started back, and find it's id:  

[code]
    /usr/local/bin/docker-compose up -d
    docker ps 
    
[/code]

Next step is to export the postgresql database via a container shell:  

[code]
    docker exec -it <container's id> bash
    
[/code]

Once inside the container go the dump directory:  

[code]
    cd /bitnami/postgresql/dump
    
[/code]

Now create a full dump (export):  

[code]
    psql -f all_pg_dbs.sql -U postgres
    
[/code]

Be aware that is manadatory to specify the password, it's that one set up in the yaml file: "password" (no quotes)

**Import the data in the target primary postgres instance**

Now let's prepare the target database. You will need to have deployed in kubernetes a new fresh database in running state. Let sysdamin know when ready.

Find the postgresql pv in the kubernetes:  

[code]
    kubectl --kubeconfig ./.kube/configrn3test -n reportnet get pv
    
[/code]

Now Sysdamin will copy the dump directory in the repective kubernetes pv

Find the id of the container of the target database:  

[code]
    docker ps
    
[/code]

Acces a shell in the target's database container:  

[code]
    docker exec -it <container's id> bash
    
[/code]

Now go to the dump location inside the container:  

[code]
    cd /bitnami/postgresql/dump
    
[/code]

And execute the import:  

[code]
    psql -f all_pg_dbs.sql -U postgres
    
[/code]

Again, specifying the the postgress password is manadatory, you have to share it with the sysadmin.

During the import disregard the error messages or warning complaining the "template" database.  
Be aware that the import takes **WAY longer** than the export, especialy due to index creation, be patient, you can do nothing to speed up the process.

**Cleanup the things:**  
stop the new created container with docker-compose that lives outside kubernetes.  

[code]
    docker stop <container's id>
    
[/code]

remove the container:  

[code]
    docker rm <container's id>
    
[/code]

find the image downloaded by docker compose and remove it:  

[code]
    docker images | grep postgis
    docker rmi <image-id>
    
[/code]

remove the /mnt/test/pgdata directory  
remove from the kubernetes pv the dump directory and file  
unmount the snapshots:  

[code]
    umount /mnt/test
    
[/code]

Sysadmin will take actions that the snapshots are no longer needed to be visible.

## Verification notes

The four-database model described (Datasets, Metabase, Keycloak, MongoDb) is confirmed by the source-derived documentation in `postgresql_db.md` and `mongodb.md`. The Metabase DB and Datasets DB are both PostgreSQL, MongoDB stores schema definitions, and Keycloak has its own database — this matches the current architecture.

**PostgreSQL image version.** The restore procedure specifies `postgis/postgis:11-2.5` and notes the image version must match production exactly. The source-derived `postgresql_db.md` confirms PostgreSQL 11.7 is the deployed version; the `11-2.5` PostGIS tag pairs PostGIS 2.5 with PostgreSQL 11, which is consistent. The instruction to match versions precisely remains valid.

**Bitnami path discrepancy.** The export step inside the container navigates to `/bitnami/postgresql/dump` and creates `all_pg_dbs.sql`. However, the `docker-compose.yml` used in this procedure mounts `./pgdata` to `/var/lib/postgresql/data`, not `/bitnami/postgresql`. The `/bitnami/postgresql/dump` path would only be correct if the target container is a Bitnami PostgreSQL image — but the restore procedure uses a `postgis/postgis` upstream image where data lives under `/var/lib/postgresql`. This is a potential error in the procedure: the `dump` directory path and the psql command path may not match the container image used. The Kubernetes production containers use Bitnami images (`bitnami/postgresql-repmgr`), so the path is valid for the production pod accessed via `docker exec`, but not necessarily valid for the intermediate `postgis/postgis` standalone container created during the restore.

**Backup policy details.** The backup schedules (8-hourly, daily, weekly for non-production; 4-hourly and daily for RN3Prod) are operational/infrastructure configuration that cannot be verified against source code. Accuracy depends on current NetApp snapshot policy configuration.

**No backup scripts in source.** No automated backup scripts were found under `/eea.reportnet3/database/`. The backup procedure described here is entirely manual and infrastructure-level. The `Postgres_daily_backup.md` wiki page provides a Kubernetes CronJob example for Keycloak backups, but there are no equivalent scripts for the Datasets or Metabase databases in the source repository.
