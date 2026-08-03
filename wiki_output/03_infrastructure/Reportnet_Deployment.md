---
title: "Reportnet Deployment"
updated: "2020-06-02 10:35"
updated_by: "Søren Roug"
---

# Reportnet Deployment

  * **Table of contents**
  * Reportnet Deployment
    * Prerequisites
      * Deployment Tools
      * Helm Charts repositories
      * Reportnet 3 Deployment Helm Charts
      * Namespace
      * Persistent Volumes
    * Considerations previous to the deployment
    * Middleware Deployment
      * Useful commands
      * PostgreSQL Cluster
      * PostgreSQL Cluster Recovery
      * Citus PostgreSQL Cluster
      * MongoDB Cluster
      * Apache Kafka
      * Redis
      * [Deprecated] ElasticSearch
      * Zipkin [Double check with Adrian if needed, we are using graylog]
      * Consul
      * Keycloack
    * Configuration and update
      * Update DB
      * Config keycloak
    * Microservices Deployment
      * Application configuration (short version)
      * Application configuration (long version)
        * Frontend
        * Api Gateway
        * Dataflow
        * Recordstore
        * Validation
        * Dataset
        * User Management
        * Document Container
      * Communication
        * Collaboration
        * Indexsearch
        * Rod
        * Maintenance
    * Load Balancer configuration (Ingress)
      * Pre-requirements and Assumptions
      * Where to find the load-balancers ?
      * Routing rules
      * HAProxy.cfg
      * Production
        * Deployment commands



This guide will describe the process to deploy the Reportnet application from scratch, using the helm charts provided as part of the deployment scripts.

[Edit this section](Reportnet_Deployment/edit.md)

## Prerequisites

[Edit this section](Reportnet_Deployment/edit.md)

### Deployment Tools

  * VPN connection to EEA's DMZ. This will not be necessary after migration to Rancher 2.
  * Kubectl: you can install the client in your workstation. You just need the configuration file and API key to access the cluster that can be generated from Rancher.
  * Helm 3: you can just install this in your workstation. No extra configuration is needed.



[Edit this section](Reportnet_Deployment/edit.md)

### Helm Charts repositories

Add the following repositories to Helm and update helm repo:  
$ `helm repo add bitnami https://charts.bitnami.com/bitnami`  
$ `helm repo add elastic https://helm.elastic.co`  
$ `helm repo add stable https://charts.helm.sh/stable` **This repo is not maintained since 2020**  
$ `helm repo add codecentric https://codecentric.github.io/helm-charts`  
$ `helm repo update`

[Edit this section](Reportnet_Deployment/edit.md)

### Reportnet 3 Deployment Helm Charts

Checkout the code from the following project <https://github.com/eea/rn3-deploy-scripts> into a known location. We will refer to that location as `$WORKSPACE`.

> Note: Many default configuration values can be overridden with either loading from an extra file or by setting variables on the command line. Always inspect the `values.yml` file in each chart to check if the values are correct. If overriding values is required just add --set variable.to.be.overrided=NewValue. Only values defined in `values.yml` can be overridden. There is no convention on how to store special values for different environments for future upgrades. However, it is possible to execute helm with different values file. To do this just add -f myValuesFile.yaml to the execution line: helm install -f myValuesFile.yaml ./mychart

[Edit this section](Reportnet_Deployment/edit.md)

### Namespace

Create a dedicated namespace for the deployment. We will refer to that location as `$TARGET_ENV`.  

[code]
    $ kubectl create namespace reportnet
    $ export TARGET_ENV=reportnet
    
[/code]

Note: At some points, can be useful to do an update on the namespace  

[code]
    $ helm -n reportnet repo update 
    
[/code]

[Edit this section](Reportnet_Deployment/edit.md)

### Persistent Volumes

In Rancher 1.6 / Kubernetes 1.12 the persistent volumes as well as the storage server itself will be provided by Infrastructure Team. Send a ticket to Helpdesk.

Rancher 2 / Kubernetes 1.24 has a storage controller that creates a volume dynamically when it sees an new Persistent Volume Claim. If a special type is not needed, then it is recommended to leave the storage class blank in the PVC.

[Edit this section](Reportnet_Deployment/edit.md)

## Considerations previous to the deployment

Deployment will be done in 3 phases.

1) First phase will have the target of deploying all the required middleware: 

  * PostgreSQL
  * MongoDB
  * Consul
  * Kafka (and Zookeeper)
  * ElasticSearch
  * Keycloak
  * Redis



Some of these components will include the pre-load of initial data (PostgreSQL and MongoDB). Other could require manual configuration (Keycloak).  
This phase only needs to be executed once during the installation of the system.

2) Second phase will deploy the different microservices that will implement Reportnet behaviour.  
Each individual component will have:  
\- A Chart for setting the configuration properties, specific for the microservice, in the Consul server (done as a job that can be deleted afterwards).  
\- A Chart for creating the microservice Deployment and Service in Kubernetes.  
\- A special Chart for creating the PVC for Recordstore service

3) Third phase will configure the Ingress entry point.

[Edit this section](Reportnet_Deployment/edit.md)

## Middleware Deployment

[Edit this section](Reportnet_Deployment/edit.md)

### Useful commands

  * Uninstall a helm pack. But it doesn't uninstall the PVC, that needs to be done manually:   

[code]    $ helm -n reportnet uninstall <full pod name> 
    
[/code]

  * Delete a pod/stop a process (--force --grace-period=0 are optional):   

[code]    $ kubectl -n reportnet delete pod <full pod name> --force --grace-period=0
    
[/code]




[Edit this section](Reportnet_Deployment/edit.md)

### PostgreSQL Cluster
[code] 
    $ helm upgrade --install postgres-cluster-helm $WORKSPACE/helm/eaa-deploy/crunchy-containers/ha/postgresql-ha \
      -n $TARGET_ENV \
      --set fullnameOverride=rn3-pg-helm,metrics.enabled=true \
      --set postgresql.replicaCount=3 \
      --set pgpool.replicaCount=3 \
      --set postgresql.username=postgres \
      --set postgresql.password=password \
      --set pgpool.maxPool=20 \
      --set pgpool.numInitChildren=25 \
      --set persistence.storageClass=reportnet \
      --set postgresql.repmgrUsername=repmgr \
      --set postgresql.repmgrPassword=XXXXXXXXXXX \
      --set postgresql.securityContext.fsGroup=200
    
[/code]

Note:   
`postgresql.securityContext.fsGroup=200` \--> can be added to the --set line if user 1001 has not write access on the physical folders.  
`persistence.storageClass=<storage class name, e.g. database>` \--> can be added to the --set line if the PV's have a storageClass  
`persistence.size=20Gi` \--> can be added tot he --set line if the PV's meant for database has a different capacity from the default one, 8 Gb (Note, in other installation it has been used 20 Gb)  
More info about this helm chart can be found here: <https://hub.helm.sh/charts/bitnami/postgresql-ha> **Note that the chart has moved to[ArtifactHUB](https://artifacthub.io/packages/helm/bitnami/postgresql-ha), but this is misleading as the chart has been copied into the EEA deploy repository and is stuck on version 2.2.2.**

