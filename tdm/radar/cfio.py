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
Store rainfall rate to NetCDF4, using the NetCDF Climate and Forecast
(CF) Metadata Conventions (http://cfconventions.org) Version 1.7.
"""

from netCDF4 import Dataset
import datetime
import os

import tdm.radar.utils as utils

strftime = datetime.datetime.strftime

GLOBAL_ATTRIBUTES = {
    "Conventions": "CF-1.7",
    "title": "Rainfall",
    "institution": "TDM",
    "source": "Radar",
    "references": "http://www.tdm-project.it",
    "history": "Estimated with https://github.com/tdm-project/tdm-tools"
}

TIME_UNIT_FMT = "%Y-%m-%d %H:%M:%S"

# HDF5 chunk size along the time dimension
T_CHUNKS = 30


def setncattr(dataset, attrs):
    for k, v in attrs.items():
        dataset.setncattr(k, v)


class NCWriter(object):

    def __init__(self, path, ga, nt, t0, t_chunks=T_CHUNKS):
        self.path = path
        self.ga = ga
        self.nt = nt
        self.t0 = t0
        self.t_chunks = min(t_chunks, nt)
        try:
            os.unlink(self.path)
        except FileNotFoundError:
            pass
        self.ds = Dataset(self.path, "w")
        self.ds.set_auto_mask(False)
        self.ds.set_always_mask(False)
        setncattr(self.ds, GLOBAL_ATTRIBUTES)
        self.__create_variables()
        self.__attach_crs()
        xpos, ypos = ga.xpos(), ga.ypos()
        lat_, lon_ = utils.get_lat_lon(ga.sr, xpos, ypos)
        self.x[:], self.y[:], self.lat[:], self.lon[:] = xpos, ypos, lat_, lon_

    def close(self):
        self.ds.close()

    # CF conventions, sections 4.4 & 5.1
    # See also: https://code.mpimet.mpg.de/boards/1/topics/5765
    def __create_variables(self):
        timed = self.ds.createDimension("time", self.nt)
        xd = self.ds.createDimension("x", self.ga.cols)
        yd = self.ds.createDimension("y", self.ga.rows)
        self.t = self.ds.createVariable(
            "time", "f4", (timed.name,), fill_value=False
        )
        setncattr(self.t, {
            "long_name": "time",
            "standard_name": "time",
            "units": "seconds since %s" % strftime(self.t0, TIME_UNIT_FMT)
        })
        self.x = self.ds.createVariable(
            "x", "f4", (xd.name,), fill_value=False
        )
        setncattr(self.x, {
            "long_name": "x coordinate of projection",
            "standard_name": "projection_x_coordinate",
            "units": "m"
        })
        self.y = self.ds.createVariable(
            "y", "f4", (yd.name,), fill_value=False
        )
        setncattr(self.y, {
            "long_name": "y coordinate of projection",
            "standard_name": "projection_y_coordinate",
            "units": "m"
        })
        self.lat = self.ds.createVariable(
            "lat", "f4", (xd.name, yd.name), fill_value=False
        )
        setncattr(self.lat, {
            "long_name": "latitude coordinate",
            "standard_name": "latitude",
            "units": "degrees_north"
        })
        self.lon = self.ds.createVariable(
            "lon", "f4", (xd.name, yd.name), fill_value=False
        )
        setncattr(self.lon, {
            "long_name": "longitude coordinate",
            "standard_name": "longitude",
            "units": "degrees_east"
        })
        fv = utils.RAINFALL_FILL_VALUE
        self.rf_rate = self.ds.createVariable(
            "rainfall_rate", "f4", (timed.name, xd.name, yd.name),
            fill_value=fv, zlib=True, least_significant_digit=4,
            chunksizes=(self.t_chunks, self.ga.cols, self.ga.rows)
        )
        self.rf_rate.set_var_chunk_cache(
            self.t_chunks * self.ga.rows * self.ga.cols * 4, 5, 1.0
        )
        setncattr(self.rf_rate, {
            'long_name': 'estimated rainfall rate',
            'standard_name': 'rainfall_rate',
            'coordinates': 'lat lon',
            'grid_mapping': 'crs',
            'units': 'mm/hour'
        })

    # CF conventions, section 5.6.1. TODO: derive attributes from the wkt
    def __attach_crs(self):
        crs = self.ds.createVariable('crs', 'i4')  # dummy scalar (anchor)
        setncattr(crs, {
            'grid_mapping_name': 'transverse_mercator',
            'longitude_of_central_meridian': 9.0,
            'latitude_of_projection_origin': 0.0,
            'false_easting': 1500000.0,
            'false_northing': 0.0,
            'scale_factor_at_central_meridian': 0.9996,
            'semi_major_axis': 6378388.0,
            'inverse_flattening': 297,
            'projected_coordinate_system_name':
                'EPSG:3003 Monte Mario / Italy zone 1',
            'geographic_coordinate_system_name': 'Monte Mario',
            'horizontal_datum_name':  'Monte_Mario',
            'reference_ellipsoid_name': 'International 1924',
            'prime_meridian_name': "Greenwich",
            'towgs84': [-104.1, -49.1, -9.9, 0.971, -2.917, 0.714, -11.68],
            'crs_wkt': self.ga.wkt
        })

    def write(self, i, dt, rr):
        self.t[i] = (dt - self.t0).total_seconds()
        self.rf_rate[i, :, :] = rr
