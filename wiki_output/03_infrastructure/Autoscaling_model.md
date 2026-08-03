---
title: "Autoscaling model"
---

# Autoscaling model

List of pods:

Resource metrics: 

  * CPU: 50% 
  * Memory: 50%

Custom metrics: 
  * pod metrics: packets-per-second (1k)
  * object metrics: requests-per-second (10k)



external metrics:  
hystrix should be able to do things by himself?  
Is kafka handling: kafka_consumer_heartbeat_response_time_max_seconds The max time taken to receive a response to a heartbeat request ?

kafka_consumer_commit_latency_avg_seconds The average time taken for a commit request.  
kafka_consumer_commit_latency_max_seconds The max time taken for a commit request.  
kafka_consumer_fetch_latency_avg_seconds The average time taken for a fetch request.  
kafka_consumer_fetch_latency_max_seconds The max time taken for a fetch request.
[code] 
    What's the difference between fetch and commit?
[/code]

jvm_memory_used_bytes The amount of used memory // jvm_memory_committed_bytes The amount of memory in bytes that is committed for the Java virtual machine to use  
kafka_consumer_fetch_latency_max_seconds The max time taken for a fetch request

## Verification notes

This page is a working notes document — a rough list of candidate metrics and open questions — rather than a specification. There are no implemented HPA configurations to compare against: a search of the source tree at `/Users/janbliki/Documents/GitHub/eea.reportnet3/` found no Kubernetes HPA manifests (no files matching `*hpa*` or containing `HorizontalPodAutoscaler`). The source-derived `kubernetes.md` explicitly notes that no Kubernetes resource requests or limits are configured on any service Deployments, which means Kubernetes-based autoscaling cannot function without those values being set first. The metric names listed (`kafka_consumer_heartbeat_response_time_max_seconds`, `jvm_memory_used_bytes`, and so on) are standard Prometheus JVM and Kafka consumer metrics that would be valid inputs to an HPA if resource requests were configured, but their use here is speculative. The question about whether Hystrix handles autoscaling reflects a misunderstanding — Hystrix is a circuit breaker, not an autoscaler.