Values to keep in mind:  
**container.name.primary:** the name of the primary node. This name is important since it will be the name to configure in the data base url that services use.  
**container.name.replica:** The name of the replica node  
**postgresql.replicaCount:** The number of PostgreSQL nodes. Modifying this require redeploy as the connections must be rest in the PostgreSQL cluster as well as in the PgPool configuration. There will this number of PVC's claiming PV's with AccessMode RWO, so if replicaCount = 3, it will be necessary 3 PV's since 3 PVC's will be created.  
**pgpool.replicaCount:** The initial number of PgPool nodes. PgPool can be scale up/down with out redeploying  
**postgresql.username:** The name of the database admin user  
**postgresql.password:** The password of the database admin user  
**pgpool.maxPool:** The maximum number of cached connections in each Pgpool-II child process. Modification requires redeploy of pgpool (executing the same helm line will do the modification without any problem)  
**pgpool.numInitChildren:** The number of preforked Pgpool-II server processes. Modification requires redeploy of pgpool. Modification requires redeploy of pgpool (executing the same helm line will do the modification without any problem)

Please be aware that the following rule must be observed: max_pool*num_init_children <= (max_connections - superuser_reserved_connections). Note: superuser_reserved_connections=3  
Further information here: <https://www.pgpool.net/docs/latest/en/html/runtime-config-connection-pooling.html>

**postgresql.repmgrUsername:** Name of the replication manager user  
**postgresql.repmgrPassword:** Password of the replication manager user. If not provided a random one will be created. In case of database reinstallation it is important to provide this parameter otherwise replication system will not be able to start. If it is necessary to get the database passwords it can be done as follows:
[code] 
    kubectl -n reportnet get secret rn3-pg-helm-postgresql -o yaml
    
[/code]

  
The value is shown encoded in Base 64 as value of repmgr-password  

[code]
    apiVersion: v1
    data:
      postgresql-password: YYYYYYYY
      repmgr-password: ZZZZZZZZZZZ
    
[/code]

**< deprecated>**  
Init database (files are in helm/test-files)  

[code]
    $ cat metabase.sql datasets.sql > InitDB.sql
    $ kubectl cp -n $TARGET_ENV  $WORKSPACE/helm/eaa-deploy/test-files/InitDB.sql rn3-pg-helm:/tmp
    $ kubectl exec rn3-pg-helm -n $TARGET_ENV -- psql -f /tmp/InitDB.sql postgres -U postgres
    
[/code]

  
**Important note** : There is no need to have an extra process to initialize the database, editing the file $WORKSPACE/helm/eaa-deploy/crunchy-containers/ha/postgresql-ha/files/docker-entrypoint-initdb.d/postgresPreconfigDatabase.sql to add sql commands will be enough. At the moment it is done the creation of all of the databases, users and database tuning. Below this commands any extra command can be added

**Tuning up the database**

The following SQL commands will be executed as part of the deployment of the database:  

[code]
    ALTER SYSTEM SET max_connections = '500'; -- Determines the maximum number of concurrent connections to the database server. 
    ALTER SYSTEM SET shared_buffers = '1GB'; -- Sets the amount of memory the database server uses for shared memory buffers
    ALTER SYSTEM SET maintenance_work_mem = '256MB'; -- Specifies the maximum amount of memory to be used by maintenance operations, such as VACUUM, CREATE INDEX, and ALTER TABLE ADD FOREIGN KEY.
    ALTER SYSTEM SET work_mem = '64MB'; -- Specifies the amount of memory to be used by internal sort operations and hash tables before writing to temporary disk files
    ALTER SYSTEM SET checkpoint_completion_target = '0.9'; -- Specifies the target of checkpoint completion, as a fraction of total time between checkpoints
    ALTER SYSTEM SET random_page_cost = '1.1'; -- Sets the planner's estimate of the cost of a non-sequentially-fetched disk page.
    ALTER SYSTEM SET effective_io_concurrency = '300';-- Sets the number of concurrent disk I/O operations that PostgreSQL expects can be executed simultaneously
    ALTER SYSTEM SET min_wal_size = '1GB'; -- As long as WAL disk usage stays below this setting, old WAL files are always recycled for future use at a checkpoint, rather than removed
    ALTER SYSTEM SET max_wal_size = '4GB'; -- Maximum size to let the WAL grow to between automatic WAL checkpoints.
    ALTER SYSTEM SET synchronous_commit='remote_apply'; -- Specifies whether transaction commit will wait for WAL records to be written to disk before the command returns a "success" indication to the client.
    
[/code]

  
Further information about configuration can be found here: <https://www.postgresql.org/docs/11/>

Note: these or other system parameters can be altered by doing ALTER SYSTEM SET <parameter_name> in EVERY DATABASE NODE. Once it is done, the following command must be executed inside every PostgreSql pod: **pg_ctl restart. As these parameters are modified during the installation there is no need to do anything else**

Note: in case of error during installation it is advisable to remove pv's and pvc's and clean up the physical folders.

Note 2: In postgres, md5 passwords generation involves password and the user name. Generating new users/passwords can be done via <https://www.beautifyconverter.com/postgres-password.php>  
**< /deprecated>**

[Edit this section](Reportnet_Deployment/edit.md)

### PostgreSQL Cluster Recovery

In order to recover a cluster safely the following steps must be followed: 

  1. Remove the sts:   

[code]    kubectl -n $TARGET_ENV delete sts rn3-pg-helm-postgresql
    
[/code]

  2. Reinstall the database using the following command:   

[code]    helm upgrade --install postgres-cluster-helm $WORKSPACE/helm/eaa-deploy/crunchy-containers/ha/postgresql-ha \
      -n $TARGET_ENV \
     --set fullnameOverride=rn3-pg-helm \
     --set metrics.enabled=true \
     --set postgresql.replicaCount=3 \
     --set pgpool.replicaCount=3 \
     --set postgresql.username=postgres \
     --set postgresql.password=YYYYY \
     --set pgpool.maxPool=15 \
     --set pgpool.numInitChildren=32 \
     --set postgresql.repmgrUsername=repmgr \
     --set postgresql.repmgrPassword=XXXXXXXX \
     --set postgresql.livenessProbe.initialDelaySeconds=600 \
     --set postgresql.readinessProbe.enabled=false
    
[/code]

  
Note: this will deactivate readinessProbe and will delay 10 minutes the liveness probe. This way, the data from the primary node will be synchronized to the other replicas. If 600 seconds is not enough, restart the process adding more time to the initialDelaySeconds
  3. reestablish in every pgpool node the users executing the next lines inside every pgpool node:  

[code]    echo 'testuser:md599e8713364988502fa6189781bcf648f' >> /opt/bitnami/pgpool/conf/pool_passwd
    echo 'dataflow:md5928cb8f47a17c110ec3836fcbabc976b' >> /opt/bitnami/pgpool/conf/pool_passwd
    echo 'dataset:md5b48e53545a60e28f455b798e47fd3bdb' >> /opt/bitnami/pgpool/conf/pool_passwd
    echo 'validation:md51ca3e86a924c07264cf43c0f2f00ad5c' >> /opt/bitnami/pgpool/conf/pool_passwd
    echo 'recordstore:md5756b7ae2393844e708eba18629818472' >> /opt/bitnami/pgpool/conf/pool_passwd
    
[/code]

  4. Expose the DB from outside:   

[code]    kubectl -n reportnet expose svc rn3-pg-helm-pgpool --name=rn3-pg-helm-pgpool-external --type=NodePort --port=5432
    
[/code]




[Edit this section](Reportnet_Deployment/edit.md)

### Citus PostgreSQL Cluster

Download the files from this repository: <https://github.com/eea/RN3-citus-deploy>

We place ourselves in the console in the folder where we have downloaded the files and execute the following command:
[code] 
    helm -n reportnet install citus-postgis .
    
[/code]

