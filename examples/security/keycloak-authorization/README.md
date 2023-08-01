# Keycloak authorization example

This folder contains an example `Kafka` custom resource configured for OAuth 2.0 token-based authorization using Keycloak. The example resource is configured with:
- `keycloak` authorization
- the corresponding `oauth` authentication
The folder also contains a Keycloak realm export to import into your Keycloak instance to support the example.

Full instructions for Trying Red Hat Single Sign-On Authorization Services are described in the [documentation for deploying and managing AMQ Streams on OpenShift](https://access.redhat.com/documentation/en-us/red_hat_amq_streams/).

- [kafka-authz-realm.json](./kafka-authz-realm.json)
  - The Keycloak realm export file
- [kafka-ephemeral-oauth-single-keycloak-authz.yaml](./kafka-ephemeral-oauth-single-keycloak-authz.yaml)
  - The Kafka CR that defines a single-node Kafka cluster with `oauth` authentication and `keycloak` authorization,
    using the `kafka-authz` realm.
- [kafka-ephemeral-oauth-single-keycloak-authz-metrics.yaml](./kafka-ephemeral-oauth-single-keycloak-authz-metrics.yaml)
  - The Kafka CR that defines a single-node Kafka cluster with `oauth` authentication and `keycloak` authorization, using the `kafka-authz` realm.
