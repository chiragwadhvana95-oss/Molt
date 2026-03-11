#!/bin/sh
# Gradle wrapper script

GRADLE_HOME="${HOME}/.gradle/wrapper/dists/gradle-7.0.2-bin"
export GRADLE_HOME
exec "$GRADLE_HOME/bin/gradle" "$@"