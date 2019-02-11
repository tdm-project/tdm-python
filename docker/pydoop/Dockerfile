FROM tdmproject/tdm-tools:latest
MAINTAINER simone.leo@crs4.it

ARG HADOOP_VERSION=3.0.3
ARG JAVA_VERSION=8

ENV HADOOP_HOME=/opt/hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-${JAVA_VERSION}-openjdk-amd64

COPY resources /tmp/resources

RUN apt update && apt install openjdk-${JAVA_VERSION}-jdk && \
    bash /tmp/resources/install_hadoop.sh && \
    pip install --pre pydoop && \
    rm -rf /tmp/resources

ENV PATH="${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}"

COPY entrypoint.sh /

ENTRYPOINT ["/entrypoint.sh"]
