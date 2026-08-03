---
title: "Postgres daily backup"
---

# Postgres daily backup

This cronjob dumps the keycloak database daily, deletes dumps older than 30 days, and lists the backup folder for verification in log output. Does not delete if backup fails that day. It is an example and has not been tested.
[code] 
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: postgres-backups
      labels:
        component: dump-postgres
      annotations:
        "helm.sh/resource-policy": keep
    spec:
      accessModes:
      - ReadWriteMany
      resources:
        requests:
          storage: 30Gi
    ---
    apiVersion: batch/v1
    kind: CronJob
    metadata:
      name: dump-postgres
      labels:
        component: dump-postgres
    
    spec:
      timeZone: 'Europe/Copenhagen'
      schedule: "0 2 * * *" 
      concurrencyPolicy: Forbid
      jobTemplate:
        spec:
    
          template:
            spec:
              containers:
              - name: pgdump
                image: bitnami/postgresql-repmgr:11.7.0-debian-10-r74
                command:
                  - /bin/bash
                args: ['sh', '-c', 'pg_dump -Fc -f /backups/dump-$(date +%Y-%m-%d).psql && find /backups -type f -mtime +30 -ls -delete && ls -l /backups']
                env:
                - name: LANG
                  value: en_US.UTF-8
                - name: PGHOST
                  value: rn3-pg-helm-postgresql
                - name: PGDATABASE
                  value: keycloak
                - name: PGUSER
                  value: postgres
                - name: PGPASSWORD
                - valueFrom:
                    secretKeyRef:
                      name: rn3-pg-helm-postgresql
                      key: postgresql-password
    
                resources:
                  limits:
                    memory: 512Mi
                  requests:
                    memory: 128Mi
    
                volumeMounts:
                - mountPath: /backups
                  name: postgres-backups
    
              restartPolicy: Never
    
              volumes:
              - name: postgres-backups
                persistentVolumeClaim:
                  claimName: postgres-backups

## Verification notes

No source code verification applicable — operational runbook; accuracy depends on current infrastructure configuration, not source code.

The Kubernetes service name `rn3-pg-helm-postgresql` and the secret name `rn3-pg-helm-postgresql` (with key `postgresql-password`) are consistent with the Bitnami PostgreSQL-repmgr Helm chart naming pattern used in the project. The image `bitnami/postgresql-repmgr:11.7.0-debian-10-r74` matches the PostgreSQL 11.7 version documented in `postgresql_db.md`. The manifest targets only the `keycloak` database; the Metabase and Datasets databases are not covered by this example CronJob. The document itself notes it "has not been tested", so the YAML should be validated before use in production.
    
[/code]
