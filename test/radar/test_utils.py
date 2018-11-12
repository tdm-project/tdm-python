from datetime import datetime, timedelta
import io
import os
import shutil
import tempfile
import unittest

import numpy as np
import tdm.radar.utils as utils


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

        events = list(utils.events(dts, names, min_len=100))
        self.assertEqual(len(events), 4)
        dt_chunks, name_chunks = zip(*events)
        exp_lengths = [1001, 10001 - 1001, 50001 - 10001, 100000 - 50001]
        for seq in dt_chunks, name_chunks:
            self.assertEqual([len(_) for _ in seq], exp_lengths)
        self.assertEqual(dt_chunks[0], dts[:1001])
        self.assertEqual(dt_chunks[1], dts[1001:10001])
        self.assertEqual(dt_chunks[2], dts[10001:50001])
        self.assertEqual(dt_chunks[3], dts[50001:])
        self.assertEqual(name_chunks[0], names[:1001])
        self.assertEqual(name_chunks[1], names[1001:10001])
        self.assertEqual(name_chunks[2], names[10001:50001])
        self.assertEqual(name_chunks[3], names[50001:])

        events = list(utils.events(dts, names, min_len=timedelta(days=1)))
        self.assertEqual(len(events), 3)
        dt_chunks, name_chunks = zip(*events)
        exp_lengths = [10001 - 1001, 50001 - 10001, 100000 - 50001]
        for seq in dt_chunks, name_chunks:
            self.assertEqual([len(_) for _ in seq], exp_lengths)
        self.assertEqual(dt_chunks[0], dts[1001:10001])
        self.assertEqual(dt_chunks[1], dts[10001:50001])
        self.assertEqual(dt_chunks[2], dts[50001:])
        self.assertEqual(name_chunks[0], names[1001:10001])
        self.assertEqual(name_chunks[1], names[10001:50001])
        self.assertEqual(name_chunks[2], names[50001:])

    def test_single(self):
        N = 1000
        mu, sigma = 60, 5
        deltas = np.random.normal(mu, sigma, N - 1)
        start = datetime(2018, 1, 1, 0, 0, 0)
        dts = [start]
        for d in deltas:
            dts.append(dts[-1] + timedelta(seconds=d))
        names = [datetime.strftime(_, utils.FMT) for _ in dts]
        events = list(utils.events(dts, names, min_len=100))
        self.assertEqual(len(events), 1)
        dt_chunk, name_chunk = events[0]
        self.assertEqual(dt_chunk, dts)
        self.assertEqual(name_chunk, names)


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


CASES = [
    TestEvents,
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
