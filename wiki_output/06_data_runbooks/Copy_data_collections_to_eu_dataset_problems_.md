---
title: "Copy data collections to eu dataset problems"
---

# Copy data collections to eu dataset problems

It has been reported in some cases that pressing the button for copying data collection to eu dataset, the procedure seems stuck (e.g. <https://taskman.eionet.europa.eu/issues/154188#change-720318>). One of the first things to monitor is if there are locks in the lock table. As it's difficult to specify what lock belongs to what dataflow in the lock table, the best approach would be to just delete old locks.

## Verification notes

The `lock` table referenced in this runbook is confirmed in `V1__Init_Metabase_BD.sql` as `public.lock` (singular). Any direct SQL against this table should use the name `lock`, not `locks`. The `lock_criteria` column is stored as `bytea` (serialised binary), so filtering locks by dataflow ID requires decoding the criteria — consistent with the separate runbook `Get_lock_record_information.md` which provides the procedure for doing this. No further verifiable technical claims are made in this runbook.
