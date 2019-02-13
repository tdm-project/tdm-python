#!/usr/bin/env bash

set -euo pipefail

dir_name=grib2
tar_name=wgrib2.tgz
url=ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/${tar_name}
wd=$(mktemp -d)

pushd "${wd}"
wget ${url}
tar xf ${tar_name}
pushd ${dir_name}
sed -i -e 's|^USE_NETCDF3=1|USE_NETCDF3=0|' makefile
sed -i -e 's|^USE_NETCDF4=0|USE_NETCDF4=1|' makefile
sed -i -e 's|check install|install|g' makefile
netcdf4_tar_name=$(grep -m 1 'netcdf4src=' makefile | cut -d '=' -f 2)
netcdf4_url=ftp://ftp.unidata.ucar.edu/pub/netcdf/"${netcdf4_tar_name}"
hdf5_tar_name=$(grep -m 1 'hdf5src:=' makefile | cut -d '=' -f 2)
hdf5_version=$(echo ${hdf5_tar_name} | cut -d '-' -f 2 | cut -d '.' -f 1-3)
hdf5_maj_min=$(echo ${hdf5_version} | cut -d '.' -f 1-2)
hdf5_url=https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-${hdf5_maj_min}/hdf5-${hdf5_version}/src/hdf5-${hdf5_version}.tar.gz
wget "${netcdf4_url}"
tar xf "${netcdf4_tar_name}"
wget "${hdf5_url}"
tar xf "${hdf5_tar_name}"
FC=gfortran CC=gcc make
install wgrib2/wgrib2 /usr/local/bin
popd
popd

rm -rf "${wd}"
