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
Software tools for the TDM Project (http://www.tdm-project.it/en).
"""

from setuptools import setup
from tdm.version import VERSION

setup(
    name='tdm',
    version=VERSION,
    url='https://github.com/tdm-project/tdm-tools',
    description='TDM Tools - http://www.tdm-project.it/en/',
    long_description=__doc__,
    author=', '.join((
        'Simone Leo',
        'Gianluigi Zanetti',
    )),
    author_email=', '.join((
        '<simone.leo@crs4.it>',
        '<gianluigi.zanetti@crs4.it>',
    )),
    license='Apache-2.0',
    platforms=['Linux'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'Intended Audience :: Science/Research',
    ],
    packages=['tdm', 'tdm.gfs', 'tdm.gfs.noaa', 'tdm.radar', 'tdm.wrf'],
    scripts=[
        'bin/tdm_gfs_fetch',
        'bin/tdm_link_grib',
        'bin/tdm_map_to_lonlat',
        'bin/tdm_map_to_tree',
        'bin/tdm_radar_events',
        'bin/tdm_radar_nc_to_geo',
        'bin/tdm_rainfall',
        'bin/tdm_wrf_configurator',
        'bin/tdm_grib2cf',
    ],
)
