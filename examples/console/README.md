# Console Resources

This folder contains example resources that may be used to deploy the AMQ Streams Console

* [Prometheus](./resources/prometheus): OpenShift resources that may be used to deploy a Prometheus operator along with a Prometheus instance and associated configuration. These resources are configured to scrape the metrics from OpenShift and Kafka instances.
* [Kafka](./resources/kafka): Deploys an example Kafka cluster, metrics export configuration, and a KafkaUser used by the AMQ Streams Console to connect to the cluster.
* [Console](./resources/console): Resources to deploy the AMQ Streams Console, its required service account and security bindings, and networking configuration to access the user interface.
