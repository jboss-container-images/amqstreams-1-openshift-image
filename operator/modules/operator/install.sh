#!/bin/bash
set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# Add strimzi user with UID 1001
# The user is in the group 0 to have access to the mounted volumes and storage
useradd -r -m -u 1001 -g 0 strimzi

# untar the artifact containing license information
mkdir -p ${PRODUCT_LICENSE_DIR}
mv ${SOURCES_DIR}/*.tar.gz ${LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tar.gz -C ${PRODUCT_LICENSE_DIR} --no-same-owner

# create destination folder of scripts and jars
mkdir -p ${STRIMZI_HOME}

# unzip all archives/artifacts with operators scripts and jars
for z in ${SOURCES_DIR}/*-dist.zip;
do
    unzip -qo $z -d ${STRIMZI_HOME}/;
done

# extract all the operator related scripts
unzip ${SOURCES_DIR}/strimzi-operator-scripts.zip -d ${SCRIPTS_DIR}

# patch to remove "tini"
FILES=$(find ${SCRIPTS_DIR} -type f -name "*.sh")
for f in $FILES
do
  sed -i 's/\/usr\/bin\/tini -w -e 143 -- //' $f
done

# copy module related scripts
cp -r ${SCRIPTS_DIR}/* ${STRIMZI_HOME}/bin

chmod -R 0755 ${STRIMZI_HOME}/bin
chmod -R 0755 ${STRIMZI_HOME}/lib
