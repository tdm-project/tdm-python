#!/usr/bin/env bash

# `apt-get install cdo` installs hundreds of packages

set -euo pipefail

cdosite=https://code.mpimet.mpg.de//attachments/download/18264
cdosrc=cdo-1.9.5
cdourl=${cdosite}/${cdosrc}.tar.gz
wd=$(mktemp -d)

pushd "${wd}"
wget ${cdourl}
tar xf ${cdosrc}.tar.gz
pushd ${cdosrc}
./configure --with-netcdf --with-eccodes --with-grib_api
make -j$(grep -c ^processor /proc/cpuinfo)
make install
popd
popd

rm -rf "${wd}"
