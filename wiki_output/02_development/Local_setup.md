---
title: "Local setup"
---

# Local setup

[Edit this section](Local_setup/edit.md)

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
        image: confluentinc/cp-kafka:latest
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
          - 9000:9000
        environment:
          KAFKA_BROKERCONNECT: kafka:29092
    
[/code]

\- Go to the kafka directory which contains the docker-compose.yml file and run `docker-compose up`  
\- use docker-compose stop & docker-compose start to stop and start containers  
\- To view the ui go to <http://localhost:9000/>

[Edit this section](Local_setup/edit.md)

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

[Edit this section](Local_setup/edit.md)

## Set up Postgres database

\- docker run --name crunchy-postgres -p 5432:5432 -e POSTGRES_USER=root -e POSTGRES_PASSWORD=root postgis/postgis

[Edit this section](Local_setup/edit.md)

### Setup database METABASE

Run the following:  
\- CREATE DATABASE metabase;  
\- CREATE ROLE testuser;  
\- CREATE ROLE dataflow;  
\- CREATE ROLE dataset;  
\- CREATE ROLE validation;  
\- CREATE ROLE recordstore;  
\- run scripts <https://github.com/eea/rn3-deploy-scripts/tree/master/helm/database/src/main/resources/db/migration>

Instead of running all files one by one you can use the following command which will run them all:  
\- Clone rn3-deploy-scripts  
\- Go to rn3-deploy-scripts/tree/master/helm/database/src/main/resources/db/migration folder  
\- Run 
[code]
    docker cp migration crunchy-postgres:/
[/code]

  
\- Run 
[code]
    docker exec -it crunchy-postgres /bin/bash
[/code]

  
\- go to migration folder and for each file run psql -h localhost -d metabase -f fileName

After all tables are created in database metabase, run the following queries:  

[code]
    INSERT INTO public.data_provider_group(id, "name", "type")VALUES(1, 'EEA Member countries', 'COUNTRY');
    
    INSERT INTO public.data_provider(id, "label", code, group_id)VALUES(2, 'Austria', 'AT', 1);
    INSERT INTO public.data_provider(id, "label", code, group_id)VALUES(7, 'Bulgaria', 'BG', 1);
    
[/code]

  
You can add more providers in table data_provider in similar way.

## Verification notes

This page covers the older of the two local setup variants; `Local_setup_.md` is the more recent version and supersedes several details here.

The `datasetInitCommands.txt` file referenced at `eea.reportnet3/recordstore-service/src/main/resources/datasetInitCommands.txt` exists in the source and the path is correct.

The `consulKV.json` file referenced at `eea.reportnet3/configuration/consulKV.json` exists and contains all thirteen `eea.keycloak.*` Consul keys described in the Keycloak setup steps, including `eea.keycloak.publicKey`, `eea.keycloak.secret`, `eea.keycloak.host`, and `eea.keycloak.redirect_uri`. The key paths shown are accurate.

The `RealmReportnetKeycloakBackup.json` referenced at `https://github.com/eea/eea.reportnet3/blob/develop/configuration/RealmReportnetKeycloakBackup.json` exists in the source at `configuration/RealmReportnetKeycloakBackup.json`.

The Keycloak Docker image used here is `eeacms/rn3-keycloak:1.0` with environment variables `KEYCLOAK_ADMIN=admin` and `KEYCLOAK_ADMIN_PASSWORD=admin`. The more recent `Local_setup_.md` uses the same image with `KEYCLOAK_USER` and `KEYCLOAK_PASSWORD` instead. Neither image reference could be confirmed in the main source repository (no Dockerfile or compose file references either tag), so the correct current image tag cannot be verified from source alone.

The `eea.keycloak.redirect_uri` Consul key is described here as pointing to `http://localhost:3000/data-flow-task/`. The actual default value encoded in `consulKV.json` is `${KEYCLOAK_REDIRECT_URI:http://k8s-node001.devoami.altia.es:30445/data-flow-task/}`, which is an environment-variable placeholder defaulting to a development server address rather than localhost. The instruction to set this to `http://localhost:3000/data-flow-task/` remains necessary for local development but the consulKV.json import will not give you that value automatically.

This page does not mention the `orchestrator_db` database, which the newer `Local_setup_.md` includes. The orchestrator service requires a separate PostgreSQL database (`orchestrator_db`) with its own Flyway migration scripts at `eea.reportnet3/database/src/main/resources/db/migration/orchestrator_db/`. Omitting this step will prevent the Orchestrator Service from starting.

