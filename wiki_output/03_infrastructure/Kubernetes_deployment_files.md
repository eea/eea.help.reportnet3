---
title: "Kubernetes deployment files"
updated: "2019-11-08 13:47"
updated_by: "Jorge Saenz"
---

# Kubernetes deployment files

  * **Table of contents**
  * Kubernetes deployment files
    * The helm repository
    * Docker Images
    * Kubernetes namespace
    * Storage classes
    * Ingress
    * Infrastructure services
    * Old installation
      * Mongo
      * Microservice Template
      * Keycloak
      * Kafka
      * Zookeeper
        * Zookeeper Config Map
        * Zookeeper Service
        * Zookeeper Headless Service
        * Zookeeper Pod Disruption
        * Zookeeper StatefulSet
      * Kafka Instance
        * Kafka Instance - Role Base Access
        * Kafka Instance - Config Map
        * Kafka Instance - Headless Service
        * Kafka Instance - Bootstrap Service
        * Kafka Instance - Pod Disruption
        * Kafka Instance - StatefulSet
      * Kafka Manager
        * Kafka Manager - Config Map
        * Kafka Manager - Service and Deployment



> Note: The preferred way to specify the deployment of the system would be to provide a [Helm 3.0](https://helm.sh/docs/) release. This would allow us to override e.g. the namespace choice.

The purpose of this page is to collaborate on the Kubernetes scripts for deployment in _production._ Don't put passwords or private keys in this wiki. Instead, specify that the value will be taken from a [Secret](https://kubernetes.io/docs/concepts/configuration/secret/).

Kubernetes at EEA is version 1.12.7. We are about to launch version 1.24.

[Edit this section](Kubernetes_deployment_files/edit.md)

## The helm repository

We want to be able to do proper rollbacks of deployments and also have the ability to create charts that are released for staging, but not production. Ideally we would also like to be compatible with Rancher 2.x Kubernetes catalogs later. Since we historically have used GitHub for Rancher catalog deployments we'll also use GitHub for Helm charts. There is an article on how to use [GitHub Pages](https://tech.paulcz.net/blog/creating-a-helm-chart-monorepo-part-1/), which seems to have what we need.

Source repository for Helm Charts: <https://github.com/eea/rn3-deploy-scripts>. The Helm deployment repository would be <https://eea.github.io/rn3-deploy-scripts>.

[Edit this section](Kubernetes_deployment_files/edit.md)

## Docker Images

  * <https://hub.docker.com/repository/docker/eeacms/dataset-service>
  * <https://hub.docker.com/repository/docker/eeacms/api-gateway>



[Edit this section](Kubernetes_deployment_files/edit.md)

## Kubernetes namespace

The namespace for the deployment of Reportnet 3 and potential legacy components such as ROD shall be 'reportnet'.  

[code]
    apiVersion: v1
    kind: Namespace
    metadata:
      name: reportnet
      labels:
        name: reportnet
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

## Storage classes

This is not decided yet, but from EEA side we would like something that reflects the usage even if it results in the same type of storage to be provisioned. Examples: 'database', 'configuration', 'blobs'. We can then later e.g. switch to SSD for the database class.

[Edit this section](Kubernetes_deployment_files/edit.md)

## Ingress

This is not yet complete. What are we going to call the new R3 frontend?
[code] 
    apiVersion: extensions/v1beta1
    kind: Ingress
    metadata:
      name: global-lb
    # annotations:
    #   io.rancher.scheduler.affinity.host_label: "ip=10.50.4.173" 
    spec:
      tls:
      - hosts:
        - rod.eionet.europa.eu
        secretName: eionet-star-tls
      rules:
      - host: rod.eionet.europa.eu
        http:
          paths:
          - backend:
              serviceName: rod3-appl
              servicePort: 8080
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

## Infrastructure services

Place holders

Name  | EEA  | Altia/Tracasa   
---|---|---  
targetNameSpace  |  reportnet  |  eea-helm3   
dbClass  |  database  |  rook-ceph-block 
[code] 
    # Define some variables
    targetNameSpace=reportnet
    dbClass=database
    # Install stable repo as charts repository
    helm repo add stable https://kubernetes-charts.storage.googleapis.com/
    # consul requests 1 GB volume with no storageClass
    helm install consul stable/consul  --namespace=${targetNamespace}
    # Mongo
    helm install mongo stable/mongodb --namespace=${targetNamespace} --set global.storageClass=${dbClass},usePassword=false
    
    # Kafka
    # Install bitnami repo as charts repository
    helm repo add bitnami https://charts.bitnami.com/bitnami
    
    helm install bootstrap bitnami/kafka --namespace=${targetNamespace}
    
    # Redis
    helm install redis stable/redis --namespace=${targetNamespace} --set usePassword=false
    
    # Get the reportnet charts
    git clone https://github.com/eea/reportnet-helm.git
    
    helm install application-config application-config --namespace=${targetNamespace}
    
    # Remove completed configuration Jobs
    helm uninstall application-config --namespace=${targetNamespace}
    
    helm install api-gateway-preconfig reportnet-api-gateway/preconfig --namespace=${targetNamespace}
    
    # Remove completed configuration Jobs
    helm uninstall api-gateway-preconfig --namespace=${targetNamespace}
    # Install the release if it is not created, otherwise it upgrades the release.
    # -–wait makes that all the created object (Pods, services, statefulsets…) are ready before marking the release as successful
    helm upgrade api-gateway reportnet-api-gateway/service --namespace=${targetNamespace} -i  --wait
    
[/code]  
  
[Edit this section](Kubernetes_deployment_files/edit.md)

## Old installation

[Edit this section](Kubernetes_deployment_files/edit.md)

### Mongo

The variable $TARGET_ENV is expected to be 'reportnet'.
[code] 
    apiVersion: apps/v1beta1
    kind: StatefulSet
    metadata:
      name: mongo
    spec:
      serviceName: "mongo" 
      replicas: 2
      updateStrategy:
        type: RollingUpdate
      template:
        metadata:
          labels:
            role: mongo
            environment: $TARGET_ENV
        spec:
          terminationGracePeriodSeconds: 30
          containers:
            - name: mongo
              image: mongo:4.0.12
              command:
                - mongod
                - "--replSet" 
                - rs0
                - "--bind_ip" 
                - 0.0.0.0
                - "--smallfiles" 
              ports:
                - containerPort: 27017
              volumeMounts:
                - name: mongo-persistent-storage
                  mountPath: /data/db
            - name: mongo-sidecar
              image: cvallance/mongo-k8s-sidecar
              env:
                - name: KUBE_NAMESPACE
                  value: "$TARGET_ENV" 
                - name: MONGO_SIDECAR_POD_LABELS
                  value: "role=mongo,environment=$TARGET_ENV" 
                - name: MONGO_SIDECAR_SLEEP_SECONDS
                  value: "5" 
                - name: MONGO_SIDECAR_UNHEALTHY_SECONDS
                  value: "15" 
                - name: MONGO_PORT
                  value: "27017" 
                - name: KUBERNETES_MONGO_SERVICE_NAME
                  value: "mongo" 
      volumeClaimTemplates:
        - metadata:
            name: mongo-persistent-storage
          spec:
            accessModes:
              - "ReadWriteOnce" 
            storageClassName: database
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

### Microservice Template

This includes the definition of the Service and the Deployment of a Microservice.   
It can be used as well for the deployment of Lightweight Javascript Frontend application.

Still needs some refinement:  
\- Retrieve passwords from Secret  
\- Declare Environment Variables in ConfigMap (to have a more standard deployment file)

The variable $MICROSERVICE_NAME refers to the name of the microservice ('dataset', 'dataflow', etc).  
The variable $TARGET_ENV is expected to be 'reportnet'.  
The variable $NUM_REPLICAS is expected to be the number of replicas to be deployed.  
The variable $MICROSERVICE_IMAGE is expected to be the docker image of the microservice.  
The variable $MICROSERVICE_PORT is expected to be the port where the microservice is listening.
[code] 
    kind: Service
    apiVersion: v1
    metadata:
      name: dataset
      labels:
        name: dataset
        cleanup: "$TARGET_ENV-reportnet3-services" 
    spec:
      ports:
      - protocol: TCP
        port: $MICROSERVICE_PORT
      selector:
        name: $MICROSERVICE_NAME
      type: NodePort
      sessionAffinity: None
    ---
    kind: Deployment
    apiVersion: extensions/v1beta1
    metadata:
      name: dataset
      labels:
        name: dataset
        cleanup: "$TARGET_ENV-reportnet3-services" 
    spec:
      replicas: $NUM_REPLICAS
      template:
        metadata:
          labels:
            name: $MICROSERVICE_NAME
            cleanup: "$TARGET_ENV-reportnet3-services" 
        spec:
          containers:
          - name: dataset
            image: $MICROSERVICE_IMAGE
            imagePullPolicy: Always
            ports:
            - containerPort: $MICROSERVICE_PORT
              protocol: TCP
            readinessProbe:
              tcpSocket:
                port: $MICROSERVICE_PORT
              initialDelaySeconds: 20
              periodSeconds: 10
            livenessProbe:
              tcpSocket:
                port: $MICROSERVICE_PORT
              initialDelaySeconds: 15
              periodSeconds: 20
            env:
            - name: CONSUL_HOST
              value: "$CONSUL_SERVER" 
            - name: CONSUL_PORT
              value: '8500'
            - name: METABASE_CONNECTION_URL
              value: jdbc:postgresql://$POSTGRES_SERVER:5432/metabase
            - name: METABASE_CONNECTION_USER
              value: testuser
            - name: METABASE_CONNECTION_PASSWORD
              valueFrom:
                configMapKeyRef:
                  name: ms-config-map
                  key: pgpassword
            - name: KAFKA_BOOTSTRAP_URL
              value: bootstrap:9092
            - name: MONGO_DB_HOST
              value: mongo
            - name: MONGO_DB_PORT
              value: '27017'
          volumes:
          - name: data-volume
            configMap:
              name: ms-config-map
          restartPolicy: Always
          dnsPolicy: ClusterFirst
      strategy:
        type: RollingUpdate
        rollingUpdate:
          maxUnavailable: 1
          maxSurge: 1
    
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

### Keycloak

This includes the definition of the Keycloak Service acting as IAM for Reportnet3 and managing permissions and user authentication through EULogin.

The variable $TARGET_ENV is expected to be 'reportnet'.  
The variable $KEYCLOAK_NAME is expected to be the docker image of the custom Keycloak (to support integration with EuLogin).  
The variable $TO_BE_RETRIEVED_FROM_SECRET specifies values that should be retrieved from a Secret.
[code] 
    apiVersion: v1
    kind: Service
    metadata:
      name: keycloak
      labels:
        app: keycloak
    spec:
      ports:
      - name: http
        port: 8080
      selector:
        app: keycloak
      type: NodePort
      sessionAffinity: None
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: keycloak
      namespace: $TARGET_ENV
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: keycloak
      template:
        metadata:
          labels:
            app: keycloak
        spec:
          containers:
          - name: keycloak
            image: $KEYCLOAK_IMAGE
            imagePullPolicy: "Always" 
            env:
            - name: KEYCLOAK_USER
              value: "$TO_BE_RETRIEVED_FROM_SECRET" 
            - name: KEYCLOAK_PASSWORD
              value: "$TO_BE_RETRIEVED_FROM_SECRET" 
            - name: PROXY_ADDRESS_FORWARDING
              value: "true" 
            ports:
            - name: http
              containerPort: 8080
            - name: https
              containerPort: 8443
            readinessProbe:
              httpGet:
                path: /auth/realms/master
                port: 8080
    
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

### Kafka

This includes the definition of the Kafka instances. Kafka is composed by three elements: Zookeeper, Kafka Instance and Kafka Manager  
The variable $TARGET_ENV is expected to be 'reportnet'.  
The variable $STORAGE CLASS is expected to be the StorageClass available in the Kubernetes cluster.

[Edit this section](Kubernetes_deployment_files/edit.md)

### Zookeeper

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Zookeeper Config Map
[code] 
    kind: ConfigMap
    metadata:
      name: zookeeper-config
      namespace: $TARGET_ENV
    apiVersion: v1
    data:
      init.sh: |-
        #!/bin/bash
        set -x
    
        cp /usr/etc/zookeeper-config-map/* /usr/etc/zookeeper/
    
        [ -z "$ID_OFFSET" ] && ID_OFFSET=1
        export ZOOKEEPER_SERVER_ID=$((${HOSTNAME##*-} + $ID_OFFSET))
        echo "${ZOOKEEPER_SERVER_ID:-1}" | tee /var/lib/zookeeper/data/myid
        sed -i "s/server\.$ZOOKEEPER_SERVER_ID\=[a-z0-9.-]*/server.$ZOOKEEPER_SERVER_ID=0.0.0.0/" /usr/etc/zookeeper/zoo.cfg
    
      zoo.cfg: |-
        tickTime=2000
        dataDir=/var/lib/zookeeper/data
        dataLogDir=/var/lib/zookeeper/log
        clientPort=2181
        initLimit=5
        syncLimit=2
        heap=512M
        server.1=zoo-0.zoo:2888:3888:participant
        server.2=zoo-1.zoo:2888:3888:participant
        server.3=zoo-2.zoo:2888:3888:participant
        server.4=zoo-3.zoo:2888:3888:participant
        server.5=zoo-4.zoo:2888:3888:participant
    
      log4j.properties: |-
        log4j.rootLogger=INFO, stdout
        log4j.appender.stdout=org.apache.log4j.ConsoleAppender
        log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
        log4j.appender.stdout.layout.ConversionPattern=[%d] %p %m (%c)%n
    
        # Suppress connection log messages, three lines per livenessProbe execution
        log4j.logger.org.apache.zookeeper.server.NIOServerCnxnFactory=WARN
        log4j.logger.org.apache.zookeeper.server.NIOServerCnxn=WARN
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Zookeeper Service
[code] 
    apiVersion: v1
    kind: Service
    metadata:
      name: zoo
      namespace: $TARGET_ENV
    spec:
      ports:
      - port: 2888
        name: peer
      - port: 3888
        name: leader-election
      clusterIP: None
      selector:
        app: zookeeper
        storage: persistent
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Zookeeper Headless Service
[code] 
    apiVersion: v1
    kind: Service
    metadata:
      name: zookeeper
      namespace: $TARGET_ENV
    spec:
      ports:
      - port: 2181
        name: client
        nodePort: 32767
      selector:
        app: zookeeper
      type: NodePort 
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Zookeeper Pod Disruption
[code] 
    apiVersion: policy/v1beta1
    kind: PodDisruptionBudget
    metadata:
      name: zookeeper-pdb
      namespace: $TARGET_ENV
    spec:
      selector:
        matchLabels:
          app: zookeeper
      maxUnavailable: 1
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Zookeeper StatefulSet
[code] 
    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: zoo
    spec:
      selector:
        matchLabels:
          app: zookeeper
          storage: persistent
      serviceName: "zoo" 
      replicas: 3
      updateStrategy:
        type: RollingUpdate
      template:
        metadata:
          labels:
            app: zookeeper
            storage: persistent
        spec:
          affinity:
            podAntiAffinity:
              preferredDuringSchedulingIgnoredDuringExecution:
                - weight: 100
                  podAffinityTerm:
                    labelSelector:
                      matchExpressions:
                        - key: "app" 
                          operator: In
                          values:
                          - zookeeper
                    topologyKey: "failure-domain.beta.kubernetes.io/zone" 
              requiredDuringSchedulingIgnoredDuringExecution:
                - labelSelector:
                    matchExpressions:
                      - key: "app" 
                        operator: In
                        values:
                        - zookeeper
                  topologyKey: "kubernetes.io/hostname" 
          terminationGracePeriodSeconds: 10
          initContainers:
          - name: init-config
            image: solsson/kafka-initutils@sha256:c98d7fb5e9365eab391a5dcd4230fc6e72caf929c60f29ff091e3b0215124713 
            command: ['/bin/bash', '/usr/etc/zookeeper-config-map/init.sh']
            volumeMounts:
            - name: config-map
              mountPath: /usr/etc/zookeeper-config-map
            - name: config
              mountPath: /usr/etc/zookeeper
            - name: data
              mountPath: /var/lib/zookeeper/data
            - name: curl
              mountPath: /etc/prometheus
          containers:
          - name: zookeeper
            image: gcr.io/google_containers/kubernetes-zookeeper:1.0-3.4.10
            env:
            - name: KAFKA_LOG4J_OPTS
              value: -Dlog4j.configuration=file:/etc/kafka/log4j.properties
            command:
            - /opt/zookeeper/bin/zkServer.sh
            - start-foreground
            ports:
            - containerPort: 2181
              name: client
            - containerPort: 2888
              name: peer
            - containerPort: 3888
              name: leader-election
            - name: jmx
              containerPort: 5555
            resources:
              limits:
                memory: 1Gi
              requests:
                cpu: 250m
                memory: 1Gi
            readinessProbe:
              exec:
                command:
                - /bin/sh
                - -c
                - '[ "imok" = "$(echo ruok | nc -w 1 -q 1 127.0.0.1 2181)" ]'
              initialDelaySeconds: 10
              timeoutSeconds: 5
            livenessProbe:
              exec:
                command:
                - /bin/sh
                - -c
                - '[ "imok" = "$(echo ruok | nc -w 1 -q 1 127.0.0.1 2181)" ]'
              initialDelaySeconds: 10
              timeoutSeconds: 5
            volumeMounts:
            - name: config
              mountPath: /usr/etc/zookeeper
            - name: data
              mountPath: /var/lib/zookeeper/data
            - name: curl
              mountPath: /etc/prometheus
          tolerations:
          - effect: NoSchedule
            key: dedicated
            operator: Equal
            value: quorum
          volumes:
          - name: config-map
            configMap:
              name: zookeeper-config
          - name: config
            emptyDir: {}
          - name: curl
            emptyDir: {}
      volumeClaimTemplates:
      - metadata:
          name: data
        spec:
          accessModes: [ "ReadWriteOnce" ]
          storageClassName: $STORAGE_CLASS
          resources:
            requests:
              storage: 1Gi
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

### Kafka Instance

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Instance - Role Base Access
[code] 
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: kafka-labeling
    rules:
    - apiGroups:
      - "" 
      - extensions
      - apps
      resources:
      - pods
      - pods/log
      - pods/attach
      - pods/exec
      - pods/portforward
      - pods/proxy
      verbs:
      - get
      - list
      - watch
      - exec
      - update
      - patch
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: role-labeling
    subjects:
    - kind: ServiceAccount
      name: default
    roleRef:
      kind: Role
      name: kafka-labeling
      apiGroup: "" 
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Instance - Config Map

See [20-broker-config.yaml](Kubernetes_deployment_files/attachments/75543)

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Instance - Headless Service
[code] 
    apiVersion: v1
    kind: Service
    metadata:
      name: broker
    spec:
      ports:
      - port: 9092
      clusterIP: None
      selector:
        app: kafka
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Instance - Bootstrap Service
[code] 
    apiVersion: v1
    kind: Service
    metadata:
      name: bootstrap
    spec:
      ports:
      - port: 9092
      selector:
        app: kafka
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Instance - Pod Disruption
[code] 
    apiVersion: policy/v1beta1
    kind: PodDisruptionBudget
    metadata:
      name: kafka-pdb
    spec:
      selector:
        matchLabels:
          app: kafka
      maxUnavailable: 1
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Instance - StatefulSet
[code] 
    apiVersion: apps/v1
    kind: StatefulSet
    metadata:
      name: kafka
    spec:
      selector:
        matchLabels:
          app: kafka
      serviceName: "broker" 
      replicas: 3
      updateStrategy:
        type: OnDelete
      template:
        metadata:
          labels:
            app: kafka
        spec:
          affinity:
            podAntiAffinity:
              requiredDuringSchedulingIgnoredDuringExecution:
                - labelSelector:
                    matchExpressions:
                      - key: "app" 
                        operator: In
                        values:
                        - kafka
                  topologyKey: "kubernetes.io/hostname" 
              preferredDuringSchedulingIgnoredDuringExecution:
                - weight: 100
                  podAffinityTerm:
                    labelSelector:
                      matchExpressions:
                        - key: "app" 
                          operator: In
                          values:
                          - kafka
                    topologyKey: "failure-domain.beta.kubernetes.io/zone" 
            podAffinity:
              preferredDuringSchedulingIgnoredDuringExecution:
                - weight: 100
                  podAffinityTerm:
                    labelSelector:
                      matchExpressions:
                        - key: "app" 
                          operator: In
                          values:
                          - zookeeper
                    topologyKey: "kubernetes.io/hostname" 
          terminationGracePeriodSeconds: 30
          initContainers:
          - name: init-config
            image: solsson/kafka-initutils@sha256:18bf01c2c756b550103a99b3c14f741acccea106072cd37155c6d24be4edd6e2
            env:
            - name: NODE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: spec.nodeName
            - name: POD_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.name
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
            command: ['/bin/bash', '/etc/kafka-configmap/init.sh']
            volumeMounts:
            - name: configmap
              mountPath: /etc/kafka-configmap
            - name: config
              mountPath: /etc/kafka
            - name: curl
              mountPath: /etc/prometheus
          containers:
          - name: broker
            image: solsson/kafka:1.1@sha256:ba863ca7dc28563930584e37f93d57c2cbf3f46b1c1fa104fe8af7bcc0c31df4
            env:
            - name: KAFKA_HEAP_OPTS
              value : "-Xmx4G -Xms4G" 
            - name: KAFKA_LOG4J_OPTS
              value: -Dlog4j.configuration=file:/etc/kafka/log4j.properties
            - name: KAFKA_JVM_PERFORMANCE_OPTS
              value: -server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:InitiatingHeapOccupancyPercent=35 -XX:+DisableExplicitGC -Djava.awt.headless=true
            - name: JMX_PORT
              value: "5555" 
            - name: KAFKA_OPTS
              value: -javaagent:/etc/prometheus/jmx_prometheus_javaagent-0.2.0.jar=5556:/etc/kafka-configmap/kafka-prometheus-monitoring.yml
            ports:
            - name: inside
              containerPort: 9092
            - name: outside
              containerPort: 9094
            - name: jmx
              containerPort: 5555
            command:
            - sh
            - -c
            - "./bin/kafka-server-start.sh /etc/kafka/server.properties --override log.dirs=/var/lib/kafka/data/topics" 
            resources:
              limits:
                cpu: 2
                memory: 5Gi
              requests:
                cpu: 250m
                memory: 5Gi
            readinessProbe:
              tcpSocket:
                port: 9092
              timeoutSeconds: 1
            volumeMounts:
            - name: configmap
              mountPath: /etc/kafka-configmap
            - name: config
              mountPath: /etc/kafka
            - name: data
              mountPath: /var/lib/kafka/data
            - name: curl
              mountPath: /etc/prometheus
          volumes:
          - name: configmap
            configMap:
              name: broker-config-kafka
          - name: curl
            emptyDir: {}
          - name: config
            emptyDir: {}
      volumeClaimTemplates:
      - metadata:
          name: data
        spec:
          accessModes: ["ReadWriteOnce"]
          storageClassName: $STORAGE_CLASS
          resources:
            requests:
              storage: 10Gi
    
[/code]

[Edit this section](Kubernetes_deployment_files/edit.md)

### Kafka Manager

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Manager - Config Map

See [10kafka-manager-config.yml](Kubernetes_deployment_files/attachments/75544)

[Edit this section](Kubernetes_deployment_files/edit.md)

#### Kafka Manager - Service and Deployment
[code] 
    apiVersion: apps/v1beta2
    kind: Deployment
    metadata:
      name: kafka-manager
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: kafka-manager
      template:
        metadata:
          labels:
            app: kafka-manager
        spec:
          containers:
          - name: kafka-manager
            image: solsson/kafka-manager@sha256:5db7d54cdb642ec5a92f37a869fdcf2aa479b2552e900b2d2b83b38a1806c2de
            ports:
            - containerPort: 80
            env:
            - name: ZK_HOSTS
              value: zookeeper.$TARGET_ENV:2181
            command:
            - ./bin/kafka-manager
            - -Dhttp.port=80
            - -Dplay.http.context=/kafka-manager
            resources:
              limits:
                cpu: 4
                memory: 2Gi
              requests:
                cpu: 50m
                memory: 2Gi
            volumeMounts:
              - mountPath: /opt/kafka-manager/conf/logback.xml
                name: configmap
                subPath: logback.xml
                readOnly: true
          volumes:
            - name: configmap
              configMap:
                name: kafka-manager-configmap
    ---
    kind: Service
    apiVersion: v1
    metadata:
      name: kafka-manager
    spec:
      selector:
        app: kafka-manager
      ports:
      - protocol: TCP
        port: 80
        targetPort: 80
    
[/code]

## Verification notes

This page was last updated November 2019 and is substantially obsolete. The following discrepancies were identified.

**No k8s manifests in the current source tree.** A search of `/Users/janbliki/Documents/GitHub/eea.reportnet3/` finds no `k8s/` or `kubernetes/` directories. The deployment manifests in this page are not present in the source repository in their current form. Deployment is handled via Helm charts in the external `https://github.com/eea/rn3-deploy-scripts` repository, referenced in `Reportnet_Deployment.md`. The inline YAML on this page predates the Helm chart migration.

**Kubernetes version.** The page states "Kubernetes at EEA is version 1.12.7. We are about to launch version 1.24." The source-derived `kubernetes.md` confirms that the observed sandbox cluster was running `v1.12.7-rancher1`. Newer environments listed in `Environments.md` (RN3test, RN3dev) reference Rancher 2 instances, suggesting version 1.24 or later has since been deployed for some environments, but this is not confirmed by source inspection.

**Deprecated Kubernetes API versions.** The Zookeeper and Kafka manifests use `apiVersion: apps/v1beta1` and `apiVersion: policy/v1beta1`, which were removed in Kubernetes 1.16 and 1.25 respectively. The Microservice Template and Kafka Manager use `apiVersion: extensions/v1beta1` and `apiVersion: apps/v1beta2`, both of which were removed in Kubernetes 1.16. These manifests cannot be applied to any cluster running Kubernetes 1.16 or later without updating the API versions.

**Kafka image.** The Kafka StatefulSet uses `solsson/kafka:1.1`, which corresponds to Apache Kafka 1.1. The source-derived `kubernetes.md` records Kafka 2.5.0 (`bitnami/kafka:2.5.0-debian-10-r91`) as the version in use. The Kafka Manager image (`solsson/kafka-manager`) is a community image that is no longer maintained.

**Zookeeper image.** The StatefulSet uses `gcr.io/google_containers/kubernetes-zookeeper:1.0-3.4.10` (Zookeeper 3.4.10). The source-derived `kubernetes.md` records Zookeeper 3.6.1 in deployment.

**MongoDB.** The MongoDB StatefulSet uses `mongo:4.0.12`. `Environments.md` lists MongoDB 3.6 in the "Side Services version" section, and the `Reportnet_Deployment.md` page deploys via `stable/mongodb-replicaset`. Neither matches 4.0.12.

**Helm repository URL.** The chart repository URL `https://kubernetes-charts.storage.googleapis.com/` is obsolete; the stable charts repository was deprecated in November 2020 and this URL no longer serves charts. The `Reportnet_Deployment.md` page already notes this for some charts.

**Missing services.** The manifests cover only infrastructure components and a generic microservice template. The Orchestrator Service and Inspire Harvester — both present in the current source tree — are not mentioned. Neither is the Citus PostgreSQL cluster, which is the dataset record store and visible in the deployment maps in `Environments.md`.
