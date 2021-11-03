# AMQ Streams Drain Cleaner

AMQ Streams Drain Cleaner is a utility which helps with moving the Kafka pods [deployed by AMQ Streams]( https://access.redhat.com/documentation/en-us/red_hat_amq_streams/2.0/html/deploying_and_upgrading_amq_streams_on_openshift) from Kubernetes nodes which are being drained.
It is useful if you want the AMQ Streams operator to move the pods instead of Kubernetes itself.
The advantage of this approach is that the AMQ Streams operator makes sure that no Kafka topics become under-replicated during the node draining.

For more information on deploying and using the Drain Cleaner with AMQ Streams, see [Deploying and upgrading AMQ Streams on OpenShift](https://access.redhat.com/documentation/en-us/red_hat_amq_streams/2.0/html-single/deploying_and_upgrading_amq_streams_on_openshift)
