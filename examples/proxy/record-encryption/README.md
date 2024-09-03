# Streams for Apache Kafka Proxy Record Encryption Filter Examples

The Record Encryption filter provides an Encryption-at-Rest solution for Apache Kafka(tm) which is transparent to both clients and brokers. The filter takes
responsibility to encrypt messages that are sent by producing applications so the Kafka Broker never sees the plain text content of the messages.  The filter also takes responsibility
to decrypt the message before they are returned to consuming applications.

In this directory, you'll find examples that help you deploy AMQ Stream Proxy with the Record Encryption Filter to your OpenShift Cluster so that you may try out the feature together
with you own application.

The filter relies on a Key Management System (KMS). The role of the KMS is to provide cryptographic functions and act as a repository of key-material. The KMS is *not* part of Streams for Apache Kafka.  It is external and must be provided by the deployer of the system.  For this Technology Preview release, you can choose
between HashiCorp Vault&#8482; or AWS KMS&#8482;.


Follow the [KMS preparation instructions](./PREPARE_KMS.md) then proceed to deploy one of the examples.  

* [Cluster IP](./cluster-ip)
* [External Load Balancer](./load-balancer)

