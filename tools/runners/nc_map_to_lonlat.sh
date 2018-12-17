#!/usr/bin/env bash

set -euo pipefail

# bash grib2cf.sh in_dir out_dir

in_dir=${1:-/data/simulations/netcdf}
out_dir=${2:-/data/simulations/netcdf-lonlat}
lon_range=${3:-"4.5:512:0.0226"}
lat_range=${4:-"36.0:512:0.0226"}


wd=$(mktemp -d)
echo "work dir: ${wd}"
lst="${wd}"/lst.txt
log="${wd}"/map_to_lonlat.log
rd="${wd}"/map_to_lonlat.results

find "${in_dir}" -mindepth 1 -maxdepth 1 -type f > "${lst}"
parallel -a "${lst}" -j32 --progress --joblog "${log}" --results "${rd}" \
  docker run --rm \
    -v "${in_dir}":"${in_dir}":ro -v "${out_dir}":"${out_dir}" \
    crs4/tdm-tools tdm_map_to_lonlat --lon-range ${lon_range} \
                                     --lat-range ${lat_range} \
                                     -o "${out_dir}" {} \;

echo "work dir was: ${wd}"
