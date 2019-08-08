#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
STUNNEL_DIR=${SCRIPT_DIR}/stunnel-scripts
S2I_DIR=${SCRIPT_DIR}/s2i-scripts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

mkdir $KAFKA_HOME
mkdir $STUNNEL_HOME
mkdir $S2I_HOME
mkdir -p -m g+rw /usr/local/var/run/

tar xvfz "${SOURCES_DIR}/kafka.tar.gz" -C ${KAFKA_HOME} --strip-components=1

mkdir /opt/prometheus
mkdir /opt/prometheus/config
cp -r ${SOURCES_DIR}/jmx_prometheus_javaagent.jar /opt/prometheus/jmx_prometheus_javaagent.jar
cp -r ${SOURCES_DIR}/kafka-agent.jar ${KAFKA_HOME}/libs

chown -R jboss:root ${KAFKA_HOME}
chmod -R 0755 ${KAFKA_HOME}
chown -R jboss:root /opt/prometheus
chmod -R 0755 /opt/prometheus

cp -r ${SCRIPTS_DIR}/* ${KAFKA_HOME}/
chmod -R 755 ${KAFKA_HOME}

cp -r ${STUNNEL_DIR}/* ${STUNNEL_HOME}/
chmod -R 755 ${STUNNEL_HOME}

cp -r ${S2I_DIR}/* ${S2I_HOME}/
chmod -R 755 ${S2I_HOME}

mkdir -p ${PRODUCT_LICENSE_DIR}
cp ${KAFKA_HOME}/docs/licen*/* ${PRODUCT_LICENSE_DIR}
