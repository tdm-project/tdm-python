FROM ubuntu:18.04
MAINTAINER simone.leo@crs4.it

RUN echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/99yes && \
    apt update && \
    apt upgrade && \
    apt install libgdal-dev \
      python3-dev \
      python3-numpy \
      python3-pip && \
    ln -rs /usr/bin/python3 /usr/bin/python && \
    ln -rs /usr/bin/pip3 /usr/bin/pip && \
    pip install --no-cache-dir pyyaml

RUN CFLAGS="$(gdal-config --cflags)" pip install --no-cache-dir gdal==$(gdal-config --version)

COPY . /build/tdm-tools
WORKDIR /build/tdm-tools

RUN python setup.py install
