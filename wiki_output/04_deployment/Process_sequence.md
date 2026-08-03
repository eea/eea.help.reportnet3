---
title: "Process sequence"
---

# Process sequence

[Edit this section](Process_sequence/edit.md)

## Import

[Edit this section](Process_sequence/edit.md)

### BigFileImport

private DatasetValue readLines(final InputStream inputStream, final Long partitionId,  
final String idTableSchema, Long datasetId, String fileName, boolean replace,  
DataSetSchema dataSetSchema, ConnectionDataVO connectionDataVO)

Persist file in filesystem /reportnet3-data/input/  
CSV: **read in chucks of 5000 lines and insert to database**

**Chuck log line starts with** :  
[pool-3-thread-2] 2022-09-16_00:00:00.000 INFO o.e.d.s.impl.DatasetServiceImpl -Processing entries at method readLines in dataset 37900  
**Import sequence** :  
[pool-3-thread-2] 2022-09-16_00:00:00.000 INFO o.e.d.s.impl.DatasetServiceImpl - RN3-Import file: Temporary binary files CREATED for datasetId=37900  
...  
[pool-3-thread-2] 2022-09-16_00:00:00.000 INFO o.e.d.s.impl.DatasetServiceImpl - RN3-Import file: Temporary binary files CREATED for datasetId=37900  
**Ends with** :  
[pool-3-thread-2] 2022-09-16_00:00:00.000 INFO o.e.d.s.impl.DatasetServiceImpl -Reading Csv File Completed in dataset 37900

## Verification notes

The `readLines` method mentioned in this document exists at `dataset-service/src/main/java/org/eea/dataset/service/file/CSVReaderStrategy.java` (line 156), not in `DatasetServiceImpl` as the log class `o.e.d.s.impl.DatasetServiceImpl` might suggest. The log message "Processing entries at method readLines" is emitted from `CSVReaderStrategy.java` line 159. The chunk size of 5000 lines is confirmed at line 204 of `CSVReaderStrategy.java` and also at line 122 of `CSVSegmentedReaderStrategy.java`.

The file path `/reportnet3-data/input/` cited as the filesystem location for persisted import files is not confirmed in the dataset service source code examined; no reference to this path was found in `CSVReaderStrategy.java`. This path may be configured via an external property (Consul KV or environment variable) rather than hardcoded.

The log prefix format (`[pool-3-thread-2] 2022-09-16_00:00:00.000 INFO o.e.d.s.impl.DatasetServiceImpl`) is illustrative and the class name abbreviation (`o.e.d.s.impl`) corresponds to `org.eea.dataset.service.impl`, which is consistent with `DatasetServiceImpl`. However, the `readLines` method is actually in `CSVReaderStrategy`, so the log class in practice would be `o.e.d.s.f.CSVReaderStrategy` for that specific log line.

This document covers only the `BigFileImport` sequence. No other process sequences (validation, release, export) are documented, which limits its usefulness as a general reference.
