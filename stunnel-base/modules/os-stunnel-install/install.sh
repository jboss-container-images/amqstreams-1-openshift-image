#!/bin/bash

set -e

mkdir $STUNNEL_HOME
mkdir -p -m g+rw /usr/local/var/run/

chown -R jboss:root ${STUNNEL_HOME}
chmod 0755 ${STUNNEL_HOME}
chmod -R g+rwX ${STUNNEL_HOME}
