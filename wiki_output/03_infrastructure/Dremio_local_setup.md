---
title: "Dremio local setup"
---

# Dremio and Minio local setup

\- Create a file with name docker-compose.yml with the following content:  

[code]
    version: "3" 
    
    services:
      dremio:
        image: dremio/dremio-oss:24.1.0
        container_name: dremio-gis
        networks:
          dremio_net:
        ports:
          - 9047:9047
          - 31010:31010
          - 45678:45678          
      minio:
        image: minio/minio:RELEASE.2024-12-18T13-15-44Z
        container_name: minio
        environment:
          - MINIO_ROOT_USER=admin
          - MINIO_ROOT_PASSWORD=password
          - MINIO_DOMAIN=minio
        networks:
          dremio_net:
        ports:
          - 9001:9001
          - 9000:9000
        command: ["server", "/data", "--console-address", ":9001"]
    networks:
      dremio_net:       
    
[/code]

  
\- From terminal go to the directory which contains the docker-compose.yml file and run docker−compose up
[code] 
    If the version of minio is before 2024, it will not be compatible with our pom.xml dependencies. If needed use this image for minio
    image: minio/minio:RELEASE.2024-12-18T13-15-44Z
    
[/code]

[Edit this section](Dremio_local_setup/edit.md)

## Set up Minio

\- Enter minio on <http://localhost:9001>  
\- In "Buckets" tab create Bucket "rn3-dataset"   
\- Enter Bucket "rn3-dataset" and make "access policy" public and encryption disabled  
\- In "Buckets" tab create Bucket "rn3-dataset-iceberg"   
\- Enter Bucket "rn3-dataset-iceberg" and make "access policy" public and encryption disabled  
\- From tab "Object Browser" -> we can upload files in buckets

[Edit this section](Dremio_local_setup/edit.md)

## Set up Dremio

\- Enter dremio on <http://localhost:9047> and create an account

[Edit this section](Dremio_local_setup/edit.md)

### Connect to s3 storage from dremio

[Edit this section](Dremio_local_setup/edit.md)

#### rn3-dataset

\- Click the + sign for adding datasource  
\- Select Object storage amazon s3   
\- In "General" tab: 

  1. check "no authentication" 
  2. uncheck "Encrypt connection" 
  3. click the + sign for adding bucket and write "rn3-dataset"

\- In "Advanced options" tab 
  1. check "Enable compatibility mode" 
  2. in "Default CTAS Format" select "PARQUET" 
  3. add connection properties   

[code]     fs.s3a.path.style.access = true
     fs.s3a.endpoint = minio:9000
    
[/code]




[Edit this section](Dremio_local_setup/edit.md)

#### rn3-dataset-iceberg

\- Click the + sign for adding datasource  
\- Select Object storage amazon s3  
\- In "General" tab: 

  1. check "no authentication" 
  2. uncheck "Encrypt connection" 
  3. click the + sign for adding bucket and write "rn3-dataset-iceberg"

\- In "Advanced options" tab 
  1. check "Enable compatibility mode" 
  2. in "Default CTAS Format" select "ICEBERG" 
  3. add connection properties  

[code]     fs.s3a.path.style.access = true
     fs.s3a.endpoint = minio:9000
    
[/code]

  4. add Allowlisted buckets  

[code]     
     rn3-dataset-iceberg
    
[/code]




[Edit this section](Dremio_local_setup/edit.md)

### Add dremio plugin for spatial data

1\. download jar from here: <https://github.com/sheinbergon/dremio-udf-gis> (Jar can be found here: <https://github.com/sheinbergon/dremio-udf-gis/releases/tag/0.12.0>)  
2\. Run this command to put the jar on dremio container :   
docker cp dremio-udf-gis-0.12.0.jar dremio-gis:/opt/dremio/jars/3rdparty/dremio-udf-gis-0.12.0.jar

[Edit this section](Dremio_local_setup/edit.md)

