# Streams for Apache Kafka Proxy Record Validation, exposed by External Load Balancer

In this example, an instance of Apache Kafka is deployed using Streams for Apache Kafka.  Apicurio
Registry is deployed to the cluster too.

The Streams Proxy is deployed with configuration to perform record validation.  The configuration ensures that
any records sent to a topic called `people` adhere to a `person` schema.

Finally, kafka command line tools (run off cluster) are used to send valid and invalid record to the `people` topic
so that the effects of the validation can be observed.

# Prerequisites

* [KMS is prepared](../PREPARE_KMS.md).
* Vault CLI

* Administrative access to the OpenShift Cluster being used to evaluate AMQ Stream Proxy
* OpenShift CLI (oc)
* Streams for Apache Kafka Operator is installed namespace wide
* Apache Kafka CLI tools (`kafka-topics.sh`, `kafka-console-producer.sh`, and `kafka-console-consumer.sh`) found in the `bin` directory of the Streams for Apache Kafka on RHEL distribution.

# Deploying the Example

1. Deploy the Example
   ```sh
   oc apply -k load-balancer
   ```
2. Get the external address of the proxy service
   ```sh
   LOAD_BALANCER_ADDRESS=$(oc get service -n kafka-proxy proxy-service --template='{{(index .status.loadBalancer.ingress 0).hostname}}')
   ```
3. Now update the `brokerAddressPattern:` to match the `LOAD_BALANCER_ADDRESS`:
   ```sh
     sed -i  "s/\(brokerAddressPattern:\).*$/\1 ${LOAD_BALANCER_ADDRESS}/" load-balancer/proxy/proxy-config.yaml
   ```
4. Reapply and bounce:
   ```sh
      oc apply -k load-balancer && oc delete pod -n proxy --all
   ```

5. Create the example schema in the registry:

   ```sh
   REGISTRY_URL=http://$(oc get apicurioregistries.registry.apicur.io -n schema-registry registry --template='{{.status.info.host}}')
   curl -X POST ${REGISTRY_URL}/apis/registry/v2/groups/default/artifacts -H "Content-Type: application/json; artifactType=JSON" -H "X-Registry-ArtifactId: Person" --data @schemas/person.schema.json
   ```

# Try out the example

1. Create a topic `people` on the cluster, via the proxy:
   ```sh
   kafka-topics.sh --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --create -topic people
   ```
   Note it may take a minute or two for `${LOAD_BALANCER_ADDRESS}` to resolve in your environment and for the load balancer to begin routing
   network traffic.

2. Produce a record to the topic with a record value that matches the schema.
   ```sh
   cat record-examples/valid-person.json |  kafka-console-producer.sh --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic people --sync
   ```
3. Consume messages showing the record reached the broker.
   ```sh
    kafka-console-consumer.sh  --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic people --from-beginning --timeout-ms 10000
   ```   
4. Produce invalid records to the topic.  You will see the producer reject the invalid records with an exception.
   ```sh
   cat record-examples/invalid-person-invalid-age.json | kafka-console-producer.sh --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic people --sync
   ```

   ```sh
   cat record-examples/invalid-person-malformed.json | kafka-console-producer.sh --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic people --sync
   ```

5. Consume messages showing that no rejected records reached the broker.
   ```sh
    kafka-console-consumer.sh  --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic people --from-beginning --timeout-ms 10000
   ```   

# Cleaning up

When you have finished with this example, you can remove it from the OpenShift Cluster:

```sh
oc delete -k load-balancer
```

