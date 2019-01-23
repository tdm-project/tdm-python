#!/usr/bin/env python

# Copyright 2018-2019 CRS4
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# No real check for now, except for the presence of some attributes.

from netCDF4 import Dataset
import argparse
import os
import sys


def dump_nc_attrs(obj, indent=0):
    for k in obj.ncattrs():
        print("%s%s: %s" % (" " * indent, k, obj.getncattr(k)))


def check(nc_path):
    ds = Dataset(nc_path, "r")
    print("  global attributes:")
    dump_nc_attrs(ds, indent=4)
    temp = ds.variables["time"]
    print("  variable 'time':")
    dump_nc_attrs(temp, indent=4)


def main(args):
    nc_paths = [os.path.join(args.nc_dir, _)
                for _ in os.listdir(args.nc_dir)
                if _.endswith(".nc")]
    print("found %d files" % len(nc_paths))
    for p in nc_paths:
        print("checking: '%s'" % p)
        check(p)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nc_dir", metavar="NETCDF_DIR")
    main(parser.parse_args(sys.argv[1:]))