**Configuration**  
In the secrets file in the templates folder, we have to put the password and the user in base 64.  
and on the master node we have to execute the following commands:
[code] 
    ALTER SYSTEM SET max_connections = '1500';
    ALTER SYSTEM SET shared_buffers = '8GB';
    ALTER SYSTEM SET effective_cache_size = '24GB';
    ALTER SYSTEM SET maintenance_work_mem = '2GB';
    ALTER SYSTEM SET checkpoint_completion_target = '0.9';
    ALTER SYSTEM SET wal_buffers = '16MB';
    ALTER SYSTEM SET default_statistics_target = '500';
    ALTER SYSTEM SET random_page_cost = '1.1';
    ALTER SYSTEM SET effective_io_concurrency = '200';
    ALTER SYSTEM SET work_mem = '256MB';
    ALTER SYSTEM SET min_wal_size = '4GB';
    ALTER SYSTEM SET max_wal_size = '16GB';
    ALTER SYSTEM SET max_worker_processes = '12';
    ALTER SYSTEM set max_parallel_workers_per_gather = '4';
    ALTER SYSTEM set max_parallel_workers = '12';
    ALTER SYSTEM set max_parallel_maintenance_workers = '4';
    set citus.shard_count = 64;
    SET citus.shard_replication_factor = 3;
    select pg_reload_conf();
    
