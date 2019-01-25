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
Estimate rainfall from radar output images and store results into NetCDF4
datasets, using the NetCDF Climate and Forecast (CF) Metadata Conventions
(http://cfconventions.org) Version 1.7.
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
T_CHUNKS = 30


def setncattr(dataset, attrs):
    for k, v in attrs.items():
        dataset.setncattr(k, v)


# CF conventions, sections 4.4 & 5.1
# See also: https://code.mpimet.mpg.de/boards/1/topics/5765
def create_variables(dataset, cols, rows, nt, t0, t_chunks=T_CHUNKS):
    timed = dataset.createDimension("time", nt)
    xd = dataset.createDimension("x", cols)
    yd = dataset.createDimension("y", rows)
    t = dataset.createVariable("time", "f4", (timed.name,), fill_value=False)
    setncattr(t, {
        "long_name": "time",
        "standard_name": "time",
        "units": "seconds since %s" % strftime(t0, TIME_UNIT_FMT)
    })
    x = dataset.createVariable("x", "f4", (xd.name,), fill_value=False)
    setncattr(x, {
        "long_name": "x coordinate of projection",
        "standard_name": "projection_x_coordinate",
        "units": "m"
    })
    y = dataset.createVariable("y", "f4", (yd.name,), fill_value=False)
    setncattr(y, {
        "long_name": "y coordinate of projection",
        "standard_name": "projection_y_coordinate",
        "units": "m"
    })
    lat = dataset.createVariable(
        "lat", "f4", (xd.name, yd.name), fill_value=False
    )
    setncattr(lat, {
        "long_name": "latitude coordinate",
        "standard_name": "latitude",
        "units": "degrees_north"
    })
    lon = dataset.createVariable(
        "lon", "f4", (xd.name, yd.name), fill_value=False
    )
    setncattr(lon, {
        "long_name": "longitude coordinate",
        "standard_name": "longitude",
        "units": "degrees_east"
    })
    fv = utils.RAINFALL_FILL_VALUE
    t_chunks = min(t_chunks, nt)
    rf_rate = dataset.createVariable(
        "rainfall_rate", "f4", (timed.name, xd.name, yd.name),
        fill_value=fv, zlib=True, least_significant_digit=4,
        chunksizes=(t_chunks, cols, rows)
    )
    rf_rate.set_var_chunk_cache(t_chunks * rows * cols * 4, 5, 1.0)
    setncattr(rf_rate, {
        'long_name': 'estimated rainfall rate',
        'standard_name': 'rainfall_rate',
        'coordinates': 'lat lon',
        'grid_mapping': 'crs',
        'units': 'mm/hour'
    })
    return t, x, y, lat, lon, rf_rate


# CF conventions, section 5.6.1. TODO: derive attributes from the wkt
def attach_crs(dataset, wkt):
    crs = dataset.createVariable('crs', 'i4')  # dummy scalar (anchor)
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
        'crs_wkt': wkt
    })


def write_rainfall(rf_rate, t, event):
    t[:] = [(_[0] - event[0][0]).total_seconds() for _ in event]
    print("  0/%d" % len(event))
    for i, (_, path) in enumerate(event):
        if ((i + 1) % 100 == 0):
            print("  %d/%d" % (i + 1, len(event)))
        signal = utils.get_image_data(path)
        rf_rate[i, :, :] = utils.estimate_rainfall(signal)


def write_avg_rainfall(rf_rate, t, groups):
    t[:] = [(_[0] - groups[0][0]).total_seconds() for _ in groups]
    for i, (dt, rr) in enumerate(utils.avg_rainfall(groups)):
        print("  %s (%d/%d)" % (strftime(dt, utils.FMT), i + 1, len(groups)))
        rf_rate[i, :, :] = rr


def main(args):
    try:
        os.makedirs(args.out_dir)
    except FileExistsError:
        pass
    ga = utils.GeoAdapter(args.footprint)
    xpos, ypos = ga.xpos(), ga.ypos()
    lat_, lon_ = utils.get_lat_lon(ga.sr, xpos, ypos)
    dt_path_pairs = utils.get_images(args.img_dir)
    groups = None
    if args.resolution:
        group_gen = utils.group_images(dt_path_pairs, args.resolution)
        groups = [(dt, list(g)) for dt, g in group_gen]
        nt, t0 = len(groups), groups[0][0]
    else:
        nt, t0 = len(dt_path_pairs), dt_path_pairs[0][0]
    ds_path = os.path.join(args.out_dir, "%s.nc" % strftime(t0, utils.FMT))
    print('saving "%s"' % ds_path)
    try:
        os.unlink(ds_path)
    except FileNotFoundError:
        pass
    ds = Dataset(ds_path, "w")
    ds.set_auto_mask(False)
    ds.set_always_mask(False)
    setncattr(ds, GLOBAL_ATTRIBUTES)
    t, x, y, lat, lon, rf_rate = create_variables(
        ds, ga.cols, ga.rows, nt, t0, t_chunks=args.t_chunks
    )
    attach_crs(ds, ga.wkt)
    x[:], y[:], lat[:], lon[:] = xpos, ypos, lat_, lon_
    if groups:
        write_avg_rainfall(rf_rate, t, groups)
    else:
        write_rainfall(rf_rate, t, dt_path_pairs)
    ds.close()


def add_parser(subparsers):
    parser = subparsers.add_parser("rainfall", description=__doc__)
    parser.add_argument("img_dir", metavar="PNG_IMG_DIR")
    parser.add_argument("footprint", metavar="GEOTIFF_FOOTPRINT")
    parser.add_argument("-r", "--resolution", metavar="N_SECONDS", type=int,
                        help="output average rainfall over N_SECONDS windows")
    parser.add_argument("-o", "--out-dir", metavar="DIR", default=os.getcwd())
    parser.add_argument("--t-chunks", metavar="N", type=int, default=T_CHUNKS,
                        help="chunk size along the t dimension")
    parser.set_defaults(func=main)
