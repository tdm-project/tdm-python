from datetime import datetime, timedelta
from itertools import product
import itertools as it
import os
import numpy as np

import gdal
from gdal import osr

gdal.UseExceptions()

strptime = datetime.strptime
splitext = os.path.splitext

FMT = "%Y-%m-%d_%H:%M:%S"
MIN_DT, MAX_DT = datetime.min, datetime.max

# The radar is supposed to generate an image every minute. In practice, while
# the peak is at 60s, deltas can go below 50 and above 70 (data from >120K
# images). 200s seems a good threshold for separating between events (i.e., a
# delta larger than that means the radar has been turned off and on again).
EVENT_THRESHOLD = 200

# Ignore events that last less than this, in seconds
MIN_EVENT_LEN = 24 * 60 * 60


class GeoAdapter(object):

    def __init__(self, template):
        self.raster = gdal.Open(template)
        oX, pxlW, _1, oY, _2, pxlH = self.raster.GetGeoTransform()
        # we only deal with rectangular, axis-aligned images
        if _1 or _2:
            raise RuntimeError("%s: unsupported transform")
        self.wkt = self.raster.GetProjectionRef()
        self.sr = osr.SpatialReference(wkt=self.wkt)
        factor = self.sr.GetLinearUnits()  # mult factor to get meters
        self.cols, self.rows = self.raster.RasterXSize, self.raster.RasterYSize
        self.oX, self.oY = oX, oY
        self.pxlW, self.pxlH = factor * pxlW, factor * pxlH

    def save_as_gtiff(self, fname, data, metadata=None):
        raster = gdal.GetDriverByName('GTiff').Create(
            fname, self.cols, self.rows, 1, gdal.GDT_Float32
        )
        raster.SetGeoTransform((self.oX, self.pxlW, 0, self.oY, 0, self.pxlH))
        if isinstance(metadata, dict):
            raster.SetMetadata(metadata)
        band = raster.GetRasterBand(1)
        band.WriteArray(data)
        raster.SetProjection(self.wkt)
        band.FlushCache()

    def compute_distance_field(self):
        x = self.pxlW * (np.arange(-(self.cols/2), (self.cols/2), 1) + 0.5)
        y = self.pxlH * (np.arange(-(self.rows/2), (self.rows/2), 1) + 0.5)
        xx, yy = np.meshgrid(x, y, sparse=True)
        return 10 * np.log(xx**2 + yy**2)

    def xpos(self):
        return self.oX + self.pxlW * np.arange(self.cols)

    def ypos(self):
        return self.oY + self.pxlH * np.arange(self.rows)


def get_raw_radar_images(root, after=MIN_DT, before=MAX_DT):
    ls = []
    for bn in os.listdir(root):
        dt_string = splitext(bn)[0]
        try:
            dt = strptime(dt_string, FMT)
        except ValueError:
            continue
        if dt < after or dt > before:
            continue
        ls.append((dt, os.path.join(root, bn)))
    ls.sort()
    return ls


def get_grouped_raw_radar_images(root, delta, after=MIN_DT, before=MAX_DT):
    assert isinstance(delta, timedelta)

    def grouper(p):
        return after + delta * ((p[0] - after) // delta)

    return it.groupby(get_raw_radar_images(root, after, before), grouper)


def estimate_rainfall(signal, mask):
    "This is specific to XXX radar signal"
    Z = 10**(0.1*(0.39216 * signal - 8.6))
    return (Z/300)**(1/1.5) * mask


# https://gis.stackexchange.com/questions/139906
def get_wkt(srs_code):
    # checks? we need no stinking checks!
    geo, code = srs_code.split(':')
    srs = osr.SpatialReference()
    # force geo to EPSG for the time being
    srs.ImportFromEPSG(int(code))
    return srs.ExportToWkt()


def warp(in_path, out_path, t_srs, s_srs=None, error_threshold=None):
    src_ds = gdal.Open(in_path)
    dst_wkt = get_wkt(t_srs)
    src_wkt = None if s_srs is None else get_wkt(s_srs)
    error_threshold = error_threshold if error_threshold is not None else 0.125
    resampling = gdal.GRA_NearestNeighbour
    # Call AutoCreateWarpedVRT() to fetch default values for target raster
    # dimensions and geotransform
    tmp_ds = gdal.AutoCreateWarpedVRT(src_ds,
                                      src_wkt,
                                      dst_wkt,
                                      resampling,
                                      error_threshold)
    # Create the final warped raster
    gdal.GetDriverByName('GTiff').CreateCopy(out_path, tmp_ds)


def events(dts, names, min_len=MIN_EVENT_LEN, threshold=EVENT_THRESHOLD):
    assert len(dts) == len(names)
    if not isinstance(min_len, timedelta):
        min_len = timedelta(seconds=min_len)
    deltas = np.array([(dts[i+1] - dts[i]).total_seconds()
                       for i in range(len(dts) - 1)])
    big_delta_idx = np.argwhere(deltas > threshold)[:, 0]
    dts_idx = np.insert(1 + big_delta_idx, 0, 0)
    dts_idx = np.append(dts_idx, len(dts))
    for i in range(dts_idx.size - 1):
        b, e = dts_idx[i], dts_idx[i+1]
        if dts[e - 1] - dts[b] < min_len:
            continue
        yield dts[b: e], names[b: e]


def get_lat_lon(source_sr, xpos, ypos):
    target_sr = osr.SpatialReference()
    target_sr.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(source_sr, target_sr)
    lon, lat, _ = zip(*transform.TransformPoints(list(product(xpos, ypos))))
    lon = np.array(lon).reshape(len(ypos), len(xpos))
    lat = np.array(lat).reshape(len(ypos), len(xpos))
    return lat, lon
