#!/usr/bin/env bash

set -euo pipefail

# bash grib2cf.sh in_dir out_dir

in_dir=${1:-/data/simulations/netcdf-lonlat}
out_dir=${2:-/data/simulations/tdm-tree}
url_root=${3:-"https://rest.tdm-project.it"}

wd=$(mktemp -d)
echo "work dir: ${wd}"
lst="${wd}"/lst.txt
log="${wd}"/map_to_tree.log
rd="${wd}"/map_to_tree.results

find "${in_dir}" -mindepth 1 -maxdepth 1 -type f > "${lst}"
parallel -a "${lst}" -j32 --progress --joblog "${log}" --results "${rd}" \
  docker run --rm \
    -v "${in_dir}":"${in_dir}":ro -v "${out_dir}":"${out_dir}" \
    crs4/tdm-tools tdm map_to_tree --url-root ${url_root} \
                                     -o "${out_dir}" {} \;

echo "work dir was: ${wd}"
