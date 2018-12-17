#!/bin/bash

set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts

mkdir $STUNNEL_HOME
mkdir -p -m g+rw /usr/local/var/run/

cp -r ${SCRIPTS_DIR}/* ${STUNNEL_HOME}/

chown -R jboss:root ${STUNNEL_HOME}
chmod 0755 ${STUNNEL_HOME}
chmod -R g+rwX ${STUNNEL_HOME}
