#!/bin/bash

set -e

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

mkdir ${PRODUCT_LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tgz -C ${PRODUCT_LICENSE_DIR}
 
mv "${SOURCES_DIR}/cluster-operator.jar" /
