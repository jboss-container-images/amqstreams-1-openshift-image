# AMQ Streams Proxy Envelope Encryption, exposed using Cluster-IP

In this example, an instance of Apache Kafka is deployed using AMQ Stream.  The instance is proxied using
AMQ Streams Proxy configured with Envelope Encyption.  The proxy is exposed within the cluster using a
Cluster-IP.

# Prerequsistes

* [KMS is prepared](../PREPARE_KMS.md).
* Vault CLI

* Administrative access to the OpenShift Cluster being used to evaluate AMQ Stream Proxy
* OpenShift CLI (oc)
* AMQ Stream Operator installed namespace wide

# Deploying the Example

1. Deploy the Example
   ```sh
   oc apply -k cluster-ip
   ```

# Try out the example

1. Create a key for topic `trades` in the KMS:
   ```
   vault write -f transit/keys/KEK_trades
   ```
2. Create a topic `trades` on the cluster, via the proxy:
   ```
   oc run -n proxy -qi proxy-producer --image=registry.redhat.io/amq-streams/kafka-36-rhel8:2.6.0-4 --rm=true --restart=Never -- kafka-topics.sh --bootstrap-server proxy-service:9092 --create -topic trades
   ```
3. Produce some messages to the topic:
   ```
   echo 'IBM:100\nAPPLE:99' | oc run -n proxy -qi proxy-producer --image=registry.redhat.io/amq-streams/kafka-36-rhel8:2.6.0-4 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server proxy-service:9092 --topic trades   
   ```
4. Consume messages *direct* from the Kafka Cluster, showing that they are encrypted.
   ```
    oc run -n kafka cluster-consumer -qi --image=registry.redhat.io/amq-streams/kafka-36-rhel8:2.6.0-4 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic trades --from-beginning --timeout-ms 10000
   ```
5. Consume messages from the *proxy* showing they get decrypted automatically.   
   ```
    oc run -n proxy proxy-consumer -qi --image=registry.redhat.io/amq-streams/kafka-36-rhel8:2.6.0-4 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server proxy-service:9092 --topic trades --from-beginning --timeout-ms 10000
   ```   

# Cleaning up

When you have finished with this example, you can remove it from the OpenShift Cluster like this:

```sh
oc apply -d cluster-ip
```

To remove the KMS configuration, see [the KMS cleanup instructions](../PREPARE_KMS.md#cleaning-up).

