#!/usr/bin/env bash
set -x
shift

. ${STRIMZI_HOME}/bin/dynamic_resources.sh

# expand gc options based upon java version
function get_gc_opts {
  if [ "${STRIMZI_GC_LOG_ENABLED}" == "true" ]; then
    # The first segment of the version number is '1' for releases < 9; then '9', '10', '11', ...
    JAVA_MAJOR_VERSION=$(java -version 2>&1 | sed -E -n 's/.* version "([0-9]*).*$/\1/p')
    if [ "$JAVA_MAJOR_VERSION" -ge "9" ] ; then
      echo "-Xlog:gc*:stdout:time -XX:NativeMemoryTracking=summary"
    else
      echo "-verbose:gc -XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCTimeStamps -XX:NativeMemoryTracking=summary"
    fi
  else
    # no gc options
    echo ""
  fi
}

MAX_HEAP=`get_heap_size`
if [ -n "$MAX_HEAP" ]; then
  JAVA_OPTS="-Xms${MAX_HEAP}m -Xmx${MAX_HEAP}m $JAVA_OPTS"
fi

export MALLOC_ARENA_MAX=2

# Make sure that we use /dev/urandom
JAVA_OPTS="${JAVA_OPTS} -Dvertx.cacheDirBase=/tmp -Djava.security.egd=file:/dev/./urandom"

# Enable GC logging for memory tracking
JAVA_OPTS="${JAVA_OPTS} $(get_gc_opts)"

exec java $JAVA_OPTS -classpath $JAVA_CLASSPATH $JAVA_MAIN $@
