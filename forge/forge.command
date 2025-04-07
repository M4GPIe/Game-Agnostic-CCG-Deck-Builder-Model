#!/bin/sh
cd $(dirname "${0}")
java -Xmx4096m -Dio.netty.tryReflectionSetAccessible=true -Dfile.encoding=UTF-8 -jar forge-gui-desktop-2.0.03-SNAPSHOT-jar-with-dependencies.jar
