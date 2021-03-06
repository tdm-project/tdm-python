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

import os
import tempfile
import cdo

GRID_DESC = """\
gridtype = lonlat
xsize = {}
ysize = {}
xfirst = {}
xinc = {}
yfirst = {}
yinc = {}
"""


def map_to_region(fin, fout,
                  xfirst, xinc, xsize,
                  yfirst, yinc, ysize):
    gfname = tempfile.mktemp()
    with open(gfname, 'w') as o:
        o.write(GRID_DESC.format(xsize, ysize, xfirst, xinc, yfirst, yinc))
    c = cdo.Cdo()
    c.remapbil(gfname, input=fin, output=fout)
    os.unlink(gfname)


def main(args):
    try:
        os.makedirs(args.out_dir)
    except FileExistsError:
        pass
    fin = args.nc_path
    root, ext = os.path.splitext(os.path.basename(fin))
    fout = os.path.join(args.out_dir, ''.join([root, '-lonlat', ext]))
    xfirst, xsize, xinc = args.lon_range.split(':')
    yfirst, ysize, yinc = args.lat_range.split(':')
    map_to_region(fin, fout, xfirst, xinc, xsize, yfirst, yinc, ysize)


def add_parser(subparsers):
    parser = subparsers.add_parser("map_to_lonlat")
    parser.add_argument("nc_path", metavar="NETCDF_FILE")
    parser.add_argument("-o", "--out-dir", metavar="DIR", default=os.getcwd())
    parser.add_argument("--lat-range", metavar="LAT_RANGE",
                        help="<startlat>:<steps>:<inc> in degrees")
    parser.add_argument("--lon-range", metavar="LON_RANGE",
                        help="<startlon>:<steps>:<inc> in degrees")
    parser.set_defaults(func=main)
