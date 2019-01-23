#!/usr/bin/env bash

set -euo pipefail

die() {
    echo $1 1>&2
    exit 1
}

[ $# -ne 2 ] && die "usage: $0 IN_DIR OUT_DIR"
in_dir="$1"
out_dir="$2"

[ -d "${out_dir}" ] || mkdir -p "${out_dir}"

wd=$(mktemp -d)
echo "work dir: ${wd}"
nc_list="${wd}"/nc_list.txt
log="${wd}"/nc_to_geotiff.log
rd="${wd}"/results

find "${in_dir}" -type f -name '*.nc' > "${nc_list}"

parallel -a "${nc_list}" -j32 --progress --joblog "${log}" --results "${rd}" \
  docker run --rm \
    -v "${in_dir}":"${in_dir}":ro -v "${out_dir}":"${out_dir}" \
    crs4/tdm-tools tdm radar_nc_to_geo -o "${out_dir}"/{/.} {}\;

echo "work dir was: ${wd}"
