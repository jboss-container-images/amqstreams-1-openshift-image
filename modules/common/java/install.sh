#!/bin/sh
set -e

SCRIPT_DIR=$(dirname $0)
SCRIPTS_DIR=${SCRIPT_DIR}/scripts

mv ${SCRIPTS_DIR}/launch_java.sh /bin

chmod -R ug+x /bin/launch_java.sh
chown jboss:root /bin/launch_java.sh