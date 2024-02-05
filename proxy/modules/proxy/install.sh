#!/bin/bash
set -eo pipefail

SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses
PRODUCT_LICENSE_DIR=${LICENSE_DIR}/${COM_REDHAT_COMPONENT}

# Add kroxylicious user with UID 1001
# The user is in the group 0 to have access to the mounted volumes and storage
useradd -r -m -u 1001 -g 0 kroxylicious

# untar the artifact containing license information
mkdir -p ${PRODUCT_LICENSE_DIR}
mv ${SOURCES_DIR}/kroxylicious-app-licenses.tar.gz ${LICENSE_DIR}
tar -xvzf ${LICENSE_DIR}/kroxylicious-app-licenses.tar.gz -C ${PRODUCT_LICENSE_DIR} --no-same-owner

# create destination folder of scripts, jars and config
mkdir -p ${KROXYLICIOUS_HOME}

# unzip archive/artifact with bridge scripts and jars
TMP=$(zipinfo -1  ${SOURCES_DIR}/kroxylicious-app.zip | grep -oE '^[^/]+' | uniq)
unzip ${SOURCES_DIR}/kroxylicious-app.zip
mv ${TMP}/* ${KROXYLICIOUS_HOME}/

chmod -R 0755 ${KROXYLICIOUS_HOME}/bin
chmod -R 0755 ${KROXYLICIOUS_HOME}/libs
