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

from datetime import datetime, timedelta
import io
import os
import shutil
import tempfile
import unittest

import gdal
import numpy as np
import tdm.radar.utils as utils

gdal.UseExceptions()


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(THIS_DIR, "data")


class TestEvents(unittest.TestCase):

    def test_multi(self):
        N = 100000
        mu, sigma = 60, 5
        deltas = np.random.normal(mu, sigma, N - 1)
        event_idx = [1000, 10000, 50000]
        secs_between = 60 * 60
        deltas[event_idx] = secs_between
        start = datetime(2018, 1, 1, 0, 0, 0)
        dts = [start]
        for d in deltas:
            dts.append(dts[-1] + timedelta(seconds=d))
        names = [datetime.strftime(_, utils.FMT) for _ in dts]
        dt_path_pairs = list(zip(dts, names))

        events = list(utils.events(dt_path_pairs, min_len=100))
        self.assertEqual(len(events), 4)
        exp_lengths = [1001, 10001 - 1001, 50001 - 10001, 100000 - 50001]
        self.assertEqual([len(_) for _ in events], exp_lengths)
        self.assertEqual(events[0], dt_path_pairs[:1001])
        self.assertEqual(events[1], dt_path_pairs[1001:10001])
        self.assertEqual(events[2], dt_path_pairs[10001:50001])
        self.assertEqual(events[3], dt_path_pairs[50001:])

        events = list(utils.events(dt_path_pairs, min_len=timedelta(days=1)))
        self.assertEqual(len(events), 3)
        exp_lengths = [10001 - 1001, 50001 - 10001, 100000 - 50001]
        self.assertEqual([len(_) for _ in events], exp_lengths)
        self.assertEqual(events[0], dt_path_pairs[1001:10001])
        self.assertEqual(events[1], dt_path_pairs[10001:50001])
        self.assertEqual(events[2], dt_path_pairs[50001:])

    def test_single(self):
        N = 1000
        mu, sigma = 60, 5
        deltas = np.random.normal(mu, sigma, N - 1)
        start = datetime(2018, 1, 1, 0, 0, 0)
        dts = [start]
        for d in deltas:
            dts.append(dts[-1] + timedelta(seconds=d))
        names = [datetime.strftime(_, utils.FMT) for _ in dts]
        dt_path_pairs = list(zip(dts, names))
        events = list(utils.events(dt_path_pairs, min_len=100))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], dt_path_pairs)

    def test_small(self):
        dt_path_pairs = [(datetime(2018, 1, 1, 0, 0, 0), "/foo/bar")]
        events = list(utils.events(dt_path_pairs, min_len=0))
        self.assertEqual(events, [dt_path_pairs])
        events = list(utils.events(dt_path_pairs))
        self.assertEqual(events, [])
        events = list(utils.events([]))
        self.assertEqual(events, [])


