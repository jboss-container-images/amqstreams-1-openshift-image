#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# Add strimzi user with UID 1001
useradd -r -m -u 1001 -g 0 strimzi

# untar the artifact containing license information
mkdir -p ${PRODUCT_LICENSE_DIR}
mv ${SOURCES_DIR}/drain-cleaner-licenses.tar.gz ${LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/drain-cleaner-licenses.tar.gz -C ${PRODUCT_LICENSE_DIR} --no-same-owner

mkdir -p ${STRIMZI_HOME}

# copy jar and execution script
cp ${SOURCES_DIR}/drain-cleaner.jar /
cp ${SCRIPT_DIR}/application /

chmod -R 0755 ${STRIMZI_HOME}/
chmod 0755 /application
