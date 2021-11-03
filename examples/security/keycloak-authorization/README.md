# Keycloak authorization example

This folder contains an example `Kafka` custom resource configured for OAuth 2.0 token-based authorization using Keycloak. The example resource is configured with: 
- `keycloak` authorization 
- the corresponding `oauth` authentication
The folder also contains a Keycloak realm export to import into your Keycloak instance to support the example.

Full instructions for the example are available in the [AMQ Streams on OpenShift documentation](https://access.redhat.com/documentation/en-us/red_hat_amq_streams/2.0/html-single/using_amq_streams_on_openshift#proc-oauth-authorization-keycloak-example_str).

* [kafka-authz-realm.json](./kafka-authz-realm.json)
    * The Keycloak realm export file
* [kafka-ephemeral-oauth-single-keycloak-authz.yaml](./kafka-ephemeral-oauth-single-keycloak-authz.yaml)
    * The Kafka CR that defines a single-node Kafka cluster with `oauth` authentication and `keycloak` authorization,
    using the `kafka-authz` realm. See [AMQ Streams on OpenShift documentation](https://access.redhat.com/documentation/en-us/red_hat_amq_streams/2.0/html/using_amq_streams_on_openshift#proc-oauth-authorization-keycloak-example_str) for proper preparation and deployment.
