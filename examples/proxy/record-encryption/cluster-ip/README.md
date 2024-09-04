# Streams for Apache Kafka Proxy Record Encryption, exposed using Cluster-IP

In this example, an instance of Apache Kafka is deployed using AMQ Stream.  The instance is proxied using
Streams for Apache Kafka Proxy is configured with Record Encryption.  The proxy is exposed within the cluster using a
Cluster-IP.

# Prerequisites

* [KMS is prepared](../PREPARE_KMS.md).
* Vault CLI or AWS CLI 

* Administrative access to the OpenShift Cluster being used to evaluate AMQ Stream Proxy
* OpenShift CLI (oc)
* Streams for Apache Kafka Operator (installed namespace wide)

# Deploying the Example

1. Edit `cluster-ip/proxy/proxy-config.yaml` and `base/proxy/kustomization.yaml`. Uncomment either the
   configuration for Vault or AWS, depending on your KMS provider.

2. Deploy the Example
   ```sh
   oc apply -k cluster-ip
   ```

# Try out the example

1. Create a key for topic `trades` in the KMS:
   ```sh
   # For Vault
   vault write -f transit/keys/KEK_trades
   # For AWS
   aws kms create-alias --alias-name alias/KEK_trades --target-key-id $(aws kms create-key | jq -r '.KeyMetadata.KeyId')
   ```
2. Create a topic `trades` on the cluster, via the proxy:
   ```sh
   oc run -n kafka-proxy -qi create-topic --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-topics.sh --bootstrap-server proxy-service:9092 --create -topic trades
   ```
3. Produce some messages to the topic:
   ```sh
   echo 'IBM:100\nAPPLE:99' | oc run -n kafka-proxy -qi proxy-producer --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server proxy-service:9092 --topic trades
   ```
4. Consume messages *direct* from the Kafka Cluster, showing that they are encrypted.
   ```sh
    oc run -n kafka cluster-consumer -qi --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic trades --from-beginning --timeout-ms 10000
   ```
5. Consume messages from the *proxy* showing they get decrypted automatically.   
   ```sh
    oc run -n kafka-proxy proxy-consumer -qi --image=registry.redhat.io/amq-streams/kafka-37-rhel9:2.7.0 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server proxy-service:9092 --topic trades --from-beginning --timeout-ms 10000
   ```   

# Cleaning up

When you have finished with this example, you can remove it from the OpenShift Cluster like this:

```sh
oc delete -k cluster-ip
```

To remove the KMS configuration, see [the KMS cleanup instructions](../PREPARE_KMS.md#cleaning-up).

