from datetime import datetime, timedelta
import io
import os
import shutil
import tempfile
import unittest
import tdm.radar.utils as utils


class TestGetImages(unittest.TestCase):

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
            p = os.path.join(self.wd, "%s.png" % name)
            with io.open(p, "wb"):
                pass
            self.info.append((datetime.strptime(name, self.FMT), p))  # sorted
        with io.open(os.path.join(self.wd, "README.txt"), "wb"):
            pass

    def tearDown(self):
        shutil.rmtree(self.wd)

    def test_get(self):
        exp_res = self.info[2:-1]
        ls = list(utils.get_raw_radar_images(self.wd, self.AFTER, self.BEFORE))
        self.assertEqual(len(ls), len(exp_res))
        self.assertEqual(ls, exp_res)

    def test_get_all(self):
        after, before = datetime.min, datetime.max
        exp_res = self.info
        ls = list(utils.get_raw_radar_images(self.wd, after, before))
        self.assertEqual(len(ls), len(exp_res))
        self.assertEqual(ls, exp_res)

    def test_get_grouped(self):
        delta = timedelta(minutes=5)
        exp_res = {
            datetime(2018, 5, 1, 23, 20): self.info[2:7],
            datetime(2018, 5, 1, 23, 25): self.info[7:12],
        }
        res = {dt: list(g) for dt, g in utils.get_grouped_raw_radar_images(
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
        res = {dt: list(g) for dt, g in utils.get_grouped_raw_radar_images(
            self.wd, delta, datetime.min, datetime.max
        )}
        self.assertEqual(len(res), len(exp_res))
        self.assertEqual(res, exp_res)


CASES = [
    TestGetImages,
]


def suite():
    ret = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    for c in CASES:
        ret.addTest(test_loader.loadTestsFromTestCase(c))
    return ret


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run((suite()))
