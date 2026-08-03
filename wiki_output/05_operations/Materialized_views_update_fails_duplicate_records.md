---
title: "Materialized views update fails duplicate records"
---

# Materialized views update fails duplicate records

Case when :

Running create materialized views API and it fails :  
`{{PROD}}/recordstore/createUpdateQueryView?datasetId=78389&isMaterialized=false`

ERROR   
`ERROR: (500) more than one row returned by a subquery used as an expression`

We take the faulty query :   

[code]
    create materialized view if not exists dataset_78389."mapreference" as (
    select
        rv.id as record_id,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf160e') as "mapreferencecode_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf160e') as "mapreferencecode" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf160f') as "title_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf160f') as "title" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1610') as "description_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1610') as "description" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1611') as "datepublished_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1611') as "datepublished" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1612') as "hyperlink_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1612') as "hyperlink" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1613') as "resourcetype_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1613') as "resourcetype" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1614') as "category_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1614') as "category" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1615') as "maplanguage_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1615') as "maplanguage" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1616') as "pointofcontactemail_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1616') as "pointofcontactemail" ,
        (
        select
            fv.id
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1617') as "pointofcontactorganisation_id" ,
        (
        select
            case
                when fv.value = '' then null
                else fv.value
            end
        from
            dataset_78389.field_value fv
        where
            fv.id_record = rv.id
            and fv.id_field_schema = '6780fcf34521e50001cf1617') as "pointofcontactorganisation" 
    from
        dataset_78389.record_value rv
    inner join dataset_78389.table_value tv on
        rv.id_table = tv.id
    where
        tv.id_table_schema = '6780fcf34521e50001cf160c')
    
[/code]

Each select case has an **id_field_schema**   
for each one we run this query :
[code] 
    select
        *
    from
        dataset_78389.field_value
    where
        id in (
        select
            max(id)
        from
            dataset_78389.field_value
        where
            id_field_schema = '6780fcf34521e50001cf1610'
        group by
            id_record
        having
            count(*) > 1)
    
[/code]

If this query finds records it means that we have issue for this **id_table_schema**

Finally we can delete those records

## Verification notes

**Materialized views in source.** A search of the database migration scripts under `database/src/main/resources/db/migration/` found no `CREATE MATERIALIZED VIEW` statements. Materialized views are created dynamically at runtime by the Recordstore Service, not via Flyway migrations. The endpoint `PUT /recordstore/createUpdateQueryView` is confirmed in `RecordStoreControllerImpl.java` (line 677), where it accepts `datasetId` and `isMaterialized` parameters — matching the URL shown in the wiki (`/recordstore/createUpdateQueryView?datasetId=78389&isMaterialized=false`).

**Dataset schema.** The per-dataset schema naming pattern `dataset_78389` (where 78389 is the dataset ID) is consistent with the Recordstore's schema-per-dataset design documented in `postgresql_db.md`. Tables `field_value`, `record_value`, and `table_value` within each dataset schema are confirmed in `postgresql_db.md` as part of the per-dataset schema structure.

**Duplicate detection query.** The query pattern — grouping `field_value` by `id_record` with `HAVING count(*) > 1` — is a standard SQL duplicate-detection approach. The columns `id_record`, `id_field_schema`, `id`, and `value` in `field_value` are consistent with the field value entity structure in the dataset service source.

The root cause (duplicate `field_value` rows for the same record and field schema) is not handled by any automated cleanup job visible in the codebase. Manual deletion as described here is the only documented remedy.
