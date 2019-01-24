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
import datetime
import os
import shutil
import subprocess
import sys
import tempfile

import gdal
import numpy as np

from tdm.radar import utils

gdal.UseExceptions()

SpatialReference = gdal.osr.SpatialReference
splitext = os.path.splitext
strftime = datetime.datetime.strftime
strptime = datetime.datetime.strptime

# https://www.awaresystems.be/imaging/tiff/tifftags/datetime.html
TIFF_DT_FMT = "%Y-%m-%d %H:%M:%S"
TIFF_EXT = frozenset((".tif", ".tiff"))


def scan_gtiffs(gtiff_img_dir):
    rval = {}
    for name in os.listdir(gtiff_img_dir):
        head, ext = splitext(name)
        if ext.lower() not in TIFF_EXT:
            continue
        dt = strptime(head, utils.FMT)
        rval[dt] = os.path.join(gtiff_img_dir, name)
    return rval


def compare_gtiff(fn1, fn2):
    ds1, ds2 = [gdal.Open(_) for _ in (fn1, fn2)]
    assert ds1.GetGeoTransform() == ds2.GetGeoTransform()
    sr1, sr2 = [SpatialReference(wkt=_.GetProjectionRef()) for _ in (ds1, ds2)]
    assert sr1.IsSame(sr2)
    assert ds1.RasterCount == ds2.RasterCount == 1
    b1, b2 = [_.GetRasterBand(1) for _ in (ds1, ds2)]
    ma1, ma2 = [utils.band_to_ma(_) for _ in (b1, b2)]
    assert np.array_equal(ma1.mask, ma2.mask)
    assert np.ma.allclose(ma1, ma2, atol=1e-4)


def rm_f(*paths):
    for p in paths:
        try:
            os.unlink(p)
        except FileNotFoundError:
            pass


def main(args):
    dt_path_pairs = utils.get_images(args.png_img_dir)
    ga = utils.GeoAdapter(args.footprint)
    gtiff_map = scan_gtiffs(args.gtiff_img_dir)
    assert {_[0] for _ in dt_path_pairs}.issubset(gtiff_map)
    wd = tempfile.mkdtemp(prefix="tdm_")
    in_fn = os.path.join(wd, "orig.tif")
    warped_fn = os.path.join(wd, "warped.tif")
    t_srs = "EPSG:4326"
    n_pairs = len(dt_path_pairs)
    for i, (dt, path) in enumerate(dt_path_pairs):
        rm_f(in_fn, warped_fn)
        print("checking %s (%d/%d)" % (gtiff_map[dt], i + 1, n_pairs))
        signal = utils.get_image_data(path)
        rain = utils.estimate_rainfall(signal)
        metadata = {"TIFFTAG_DATETIME": strftime(dt, TIFF_DT_FMT)}
        ga.save_as_gtiff(in_fn, rain, metadata)
        subprocess.check_call(["gdalwarp", "-t_srs", t_srs, in_fn, warped_fn])
        compare_gtiff(gtiff_map[dt], warped_fn)
    shutil.rmtree(wd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("png_img_dir", metavar="PNG_IMG_DIR")
    parser.add_argument("footprint", metavar="GEOTIFF_FOOTPRINT")
    parser.add_argument("gtiff_img_dir", metavar="GEOTIFF_IMG_DIR")
    main(parser.parse_args(sys.argv[1:]))
