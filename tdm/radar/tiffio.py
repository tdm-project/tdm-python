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
Store rainfall rate to GeoTIFF.
"""

import os

from .io import RainfallWriter
from .utils import FMT as ORIG_FMT

join = os.path.join

# https://www.awaresystems.be/imaging/tiff/tifftags/datetime.html
DT_TAG = "TIFFTAG_DATETIME"
DT_FMT = "%Y-%m-%d %H:%M:%S"


class GTiffWriter(RainfallWriter):

    def __init__(self, out_dir, ga):
        self.out_dir = out_dir
        self.ga = ga

    def write(self, i, dt, rr):
        path = join(self.out_dir, f"{dt.strftime(ORIG_FMT)}.tif")
        metadata = {DT_TAG: dt.strftime(DT_FMT)}
        self.ga.save_as_gtiff(path, rr, metadata=metadata)
