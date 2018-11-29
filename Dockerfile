FROM ubuntu:18.04
MAINTAINER simone.leo@crs4.it

RUN echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/99yes && \
    apt update && \
    apt upgrade && \
    apt install \
      gdal-bin \
      libeccodes-dev \
      libgdal-dev \
      netcdf-bin \
      python3-dev \
      python3-numpy \
      python3-pip \
      wget && \
    apt-get clean && \
    ln -rs /usr/bin/python3 /usr/bin/python && \
    ln -rs /usr/bin/pip3 /usr/bin/pip

# `apt-get install cdo` installs hundreds of packages
ENV cdosite https://code.mpimet.mpg.de//attachments/download/18264
ENV cdosrc cdo-1.9.5
ENV cdourl ${cdosite}/${cdosrc}.tar.gz
RUN wget ${cdourl} && \
    tar xf ${cdosrc}.tar.gz && \
    cd ${cdosrc} && \
    ./configure --with-netcdf --with-eccodes --with-grib_api && \
    make -j$(grep -c ^processor /proc/cpuinfo); make install && \
    cd .. && \
    rm -rf ${cdosrc}*

RUN CFLAGS="$(gdal-config --cflags)" pip install --no-cache-dir \
    gdal==$(gdal-config --version)

RUN pip install --no-cache-dir Cython && \
    pip install --no-cache-dir \
        cdo \
        imageio \
        netCDF4 \
        pyyaml \
        scipy \
        xarray

COPY . /build/tdm-tools
WORKDIR /build/tdm-tools

RUN python setup.py install
