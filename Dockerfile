FROM ubuntu:18.04
MAINTAINER simone.leo@crs4.it

RUN echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/99yes && \
    apt update && \
    apt upgrade && \
    apt install \
      gdal-bin \
      libgdal-dev \
      python3-dev \
      python3-numpy \
      python3-pip && \
    ln -rs /usr/bin/python3 /usr/bin/python && \
    ln -rs /usr/bin/pip3 /usr/bin/pip

RUN CFLAGS="$(gdal-config --cflags)" pip install --no-cache-dir \
    gdal==$(gdal-config --version)

RUN pip install --no-cache-dir \
    imageio \
    netCDF4 \
    pyyaml

COPY . /build/tdm-tools
WORKDIR /build/tdm-tools

RUN python setup.py install
