---
title: "Local setup"
---

# Local setup

[Edit this section](Local_setup_/edit.md)

## Create docker container for kafka

docker-compose.yml file to be used:
[code] 
    version: '3'
    services:
      zookeeper:
        image: confluentinc/cp-zookeeper:latest
        environment:
          ZOOKEEPER_CLIENT_PORT: 2181
          ZOOKEEPER_TICK_TIME: 2000
    
      kafka:
        image: confluentinc/cp-kafka:7.4.0 #kafka versions above this do not use Zookeeper.
        depends_on:
          - zookeeper
        ports:
          - 9092:9092
        environment:
          KAFKA_BROKER_ID: 1
          KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
          KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
          KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
          KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
          KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
          KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
          KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
    
      kafdrop:
        image: obsidiandynamics/kafdrop:latest
        depends_on:
          - kafka
        ports:
          - 9002:9000
        environment:
          KAFKA_BROKERCONNECT: kafka:29092
    
[/code]

\- Go to the kafka directory which contains the docker-compose.yml file and run `docker-compose up`  
\- use docker-compose stop & docker-compose start to stop and start containers  
\- To view the ui go to <http://localhost:9002/>

[Edit this section](Local_setup_/edit.md)

## Create docker container for mongodb

docker-compose.yml file to be used:  

[code]
    version: '3'
    
    services:
      mongo:
        image: mongo
        ports:
            - "27017:27017" 
      mongo-express:
        image: mongo-express
        environment:
            - ME_CONFIG_OPTIONS_EDITORTHEME=ambiance
            - ME_CONFIG_MONGODB_PORT=27018
            - ME_CONFIG_BASICAUTH_USERNAME=root
            - ME_CONFIG_BASICAUTH_PASSWORD=root
        depends_on:
            - mongo
        ports:
            - "8888:8081" 
    
[/code]

\- Go to the mongo directory which contains a docker-compose.yml file and run `docker-compose up`  
\- You can view the ui in <http://localhost:8888/> using credentials username=root, password=root  
\- You can also use mongodb compass client and the uri mongodb://localhost:27017/.

[Edit this section](Local_setup_/edit.md)

## Set up Postgres database

\- docker run --name crunchy-postgres -p 5432:5432 -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root postgis/postgis

[Edit this section](Local_setup_/edit.md)

### Setup database METABASE

Run the following by logging in postgres db with root/root:  

[code]
    CREATE DATABASE metabase;
    CREATE ROLE testuser;
    CREATE ROLE dataflow;
    CREATE ROLE dataset;
    CREATE ROLE validation;
    CREATE ROLE recordstore;
    
[/code]

\- run scripts <https://github.com/eea/rn3-deploy-scripts/tree/master/helm/database/src/main/resources/db/migration> (the scripts should run in the specified order)

Instead of running all files one by one you can use the following command which will run them all:  
\- Clone rn3-deploy-scripts  
\- Go to rn3-deploy-scripts/tree/master/helm/database/src/main/resources/db/migration folder

**For Linux:**  
\- Run `docker cp migration crunchy-postgres:/`   
\- Run `docker exec -it crunchy-postgres /bin/bash`  
\- go to migration folder and for each file run psql -h localhost -d metabase -f fileName

**For Windows:**  
\- Run `docker cp rn3-deploy-scripts\helm\database\src\main\resources\db\migration {containerId}:/tmp/migration`   
\- go to /tmp/migration folder and for each file run `psql -h localhost -d metabase -f fileName`

After all tables are created in database metabase, run the following queries:  

[code]
    INSERT INTO public.data_provider_group(id, "name", "type")VALUES(2, 'All countries: EEA member countries PLUS other countries and territories', 'COUNTRY');
    
    INSERT INTO public.data_provider(id, "label", code, group_id)VALUES(2, 'Austria', 'AT', 2);
    INSERT INTO public.data_provider(id, "label", code, group_id)VALUES(7, 'Bulgaria', 'BG', 2);
    
    ALTER TABLE public.task ADD COLUMN IF NOT EXISTS "task_type" varchar NULL;
    
[/code]

You can add more providers in table data_provider in similar way.

[Edit this section](Local_setup_/edit.md)

### Setup database orchestrator_db

Run the following by logging in postgres db with root/root:  
\- `CREATE DATABASE orchestrator_db;`  
\- Run the following scripts <https://github.com/eea/eea.reportnet3/tree/MasterArchitectureBranch/database/src/main/resources/db/migration/orchestrator_db>

