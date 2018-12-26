FROM amd64/ubuntu:bionic
LABEL Dan Lanier="lanier4@illinois.edu"

RUN apt-get update && apt-get install -y openjdk-8-jdk

RUN export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN export PATH=$PATH:$JAVA_HOME/bin

ENV CROMWELL_JAR_LOC  /usr/locl/etc
COPY files/* ${CROMWELL_JAR_LOC}/

# https://github.com/broadinstitute/cromwell/releases/download/36/cromwell-36.jar

