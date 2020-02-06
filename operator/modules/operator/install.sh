#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# untar the artifact containing license information
mkdir -p ${PRODUCT_LICENSE_DIR}
mv ${SOURCES_DIR}/*.tar.gz ${LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tar.gz -C ${PRODUCT_LICENSE_DIR}

# create destination folder of scripts and jars
mkdir -p ${STRIMZI_HOME}

# unzip all archives/artifacts with operators scripts and jars
for z in ${SOURCES_DIR}/*-dist.zip;
do
    unzip -qo $z -d ${STRIMZI_HOME}/;
done

# copy module related scripts
cp -r ${SCRIPTS_DIR}/* ${STRIMZI_HOME}/bin

chmod -R 0755 ${STRIMZI_HOME}/bin
chmod -R 0755 ${STRIMZI_HOME}/lib