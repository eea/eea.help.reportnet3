---
title: "Locate mongo record duplicates"
---

# Locate mongo record duplicates

Use Case :

Collection PKCatalogue should have unique pkID

Search for pkID duplicates with the following aggregation:   
In PKCatalogue collection
[code] 
    [
      {
        $group:
          /**
           * _id: The id of the group.
           * fieldN: The first field name.
           */
          {
            _id: {
              idPk: "$idPk",
            },
            uniqueIds: {
              $addToSet: "$idPk",
            },
            count: {
              $sum: 1,
            },
          },
      },
      {
        $match:
          /**
           * query: The query in MQL.
           */
          {
            count: {
              $gt: 1,
            },
          },
      },
    ]
    
[/code]

Results will have the form :
[code] 
    {
      "_id": {
        "idPk": {
          "$oid": "64d0c8d7ee8e640001117607" 
        }
      },
      "uniqueIds": [
        {
          "$oid": "64d0c8d7ee8e640001117607" 
        }
      ],
      "count": 2
    }
    
[/code]

Identify the dataflows have the pkID issues (issues with fail to clone or fail to import properly)  
in the DataSetSchema collection
[code] 
    { "tableSchemas.recordSchema.fieldSchemas._id" :  ObjectId('64d0c8d7ee8e640001117607') }
    
[/code]

Search the PKCataglogue records :
[code] 
    {idPk: ObjectId('64d0c8d7ee8e640001117607')}
    
[/code]

Merge the duplicate records in the referenceBy array :
[code] 
    {
      "_id": {
        "$oid": "650d4784674dc10001d3a797" 
      },
      "idPk": {
        "$oid": "64d0c8d7ee8e640001117607" 
      },
      "referencedBy": [
        {
          "$oid": "64a2cb4b716663000112bbf7" 
        },
        {
          "$oid": "64a2cc334d58b400013e4310" 
        },
        {
          "$oid": "64a2ca1e52e82b00013a20c6" 
        }
      ],
      "_class": "org.eea.dataset.persistence.schemas.domain.pkcatalogue.PkCatalogueSchema" 
    }
    
[/code]
[code] 
    {
      "_id": {
        "$oid": "650d4784b1be3f00011c65a4" 
      },
      "idPk": {
        "$oid": "64d0c8d7ee8e640001117607" 
      },
      "referencedBy": [
        {
          "$oid": "64a2ca1e52e82b00013a20c6" 
        }
      ],
      "_class": "org.eea.dataset.persistence.schemas.domain.pkcatalogue.PkCatalogueSchema" 
    }

## Verification notes

**MongoDB collection name.** The document refers to `PKCatalogue` as the collection name. This is confirmed: `PkCatalogueSchema.java` in `dataset-service/src/main/java/org/eea/dataset/persistence/schemas/domain/pkcatalogue/` is annotated `@Document(collection = "PKCatalogue")`.

**Java class name.** The `_class` discriminator value shown in the example documents — `org.eea.dataset.persistence.schemas.domain.pkcatalogue.PkCatalogueSchema` — matches the actual class name and package exactly.

**Field name.** The aggregation groups by `idPk`, which matches the `@Field(value = "idPk")` annotation on `PkCatalogueSchema.idPk`. Note that `idPk` is annotated `@Id`, making it the MongoDB document `_id`, not a separate field. Grouping by `$idPk` in an aggregation pipeline is therefore equivalent to grouping by `$_id`. This is unusual but not incorrect.

**`DataSetSchema` collection query.** The duplicate identification query targets the `DataSetSchema` collection searching by `tableSchemas.recordSchema.fieldSchemas._id`. This collection name is confirmed: `DataSetSchema.java` in `dataset-service` carries `@Document(collection = "DataSetSchema")`.

**Typographical error.** On line 73 the document reads "Search the PKCataglogue records" — `PKCataglogue` is a misspelling of `PKCatalogue`. This does not affect the correctness of the query itself but should be corrected.
    
[/code]
