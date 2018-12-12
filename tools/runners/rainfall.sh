#!/usr/bin/env bash

set -euo pipefail

in_dir="/data/radar_data/raw_events"
footprint="/data/radar_data/radarmappatipo.tif"
out_dir="/data/radar_data/netcdf"

wd=$(mktemp -d)
echo "work dir: ${wd}"
lst="${wd}"/lst.txt
log="${wd}"/rainfall.log
rd="${wd}"/results

find "${in_dir}" -mindepth 1 -maxdepth 1 -type d > "${lst}"
parallel -a "${lst}" -j32 --progress --joblog "${log}" --results "${rd}" \
  docker run --rm \
    -v /data/radar_data:/data/radar_data:ro -v "${out_dir}":/out_dir \
    crs4/tdm-tools tdm_rainfall {} "${footprint}" \
    -o /out_dir --t-chunks 120 -r 3600\;

echo "work dir was: ${wd}"
