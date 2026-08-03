---
title: "Citus findings coordinator workers"
---

# Citus findings coordinator workers

1\. when there are workers down we can still read but write operations are not possible  
2\. when all workers are down we can still read in coordinator but we shouldn't (coordinator is not supposed to keep shards)  
3\. tried `SELECT rebalance_table_shards();` but coordinator still has shards  
4\. tried `SELECT citus_drain_node('172.17.0.2', 5432);` but coordinator still has shards

## Verification notes

This page describes observed runtime behaviour rather than configuration or code logic, so there is limited source-code material to verify against. The observations are consistent with known Citus behaviour: when the coordinator holds shards (which can happen if `create_reference_table` is used rather than `create_distributed_table`, or if shards were placed on the coordinator before workers were registered), `rebalance_table_shards()` and `citus_drain_node()` do not move them off the coordinator.

The source confirms that Reportnet3 registers all per-dataset tables as reference tables via `datasetInitCommandsCitusComplete.txt` (`SELECT create_reference_table(...)` for all eleven tables). Reference tables are replicated in full to every node including the coordinator by design; they are not drained or rebalanced. The observations in findings 3 and 4 are therefore an expected consequence of using `create_reference_table`, not a Citus defect or misconfiguration — though the document does not explain this distinction. A developer reading this page should understand that the coordinator holding data is intentional in a reference-table topology.
