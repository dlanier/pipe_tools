FROM amd64/ubuntu:bionic
LABEL Dan Lanier="lanier4@illinois.edu"

RUN apt-get update && apt-get install -y openjdk-8-jdk vim python3-pip git
RUN pip3 install -I numpy pandas scipy scikit-learn pyyaml xmlrunner jupyter

RUN export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/
RUN export PATH=$PATH:$JAVA_HOME/bin

#ENV CROMWELL_JAR_LOC  /usr/locl/etc
ENV CROMWELL_JAR_LOC  /usr/local/etc
COPY jar_files/* ${CROMWELL_JAR_LOC}/

# RUN curl https://github.com/broadinstitute/cromwell/releases/download/36/womtool-36.jar
# RUN curl  https://github.com/broadinstitute/cromwell/releases/download/36/cromwell-36.jar

# add admin user - prevent running as root
# administrator account:
RUN adduser --disabled-login --gecos "" spanky; echo "spanky:spanky" | chpasswd
RUN usermod -aG sudo spanky
USER spanky


# set up for a run_directory /home directory
ENV SRC_LOC /home

# Example: Clone from github -- removes repo root name this way & allows local nameing for src
# RUN git clone https://github.com/KnowEnG/Samples_Clustering_Pipeline.git ${SRC_LOC} 

WORKDIR ${SRC_LOC}

# Build and push pasties:
# docker build --no-cache -t aka1spanky/ncsa:dev0 .
# docker login --username=${whodakine} --password=${123password4me} 
# docker push aka1spanky/ncsa:dev0

# pandoc - LaTeX >> pdf
# http:http://pandoc.org/installing.html

 

