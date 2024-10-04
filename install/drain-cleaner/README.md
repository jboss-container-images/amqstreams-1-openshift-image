# Streams for Apache Kafka Drain Cleaner

Streams for Apache Kafka Drain Cleaner is a utility which helps with moving the Kafka pods deployed by  Streams for Apache Kafka from Kubernetes nodes which are being drained.
It is useful if you want the Streams for Apache Kafka operator to move the pods instead of Kubernetes itself.
The advantage of this approach is that the Streams for Apache Kafka operator makes sure that no Kafka topics become under-replicated during the node draining.


For more information and installation guide, see [documentation for Streams for Apache Kafka on OpenShift](https://access.redhat.com/documentation/en-us/red_hat_amq_streams/).
