FROM crs4/tdm-base:latest
MAINTAINER simone.leo@crs4.it

RUN pip install --no-cache-dir \
        Cython \
	numpy && \
    CFLAGS="$(gdal-config --cflags)" pip install --no-cache-dir \
        gdal==$(gdal-config --version) && \
    pip install --no-cache-dir \
        cdo \
        cf-units \
        imageio \
        netCDF4 \
        pyyaml \
        scipy \
        xarray

COPY . /build/tdm-tools
WORKDIR /build/tdm-tools

RUN python setup.py install
