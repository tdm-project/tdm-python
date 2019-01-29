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

import argparse
from datetime import datetime
import sys

import gdal
import numpy as np

from tdm.radar.tiffio import DT_TAG, DT_FMT
import tdm.radar.utils as utils

gdal.UseExceptions()


def check(ga, rr, dt, gtiff_path):
    dataset = gdal.Open(gtiff_path)
    assert dataset.RasterCount == 1
    ma = utils.band_to_ma(dataset.GetRasterBand(1))
    assert np.array_equal(ma.mask, rr.mask)
    assert np.ma.allclose(ma, rr)
    assert dataset.GetGeoTransform() == (ga.oX, ga.pxlW, 0, ga.oY, 0, ga.pxlH)
    sr = gdal.osr.SpatialReference(wkt=dataset.GetProjectionRef())
    assert sr.IsSame(ga.sr)
    metadata = dataset.GetMetadata()
    assert DT_TAG in metadata
    assert datetime.strptime(metadata[DT_TAG], DT_FMT) == dt


def main(args):
    gtiff_map = utils.scan_gtiffs(args.gtiff_dir)
    dt_path_pairs = utils.get_images(args.png_dir)
    if args.resolution:
        groups = utils.group_images(dt_path_pairs, args.resolution)
        dt_rr_stream = utils.avg_rainfall(groups)
    else:
        dt_rr_stream = ((dt, utils.estimate_rainfall(utils.get_image_data(_)))
                        for (dt, _) in dt_path_pairs)
    ga = utils.GeoAdapter(args.footprint)
    for dt, rr in dt_rr_stream:
        assert dt in gtiff_map
        check(ga, rr, dt, gtiff_map[dt])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gtiff_dir", metavar="GEOTIFF_RAINFALL_DIR")
    parser.add_argument("png_dir", metavar="PNG_DIR")
    parser.add_argument("footprint", metavar="GEOTIFF_FOOTPRINT")
    parser.add_argument("-r", "--resolution", metavar="N_SECONDS", type=int,
                        help="set to same value passed to the rainfall script")
    main(parser.parse_args(sys.argv[1:]))
