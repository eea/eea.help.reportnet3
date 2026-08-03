---
title: "Add worker node"
---

# Add worker node

We can use the citus function `citus_add_node` to add workers to citus.  
Before adding any workers, we need to create the proper database and install the citus extension on the worker.

If we use as an example the [Reportnet3 citus setup](Reportnet3_citus_setup.md) guide, and try to add a 3rd worker we can do the following:

[Edit this section](Add_worker_node/edit.md)

#### Create the worker node

This creates the worker with database `datasets` and the citus extension already installed  

[code]
    docker run -d --name citus_demo_worker_3 --net citus_demo_network -p 5503:5432 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=datasets eeacms/citus-postgis:2022-06-27T0919
[/code]

[Edit this section](Add_worker_node/edit.md)

#### Connect to the coordinator
[code] 
    docker exec -it reportnet_citus_coordinator psql -U postgres -d datasets
[/code]

[Edit this section](Add_worker_node/edit.md)

#### Add the worker
[code] 
    SELECT citus_add_node('172.17.0.5', 5432);
[/code]

## Verification notes

No source code verification applicable — operational runbook; commands should be verified against the current Citus cluster version.

The `citus_add_node` function is confirmed as the correct function name for the Citus version implied by the `eeacms/citus-postgis:2022-06-27T0919` image. The runbook correctly uses a `--net citus_demo_network` flag, but the setup guide (`Reportnet3_citus_setup.md`) does not create a named Docker network — it relies on the default Docker bridge network and uses explicit IP addresses. The `--net citus_demo_network` flag in this document would therefore fail if the coordinator and existing workers were started without that named network. A reader following both documents in sequence would encounter this inconsistency.

After adding a worker, existing reference tables (all per-dataset tables in Reportnet3 are registered as reference tables via `create_reference_table`) are not automatically replicated to the new worker. The operator must run `SELECT replicate_reference_tables()` or `SELECT citus_copy_shard_placement(...)` on each table to make the new node consistent. This step is absent from the runbook.
