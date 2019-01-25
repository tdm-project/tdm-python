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
import unittest

import numpy as np
from tdm.radar.events import split as split_events
from tdm.radar.utils import FMT as DT_FMT


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
        names = [datetime.strftime(_, DT_FMT) for _ in dts]
        dt_path_pairs = list(zip(dts, names))

        events = list(split_events(dt_path_pairs, min_len=100))
        self.assertEqual(len(events), 4)
        exp_lengths = [1001, 10001 - 1001, 50001 - 10001, 100000 - 50001]
        self.assertEqual([len(_) for _ in events], exp_lengths)
        self.assertEqual(events[0], dt_path_pairs[:1001])
        self.assertEqual(events[1], dt_path_pairs[1001:10001])
        self.assertEqual(events[2], dt_path_pairs[10001:50001])
        self.assertEqual(events[3], dt_path_pairs[50001:])

        events = list(split_events(dt_path_pairs, min_len=timedelta(days=1)))
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
        names = [datetime.strftime(_, DT_FMT) for _ in dts]
        dt_path_pairs = list(zip(dts, names))
        events = list(split_events(dt_path_pairs, min_len=100))
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0], dt_path_pairs)

    def test_small(self):
        dt_path_pairs = [(datetime(2018, 1, 1, 0, 0, 0), "/foo/bar")]
        events = list(split_events(dt_path_pairs, min_len=0))
        self.assertEqual(events, [dt_path_pairs])
        events = list(split_events(dt_path_pairs))
        self.assertEqual(events, [])
        events = list(split_events([]))
        self.assertEqual(events, [])


if __name__ == '__main__':
    unittest.main()
