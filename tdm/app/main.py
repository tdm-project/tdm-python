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

"""\
TDM command line tools. For tool-specific help, run tdm <SUB-COMMAND> --help.
"""

import argparse
import importlib

from tdm import __version__ as version

SUB_COMMANDS = [
    'gfs_fetch',
    'map_to_lonlat',
    'map_to_tree',
    'radar_events',
    'radar_nc_to_geo',
    'rainfall',
    'wrf_configurator',
    'grib2cf',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-V', '--version', action='version', version=version)
    subparsers = parser.add_subparsers(help="sub-commands")
    for cmd in SUB_COMMANDS:
        mod = importlib.import_module(f"{__package__}.{cmd}")
        mod.add_parser(subparsers)
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.error("too few arguments")
