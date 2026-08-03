---
title: "Remove worker node"
---

# Remove worker node

  1. Drain the worker node  
`SELECT * from citus_drain_node('172.17.0.4', 5432);`  
Alternative way to drain multiple nodes 
    1. Run this for each node that you want to remove:  
`SELECT * FROM citus_set_node_property(node_hostname, node_port, 'shouldhaveshards', false);`
    2. Drain them all at once with `rebalance_table_shards`:  
`SELECT * FROM rebalance_table_shards(drain_only := true);`
  2. Wait until the command finishes
  3. Remove the node  
`select citus_remove_node('172.17.0.4', 5432);`

## Verification notes

No source code verification applicable — operational runbook; commands should be verified against the current Citus cluster version.

The `citus_drain_node`, `citus_set_node_property`, `rebalance_table_shards`, and `citus_remove_node` functions are all current Citus API names and are consistent with the image tag `eeacms/citus-postgis:2022-06-27T0919` used in the setup guide.

However, because all Reportnet3 per-dataset tables are registered as Citus reference tables (using `SELECT create_reference_table(...)`, not `SELECT create_distributed_table(...)`), the drain step behaves differently from what a reader familiar with distributed-table sharding might expect. Reference table replicas cannot be drained in the same way as distributed shards; `citus_drain_node` moves shard placements for distributed tables but reference table copies on a worker are removed automatically when the node is removed with `citus_remove_node`. Step 1 of this runbook may therefore be a no-op for a cluster where all tables are reference tables, or may fail with a message indicating there are no shards to drain. This should be confirmed against the live cluster before executing in a production context.
