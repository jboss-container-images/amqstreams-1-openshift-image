#!/bin/bash
set -e

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

mkdir ${PRODUCT_LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/*.tgz -C ${PRODUCT_LICENSE_DIR}

# copy module related scripts
cp -r ${SCRIPTS_DIR}/* /bin

# unzip all archives with operators scripts and jars
unzip -qo '${SOURCES_DIR}/*-dist.zip'

# copy operators related scripts
cp -r ${SOURCES_DIR}/bin/* /bin
# copy operators related jars
cp -r ${SOURCES_DIR}/lib/* /lib

chmod -R 0755 bin
chmod -R 0755 lib