[/code]
[code] 
    CREATE EXTENSION if not exists citus;
    CREATE extension if not exists postgis;
    CREATE extension if not exists fuzzystrmatch;
    CREATE EXTENSION if not exists postgis_tiger_geocoder;
    
    SELECT run_command_on_workers('CREATE EXTENSION if not exists citus');
    SELECT run_command_on_workers('CREATE EXTENSION if not exists postgis');
    SELECT run_command_on_workers('CREATE extension if not exists fuzzystrmatch');
    SELECT run_command_on_workers('CREATE EXTENSION if not exists postgis_tiger_geocoder');
    
    create or replace function public.is_valid_json(value text)
     returns boolean
    as
    $$
    begin
     return (value::json is not null);
    exception
     when others then
     return false;
    end;
    $$
    language plpgsql
    immutable;
    
    select run_command_on_workers ('create or replace function public.is_valid_json(value text)
     returns boolean
    as
    $$
    begin
     return (value::json is not null);
    exception
     when others then
     return false;
    end;
    $$
    language plpgsql
    immutable;')
    
    CREATE OR REPLACE FUNCTION public.insert_geometry_function()
     RETURNS trigger
     LANGUAGE plpgsql
    AS $function$ begin NEW.geometry := public.ST_GeomFromText(public.ST_AsText(public.ST_Transform(public.ST_SetSRID(public.ST_GeomFromGeoJSON(NEW.value::json->'geometry'),
    ((NEW.value::json->'properties')::json->>'srid')::integer),
    4326)),4326);
    return new;
    exception
    when others then
    NEW.geometry := null;
    if new.value <> '' then
        new.geometry_error := sqlstate || ' ' || sqlerrm;
    end if;
    return new;
    end;
    $function$
    ;
    
    select run_command_on_workers ('CREATE OR REPLACE FUNCTION public.insert_geometry_function()
     RETURNS trigger
     LANGUAGE plpgsql
    AS $function$ begin NEW.geometry := public.ST_GeomFromText(public.ST_AsText(public.ST_Transform(public.ST_SetSRID(public.ST_GeomFromGeoJSON(NEW.value::json->''geometry''),
    ((NEW.value::json->''properties'')::json->>''srid'')::integer),
    4326)),4326);
    return new;
    exception
    when others then
    NEW.geometry := null;
    if new.value <> '''' then
        new.geometry_error := sqlstate || '' '' || sqlerrm;
    end if;
    return new;
    end;
    $function$
    ;');
    
    create type public.geom_update as (id text, value text);
    select run_command_on_workers ('create type public.geom_update as (id text, value text)');
    
    CREATE OR REPLACE FUNCTION public.insert_geometry_function_noTrigger(datasetId int8, arr public.geom_update[]) RETURNS text AS $$
            declare
            geomErr text;
            geom public.geometry;
            idKey text;
            valueKey text;
            query text;
            queryerror text;
            begin       
                    FOREACH idKey,valueKey in array arr
                       loop
                           begin                            
                          RAISE NOTICE 'another_func(%,%)', idKey,valueKey;
                          geom := public.ST_GeomFromText(public.ST_AsText(public.ST_Transform(public.ST_SetSRID(public.ST_GeomFromGeoJSON(valueKey::json->'geometry'),((valueKey::json->'properties')::json->>'srid')::integer),4326)),4326);
                          RAISE NOTICE 'Geom (%)', geom::text; 
                          query := 'update dataset_'|| datasetId ||'.field_value fv set geometry = '''|| geom::text ||''' , geometry_error = null where fv.id = '''||idKey||'''';
                          RAISE NOTICE 'Query: %', query;
                          execute query; 
                          exception when others then
                            geom := null;
                            RAISE NOTICE 'Geom Err';
                          if valueKey <> '' then
                            geomErr := sqlstate || ' ' || sqlerrm;
                            RAISE NOTICE 'Geom Err: % in dataset %', geomErr,datasetId;
                            queryerror := 'update dataset_'|| datasetId ||'.field_value fv set geometry = null , geometry_error = '''|| geomErr ||''' where fv.id = '''||idKey||'''';
                            RAISE NOTICE 'Query Err: %', query;
                                execute queryerror;
                        end if;
                    end;
                       END LOOP;
                   return 'Finish';
            end;
    $$ LANGUAGE plpgsql;
    
    select run_command_on_workers ('CREATE OR REPLACE FUNCTION public.insert_geometry_function_noTrigger(datasetId int8, arr public.geom_update[]) RETURNS text AS $$
            declare
            geomErr text;
            geom public.geometry;
            idKey text;
            valueKey text;
            query text;
            queryerror text;
            begin       
                    FOREACH idKey,valueKey in array arr
                       loop
                           begin                            
                          RAISE NOTICE ''another_func(%,%)'', idKey,valueKey;
                          geom := public.ST_GeomFromText(public.ST_AsText(public.ST_Transform(public.ST_SetSRID(public.ST_GeomFromGeoJSON(valueKey::json->''geometry''),((valueKey::json->''properties'')::json->>''srid'')::integer),4326)),4326);
                          RAISE NOTICE ''Geom (%)'', geom::text; 
                          query := ''update dataset_''|| datasetId ||''.field_value fv set geometry = ''''|| geom::text ||'''' , geometry_error = null where fv.id = ''''||idKey||'''''';
                          RAISE NOTICE ''Query: %'', query;
                          execute query; 
                          exception when others then
                            geom := null;
                            RAISE NOTICE ''Geom Err'';
                          if valueKey <> '''' then
                            geomErr := sqlstate || '' '' || sqlerrm;
                            RAISE NOTICE ''Geom Err: % in dataset %'', geomErr,datasetId;
                            queryerror := ''update dataset_''|| datasetId ||''.field_value fv set geometry = null , geometry_error = ''''|| geomErr ||'''' where fv.id = ''''||idKey||'''''';
                            RAISE NOTICE ''Query Err: %'', query;
                                execute queryerror;
                        end if;
                    end;
                       END LOOP;
                   return ''Finish'';
            end;
    $$ LANGUAGE plpgsql;')
    
[/code]

[Edit this section](Reportnet_Deployment/edit.md)

### MongoDB Cluster

2 steps 

  1. Deploy cluster
  2. Load initial database (optional)


[code] 
    $ helm upgrade --install mongo stable/mongodb-replicaset -n $TARGET_ENV \
      --set securityContext.enabled=false \
      --set metrics.enabled=true \
      --set persistentVolume.storageClass=reportnet
    
[/code]

note:   
By default, mongodb-replicaset creates 3 instances, meaning that it is required 3 PV's with access modes: RWO,ROX,RWX. Mongo doesn't share a phisical storage but replicates, that's why it is necessary 3 PV's  
`persistentVolume.storageClass=<storage class name>` can be added to --set line if PV's for mongo are created with storageClass.   
`persistentVolume.size=<size of PV's>` can be added to --set line if PV's for mongo have different size than 10 Gb, which is the default. In other installations it has been used 20 GB (persistentVolume.size=20Gi)

More info about this chart here: <https://hub.helm.sh/charts/stable/mongodb-replicaset> **This chart no longer exists at the location!**

note:  
It is not necessary to initiate mongo database as it will be created the first time a user creates a schema. However, if for some reason it is necessary to initialize the database it can be done as follows:
[code] 
    kubectl cp -n $TARGET_ENV  $WORKSPACE/helm/eaa-deploy/test-files/insertMongo.js mongo-mongodb-replicaset-0:/tmp
    kubectl -n $TARGET_ENV exec -it mongo-mongodb-replicaset-0  -- mongoimport -d dataset_schema --drop -c DataSetSchema --file /tmp/insertMongo.js
    
[/code]

[Edit this section](Reportnet_Deployment/edit.md)

### Apache Kafka
[code] 
    $ helm upgrade --install zookeeper bitnami/zookeeper --namespace=$TARGET_ENV \
      --set metrics.enabled=true \
      --set replicaCount=3 \
      --set persistence.storageClass=reportnet
    $ helm upgrade --install bootstrap bitnami/kafka --namespace=$TARGET_ENV \
      --set zookeeper.enabled=false \
      --set externalZookeeper.servers=zookeeper.$TARGET_ENV.svc.cluster.local \
      --set replicaCount=3 \
      --set defaultReplicationFactor=3 \
      --set numPartitions=8 \
      --set metrics.kafka.enabled=true \
      --set persistence.storageClass=reportnet
    
[/code]

Note:

Zookeeper 

  * securityContext.fsGroup=200 in case there is no write permissions for user 1001
  * replicaCount=3 this means that 3 PV's will be required with access modes RWO,ROX,RWX
  * persistence.storageClass=<storage class name> in case the PV's has a storage class name
  * persistence.size=<pv size> \--> in case the PV's has a different size than 8Gb (in previous installation it has been used 20Gb)

Kafka 
  * replicaCount=3 this means that 3 PV's will be required with access modes RWO,ROX,RWX
  * persistence.storageClass=<storage class name> in case the PV's has a storage class name
  * persistence.size=<pv size> \--> in case the PV's has a different size than 8Gb (in previous installation it has been used 20Gb)



More info here:  
zookeeper: <https://artifacthub.io/packages/helm/bitnami/zookeeper>  
kafka: <https://artifacthub.io/packages/helm/bitnami/kafka>

Once the whole system is fully working it could be advisable to execute the following commands:  

[code]
    kubectl -n $TARGET_ENV exec -it bootstrap-kafka-0 -- kafka-configs.sh --zookeeper zookeeper.$TARGET_ENV.svc.cluster.local \
      --alter --entity-type topics --entity-name COMMAND_TOPIC --add-config retention.ms=300000
    kubectl -n $TARGET_ENV exec -it bootstrap-kafka-0 -- kafka-configs.sh --zookeeper zookeeper.$TARGET_ENV.svc.cluster.local \
      --alter --entity-type topics --entity-name BROADCAST_TOPIC --add-config retention.ms=300000
    kubectl -n $TARGET_ENV exec -it bootstrap-kafka-0 -- kafka-configs.sh --zookeeper zookeeper.$TARGET_ENV.svc.cluster.local \
      --alter --entity-type topics --entity-name DATA_REPORTING_TOPIC --add-config retention.ms=300000
    kubectl -n $TARGET_ENV exec -it bootstrap-kafka-0 -- kafka-configs.sh --zookeeper zookeeper.$TARGET_ENV.svc.cluster.local \
      --alter --entity-type topics --entity-name COMMAND_TOPIC --add-config delete.retention.ms=3600000
    kubectl -n $TARGET_ENV exec -it bootstrap-kafka-0 -- kafka-configs.sh --zookeeper zookeeper.$TARGET_ENV.svc.cluster.local \
      --alter --entity-type topics --entity-name BROADCAST_TOPIC --add-config delete.retention.ms=3600000
    kubectl -n $TARGET_ENV exec -it bootstrap-kafka-0 -- kafka-configs.sh --zookeeper zookeeper.$TARGET_ENV.svc.cluster.local \
      --alter --entity-type topics --entity-name DATA_REPORTING_TOPIC --add-config delete.retention.ms=3600000
    
    
[/code]

This is to speed up the cleaning messages process. By default messages remains a week in the cluster. As this messages are consumed at the moment, the retention policy should be faster.

[Edit this section](Reportnet_Deployment/edit.md)

### Redis
[code] 
    $ helm upgrade --install redis bitnami/redis --namespace=$TARGET_ENV \
      --set usePassword=false \
      --set cluster.slaveCount=3 \
      --set metrics.enabled=true \
      --set cluster.enabled=true \
      --set sentinel.enabled=true \
      --set master.disableCommands="" \
      --set global.storageClass=<storage class name> \
      --set master.persistence.size=<PV size> \
      --set slave.persistence.size=<PV size>
    
[/code]

if it was necessary to access to the cache via command line it can be done with the following line:  

[code]
    $ kubectl -n $TARGET_ENV exec -it redis-master-0 redis-cli
    
[/code]

Note:   
cluster.slaveCount=3 This means there will be 4 PV's (3 slaves + 1 master node) with access modes RWO,ROX,RWX  
persistence.storageClass=<storage class name> \--> can be added to the --set line in case the PV's have storage class name  
persistence.size=<PV size> \--> can be added to the --set line in case the PV's has different sinze than 8Gb (in previous installation it has been used 20 Gb)

More info about this chart here: <https://artifacthub.io/packages/helm/bitnami/redis>

[Edit this section](Reportnet_Deployment/edit.md)

### [Deprecated] ElasticSearch
[code] 
    $ helm upgrade --install elasticsearch elastic/elasticsearch -n $TARGET_ENV  --set imageTag=7.3.2
    
[/code]

Note:  
By default elasticsearch chart will create 3 replicas, this means that 3 PV will be required with Access Modes RWO,ROX,RWX and 30 Gb each.

this Helm chart does not provide a way to inform storage class name, so the PV cannot have a storage class name.

`volumeClaimTemplate.resources.requests.storage=<PV Size>` \--> can be added to --set line to provide a different size in case the PV is not 30Gb sized

More info about this chart here: <https://github.com/elastic/helm-charts/tree/master/elasticsearch>. **As of November 2022, this chart is no longer maintained**

[Edit this section](Reportnet_Deployment/edit.md)

### Zipkin [Double check with Adrian if needed, we are using graylog]
[code] 
    $ helm upgrade --install zipkin $WORKSPACE/helm/eaa-deploy/zipkin-helm -n $TARGET_ENV \
      --set storageMethod=elasticsearch \
      --set dependencies.enabled=false
    
[/code]

Note:  
In order to access to the web console it will be necessary to provide access through the load balancer or expose the service as a node port

The Zipkin chart originally comes from <https://github.com/Financial-Times/zipkin-helm> version 0.1.1 released in 2017.

[Edit this section](Reportnet_Deployment/edit.md)

### Consul
[code] 
    $ helm upgrade --install consul stable/consul -n reportnet --set StorageClass=reportnet,Storage=20Gi
    
[/code]

note:  
By default consul chart will create 3 replicas, this means that 3 PV will be required with Access Modes RWO,ROX,RWX and 30 Gb each.

`StorageClass=<pv storage class>` \--> can be added to the --set line in case the PV's have storage class  
`Storage=<pv size>` \--> can be added to the --set line in case the PV's has a size different than 1 Gb

More info of this helm chart here: <https://github.com/helm/charts/tree/master/stable/consul> **As of June 2020, this chart is no longer maintained**

[Edit this section](Reportnet_Deployment/edit.md)

### Keycloack
[code] 
    $ helm -n $TARGET_ENV install keycloak $WORKSPACE/helm/eaa-deploy/keycloak \
      --set keycloak.replicas=2 \
      --set keycloak.persistence.dbVendor=postgres \
      --set keycloak.persistence.dbName=keycloak \
      --set keycloak.persistence.dbHost=rn3-pg-helm-pgpool.$TARGET_ENV.svc.cluster.local \
      --set keycloak.persistence.dbPort=5432 \
      --set keycloak.persistence.dbUser=testuser \
      --set keycloak.persistence.dbPassword=XXXXXX \
      --set keycloak.image.tag=1.0
      --set keycloak.image.repository=eeacms/rn3-keycloak
    
[/code]

Values to keep in mind: 

  * keycloak.replicas: number of keycloak instances running. Furthermore, setting to a value greater than 1, keycloak is deployed in HA mode
  * keycloak.username: Admin user to access keycloak
  * keycloak.password: Admin password to access keycloak. With this two values it will be possible to access the web console
  * keycloak.persistence.dbVendor: POSTGRES (it will be used the same postgres database than for the rest of services)
  * keycloak.persistence.dbHost: Url to the database or the name os database service (rn3-pg-helm)
  * keycloak.persistence.dbPort: Port to the database (5432)
  * keycloak.persistence.dbName: Name of the database to store keycloak information. It will be created if it doesn't exist
  * keycloak.persistence.dbUser: the user which Keycloak will use to access database. This user must have permissions enough to create databases, tables ....
  * keycloak.persistence.dbPassword: the password for the user to access database
  * keycloak.image.tag: the image tag being used (5.0.0 corresponding to Keycloak version 5.0.0 but we used 1.0 as the image is eea customized with an email plugin. Base keycloak image is 5.0.0)
  * keycloak.image.repository=eeacms/rn3-keycloak



The following lines will create the admin user that will allow to manage Keycloak:  

[code]
    $ kubectl --namespace=$TARGET_ENV exec -it keycloak-0 -- /opt/jboss/keycloak/bin/add-user-keycloak.sh -r master -u admin -p admin
    $ kubectl --namespace=$TARGET_ENV exec -it keycloak-0 -- /opt/jboss/keycloak/bin/jboss-cli.sh --connect command=:reload
    
[/code]

Once it is installed follow the instruction of [Keycloak Configuration Handbook.docx](Reportnet_Deployment/attachments/262174).

[Edit this section](Reportnet_Deployment/edit.md)

## Configuration and update

[Edit this section](Reportnet_Deployment/edit.md)

### Update DB

Update the database to the last version:  

[code]
    mvn -f $WORKSPACE/helm/eaa-deploy/database -DPOSTGRES_SERVER=<server name>:<port> -DPOSTGRES_USER=postgres -DPOSTGRES_PASS=XXXX flyway:migrate
    
[/code]

import the DB for Keycloak (create new db and then restore)  
restore the DB: datasets->Schemas->dataset_0 for schema: 

  * Backup it from test
  * Restore it on the new Db



[Edit this section](Reportnet_Deployment/edit.md)

### Config keycloak

expose keycloak   

[code]
    kubectl -n reportnet expose svc keycloak-http --name=keycloak-http-external --type=NodePort --port=8080
    
[/code]

go inside keycloak -> admin console -> clients -> reportnet  
valid redirect uri, put: <https://hotfixes.reportnet.europa.eu/>* (change according to domain)

[Edit this section](Reportnet_Deployment/edit.md)

## Microservices Deployment

Every microservice has it's own version so every microservice must be deployed with the desired version. At the moment the last version of every microservice is the same: Service version is 1.3.1  
in the first release to production the service version will be 3.0.0

[Edit this section](Reportnet_Deployment/edit.md)

### Application configuration (short version)

These are the command lines to configure the microservices, delete the configuration and launch them.
[code] 
    helm -n reportnet install application-preconfig ./application-config 
    helm -n reportnet install api-gateway-preconfig ./reportnet-api-gateway/preconfig 
    helm -n reportnet install communication-preconfig ./reportnet-communication/preconfig 
    helm -n reportnet install dataflow-preconfig ./reportnet-dataflow/preconfig 
    helm -n reportnet install dataset-preconfig ./reportnet-dataset/preconfig 
    helm -n reportnet install recordstore-preconfig ./reportnet-recordstore/preconfig 
    helm -n reportnet install validation-preconfig ./reportnet-validation/preconfig 
    helm -n reportnet install rod-preconfig ./reportnet-rod/preconfig 
    helm -n reportnet install ums-preconfig ./reportnet-ums/preconfig 
    helm -n reportnet install document-preconfig ./reportnet-document/preconfig 
    helm -n reportnet install collaboration-preconfig ./reportnet-collaboration/preconfig 
    
    helm -n reportnet  uninstall application-preconfig 
    helm -n reportnet  uninstall api-gateway-preconfig 
    helm -n reportnet  uninstall communication-preconfig 
    helm -n reportnet  uninstall dataflow-preconfig 
    helm -n reportnet  uninstall dataset-preconfig 
    helm -n reportnet  uninstall recordstore-preconfig 
    helm -n reportnet  uninstall validation-preconfig 
    helm -n reportnet  uninstall rod-preconfig 
    helm -n reportnet  uninstall ums-preconfig 
    helm -n reportnet  uninstall document-preconfig 
    helm -n reportnet  uninstall collaboration-preconfig 
    
    export RELEASE_VERSION=v3.0.1.1-RC1
    
    helm -n reportnet upgrade dataflow ./reportnet-dataflow/service \
      --set version=$RELEASE_VERSION \
      --set sentry.environment=hotfixes \
      --set fme.integration.callback.urlbase=https://hotfixes-api.reportnet.europa.eu \
      -i
    helm -n reportnet upgrade frontend ./reportnet-frontend/service \
      --set version=$RELEASE_VERSION \
      --set sentry.environment=hotfixes \
      --set documentationFolder=test \
      --set backend=https://hotfixes-api.reportnet.europa.eu,websocket=wss://hotfixes.reportnet.europa.eu/communication/reportnet-websocket \
      --set eulogin="https://hotfixes-auth.reportnet.europa.eu/auth/realms/Reportnet/protocol/openid-connect/auth?client_id=reportnet&redirect_uri=https%3A%2F%2hotfixes.reportnet.europa.eu%2Feulogin%2F&response_mode=fragment&response_type=code&scope=openid" \
      -i
    helm -n reportnet upgrade api-gateway ./reportnet-api-gateway/service --set version=$RELEASE_VERSION -i
    helm -n reportnet upgrade recordstore ./reportnet-recordstore/service --set version=$RELEASE_VERSION -i
    helm -n reportnet upgrade communication ./reportnet-communication/service --set version=$RELEASE_VERSION -i
    helm -n reportnet upgrade dataset ./reportnet-dataset/service --set version=$RELEASE_VERSION,replicas=2 -i
    helm -n reportnet upgrade validation ./reportnet-validation/service --set version=$RELEASE_VERSION,replicas=2 -i
    helm -n reportnet upgrade ums ./reportnet-ums/service --set version=$RELEASE_VERSION -i
    helm -n reportnet upgrade document ./reportnet-document/service --set version=$RELEASE_VERSION -i
    helm -n reportnet upgrade rod ./reportnet-rod/service --set version=$RELEASE_VERSION -i
    helm -n reportnet upgrade collaboration ./reportnet-collaboration/service --set version=$RELEASE_VERSION -i
    
[/code]

[Edit this section](Reportnet_Deployment/edit.md)

### Application configuration (long version)

Before executing this installation it is necessary to locate in $WORKSPACE/helm/eaa-deploy/application-config/files/application.properties the following properties:  
config/application/eea.keycloak.publicKey=${KEYCLOAK_CLIENT_PUBLIC_KEY:<Public key from Keycloak Realm Keys>}  
config/application/eea.keycloak.secret=${KEYCLOAK_SECRET:<Secret from Keycloak client credentials>}  
config/application/eea.keycloak.admin.password=${KEYCLOAK_ADMIN_PASSWORD:<password set for reportnet_admin user>}  
config/application/eea.keycloak.admin.user=${KEYCLOAK_ADMIN_USER:<user created to be reportnet admin, by default is reportnet_admin>}  
config/application/eea.keycloak.redirect_uri=${KEYCLOAK_REDIRECT_URI:https://<reportnet base url>/eulogin/}
[code] 
    $ helm install application-preconfig $WORKSPACE/helm/eaa-deploy/application-config -n $TARGET_ENV
    $ helm uninstall application-preconfig -n $TARGET_ENV
    
[/code]

[Edit this section](Reportnet_Deployment/edit.md)

#### Frontend

CSP Policies:  

[code]
    "default-src 'self' 'unsafe-inline' *.eionet.europa.eu  ws:; font-src 'self' data: fonts.gstatic.com; img-src 'self' data: image.flaticon.com blob:";
    
[/code]

  

[code]
    $ helm upgrade frontend $WORKSPACE/helm/eaa-deploy/reportnet-frontend/service -n $TARGET_ENV -i --wait
    
[/code]

  
Long version (change param accordingly):   

[code]
    helm -n reportnet upgrade frontend ./reportnet-frontend/service \
      --set version=$RELEASE_VERSION \
      --set sentry.environment=hotfixes \
      --set documentationFolder=test \
      --set backend=https://hotfixes-api.reportnet.europa.eu \
      --set websocket=wss://hotfixes.reportnet.europa.eu/communication/reportnet-websocket \
      --set eulogin="https://hotfixes-auth.reportnet.europa.eu/auth/realms/Reportnet/protocol/openid-connect/auth?client_id=reportnet&redirect_uri=https%3A%2F%2hotfixes.reportnet.europa.eu%2Feulogin%2F&response_mode=fragment&response_type=code&scope=openid" \
      -i
    
[/code]

Note:  
**backend** \--> can be added to the line --set line to provide the url where the ApiGateway service is exposed. By Default is <https://rn3api.eionet.europa.eu> (eea dev env)  
**websocket** \--> can be added to the line --set line to specify the url to connect with the web socket. By default is wss://rn3api.eionet.europa.eu/communication/reportnet-websocket (eea dev env)  
**eulogin** \--> can be added to the line --set line to specify the url to connect with Keycloak in order to use EuLogin. By default is: [https://rn3auth.eionet.europa.eu/auth/realms/Reportnet/protocol/openid-connect/auth?client_id=reportnet&redirect_uri=https%3A%2F%2Frn3test.eionet.europa.eu%2Feulogin%2F&response_mode=fragment&response_type=code&scope=openid](https://rn3auth.eionet.europa.eu/auth/realms/Reportnet/protocol/openid-connect/auth?client_id=reportnet&redirect_uri=https%3A%2F%2Frn3test.eionet.europa.eu%2Feulogin%2F&response_mode=fragment&response_type=code&scope=openid)

Be aware that this url has the redirect_uri param that needs to point to the url where frontend is exposed, otherwise the invocation to Keycloak will not success

[Edit this section](Reportnet_Deployment/edit.md)

#### Api Gateway

Install the preconfig. This is to be done only in the initial deployment. Not for later upgrades:  

[code]
    $ helm install api-gateway-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-api-gateway/preconfig -n $TARGET_ENV
    $ helm uninstall api-gateway-preconfig -n $TARGET_ENV
    
[/code]

  
Install/upgrade the frontend.  

[code]
    $ helm upgrade frontend $WORKSPACE/helm/eaa-deploy/reportnet-frontend/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0

[Edit this section](Reportnet_Deployment/edit.md)

#### Dataflow
[code] 
    $ helm install dataflow-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-dataflow/preconfig -n $TARGET_ENV
    $ helm uninstall dataflow-preconfig -n $TARGET_ENV
    $ helm upgrade dataflow $WORKSPACE/helm/eaa-deploy/reportnet-dataflow/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Long version (change param accordingly):  

[code]
    helm -n reportnet upgrade dataflow ./reportnet-dataflow/service \
      --set version=$RELEASE_VERSION \
      --set sentry.environment=hotfixes \
      --set fme.integration.callback.urlbase=https://hotfixes-api.reportnet.europa.eu \
      -i
    
[/code]

**fme.integration.callback.urlbase** \--> can be added to --set line to specify the url that fme needs to invoke to interact with rn3. By default it is <https://rn3api.eionet.europa.eu>  
Keep in mind that this is the backend url, this means, the url where ApiGateway is exposed  
Note: Service version is 1.0.0

[Edit this section](Reportnet_Deployment/edit.md)

#### Recordstore

[Edit this section](Reportnet_Deployment/edit.md)

##### Creation of the PVC

This creates a persistent volume claim. This creation is only necessary the first time that Reportnet is created/deployed.

> Note that the storage class is `rook-ceph-block` and there is no information on how to change it.--> This has been changed. If it is necessary to set it, add `--set storageClassName=YourStorageClass`  
> Why is this separate from the chart that needs the volume? -->No reason to set it up every time RecordStore is redeployed, only for the first time. Added comment on this section
[code] 
    $ helm upgrade recordstore-data $WORKSPACE/helm/eaa-deploy/reportnet-recordstore/pvc -n $TARGET_ENV --set storageClassName=reportnet -i --wait
    
[/code]

  
Note:  
By default this PVC expects a PV with NO storage class and a size of 10Gb and access modes ReadWriteMany.   
storageClassName=<pv storage class> \--> Can be added to --set line in case the PV has specified some storage class name  
pvc.size=<pv size>\--> Can be added to --set line in case the PV has specified some other size  
Access Mode CANNOT be modified since this PVC is meant to be shared among different instances of RecordStore microservice 

[Edit this section](Reportnet_Deployment/edit.md)

##### Deployment of the microservice
[code] 
    $ helm install recordstore-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-recordstore/preconfig -n $TARGET_ENV
    $ helm uninstall recordstore-preconfig -n $TARGET_ENV
    $ helm upgrade recordstore $WORKSPACE/helm/eaa-deploy/reportnet-recordstore/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

#### Validation

Recordstore service must be fully functional or Validation service will not start  

[code]
    $ helm install validation-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-validation/preconfig -n $TARGET_ENV
    $ helm uninstall validation-preconfig -n $TARGET_ENV
    $ helm upgrade validation $WORKSPACE/helm/eaa-deploy/reportnet-validation/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0

[Edit this section](Reportnet_Deployment/edit.md)

#### Dataset

Recordstore service must be fully functional or Dataset service will not start  

[code]
    $ helm install dataset-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-dataset/preconfig -n $TARGET_ENV
    $ helm uninstall dataset-preconfig -n $TARGET_ENV
    $ helm upgrade dataset $WORKSPACE/helm/eaa-deploy/reportnet-dataset/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0

[Edit this section](Reportnet_Deployment/edit.md)

#### User Management
[code] 
    $ helm install ums-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-ums/preconfig -n $TARGET_ENV
    $ helm uninstall ums-preconfig -n $TARGET_ENV
    $ helm upgrade ums $WORKSPACE/helm/eaa-deploy/reportnet-ums/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

#### Document Container
[code] 
    $ helm install document-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-document/preconfig -n $TARGET_ENV
    $ helm uninstall document-preconfig -n $TARGET_ENV
    $ helm upgrade document $WORKSPACE/helm/eaa-deploy/reportnet-document/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

### Communication
[code] 
    $ helm install communication-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-communication/preconfig -n $TARGET_ENV
    $ helm uninstall communication-preconfig -n $TARGET_ENV
    $ helm upgrade communication $WORKSPACE/helm/eaa-deploy/reportnet-communication/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

#### Collaboration
[code] 
    $ helm install collaboration-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-collaboration/preconfig -n $TARGET_ENV
    $ helm uninstall collaboration-preconfig -n $TARGET_ENV
    $ helm upgrade collaboration $WORKSPACE/helm/eaa-deploy/reportnet-collaboration/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

#### Indexsearch
[code] 
    $ helm install indexsearch-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-indexsearch/preconfig -n $TARGET_ENV
    $ helm uninstall indexsearch-preconfig -n $TARGET_ENV
    $ helm upgrade indexsearch $WORKSPACE/helm/eaa-deploy/reportnet-indexsearch/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

#### Rod
[code] 
    $ helm install rod-preconfig $WORKSPACE/helm/eaa-deploy/reportnet-rod/preconfig -n $TARGET_ENV
    $ helm uninstall rod-preconfig -n $TARGET_ENV
    $ helm upgrade rod $WORKSPACE/helm/eaa-deploy/reportnet-rod/service -n $TARGET_ENV -i --wait --set version=<SERVICE_VERSION>
    
[/code]

  
Note: Service version is 1.0.0 

[Edit this section](Reportnet_Deployment/edit.md)

#### Maintenance

This services is by default deactivated. When maintenance mode needs to be started, this service must be scaled to 1 replica and traffic should be redirected from internet to maintenance service instead of frontend service
[code] 
    $ helm upgrade maintenance $WORKSPACE/helm/eaa-deploy/reportnet-maintenance -n $TARGET_ENV -i --wait 
    
[/code]

  
Note: Service version is 1.0 

[Edit this section](Reportnet_Deployment/edit.md)

## Load Balancer configuration (Ingress)

[Edit this section](Reportnet_Deployment/edit.md)

### Pre-requirements and Assumptions

For this section, we are considering the current infrastructure deployed in EEA, where the Kubernetes environment is managed by Rancher, providing a Load Balancer, based on HAProxy that connects seamlessly to the Kubernetes environment.

Additionally, the following domains should be created:  
\- rn3test.eionet.europa.eu  
\- rn3auth.eionet.europa.eu  
\- rn3api.eionet.europa.eu

> What are they used for?

[Edit this section](Reportnet_Deployment/edit.md)

### Where to find the load-balancers ?

Once the lb has been launched and configured, it's easy to forget where to access them.  
They are in:   
Rancher -> Kubernetes -> Infrastructure stacks, find "rn3prod-lb" (prod) or "rn3staging-lb" (staging) ...  
Extend the stack, you will find external-lb, on the right in the three dots menu, click on upgrade/edit.

[Edit this section](Reportnet_Deployment/edit.md)

### Routing rules

Configure the routing rules as described in   
![](Reportnet_Deployment/attachments/load-balancer-routing-rules.PNG)

[Edit this section](Reportnet_Deployment/edit.md)

### HAProxy.cfg

Set up the Custom haproxy.cfg file with the following configuration:
[code] 
    defaults
    # Hopefully not necessary
    timeout connect 20s
    timeout tunnel 3600s
    timeout http-keep-alive  1s
    #timeout client 600s
    #timeout server 600s
    option http-server-close
    
    frontend 80
    redirect scheme https code 301 if { hdr(host) -i <DOMAIN_NAME> }
    redirect scheme https code 301 if { hdr(host) -i <AUTH_DOMAIN_NAME> }
    redirect scheme https code 301 if { hdr(host) -i <API_DOMAIN_NAME> }
    
    frontend 443
    acl url_websocket_upgrade hdr(Connection) -i Upgrade
    acl url_websocket hdr(Upgrade) -i websocket
    use_backend rn3-websocket if url_websocket url_websocket_upgrade
    #only for dev purposes it is allowed connections from localhost. Deactivate the line in prod
    capture request header origin len 50
    
    backend rn3test
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-Frame-Options DENY
    http-response set-header X-XSS-Protection 1;mode=block
    http-response set-header Content-Security-Policy "default-src 'self'  'unsafe-inline'  https://*.europa.eu https://geocode.arcgis.com https://static.arcgis.com ws:; font-src 'self' data: fonts.gstatic.com; img-src 'self'  data: blob: image.flaticon.com https:; child-src blob:" 
    http-response set-header Referrer-Policy no-referrer-when-downgrade
    http-response set-header Feature-Policy "camera 'self'; microphone 'self'" 
    
    backend rn3api
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-Frame-Options DENY
    http-response set-header X-XSS-Protection 1;mode=block
    http-response set-header Content-Security-Policy "default-src 'self' 'unsafe-inline' https://*.europa.eu" 
    http-response set-header Referrer-Policy no-referrer-when-downgrade
    http-response set-header Feature-Policy "camera 'self'; microphone 'self'" 
    #only for dev purposes it is allowed connections from localhost. Comment out the line in prod
    http-response set-header Access-Control-Allow-Origin %[capture.req.hdr(0)] if { capture.req.hdr(0) -m end  localhost:3000 || capture.req.hdr(0) -m end  <DOMAIN_NAME> }
    http-response del-header Access-Control-Allow-Origin if !{ capture.req.hdr(0) -m end  localhost:3000 || capture.req.hdr(0) -m end  <DOMAIN_NAME> }
    #Line for production
    http-response set-header Access-Control-Allow-Origin "https://<DOMAIN_NAME>" 
    
    backend rn3-websocket
    option http-server-close
    acl hdr_connection_upgrade hdr(Connection)                -i upgrade
    acl hdr_upgrade_websocket  hdr(Upgrade)                   -i websocket
    
[/code]

Note: Keep in mind that 

  * CSP policies are defined here
  * the symbolic urls rn3test.eionet.europa.eu, rn3auth.eionet.europa.eu and rn3api.eionet.europa.eu will be changed to match the ones created for the target environment, so HaConfig must be rewritten accordingly



[Edit this section](Reportnet_Deployment/edit.md)

### Production

[Edit this section](Reportnet_Deployment/edit.md)

#### Deployment commands
[code] 
    # --MONGO
    helm upgrade --install mongo stable/mongodb-replicaset -n reportnet \
      --set securityContext.enabled=false \
      --set persistentVolume.size=20Gi \
      --set persistentVolume.storageClass=mongo
    
    # --Kafka
    helm upgrade --install zookeeper bitnami/zookeeper --namespace=reportnet \
      --set metrics.enabled=true \
      --set replicaCount=3 \
      --set securityContext.fsGroup=200 \
      --set persistence.storageClass=kafka \
      --set persistence.size=20Gi
    helm upgrade --install bootstrap bitnami/kafka --namespace=reportnet \
      --set zookeeper.enabled=false \
      --set externalZookeeper.servers=zookeeper.reportnet.svc.cluster.local \
      --set replicaCount=3 \
      --set defaultReplicationFactor=3 \
      --set numPartitions=8 \
      --set metrics.kafka.enabled=true \
      --set persistence.storageClass=kafka \
      --set persistence.size=20Gi
    
    # --Consul
    helm upgrade --install consul stable/consul -n reportnet --set StorageClass=consul,Storage=20Gi
    
    # --Keycloak
    helm -n reportnet install keycloak codecentric/keycloak \
      --set keycloak.replicas=2 \
      --set keycloak.persistence.dbVendor=postgres \
      --set keycloak.persistence.dbName=keycloak \
      --set keycloak.persistence.dbHost=rn3-pg-helm-gpool.reportnet.svc.cluster.local \
      --set keycloak.persistence.dbPort=5432 \
      --set keycloak.persistence.dbUser=<dbUser> \
      --set keycloak.persistence.dbPassword=<dbPassword> \
      --set keycloak.image.tag=5.0.0
    
    # --Redis
    helm upgrade redis bitnami/redis --namespace=reportnet \
      --set usePassword=false \
      --set cluster.slaveCount=3 \
      --set metrics.enabled=true \
      --set cluster.enabled=true \
      --set sentinel.enabled=true \
      --set master.disableCommands="" \
      --set persistence.storageClass=redis \
      --set persistence.size=20
      -i
    
    # --Recordstore pvc
    helm -n reportnet install recordstore-data ./reportnet-recordstore/pvc --set storageClassName=reportnet,pvc.size=20Gi
    
    helm -n reportnet upgrade api-gateway ./reportnet-api-gateway/service --set version=3.0.0,sentry.environment=production,replicas=2 -i
    helm -n reportnet upgrade recordstore ./reportnet-recordstore/service --set version=3.0.0,sentry.environment=production,replicas=2 -i
    helm -n reportnet upgrade communication ./reportnet-communication/service --set version=3.0.0,sentry.environment=production -i
    helm -n reportnet upgrade dataflow ./reportnet-dataflow/service \
      --set version=3.0.0,sentry.environment=production,replicas=2,fme.integration.callback.urlbase=https://api.reportnet.europa.eu -i
    helm -n reportnet upgrade dataset ./reportnet-dataset/service  --set version=3.0.0,sentry.environment=production -i
    helm -n reportnet upgrade validation ./reportnet-validation/service --set version=3.0.0,sentry.environment=production -i
    helm -n reportnet upgrade frontend ./reportnet-frontend/service \
      --set version=3.0.0 \
      --set sentry.environment=production \
      --set backend=https://api.reportnet.europa.eu,websocket=wss://reportnet.europa.eu/communication/reportnet-websocket \
      --set eulogin="https://auth.reportnet.europa.eu/auth/realms/Reportnet/protocol/openid-connect/auth?client_id=reportnet&redirect_uri=https%3A%2F%2Freportnet.europa.eu%2Feulogin%2F&response_mode=fragment&response_type=code&scope=openid" \
      -i
    helm -n reportnet upgrade ums ./reportnet-ums/service --set version=3.0.0,sentry.environment=production,replicas=2 -i
    helm -n reportnet upgrade document ./reportnet-document/service --set version=3.0.0,sentry.environment=production -i
    helm -n reportnet upgrade rod ./reportnet-rod/service --set version=3.0.0,sentry.environment=production -i
    
[/code]

## Verification notes

This page was last updated June 2020 and is substantially obsolete in several areas. The following discrepancies were identified.

**Orchestrator Service missing.** The deployment instructions cover ApiGateway, Recordstore, Communication, Dataflow, Dataset, Validation, User Management, Document Container, Collaboration, IndexSearch, Rod, and Maintenance. The Orchestrator Service (`orchestrator-service` in source, present since at least version 3.2 per `Environments.md`) is absent from both the configuration and deployment steps. Any fresh deployment following these instructions would be missing the job coordination layer.

**Inspire Harvester missing.** The `inspire-harvester` directory exists in the source tree but has no corresponding Helm deployment instructions here.

**Service version 1.0.0 / 3.0.0 inconsistency.** Individual service sections note "Service version is 1.0.0" while the short-version block and production deployment block use `RELEASE_VERSION=v3.0.1.1-RC1` and `version=3.0.0`. The 1.0.0 notes are stale; production was at `v3.2` by the time `Environments.md` was written in 2025.

**CI/CD pipeline.** The page describes a manual Helm-based deployment process. The `Jenkinsfile` at the root of the source tree shows a Jenkins pipeline that compiles and deploys services, including a `Push to EEA GitHub` stage for release branches. The relationship between the Jenkins pipeline and the Helm chart process described here is not explained; a developer reading this page would not know how the two interact.

**Deprecated Helm repositories.** The page instructs adding `stable https://charts.helm.sh/stable` (deprecated since November 2020) and notes this itself. The `stable/mongodb-replicaset` chart used for MongoDB is explicitly flagged in the page as "no longer exists at this location." The `stable/consul` chart used for Consul is flagged as "no longer maintained since June 2020."

**ElasticSearch marked deprecated.** The deployment section for Elasticsearch is titled `[Deprecated] ElasticSearch`, and the chart is noted as unmaintained since November 2022. This is consistent with the source-derived `architecture.md`, which shows Elasticsearch used only by the Index Search Service, itself described as an incomplete prototype.

**Zipkin.** The Zipkin section carries a comment "Double check with Adrian if needed, we are using graylog," indicating awareness that Zipkin was already being phased out at time of writing. The source-derived `architecture.md` confirms Zipkin is mostly phased out; Graylog and Sentry are the active systems. No Zipkin configuration was found in any service's `logback.xml`.

**Keycloak image discrepancy.** The short-version production block uses `keycloak.image.tag=5.0.0`, while the full deployment section references `eeacms/rn3-keycloak` with `tag=1.0`. This inconsistency in the same document is unresolved. `Environments.md` lists `jboss/keycloak:5.0.0`.

**pgpool_passwd hashes.** The PostgreSQL Cluster Recovery section includes hardcoded MD5 password hashes for `testuser`, `dataflow`, `dataset`, `validation`, and `recordstore`. These were likely correct at time of writing but may not match current credentials; they are included here without the original passwords and cannot be regenerated without knowing the plaintext.

**HAProxy ingress.** The load-balancing section describes a HAProxy-based Rancher 1.x infrastructure pattern ("Rancher -> Kubernetes -> Infrastructure stacks"). The current environments (`Environments.md`) use Kubernetes Ingress objects (`ingress-apigateway`, `ingress-fmeapi` etc.) in a Rancher 2 cluster. The HAProxy instructions no longer reflect how routing is configured.

**Dremio/S3 not covered.** The page predates the data lake architecture entirely. There are no deployment instructions for S3 buckets, Dremio, or Citus configuration beyond the initial SQL setup in the Citus section.
