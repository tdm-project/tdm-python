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

import string
import glob
import os
import sys


def link_grib(src_dir, dst_dir):
    dst_paths = ['GRIBFILE.'+i+j+k for i in string.ascii_uppercase
                 for j in string.ascii_uppercase
                 for k in string.ascii_uppercase]
    for f, t in zip(glob.glob(os.path.join(src_dir, "*")), dst_paths):
        os.symlink(f, os.path.join(dst_dir, t))


def main(args):
    link_grib(args[0], args[1])


if __name__ == "__main__":
    main(sys.argv[1:])