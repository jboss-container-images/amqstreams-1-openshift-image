#!/usr/bin/env bash

set -x

# Parameters:
# $1: Path to the new truststore
# $2: Truststore password
# $3: Public key to be imported
# $4: Alias of the certificate
function create_truststore {
   keytool -keystore $1 -storepass $2 -noprompt -alias $4 -import -file $3 -storetype PKCS12
}

# Parameters:
# $1: Path to the new keystore
# $2: Truststore password
# $3: Public key to be imported
# $4: Private key to be imported
# $5: CA public key to be imported
# $6: Alias of the certificate
function create_keystore {
   RANDFILE=/tmp/.rnd openssl pkcs12 -export -in $3 -inkey $4 -name topic-operator -password pass:$2 -out $1
}

echo "Preparing certificates for internal communication"
STORE=/tmp/topic-operator/replication.truststore.p12
for CRT in /etc/tls-sidecar/cluster-ca-certs/*.crt; do
  ALIAS=$(basename "$CRT" .crt)
  echo "Adding $CRT to truststore $STORE with alias $ALIAS"
  create_truststore "$STORE" "$CERTS_STORE_PASSWORD" "$CRT" "$ALIAS"
done

create_keystore /tmp/topic-operator/replication.keystore.p12 $CERTS_STORE_PASSWORD \
    /etc/tls-sidecar/eo-certs/entity-operator.crt \
    /etc/tls-sidecar/eo-certs/entity-operator.key \
    /etc/tls-sidecar/cluster-ca-certs/ca.crt \
    entity-operator
echo "Preparing certificates for internal communication is complete"
