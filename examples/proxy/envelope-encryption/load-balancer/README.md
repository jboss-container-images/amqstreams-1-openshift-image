# AMQ Streams Proxy Envelope Encryption, exposed by External Load Balancer

In this example, an instance of Apache Kafka is deployed using AMQ Stream.  The instance is proxied using
AMQ Streams Proxy configured with Envelope Encyption.  The proxy is exposed off cluster using a Kubernetes
Service.

# Prerequsistes

* [KMS is prepared](../PREPARE_KMS.md).
* Vault CLI

* Administrative access to the OpenShift Cluster being used to evaluate AMQ Stream Proxy
* OpenShift CLI (oc)
* AMQ Stream Operator is installed namespace wide
* Apache Kafka CLI

# Deploying the Example

1. Deploy the Example
   ```sh
   oc apply -k load-balancer
   ```
2. Get the external address of the proxy service
   ```sh
   LOAD_BALANCER_ADDRESS=$(oc get service -n proxy proxy-service --template='{{(index .status.loadBalancer.ingress 0).hostname}}')
   ```
3. Now update the `brokerAddressPattern:` to match the `LOAD_BALANCER_ADDRESS`.
   ```sh
     sed -i  "s/\(brokerAddressPattern:\).*$/\1 ${LOAD_BALANCER_ADDRESS}/" load-balancer/proxy/proxy-config.yaml
   ```
4. Reapply and bounce
   ```sh
      oc apply -k load-balancer && oc delete pod -n proxy --all
   ```

# Try out the example

1. Create a key for topic `trades` in the KMS:
   ```
   vault write -f transit/keys/KEK_trades
   ```
2. Create a topic `trades` on the cluster, via the proxy:
   ```
   kafka-topics.sh --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --create -topic trades
   ```
   Note it may take a minute or two for `${LOAD_BALANCER_ADDRESS}` to resolve in your environment and for the load balancer to begin routing
   network traffic.
4. Produce some messages to the topic
   ```
   echo 'IBM:100\nAPPLE:99' | kafka-console-producer --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic trades
   ```
5. Consume messages direct from the Kafka Cluster, showing that they are encrypted.
   ```
    oc run -n kafka cluster-consumer -qi --image=registry.redhat.io/amq-streams/kafka-36-rhel8:2.6.0-4 --rm=true --restart=Never -- ./bin/kafka-console-consumer.sh  --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic trades --from-beginning --timeout-ms 10000
   ```
6. Consume messages from the proxy showing they are decrypted.   
   ```
    kafka-console-consumer --bootstrap-server ${LOAD_BALANCER_ADDRESS}:9092 --topic trades --from-beginning --timeout-ms 10000
   ```   

# Cleaning up

When you have finished with this example, you can remove it from the OpenShift Cluster like this:

```sh
oc apply -d load-balancer
```

To remove the KMS configuration, see [the KMS cleanup instructions](../PREPARE_KMS.md#cleaning-up).