[Edit this section](Local_setup_/edit.md)

### Set up database DATASETS

**NOTE** : it is import that some of the following will run as root user, this is why you need to connect at the container and then open the psql CLI tool, like this: 

  * Windows: `winpty docker exec -it crunchy-postgres //bin//sh` and then `psql` command
  * Linux: `docker exec -it crunchy-postgres /bin/sh` and then `psql` command


[code] 
    CREATE DATABASE datasets
    # exit psql CLI and enter again like this: psql -U root -d datasets
    CREATE EXTENSION postgis;
    CREATE EXTENSION postgis_topology;
    CREATE EXTENSION fuzzystrmatch;
    CREATE EXTENSION postgis_tiger_geocoder;
    # before exiting the psql CLI running as root for datasets run the the first command of the next step to be sure that will run properly
    CREATE schema dataset_0 AUTHORIZATION root;
    # after executing this command procceed with the rest of the file from the DBeaver, it doesn't matter
    
[/code]

  
\- Open datasetInitCommands.txt doc (path: eea.reportnet3/recordstore-service/src/main/resources/datasetInitCommands.txt) and replace dataset_0 in dataset_name and root in user  
\- Run all commands from the file 

\- Create following functions  

[code]
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
    
    CREATE TYPE public.geom_update AS (
        id text,
        value text);
    
    -- DROP FUNCTION public.insert_geometry_function_notrigger(int8, _geom_update);
    CREATE OR REPLACE FUNCTION public.insert_geometry_function_notrigger(datasetid bigint, arr geom_update[])
    RETURNS text
    LANGUAGE plpgsql
    AS $function$
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
    $function$
    ;
    
    --==--==--==--==--==--==--==--==--==--==--= geometry function new START --==--==--==--==--==--==--==--==--==--==--=
    --==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--=
    --DROP FUNCTION public.insert_geometry_function_notrigger_EEA(int8, int8, int8);
    
    CREATE OR REPLACE FUNCTION public.insert_geometry_function_notrigger_EAA(
        dataset_id bigint,
        limit_val bigint,
        offset_val bigint
    )
     RETURNS text
     LANGUAGE plpgsql
    AS $function$
    DECLARE
    geomErr text;
        geom public.geometry;
        idKey text;
        valueKey text;
        query text;
        queryerror text;
        dataset_val TEXT := CONCAT('dataset_', dataset_id::TEXT);
        updated_count bigint := 0;
    BEGIN
    
    FOR idKey, valueKey IN
            EXECUTE FORMAT(
                'SELECT id::TEXT, value::TEXT
                 FROM %I.field_value fv
                 WHERE fv.type IN (''POINT'',''LINESTRING'',''POLYGON'',''MULTIPOINT'',''MULTILINESTRING'',''MULTIPOLYGON'',''GEOMETRYCOLLECTION'')
                 ORDER BY id
                 OFFSET %s
                 LIMIT %s',
                dataset_val,
                offset_val,
                limit_val
            )
            LOOP
    begin
    --            RAISE NOTICE 'another_func(%,%)', idKey,valueKey;
                geom := public.ST_GeomFromText(public.ST_AsText(public.ST_Transform(public.ST_SetSRID(public.ST_GeomFromGeoJSON(valueKey::json->'geometry'),((valueKey::json->'properties')::json->>'srid')::integer),4326)),4326);
    --            RAISE NOTICE 'Geom (%)', geom::text;
                query := 'update dataset_'|| dataset_id ||'.field_value fv set geometry = '''|| geom::text ||''' , geometry_error = null where fv.id = '''||idKey||'''';
    --            RAISE NOTICE 'Query: %', query;
    execute query;
    updated_count := updated_count + 1;
                RAISE NOTICE 'updated count is %', updated_count;
                RAISE NOTICE 'updated id is %', idKey;
    
    exception when others then
                    geom := null;
                    RAISE NOTICE 'Geom Err';
                    if valueKey <> '' then
                        geomErr := sqlstate || ' ' || sqlerrm;
                        RAISE NOTICE 'Geom Err: % in dataset %', geomErr,dataset_id;
                        queryerror := 'update dataset_'|| dataset_id ||'.field_value fv set geometry = null , geometry_error = '''|| geomErr ||''' where fv.id = '''||idKey||'''';
    --                    RAISE NOTICE 'Query Err: %', query;
    execute queryerror;
    else
                        RAISE NOTICE 'Skipped update: Empty value for id % in dataset %', idKey, dataset_id;
    end if;
    end;
    END LOOP;
    
    RETURN updated_count;
    END;
    $function$
    ;
    
    --==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--==--=
    --==--==--==--==--==--==--==--==--==--==--= geometry function new END   --==--==--==--==--==--==--==--==--==--==--=
    
    
[/code]

[Edit this section](Local_setup_/edit.md)

## Set up consul

**For Linux:**  

[code]
    docker run --name=consul -p 8500:8500 -e CONSUL_BIND_INTERFACE=eth0 consul agent -server -bootstrap -ui -client=0.0.0.0 (if we restart container, all key/value pair is retained)
    
[/code]

  
\- we import key/value pairs by running `docker exec -t consul consul kv import "$(cat {pathToProject}/eea.reportnet3/configuration/consulKV.json)"`  
\- in case we want to export settings we run `docker exec -t consul consul kv export`  
\- to view the UI, we enter <http://localhost:8500>

**For Windows:**  

[code]
    docker run --name=consul -p 8500:8500 -e CONSUL_BIND_INTERFACE=eth0 hashicorp/consul agent -server -bootstrap -ui -client="0.0.0.0" (if we restart container, all key/value pair is retained)
    
[/code]

  
\- Run `docker cp eea.reportnet3\configuration\consulKV.json {containerId}:/tmp/consulKV.json`  
\- Run from inside {containerId}:/tmp/ `consul kv import "$(cat consulKV.json)"`  
\- in case we want to export settings we run `docker exec -t consul consul kv export`  
\- to view the UI, we enter <http://localhost:8500>

[Edit this section](Local_setup_/edit.md)

## Set up redis

  * For Linux: `docker run --name redis -d redis`
  * For Windows : `docker run --name redis -p 6379:6379 -d redis`



In case localhost is not recognized as redis host do the following:  

[code]
    docker inspect redis
    copy ipaddress and paste in consul -> key/value -> config -> application -> spring.redis.host
    change consul -> key/value -> config -> application -> spring.redis.port to 6379
    For Windows:
       add localhost instead of ipaddress. Final result: spring.redis.host: localhost
    
[/code]

[Edit this section](Local_setup_/edit.md)

## Set up keycloak
[code] 
     docker run --name keycloak -p 8083:8080  -e KEYCLOAK_USER=admin -e KEYCLOAK_PASSWORD=admin eeacms/rn3-keycloak:1.0 
[/code]

[Edit this section](Local_setup_/edit.md)

### Setup admin user for keycloak(if for some reason the above environment properties do not setup the admin user correctly)

  * Connect to keycloak container with: 
[code]    docker exec -it keycloak /bin/bash
[/code]

  * Inside keycloak container hit: 
[code]    $ /opt/jboss/keycloak/bin/add-user-keycloak.sh -r master -u admin -p admin
[/code]

  * Then do : 
[code]    $ /opt/jboss/keycloak/bin/jboss-cli.sh --connect command=:reload
[/code]

  * Open keycloak gui: <http://localhost:8083>
  * Login with admin/admin credentials
  * Click to **Add Realm** and in the opening realm Screen, use this json file: <https://github.com/eea/eea.reportnet3/blob/develop/configuration/RealmReportnetKeycloakBackup.json>
  * It should add a Reportnet Realm
  * If it failed, manually create a Realm named: Reportnet, then import the above file into it as a 2nd step.
  * If all is well so far, the import should have created a reportnet client, roles etc
  * If So far all good, go to 'Reportnet' Realm Settings->keys tab   
and copy the rsa_generated public key. This should go to Consul->key/Value->Config->application->`eea.keycloak.publicKey`
  * Go to Keycloak->Clients->reportnet->Tab Credentials->click Regenerate secret and copy this secret to Consul->Key/Value->application->`eea.keycloak.secret`
  * Also in Consul Set the following: 
    * Key/Value/Config/application->`eea.keycloak.redirect_uri` to be: <http://localhost:3000/eulogin/>
    * Change Key/Value/Config/application->`eea.keycloak.host` to: `${KEYCLOAK_HOST:localhost:8083}`
  * Go to Keycloak, 'Reportnet' Realm and create a user named 'reportnet_admin'. 
    * In Credentials Tab of this user, set a password (not temporary) 
    * Then go to Role-Mappings tab, assign all available roles to this user, and also, in the same page, from the drop-down named 'client Roles', select 'Realm Management', and give all roles to this user.
  * Go back to Consul, key/Value/config/ums and set the following: 
    * eea.keycloak.admin.password : the password of the user you made
    * eea.keycloak.admin.user: The username of the user you made. 
  * In Keycloak, Go to Clients -> reportnet -> Settings and set Authorization Enabled flag to true.



> **IMPORTANT NOTE** : after completing the setup of keycloak there will be a minor issue with the rights of every new user. Every time you create a new user at keycloak go to user settings, at **Groups** tab and remove every group. The groups that are creating the issue at the Dataflow-3-DATA_CUSTODIAN or something like that. After deleting those from keycloak you will be able to use this user as normal and add the user rights from the UI.

[Edit this section](Local_setup_/edit.md)

## Set up elasticSearch
[code] 
      docker run -d --name elastic -e ES_JAVA_OPTS="-Xms200m -Xmx200m" -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:8.2.2  
      add property management.health.elasticsearch.enabled=false in http://localhost:8500 -> key/value -> config -> indexsearch
    
[/code]

[Edit this section](Local_setup_/edit.md)

## Frontend setup

In file env.js comment out everything related to DEV and SANDBOX settings. In the end you will be left with the following:
[code] 
      REACT_APP_BACKEND: 'http://localhost:8010',
      REACT_APP_EULOGIN: false,
      DOCUMENTATION_FOLDER: 'test'
    
[/code]

## Verification notes

This is the more detailed and up-to-date of the two local setup pages. Most technical references can be confirmed against source.

The `datasetInitCommands.txt` path (`eea.reportnet3/recordstore-service/src/main/resources/datasetInitCommands.txt`) is correct and the file exists.

The `consulKV.json` path (`eea.reportnet3/configuration/consulKV.json`) is correct. All Consul key paths mentioned in the Keycloak setup steps (`eea.keycloak.publicKey`, `eea.keycloak.secret`, `eea.keycloak.host`, `eea.keycloak.redirect_uri`, `eea.keycloak.admin.user`, `eea.keycloak.admin.password`) are present in that file.

The `RealmReportnetKeycloakBackup.json` file exists at `configuration/RealmReportnetKeycloakBackup.json` in the source repository.

The orchestrator_db setup section references migration scripts at `https://github.com/eea/eea.reportnet3/tree/MasterArchitectureBranch/database/src/main/resources/db/migration/orchestrator_db`. The scripts exist locally at `eea.reportnet3/database/src/main/resources/db/migration/orchestrator_db/` (four migration files: V1 through V4). The branch name `MasterArchitectureBranch` in the URL cannot be confirmed from the local checkout but the scripts themselves exist.

The Keycloak Docker image `eeacms/rn3-keycloak:1.0` with environment variables `KEYCLOAK_USER=admin` and `KEYCLOAK_PASSWORD=admin` (note: this page uses `KEYCLOAK_USER`/`KEYCLOAK_PASSWORD` while `Local_setup.md` uses `KEYCLOAK_ADMIN`/`KEYCLOAK_ADMIN_PASSWORD`) cannot be confirmed against any Dockerfile in the source repository. There is no Dockerfile for Keycloak in the main source.

The `eea.keycloak.redirect_uri` value this page instructs you to set is `http://localhost:3000/eulogin/`. The encoded default value in `consulKV.json` is `${KEYCLOAK_REDIRECT_URI:http://k8s-node001.devoami.altia.es:30445/data-flow-task/}`, a dev-server address, so manually overriding the value after import remains necessary.

The frontend `env.js` setup instruction tells you to end up with `REACT_APP_EULOGIN: false` and `DOCUMENTATION_FOLDER: 'test'`. The current `frontend-service/public/env.js` already contains `REACT_APP_EULOGIN: false` and `DOCUMENTATION_FOLDER: 'test'`, but it also has an active `REACT_APP_BACKEND` pointing to the sandbox environment (`https://sandbox-api.reportnet.europa.eu`). The instruction to comment out all sandbox/dev settings and set `REACT_APP_BACKEND: 'http://localhost:8010'` is still valid; the API gateway port `8010` is confirmed by `api-gateway/src/main/resources/application.yml`.