The Kafdrop UI port shown here is `9000`. The newer `Local_setup_.md` maps it to `9002` and notes a comment that Kafka versions above 7.4.0 do not use Zookeeper. There is no docker-compose file in the main source repository to confirm which mapping is authoritative for local development.

[Edit this section](Local_setup/edit.md)

### Set up database DATASETS

\- CREATE DATABASE datasets  
\- USE datasets  
\- CREATE EXTENSION postgis;  
\- CREATE EXTENSION postgis_topology;  
\- CREATE EXTENSION fuzzystrmatch;  
\- CREATE EXTENSION postgis_tiger_geocoder;  
\- Open datasetInitCommands.txt doc (path: eea.reportnet3/recordstore-service/src/main/resources/datasetInitCommands.txt) and replace dataset_0 in dataset_name and root in user  
\- Run all commands from the file

[Edit this section](Local_setup/edit.md)

## Set up consul
[code] 
    docker run --name=consul -p 8500:8500 -e CONSUL_BIND_INTERFACE=eth0 consul agent -server -bootstrap -ui -client=0.0.0.0 (if we restart container, all key/value pair is retained)
    
[/code]

  
\- we import key/value pairs by running 
[code]
    docker exec -t consul consul kv import "$(cat {pathToProject}/eea.reportnet3/configuration/consulKV.json)"
[/code]

  
\- in case we want to export settings we run 
[code]
    docker exec -t consul consul kv export
[/code]

  
\- to view the UI, we enter <http://localhost:8500>

[Edit this section](Local_setup/edit.md)

## Set up redis

\- docker run --name redis -d redis

In case localhost is not recognized as redis host do the following:  

[code]
    docker inspect redis
    copy ipaddress and paste in consul -> key/value -> config -> application -> spring.redis.host
    change consul -> key/value -> config -> application -> spring.redis.port to 6379
    
[/code]

[Edit this section](Local_setup/edit.md)

## Set up keycloak

\- docker run --name keycloak -p 8083:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin eeacms/rn3-keycloak:1.0

[Edit this section](Local_setup/edit.md)

### Setup admin user for keycloak(for some reason the above environment properties do not setup the admin user correctly)

\- Connect to keycloak container with: 
[code]
    docker exec -it keycloak /bin/bash
[/code]

  
\- Inside keycloak container hit: 
[code]
    $ /opt/jboss/keycloak/bin/add-user-keycloak.sh -r master -u admin -p admin
[/code]

  
\- Then do : 
[code]
    $ /opt/jboss/keycloak/bin/jboss-cli.sh --connect command=:reload
[/code]

  
\- Open keycloak gui : <http://localhost:8083>  
\- Login with admin/admin credentials  
\- Click to Add Realm and in the opening realm Screen, use this json file:https://github.com/eea/eea.reportnet3/blob/develop/configuration/RealmReportnetKeycloakBackup.json  
\- It should add a Reportnet Realm  
\- If it failed, manually create a Realm named: Reportnet, then import the above file into it as a 2nd step.  
\- If all is well so far, the import should have created a reportnet client, roles etc  
\- If So far all good, go to 'Reportnet' Realm Settings->keys tab   
and copy the rsa_generated public key. This should go to Consul->key/Value->Config->application->eea.keycloak.publicKey  
\- Go to Keycloak->Clients->reportnet->Tab Credentials->click Regenerate secret and copy this secret to Consul->Key/Value->application->eea.keycloak.secret  
\- Also in Consul Set the following:  
\- Key/Value/Config/application->eea.keycloak.redirect_uri to be : <http://localhost:3000/data-flow-task/>  
\- Change Key/Value/Config/application->eea.keycloak.host to: `${KEYCLOAK_HOST:localhost:8083}`  
\- Go to Keycloak, 'Reportnet' Realm and create a user named 'reportnet_admin'.  
\- In Credentials Tab of this user, set a password (not temporary )   
\- Then go to Role-Mappings tab, assign all available roles to this user, and also, in the same page, from the drop-down named 'client Roles', select 'Realm Management', and give all roles to this user.  
\- Go back to Consul, key/Value/config/ums and set the following:  
\- eea.keycloak.admin.password : the password of the user you made  
\- eea.keycloak.admin.user: The username of the user you made.   
\- In Keycloak, Go to Clients -> reportnet -> Settings and set Authorization Enabled flag to true.

[Edit this section](Local_setup/edit.md)

## Set up elasticSearch
[code] 
      docker run -d --name elastic -e ES_JAVA_OPTS="-Xms200m -Xmx200m" -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:8.2.2  
      add property management.health.elasticsearch.enabled=false in http://localhost:8500 -> key/value -> config -> indexsearch
    
[/code]