### Change dremio field settings to support large data

Go to dremio -> settings -> support - > limits.single_field_size_bytes: 69,914,560

[Edit this section](Dremio_local_setup/edit.md)

### Consul variables

First you will have to go to your minio UI -> Access keys -> create access key and take those values
[code] 
    config/application/amazon.s3.endpoint
    config/application/amazon.s3.accessKey
    config/application/amazon.s3.secretKey
    config/application/dremio.driver-class-name -> com.dremio.jdbc.Driver
    config/application/dremio.url -> jdbc:dremio:direct=localhost:31010
    config/application/dremio.username
    config/application/dremio.password
    config/application/spring.cloud.openfeign.client.config.dremioClient.url -> http://localhost:9047
    config/application/parquet.file.path -> /reportnet3-data/input/parquet/
    config/application/dremio.jobPolling.numberOfRetries=20
    config/application/s3.default.bucket -> "rn3-dataset"."rn3-dataset" 
    config/application/s3.default.bucket.name -> rn3-dataset
    config/application/s3.default.bucket.path -> rn3-dataset/rn3-dataset  
    config/validation/exportDLPath -> /reportnet3-data/input/exportDL/
    config/validation/validation.parquet.max.file.size=200000
    config/validation/validation.split.parquet=true
    config/dataset/exportDLPath -> /reportnet3-data/input/exportDL/
    config/dataset/dremio.parquetConverter.custom=false
    config/dataset/dremio.parquetConverter.custom.maxCsvLinesPerFile=200000
    config/dataset/dremio.promote.numberOfRetries=20
    
[/code]

## Verification notes

The technical content of this page is largely consistent with the source-derived `DataLake/dremio_s3.md` document. The following observations were identified.

**Dremio version discrepancy.** The `docker-compose.yml` in this page uses `dremio/dremio-oss:24.1.0`. The source-derived `dremio_s3.md` states that Dremio 24.3.0 is the version currently deployed in the production AWS environment. For local development using 24.1.0 is close but not identical to production, which could cause behavioural differences — particularly with Iceberg table handling, which changed between patch releases.

**Bucket names confirmed.** The bucket names `rn3-dataset` and `rn3-dataset-iceberg` match the source-derived `dremio_s3.md`, which describes the default bucket for Parquet/Iceberg data and the Iceberg conversion workspace bucket.

**Consul KV keys confirmed.** The Consul variables listed (`config/application/amazon.s3.endpoint`, `config/application/dremio.driver-class-name`, `config/application/dremio.url`, and so on) are consistent with the key namespaces described in the source-derived `consul.md` and `dremio_s3.md`.

**S3 endpoint configuration.** The page sets `fs.s3a.endpoint = minio:9000` for local Minio. In production, the S3 endpoint is a NetApp-provided object store rather than AWS S3, as noted in `dremio_s3.md`. The `fs.s3a.path.style.access = true` property is required for both environments and is correctly included.

**Dremio GIS plugin.** The page instructs developers to add the `dremio-udf-gis-0.12.0.jar` for spatial data support. The source-derived `dremio_s3.md` does not mention this plugin, but spatial (GeoJSON/PostGIS) data handling is confirmed as a feature of the platform from the Recordstore and Dataset service documentation.

**`parquet.file.path` key.** The key `config/application/parquet.file.path` is listed with value `/reportnet3-data/input/parquet/`. This refers to a local filesystem path for the Recordstore's mounted PVC (used during Parquet generation before upload to S3), consistent with the PVC described in `Reportnet_Deployment.md`.

**Minio version note.** The page notes that Minio versions before 2024 are incompatible with the project's `pom.xml` dependencies. This cannot be confirmed from the source without reading the `pom.xml` S3 dependency versions, but the guidance is reasonable given that the AWS SDK versions bundled in recent Spring Boot releases require Minio RELEASE.2024+ for full compatibility.
