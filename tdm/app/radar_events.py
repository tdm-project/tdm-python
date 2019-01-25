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
Split raw radar images into per-event directories.
"""

import argparse
import datetime
import os

import tdm.radar.events as events
import tdm.radar.utils as utils

join = os.path.join
strftime = datetime.datetime.strftime


def main(args):
    print("scanning %s" % args.in_dir)
    dt_path_pairs = utils.get_images(args.in_dir)
    fmt = utils.FMT
    for event in events.split(dt_path_pairs, min_len=args.min_len):
        start_str = strftime(event[0][0], fmt)
        out_subdir = join(args.out_dir, start_str)
        try:
            os.makedirs(out_subdir)
        except FileExistsError:
            pass
        print("  event from: %s (%d time points)" % (start_str, len(event)))
        for dt, p in event:
            out_p = join(out_subdir, strftime(dt, fmt))
            with open(p, "rb") as fi, open(out_p, "wb") as fo:
                fo.write(fi.read())


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "radar_events",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=f"{__doc__}\n{events.__doc__}"
    )
    parser.add_argument("in_dir", metavar="INPUT_DIR")
    parser.add_argument("-l", "--min-len", metavar="N_SECONDS", type=int,
                        default=events.MIN_EVENT_LEN,
                        help="skip events shorter than N_SECONDS")
    parser.add_argument("-o", "--out-dir", metavar="DIR", default=os.getcwd())
    parser.set_defaults(func=main)
