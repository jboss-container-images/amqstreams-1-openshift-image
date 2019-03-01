#!/bin/sh
set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts
SOURCES_DIR=/tmp/artifacts
LICENSE_DIR=/root/licenses

mkdir $LICENSE_DIR
mv ${SOURCES_DIR}/* ${LICENSE_DIR}
chmod -R 755 ${LICENSE_DIR}

mv ${SCRIPTS_DIR}/launch_java.sh /bin

chmod -R ug+x /bin/launch_java.sh
chown jboss:root /bin/launch_java.sh
