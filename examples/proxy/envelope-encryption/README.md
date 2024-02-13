# AMQ Streams Proxy Envelope Encryption Filter Examples

The Envelope Encryption filter which provides an Encryption-at-Rest solution for Apache Kafka(tm) which is transparent to both clients and brokers. The filter takes
responsibilty to encrypt messages that are sent by producing applications so the Kafka Broker never sees the plain text content of the messages.  The filter also takes responsibilty
to decrypt the message before they are returned to consuming applications.

In this directory, you'll find examples that help you deploy AMQ Stream Proxy with the Envelope Encryption Filter to your OpenShift Cluster so that you my try out the feature together
with you own application.

The filter relies on a Key Management System (KMS). The role of the KMS is to provide cryptographic functions and act as a repository of key-material. The KMS is *not* part of AMQ Streams
Proxy.  It is external must be provided by the deployer of the system.  For this Tech Preview release, only HashiCorp Vault is supported.

You need to prepare a HashiCorp Vault instance now:

* If you have an instance of HashiCorp Vault already in your organisation, you may use it after applying some [configuration](./PREPARE_KMS.md#using-an-existing-vault-instance).
* Otherwise, there are [deployment instructions](./PREPARE_KMS.md#deploying-hashicorp-for-development) to install an *ephemeral development* instance on your OpenShift Cluster.

Once you have a Vault instance prepare, you can proceed to deploy one of the examples.  

* [Cluster IP](./cluster-ip)
* [External Load Balancer](./load-balancer)

