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
Copy radar images to HDFS, converting file names to avoid illegal characters.
"""

import argparse
import io
import os
import sys

import pydoop.hdfs as hdfs

from tdm.radar.utils import get_images

# ISO 8601 basic
OUT_FMT = "%Y%m%dT%H%M%S"


def main(args):
    host, port, out_dir = hdfs.path.split(args.out_dir)
    fs = hdfs.hdfs(host, port)
    fs.create_directory(out_dir)
    join = os.path.join
    for dt, path in get_images(args.in_dir):
        out_path = join(out_dir, f"{dt.strftime(OUT_FMT)}.png")
        if not args.overwrite and fs.exists(out_path):
            continue
        with io.open(path, "rb") as fi:
            with fs.open_file(out_path, "wb") as fo:
                fo.write(fi.read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_dir", metavar="INPUT_DIR")
    parser.add_argument("out_dir", metavar="OUTPUT_DIR")
    parser.add_argument("--overwrite", action="store_true")
    main(parser.parse_args(sys.argv[1:]))
