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

"""\
Estimate rainfall from radar images.
"""

import datetime
import os

import tdm.radar.utils as utils
import tdm.radar.cfio as cfio

strftime = datetime.datetime.strftime

OUT_FMTS = frozenset(("nc", "tif"))
T_CHUNKS = cfio.T_CHUNKS


def main(args):
    try:
        os.makedirs(args.out_dir)
    except FileExistsError:
        pass
    ga = utils.GeoAdapter(args.footprint)
    dt_path_pairs = utils.get_images(args.img_dir)
    groups = None
    if args.resolution:
        group_gen = utils.group_images(dt_path_pairs, args.resolution)
        groups = [(dt, list(g)) for dt, g in group_gen]
        nt, t0 = len(groups), groups[0][0]
    else:
        nt, t0 = len(dt_path_pairs), dt_path_pairs[0][0]
    ds_path = os.path.join(args.out_dir, "%s.nc" % strftime(t0, utils.FMT))
    print('saving "%s"' % ds_path)
    writer = cfio.NCWriter(ds_path, ga, nt, t0, t_chunks=args.t_chunks)
    if groups:
        writer.write_avg_rainfall(groups)
    else:
        writer.write_rainfall(dt_path_pairs)
    writer.close()


def add_parser(subparsers):
    parser = subparsers.add_parser("rainfall", description=__doc__)
    parser.add_argument("img_dir", metavar="PNG_IMG_DIR")
    parser.add_argument("footprint", metavar="GEOTIFF_FOOTPRINT")
    parser.add_argument("-r", "--resolution", metavar="N_SECONDS", type=int,
                        help="output average rainfall over N_SECONDS windows")
    parser.add_argument("-o", "--out-dir", metavar="DIR", default=os.getcwd())
    parser.add_argument("-f", "--format", choices=OUT_FMTS, default="nc",
                        help="output format")
    parser.add_argument("--t-chunks", metavar="N", type=int, default=T_CHUNKS,
                        help="chunk size along the t dimension (nc output)")
    parser.set_defaults(func=main)
