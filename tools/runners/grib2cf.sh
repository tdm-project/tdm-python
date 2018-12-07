#!/usr/bin/env bash

set -euo pipefail

in_dir="/data/simulations/grib2"
out_dir="/data/simulations/netcdf"

wd=$(mktemp -d)
echo "work dir: ${wd}"
lst="${wd}"/lst.txt
log="${wd}"/grib2cf.log
rd="${wd}"/results

find "${in_dir}" -mindepth 1 -maxdepth 1 -type d > "${lst}"
parallel -a "${lst}" -j32 --progress --joblog "${log}" --results "${rd}" \
  docker run --rm \
    -v "${in_dir}":"${in_dir}":ro -v "${out_dir}":"${out_dir}" \
    crs4/tdm-tools tdm_grib2cf -i {} -o "${out_dir}"\;

echo "work dir was: ${wd}"
