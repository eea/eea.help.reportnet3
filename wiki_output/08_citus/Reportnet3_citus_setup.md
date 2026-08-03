---
title: "Reportnet3 citus setup"
---

# Reportnet3 citus setup

[Edit this section](Reportnet3_citus_setup/edit.md)

#### 1\. Setup coordinator and workers
[code] 
    docker run -d --name reportnet3_citus_coordinator -p 5510:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=datasets eeacms/citus-postgis:2022-06-27T0919
    docker run -d --name reportnet3_citus_worker_1 -p 5501:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=datasets eeacms/citus-postgis:2022-06-27T0919
    docker run -d --name reportnet3_citus_worker_2 -p 5502:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=datasets eeacms/citus-postgis:2022-06-27T0919
    
[/code]

[Edit this section](Reportnet3_citus_setup/edit.md)

#### 2\. Trust the docker network in workers

  * connect to each worker  

[code]    docker exec -it reportnet3_citus_worker_1 /bin/bash
[/code]



  * go to file `/var/lib/postgresql/data/pg_hba.conf` and add the following line  

[code]    host all all 172.17.0.0/24 trust
[/code]




[Edit this section](Reportnet3_citus_setup/edit.md)

#### 3\. Setup coordinator and workers

inspect coordinator and workers to get the ips  

[code]
    docker inspect reportnet3_citus_coordinator | grep IPAddress
[/code]

setup with the above ips  

[code]
    docker exec -it reportnet_citus_coordinator psql -U postgres
[/code]
[code] 
    SELECT citus_set_coordinator_host('172.17.0.2', 5432);
    SELECT citus_add_node('172.17.0.3', 5432);
    SELECT citus_add_node('172.17.0.4', 5432);
    
[/code]

[Edit this section](Reportnet3_citus_setup/edit.md)

#### 4\. Configure extensions and create functions
[code] 
    CREATE extension if not exists postgis;
    CREATE extension if not exists fuzzystrmatch;
    CREATE EXTENSION if not exists postgis_tiger_geocoder;
    
[/code]
[code] 
    SELECT run_command_on_workers('CREATE EXTENSION if not exists postgis');
    SELECT run_command_on_workers('CREATE extension if not exists fuzzystrmatch');
    SELECT run_command_on_workers('CREATE EXTENSION if not exists postgis_tiger_geocoder');
    
[/code]
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

[Edit this section](Reportnet3_citus_setup/edit.md)

#### 5\. Create tables

  * go to repository `eea.reportnet3`
  * find file `recordsotre-service/src/main/resources/datasetInitCommands.txt`
  * replace `%dataset_name%` with `dataset_0`
  * replace `%user%` with `postgres`
  * run the commands



[Edit this section](Reportnet3_citus_setup/edit.md)

#### 6\. Distribute tables

  * go to repository `eea.reportnet3`
  * find file `recordsotre-service/src/main/resources/datasetInitCommandsCitusComplete.txt`
  * replace `%dataset_name%` with `dataset_0`
  * run the commands

## Verification notes

The Docker image tag `eeacms/citus-postgis:2022-06-27T0919` is the custom EEA image used throughout the runbook; no corresponding Docker Compose file was found in the `eea.reportnet3` repository, so the tag cannot be cross-referenced against a pinned infrastructure file. The Citus version embedded in that image tag is not stated, which makes it impossible to confirm whether the SQL functions used in step 3 (`citus_set_coordinator_host`, `citus_add_node`) and step 6 are still the current function signatures for that image.

Step 5 refers to `recordsotre-service/src/main/resources/datasetInitCommands.txt` — the path contains a typo (`recordsotre` instead of `recordstore`). The correct path is `recordstore-service/src/main/resources/datasetInitCommands.txt`, which exists and matches the content described.

Step 6 refers to `recordsotre-service/src/main/resources/datasetInitCommandsCitusComplete.txt` — same path typo. The correct path `recordstore-service/src/main/resources/datasetInitCommandsCitusComplete.txt` exists and contains ten `SELECT create_reference_table(...)` calls covering `DATASET_VALUE`, `TABLE_VALUE`, `RECORD_VALUE`, `FIELD_VALUE`, `ATTACHMENT_VALUE`, `VALIDATION`, `DATASET_VALIDATION`, `TABLE_VALIDATION`, `RECORD_VALIDATION`, `FIELD_VALIDATION`, and `TEMP_ETLEXPORT`. All eleven per-dataset tables are therefore registered as Citus reference tables, not as distributed tables — there is no `create_distributed_table` call in any of these scripts. This is a significant architectural detail that the runbook does not explain: the deployment uses reference tables (replicated to every worker) rather than sharded distributed tables.

The `%dataset_name%` placeholder in both step 5 and step 6 is replaced at runtime by `JdbcRecordStoreServiceImpl` using `LiteralConstants.DATASET_PREFIX + datasetId` (which resolves to `dataset_<id>`). The manual instruction to substitute `dataset_0` is accurate as a one-off setup example.
