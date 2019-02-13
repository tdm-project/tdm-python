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
Estimate rainfall rate for all images in the input stream.
"""

from datetime import datetime
import io
import os

import pydoop.hdfs as hdfs
import pydoop.mapreduce.api as api
import pydoop.mapreduce.pipes as pp

import tdm.radar.tiffio as tiffio
import tdm.radar.utils as utils

IN_FMT = "%Y%m%dT%H%M%S"


class Reader(api.RecordReader):

    def __init__(self, context):
        super().__init__(context)
        self.paths = context.input_split.payload
        self.n_paths = len(self.paths)

    def next(self):
        try:
            path = self.paths.pop()
        except IndexError:
            raise StopIteration
        with hdfs.open(path, "rb") as f:
            signal = utils.get_image_data(f)
        return path, signal

    def get_progress(self):
        return 1 - float(len(self.paths) / self.n_paths)


class Mapper(api.Mapper):

    def __init__(self, context):
        super().__init__(context)
        footprint_name = context.job_conf["tdm.radar.footprint.name"]
        self.ga = utils.GeoAdapter(footprint_name)

    def map(self, context):
        # TODO: look for a way to avoid the local write
        path, signal = context.key, context.value
        rr = utils.estimate_rainfall(signal)
        dt_string = os.path.splitext(hdfs.path.basename(path))[0]
        out_name = "%s.tif" % dt_string
        dt = datetime.strptime(dt_string, IN_FMT)
        metadata = {tiffio.DT_TAG: dt.strftime(tiffio.DT_FMT)}
        self.ga.save_as_gtiff(out_name, rr, metadata=metadata)
        with io.open(out_name, "rb") as f:
            value = f.read()
        context.emit(out_name, value)


class Writer(api.RecordWriter):

    def __init__(self, context):
        super().__init__(context)
        self.d = context.get_work_path()

    def emit(self, key, value):
        with hdfs.open(hdfs.path.join(self.d, key), "wb") as f:
            f.write(value)


factory = pp.Factory(mapper_class=Mapper, record_reader_class=Reader,
                     record_writer_class=Writer)


def __main__():
    pp.run_task(factory)
