#!/bin/bash
set -e

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# Add strimzi user with UID 1001
# The user is in the group 0 to have access to the mounted volumes and storage
useradd -r -m -u 1001 -g 0 strimzi

# untar the artifact containing license information
mkdir -p ${PRODUCT_LICENSE_DIR}
mv ${SOURCES_DIR}/kafka-bridge-licenses.tar.gz ${LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/kafka-bridge-licenses.tar.gz -C ${PRODUCT_LICENSE_DIR}

# create destination folder of scripts, jars and config
mkdir -p ${STRIMZI_HOME}

# untar archive/artifact with bridge scripts and jars
tar xvfz "${SOURCES_DIR}/kafka-bridge.tar.gz" -C ${STRIMZI_HOME} --strip-components=1

chmod -R 0755 ${STRIMZI_HOME}/bin
chmod -R 0755 ${STRIMZI_HOME}/libs