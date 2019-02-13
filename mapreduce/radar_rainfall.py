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
Estimate rainfall from radar images. Distributed version.
"""

import argparse
import logging
import os
import subprocess
import uuid

import pydoop.mapreduce.pipes as pipes
from pydoop import hdfs

from tdm.utils import balanced_split

MODULE = "rainfall_worker"
DEFAULT_NUM_MAPS = 10
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MODULE_PATH = os.path.join(THIS_DIR, "workers", f"{MODULE}.py")
LOG_LEVELS = 'CRITICAL', 'DEBUG', 'ERROR', 'INFO', 'WARNING'


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", metavar="INPUT_DIR")
    parser.add_argument("output", metavar="OUTPUT_DIR")
    parser.add_argument("footprint", metavar="GEOTIFF_FOOTPRINT")
    parser.add_argument(
        "--num-maps", metavar="INT", type=int, default=DEFAULT_NUM_MAPS,
    )
    parser.add_argument("--log-level", metavar="|".join(LOG_LEVELS),
                        choices=LOG_LEVELS, default="INFO")
    return parser


def list_images(input_dir):
    rval = []
    logging.info("scanning %s", input_dir)
    for entry in hdfs.lsl(input_dir):
        if all((entry["kind"] != "directory",
                not entry["name"].startswith("_"),
                entry["name"].endswith(".png"))):
            rval.append(entry["name"])
    logging.info("found %d images", len(rval))
    return rval


def main():
    parser = make_parser()
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    images = list_images(args.input)
    splits = balanced_split(images, args.num_maps)
    uri = os.path.join(args.input, "_" + uuid.uuid4().hex)
    logging.debug("saving input splits to: %s", uri)
    with hdfs.open(uri, "wb") as f:
        pipes.write_opaque_splits([pipes.OpaqueSplit(_) for _ in splits], f)
    cmd = [
        "pydoop", "submit", MODULE, args.input, args.output,
        "--do-not-use-java-record-reader",
        "--do-not-use-java-record-writer",
        "--job-name", "estimate rainfall rate",
        "--module", MODULE,
        "--num-reducers", "0",
        "--upload-file-to-cache", MODULE_PATH,
        "--upload-file-to-cache", args.footprint,
        "-D", f"mapreduce.job.maps={args.num_maps}",
        "-D", f"{pipes.EXTERNALSPLITS_URI_KEY}={uri}",
        "-D", f"tdm.radar.footprint.name={os.path.basename(args.footprint)}",
    ]
    subprocess.check_call(cmd)
    hdfs.rmr(uri)


if __name__ == "__main__":
    main()
