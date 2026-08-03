---
title: "Create new database in postgres"
---

# Create new database in postgres

In Rancher stateful sets : rn3-pg-helm-postgresql

Finding master pod  
Open shell (Exec) in one of the pgsql-ha pods and execute:  
/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh repmgr -f /opt/bitnami/repmgr/conf/repmgr.conf cluster show

In masted pod :

psql -U postgres

(password)

DROP DATABASE IF EXISTS orchestrator_db;

CREATE DATABASE orchestrator_db  
WITH   
OWNER = postgres  
ENCODING = 'UTF8'  
TEMPLATE = template0  
TABLESPACE = pg_default  
CONNECTION LIMIT = -1;

GRANT ALL PRIVILEGES ON DATABASE orchestrator_db TO postgres,testuser,dataflow,dataset,recordstore,validation;

\c orchestrator_db

CREATE extension if not exists postgis;  
CREATE extension if not exists fuzzystrmatch;  
CREATE EXTENSION if not exists postgis_tiger_geocoder;

GRANT ALL PRIVILEGES ON ALL tables in schema public to postgres,testuser,dataflow,dataset,recordstore,validation;  
grant all privileges on all sequences in schema public to postgres,testuser,dataflow,dataset,recordstore,validation;

## Verification notes

**DDL is outdated.** The `jobs` and `job_history` table DDL in this runbook matches the initial schema from `V1__Create_Job_And_Job_history_Persistance.sql`, but subsequent migrations have altered these tables significantly:

- `V2__Alter_Job_Table_And_Job_History.sql` drops the `process_id` column from both `jobs` and `job_history` and adds `release` (bool), `dataflow_id` (int8), `provider_id` (int8), and `dataset_id` (int8).
- `V3__Create_Job_Process_Persistence.sql` creates a separate `job_process` table with `id`, `job_id`, and `process_id` columns.
- `V4__Add_Prep_Code_Job_Table.sql` adds a `preparation_code` (varchar 255) column to `jobs`.

If this runbook is used to create the `orchestrator_db` from scratch, the resulting schema will be missing these columns and the `job_process` table. The recommended approach is to let Flyway apply the migrations automatically rather than running this manual DDL. If manual creation is unavoidable, the DDL must be updated to reflect the current schema after all four migrations.

**Pod naming.** The Rancher stateful set name `rn3-pg-helm-postgresql` and the repmgr script path `/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh` should be verified against the current Helm chart version in use, as Bitnami chart naming conventions have changed across versions.

\--Create table and sequence for jobs--  
CREATE TABLE IF NOT EXISTS public.jobs (  
id int8 NOT NULL,  
job_type varchar NOT NULL,  
job_status varchar NOT NULL,  
date_added timestamp NOT NULL,  
date_status_changed timestamp NOT NULL,  
parameters varchar NULL,  
creator_username varchar NULL,  
process_id varchar NULL,  
CONSTRAINT jobs_pk PRIMARY KEY (id)  
);  
CREATE SEQUENCE IF NOT EXISTS public.jobs_id_seq  
INCREMENT BY 1  
MINVALUE 1  
MAXVALUE 2147483647  
START 1  
CACHE 1  
NO CYCLE;  
\--Create table and sequence for job history--  
CREATE TABLE IF NOT EXISTS public.job_history (  
id int8 NOT NULL,  
job_id int8 NOT NULL,  
job_type varchar NOT NULL,  
job_status varchar NOT NULL,  
date_added timestamp NOT NULL,  
date_status_changed timestamp NOT NULL,  
parameters varchar NULL,  
creator_username varchar NULL,  
process_id varchar NULL,  
CONSTRAINT job_history_pk PRIMARY KEY (id)  
);  
CREATE SEQUENCE IF NOT EXISTS public.job_history_id_seq  
INCREMENT BY 1  
MINVALUE 1  
MAXVALUE 2147483647  
START 1  
CACHE 1  
NO CYCLE;
