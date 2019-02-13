#!/usr/bin/env bash

set -euo pipefail

this="${BASH_SOURCE-$0}"
this_dir=$(cd -P -- "$(dirname -- "${this}")" && pwd -P)

tar="hadoop-${HADOOP_VERSION}.tar.gz"
repo="http://www-eu.apache.org/dist/hadoop/common"

mkdir -p "${HADOOP_HOME}"
wd=$(mktemp -d)
pushd "${wd}"
wget -q -O - ${repo}/hadoop-${HADOOP_VERSION}/${tar} | tar xz
mv hadoop-${HADOOP_VERSION}/* "${HADOOP_HOME}"
popd
rm -rf "${wd}"

major_version=${HADOOP_VERSION%%.*}
if [ ${major_version} -lt 3 ]; then
    echo "Hadoop versions older than 3 not supported" 1>&2
    exit 1
fi
to_conf="${HADOOP_HOME}/etc/hadoop"
cp -f "${this_dir}"/*.xml "${to_conf}"/
for name in hadoop mapred yarn; do
    sed -i "1iexport JAVA_HOME=${JAVA_HOME}" "${to_conf}/${name}-env.sh"
done
