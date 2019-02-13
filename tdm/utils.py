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

# The balanced partitioning functions have been copied verbatim from
# https://github.com/crs4/pydoop-examples (should probably be added to Pydoop)

import itertools


def balanced_parts(L, N):
    """\
    Find N numbers that sum up to L and are as close as possible to each other.

    >>> balanced_parts(10, 3)
    [4, 3, 3]
    """
    if not (1 <= N <= L):
        raise ValueError("number of partitions must be between 1 and %d" % L)
    q, r = divmod(L, N)
    return r * [q + 1] + (N - r) * [q]


def balanced_chunks(L, N):
    """\
    Same as balanced_part, but as an iterator through (offset, length) pairs.

    >>> list(balanced_chunks(10, 3))
    [(0, 4), (4, 3), (7, 3)]
    """
    lengths = balanced_parts(L, N)
    return zip(itertools.accumulate([0] + lengths), lengths)


def balanced_split(seq, N):
    """\
    Partition seq into exactly N balanced groups.

    Returns an iterator through the groups.

    >>> seq = list(range(10))
    >>> list(balanced_split(seq, 3))
    [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    for offset, length in balanced_chunks(len(seq), N):
        yield seq[offset: offset + length]