class TestGetImages(unittest.TestCase):

    TAG = "cag01est2400"
    FMT = "%Y-%m-%d_%H:%M:%S"
    AFTER = datetime(2018, 5, 1, 23, 20)
    BEFORE = datetime(2018, 5, 1, 23, 30)
    SAMPLE = [
        "2018-05-01_23:18:03",
        "2018-05-01_23:19:04",
        # 23:20:00 (AFTER)
        "2018-05-01_23:20:05",
        "2018-05-01_23:21:03",
        "2018-05-01_23:22:04",
        "2018-05-01_23:23:02",
        "2018-05-01_23:24:03",
        # 23:25:00
        "2018-05-01_23:25:04",
        "2018-05-01_23:26:02",
        "2018-05-01_23:27:03",
        "2018-05-01_23:28:04",
        "2018-05-01_23:29:03",
        # 23:30:00 (BEFORE)
        "2018-05-01_23:30:04",
    ]

    def setUp(self):
        self.wd = tempfile.mkdtemp(prefix="tdm_")
        self.info = []
        for name in self.SAMPLE:
            p = os.path.join(self.wd, "%s%s.png" % (self.TAG, name))
            with io.open(p, "wb"):
                pass
            self.info.append((datetime.strptime(name, self.FMT), p))  # sorted
        with io.open(os.path.join(self.wd, "README.txt"), "wb"):
            pass

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_get(self):
        exp_res = self.info[2:-1]
        ls = utils.get_images(self.wd, self.AFTER, self.BEFORE)
        self.assertEqual(len(ls), len(exp_res))
        self.assertEqual(ls, exp_res)

    def test_get_all(self):
        after, before = datetime.min, datetime.max
        exp_res = self.info
        ls = utils.get_images(self.wd, after, before)
        self.assertEqual(len(ls), len(exp_res))
        self.assertEqual(ls, exp_res)
        ls = utils.get_images(self.wd)
        self.assertEqual(len(ls), len(exp_res))
        self.assertEqual(ls, exp_res)

    def test_get_grouped(self):
        delta = timedelta(minutes=5)
        exp_res = {
            datetime(2018, 5, 1, 23, 20): self.info[2:7],
            datetime(2018, 5, 1, 23, 25): self.info[7:12],
        }
        res = {dt: list(g) for dt, g in utils.get_grouped_images(
            self.wd, delta, self.AFTER, self.BEFORE
        )}
        self.assertEqual(len(res), len(exp_res))
        self.assertEqual(res, exp_res)

    def test_get_all_grouped(self):
        delta = timedelta(minutes=5)
        exp_res = {
            datetime(2018, 5, 1, 23, 15): self.info[:2],
            datetime(2018, 5, 1, 23, 20): self.info[2:7],
            datetime(2018, 5, 1, 23, 25): self.info[7:12],
            datetime(2018, 5, 1, 23, 30): self.info[12:],
        }
        res = {dt: list(g) for dt, g in utils.get_grouped_images(
            self.wd, delta, datetime.min, datetime.max
        )}
        self.assertEqual(len(res), len(exp_res))
        self.assertEqual(res, exp_res)
        res = {dt: list(g) for dt, g in utils.get_grouped_images(
            self.wd, delta
        )}
        self.assertEqual(len(res), len(exp_res))
        self.assertEqual(res, exp_res)


@unittest.skipUnless(os.path.isdir(DATA_DIR), "requires sample data")
class TestSave(unittest.TestCase):

    def setUp(self):
        self.wd = tempfile.mkdtemp(prefix="tdm_")
        self.raw_fn = os.path.join(
            DATA_DIR, "signal", "2018-05-01_23:00:04.png"
        )
        self.template = os.path.join(DATA_DIR, "radarfootprint.tif")

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_gtiff(self):
        signal = utils.get_image_data(self.raw_fn)
        rain = utils.estimate_rainfall(signal)
        ga = utils.GeoAdapter(self.template)
        out_fn = os.path.join(self.wd, "sample.tif")
        ga.save_as_gtiff(out_fn, rain)
        dataset = gdal.Open(out_fn)
        self.assertEqual(dataset.RasterCount, 1)
        band = dataset.GetRasterBand(1)
        m_band = band.GetMaskBand()
        self.assertEqual(band.GetMaskFlags(), gdal.GMF_NODATA)
        ma = np.ma.masked_array(
            band.ReadAsArray(),
            mask=(m_band.ReadAsArray() == 0),
            fill_value=band.GetNoDataValue()
        )
        self.assertTrue(np.array_equal(ma.mask, rain.mask))
        self.assertTrue(np.ma.allclose(ma, rain))
        self.assertEqual(dataset.GetGeoTransform(),
                         (ga.oX, ga.pxlW, 0, ga.oY, 0, ga.pxlH))
        sr = gdal.osr.SpatialReference(wkt=dataset.GetProjectionRef())
        self.assertTrue(sr.IsSame(ga.sr))
        # check band_to_ma
        ma2 = utils.band_to_ma(band)
        self.assertTrue(np.array_equal(ma2.mask, ma.mask))
        self.assertTrue(np.ma.allclose(ma2, ma))


if __name__ == '__main__':
    unittest.main()
