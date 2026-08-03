---
title: "Change schema in Datalakes"
---

# Change schema in Datalakes

When you are on design mode:

1\. Before changing table schema you have to **delete all of your data** for each table and each dataset.   
2\. **Change your table schema** (e.x. Add table, add field, update field name)   
3\. **Import** again your data for each dataset and each table   
4\. Do the **validations** for each dataset   
5\. Check your SQL rules. **If you change a table name or field name to something different, don't forget to go also to your manual SQL rules, to change it also there.**

## Verification notes

No source code verification applicable — operational runbook for big-data (DLH/Datalake) design-mode schema changes. The requirement to delete data before changing schema is consistent with `dataset.md`'s description of the big-data path, where table formats are managed by Dremio and structural changes require clearing data before re-importing. The note about updating SQL rules after field or table renames is consistent with how the Validation Service stores rules referencing field and table names from the schema.
