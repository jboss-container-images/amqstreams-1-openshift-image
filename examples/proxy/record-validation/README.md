# Streams for Apache Kafka Proxy Record Validation Filter Examples

The Record Validation filter ensures that all records produced to a kafka topic conform to an expected schema.
Records that don't conform to the expected schema will not be sent to the broker. Instead, the producer will
receive an error response.  Record Validation filter currently support JSON format records.  It enforces JSON
schemas.

To use the Record Validation filter, you must have a JSON schema defined for records published to the topic.
The JSON schema need to be stored in an [Apicurio Registry](https://docs.redhat.com/en/documentation/red_hat_build_of_apicurio_registry/).

In this directory, you'll find examples that help you deploy Streams for Apache Kafka with the Record Validation Filter
to your OpenShift Cluster so that you may try out the feature together with you own application.
The example provides a development instance of Apicurio Registry.

* [Cluster IP](./cluster-ip)
* [External Load Balancer](./load-balancer)

