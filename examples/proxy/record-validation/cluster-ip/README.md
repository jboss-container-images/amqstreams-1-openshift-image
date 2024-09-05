# Streams for Apache Kafka Proxy Record Validation, exposed using Cluster-IP

In this example, an instance of Apache Kafka is deployed to an OpenShift cluster using Streams for Apache Kafka, alongside Apicurio Registry, which is also deployed to the cluster.

The Streams for Apache Kafka Proxy is deployed with configuration to perform record validation.  The configuration ensures that 
any records sent to a topic called `people` adhere to a `person` schema.

Finally, Kafka command line tools are used to send valid and invalid records to the `people` topic, so the effects of the validation can be observed.
so that the effects of the validation can be observed.

# Prerequisites

* Administrative access to the OpenShift Cluster being used to evaluate Streams for Apache Kafka Proxy
* Streams for Apache Kafka Operator (installed cluster wide)
* Red Hat build of Apicurio Registry Operator (installed cluster wide)
* OpenShift CLI (`oc`)
* `cURL`
* Apache Kafka CLI tools (`kafka-topics.sh`, `kafka-console-producer.sh`, and `kafka-console-consumer.sh`) found in the `bin` directory of the Streams for Apache Kafka on RHEL distribution

# Deploying the Example

1. Deploy the Example:
   ```sh
   oc apply -k cluster-ip
   oc wait deployment/proxy --for=condition=Available=True --timeout=300s -n kafka-proxy
   ```

2. Create the example schema in the registry:

   ```sh
   REGISTRY_URL=http://$(oc get apicurioregistries.registry.apicur.io -n schema-registry registry --template='{{.status.info.host}}')
   curl -X POST ${REGISTRY_URL}/apis/registry/v2/groups/default/artifacts -H "Content-Type: application/json; artifactType=JSON" -H "X-Registry-ArtifactId: Person" --data @schemas/person.schema.json
   ```

# Try out the example

1. Create a topic `people` on the cluster, via the proxy:
   ```sh
   oc run -n kafka-proxy -qi create-topic --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-topics.sh --bootstrap-server proxy-service:9092 --create -topic people
   ```
2. Produce a record to the topic with a record value that matches the schema.
   ```sh
   cat record-examples/valid-person.json | oc run -n kafka-proxy -qi proxy-producer --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server proxy-service:9092 --topic people --sync
   ```
3. Consume messages showing the record reached the broker.
   ```sh
    oc run -n kafka-proxy proxy-consumer -qi --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server proxy-service:9092 --topic people --from-beginning --timeout-ms 10000
   ```   
4. Produce invalid records to the topic.  You will see the producer reject the invalid records with an exception.
   ```sh
   cat record-examples/invalid-person-invalid-age.json | oc run -n kafka-proxy -qi proxy-producer --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server proxy-service:9092 --topic people --sync
   ```
   
   ```sh
   cat record-examples/invalid-person-malformed.json | oc run -n kafka-proxy -qi proxy-producer --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server proxy-service:9092 --topic people --sync
   ```

5. Consume messages showing that no rejected records reached the broker.
   ```sh
    oc run -n kafka-proxy proxy-consumer -qi --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server proxy-service:9092 --topic people --from-beginning --timeout-ms 10000
   ```   

# Cleaning up

When you have finished with this example, you can remove it from the OpenShift Cluster:

```sh
oc delete -k cluster-ip
```
