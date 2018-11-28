FROM ubuntu:18.04
MAINTAINER simone.leo@crs4.it

RUN echo 'APT::Get::Assume-Yes "true";' >> /etc/apt/apt.conf.d/99yes && \
    apt update && \
    apt upgrade && \
    apt install \
      wget \
      gdal-bin \
      libgdal-dev \
      python3-dev \
      python3-numpy \
      python3-pip && \
    apt-get clean && \
    ln -rs /usr/bin/python3 /usr/bin/python && \
    ln -rs /usr/bin/pip3 /usr/bin/pip

# using `apt-get install cdo` installs hundreds of packages.
ENV cdosite https://code.mpimet.mpg.de//attachments/download/18264
ENV CDOSRC cdo-1.9.5

ENV CDOURL ${cdosite}/${CDOSRC}.tar.gz

RUN apt install \
     libnetcdf-dev netcdf-bin \
     libeccodes-dev  && \
    apt-get clean

RUN wget ${CDOURL} && \
    tar xzf ${CDOSRC}.tar.gz && \
    cd ${CDOSRC} && \
    ./configure --with-netcdf --with-eccodes  --with-grib_api && \
    make; make install; cd ..; rm -rf ${CDOSRC}*


RUN CFLAGS="$(gdal-config --cflags)" pip install --no-cache-dir \
    gdal==$(gdal-config --version)

RUN pip install --no-cache-dir Cython && \
    pip install --no-cache-dir \
    imageio \
    netCDF4 \
    xarray \
    scipy \
    cdo \
    pyyaml




# FIXME remove cached stuff
COPY . /build/tdm-tools
WORKDIR /build/tdm-tools

RUN python setup.py install
