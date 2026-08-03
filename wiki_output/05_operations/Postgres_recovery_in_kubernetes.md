---
title: "Postgres recovery in kubernetes"
---

# Postgres recovery in kubernetes

1\. change stateful set yml changes

remove probes
[code] 
    "livenessProbe": {  
                  "exec": {  
                    "command": [  
                      "sh",  
                      "-c",  
                      "PGPASSWORD=$POSTGRES_PASSWORD psql -w -U \"postgres\" -d \"postgres\"  -h 127.0.0.1 -c \"SELECT 1\""   
                    ]  
                  },  
                  "initialDelaySeconds": 30,  
                  "timeoutSeconds": 5,  
                  "periodSeconds": 700,  
                  "successThreshold": 1,  
                  "failureThreshold": 200  
                },  
                "readinessProbe": {  
                  "exec": {  
                    "command": [  
                      "sh",  
                      "-c",  
                      "PGPASSWORD=$POSTGRES_PASSWORD psql -w -U \"postgres\" -d \"postgres\"  -h 127.0.0.1 -c \"SELECT 1\""   
                    ]  
                  },  
                  "initialDelaySeconds": 5,  
                  "timeoutSeconds": 5,  
                  "periodSeconds": 700,  
                  "successThreshold": 1,  
                  "failureThreshold": 200  
                },
[/code]

command sleep 3600 in containers section of yml 
[code] 
    "command": [  
                  "sh",  
                  "-c",  
                  "echo The app is running! && sleep 3600"   
                ],
[/code]

add fsGroup to the postgresql context be able to write in the filesystem of the pod

from

"securityContext": {  
"runAsUser": 1001  
}

to

"securityContext": {  
"runAsUser": 1001,  
"fsaGroup": 2000  
}

remove pods (delete) until they restart with sleep

open sheel in rn3-pg-helm-postgresql-0 in production environment and in sandbox

from sandbox

cat /opt/bitnami/postgresql/conf/postgresql.conf

and copy the output

in production

cat > /opt/bitnami/postgresql/conf/postgresql.conf

paste the output and CTRL-CTRL-C

repeat the sequence for   
cat /opt/bitnami/postgresql/conf/pg_hba.conf  
cat > /opt/bitnami/postgresql/conf/pg_hba.conf

cat /opt/bitnami/repmgr/conf/repmgr.conf  
cat > /opt/bitnami/repmgr/conf/repmgr.conf

start the production postgres-0 pod with

/opt/bitnami/scripts/postgresql-repmgr/run.sh &

to see the current status

/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh repmgr -f /opt/bitnami/repmgr/conf/repmgr.conf cluster show

to takeover from standby and promote to master :

/opt/bitnami/scripts/postgresql-repmgr/entrypoint.sh repmgr -f /opt/bitnami/repmgr/conf/repmgr.conf standby promote

this is now ytou master node for the pgsql cluster

repeast the sequence for the other nodes without promoting them to master

repair commands can be issued to the master server for pgsql corrupted database

## Verification notes

No source code verification applicable — operational runbook; accuracy depends on current infrastructure configuration, not source code.

The pod names (`rn3-pg-helm-postgresql-0`), configuration file paths (`/opt/bitnami/postgresql/conf/postgresql.conf`, `/opt/bitnami/repmgr/conf/repmgr.conf`), and the `repmgr` commands (`cluster show`, `standby promote`) are consistent with the Bitnami PostgreSQL-repmgr deployment described in `postgresql_db.md` and with the `Check_And_Fix_Database_Errors.md` page which uses the same repmgr entrypoint path.

The document contains a typographical error: `"fsaGroup"` on the securityContext snippet should be `"fsGroup"`. This would prevent the fix from working as written. The procedure is informal ("copy the output", "paste", "CTRL-CTRL-C") and should be treated as a field note rather than a formal runbook.
