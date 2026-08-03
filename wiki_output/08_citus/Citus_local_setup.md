---
title: "Citus local setup"
---

# Citus local setup

[Edit this section](Citus_local_setup/edit.md)

## Citus docker desktop guide (citus playground)

[Edit this section](Citus_local_setup/edit.md)

### Install as in documentation <https://www.citusdata.com/blog/2021/03/20/sharding-postgres-on-a-single-citus-node/>
[code] 
    docker run -d --name citus_coordinator -p 5500:5432 -e POSTGRES_PASSWORD=mypassword citusdata/citus
    docker run -d --name citus_worker_1 -p 5501:5432 -e POSTGRES_PASSWORD=mypassword citusdata/citus
    docker run -d --name citus_worker_2 -p 5502:5432 -e POSTGRES_PASSWORD=mypassword citusdata/citus
    
[/code]
[code] 
    docker container ls
    
[/code]

CONTAINER ID IMAGE COMMAND CREATED STATUS PORTS NAMES  
a7ea62e78961 citusdata/citus "docker-entrypoint.s…" 2 hours ago Up 36 minutes (healthy) 0.0.0.0:5502->5432/tcp citus_worker_2  
7e0c27c5ddfb citusdata/citus "docker-entrypoint.s…" 2 hours ago Up 30 minutes (healthy) 0.0.0.0:5501->5432/tcp citus_worker_1  
e08e34c7dd56 citusdata/citus "docker-entrypoint.s…" 3 hours ago Up 47 minutes (healthy) 0.0.0.0:5500->5432/tcp citus_coordinator

inspect all docket images to get the IPs
[code] 
    docker container inspect a7ea62e78961
    
[/code]

...  
"IPAddress": "172.17.0.4",  
...

repeat to get all IP addresses

citus_coordinator: 172.17.0.2  
citus_worker_1: 172.17.0.3  
citus_worker_2: 172.17.0.4

[Edit this section](Citus_local_setup/edit.md)

### Change in /var/lib/postgresql/data/postgresql.conf the wal to logical

wal_level = logical

[Edit this section](Citus_local_setup/edit.md)

### Change the /var/lib/postgresql/data/pg_hba.conf and add below localhost

host all all 172.17.0.0/24 trust

[Edit this section](Citus_local_setup/edit.md)

### Connect to citus coordinator and setup the distribution

docker exec -it citus_coordinator psql -U postgres
[code] 
    SELECT citus_set_coordinator_host('172.17.0.2', 5432);
    SELECT citus_add_node('172.17.0.3', 5432);
    SELECT citus_add_node('172.17.0.4', 5432);
    
[/code]

verify
[code] 
    SELECT * from citus_remote_connection_stats();
    
[/code]

test   

[code]
    CREATE TABLE users_table (user_id bigserial primary key, age int);
    
    SELECT create_distributed_table('users_table', 'user_id');
    
    INSERT INTO users_table (age)
           SELECT 20 + (random() * 70)::int
           FROM generate_series(0, 100000);
    
    SELECT avg(age) FROM users_table;
    
    CREATE INDEX user_age ON users_table (age);
    
[/code]

Rebalance chards (if not sharded in insert)
[code] 
    SELECT rebalance_table_shards();
    
[/code]

verify   

[code]
    SELECT * FROM citus_shards;
    SELECT * from pg_dist_node;
    
[/code]

[Edit this section](Citus_local_setup/edit.md)

### Simple failover recovery

remove a node without losing data  

[code]
    SELECT citus_drain_node('172.17.0.3', 5432);
    
[/code]

  
the node is clean and can be removed

add the node back and enable accept sharding   

[code]
    SELECT * from master_set_node_property('172.17.0.3', 5432, 'shouldhaveshards', true);
    
[/code]

  
rebalance shards  

[code]
    SELECT rebalance_table_shards();
    
[/code]

distribution should be balanced in all hosts   

[code]
    SELECT * FROM citus_shards;
    SELECT * from pg_dist_node;
    
[/code]

## Verification notes

No source code verification applicable — operational runbook; commands should be verified against the current Citus cluster version.

Two additional notes from cross-referencing the production setup:

The image used in this guide is `citusdata/citus` (the upstream community image) rather than the EEA-specific `eeacms/citus-postgis` image referenced in the production setup guide (`Reportnet3_citus_setup.md`). The production image includes PostGIS, which is required by Reportnet3. The local setup described here is suitable for learning Citus concepts but is not a faithful reproduction of the production configuration; the step to create PostGIS extensions and the geometry-related functions from `Reportnet3_citus_setup.md` are absent here.

The `master_set_node_property` function used in the "add the node back" step is the pre-Citus 11 name for what became `citus_set_node_property`. If the local `citusdata/citus` image is Citus 11 or later, this function may have been removed or aliased. The production image tag `2022-06-27T0919` pre-dates Citus 11 (released October 2022), so the old function name is likely correct for that image, but testers using a current `citusdata/citus:latest` image should use `citus_set_node_property` instead.
