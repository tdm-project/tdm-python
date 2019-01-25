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
By "event" we mean any time interval during which the radar acquired images.

Ideally, events should be defined by prior knowledge. This module provides a
simple heuristic to automatically split an arbitrary number of images into
"events" during which the radar has been continuously on. Since the radar
acquires an image every minute or so (most time deltas are between 50 and 70
seconds), we can assume that a time difference of more than a few minutes
represents a pause.
"""

from datetime import timedelta

import numpy as np

# minimum pause between distinct events, in seconds
EVENT_THRESHOLD = 200

# Ignore events that last less than this, in seconds
MIN_EVENT_LEN = 24 * 60 * 60


def split(dt_path_pairs, min_len=MIN_EVENT_LEN, threshold=EVENT_THRESHOLD):
    """\
    Split a sequence of (datetime, path) pairs into "events".
    """
    if not isinstance(min_len, timedelta):
        min_len = timedelta(seconds=min_len)
    p, N = dt_path_pairs, len(dt_path_pairs)
    if N == 0:
        return
    deltas = np.array([(p[i+1][0] - p[i][0]).total_seconds()
                       for i in range(N - 1)])
    big_delta_idx = np.argwhere(deltas > threshold)[:, 0]
    dts_idx = np.insert(1 + big_delta_idx, 0, 0)
    dts_idx = np.append(dts_idx, N)
    for i in range(dts_idx.size - 1):
        b, e = dts_idx[i], dts_idx[i+1]
        if p[e - 1][0] - p[b][0] < min_len:
            continue
        yield p[b: e]
