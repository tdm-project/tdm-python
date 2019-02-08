FROM ubuntu:18.04
MAINTAINER simone.leo@crs4.it

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

RUN echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/99yes && \
    apt update && \
    apt upgrade && \
    apt install \
      gdal-bin \
      gfortran \
      libeccodes-dev \
      libgdal-dev \
      libudunits2-dev \
      m4 \
      netcdf-bin \
      python3-dev \
      python3-pip \
      wget && \
    apt-get clean && \
    ln -rs /usr/bin/python3 /usr/bin/python && \
    ln -rs /usr/bin/pip3 /usr/bin/pip

COPY scripts /scripts

RUN bash /scripts/install_cdo.sh && \
    bash /scripts/install_wgrib2.sh && \
    rm -rf /scripts
