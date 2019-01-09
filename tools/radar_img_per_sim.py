"""\
Select radar images in the time range of each meteo sim.

Works on NetCDF datasets created with tdm_grib2cf.
"""
import datetime
import argparse
import os
import sys

import tdm.radar.utils as utils
import cdo

basename = os.path.basename
join = os.path.join
strftime = datetime.datetime.strftime
strptime = datetime.datetime.strptime

FMT = "%Y-%m-%dT%H:%M:%S"
MODELS = frozenset(("bolam", "moloch"))


# E.g., bolam_2018073001_6155f56b-40b1-4b9f-bad7-e785940b2076.nc
def get_paths(nc_dir):
    rval = {}
    for name in os.listdir(nc_dir):
        tag, ext = os.path.splitext(name)
        if ext != ".nc":
            continue
        parts = tag.split("_")
        if parts[0] not in MODELS:
            continue
        ts = parts[1]
        if ts == "IFS":
            ts = parts[2]
        date = strptime(ts, "%Y%m%d%H").date()
        date_str = datetime.date.strftime(date, "%Y-%m-%d")
        rval.setdefault(date_str, []).append(join(nc_dir, name))
    return rval


def get_dt_range(cdo_obj, nc):
    out = cdo_obj.showtimestamp(input=nc)[0]
    dts = [strptime(_, FMT) for _ in out.split()]
    return min(dts), max(dts)


def main(args):
    nc_paths = get_paths(args.sim_dir)
    c = cdo.Cdo()
    for date_str, nc_list in nc_paths.items():
        print("%s IN:" % date_str)
        start_list, stop_list = [], []
        for nc in nc_list:
            start, stop = get_dt_range(c, nc)
            print("  %s (%s to %s)" % (basename(nc), start, stop))
            start_list.append(start)
            stop_list.append(stop)
        start, stop = min(start_list), max(stop_list)
        out_subd = join(args.out_dir, date_str)
        print("%s OUT:" % date_str)
        print("  %s (%s to %s)" % (date_str, start, stop))
        sys.stdout.flush()
        try:
            os.makedirs(out_subd)
        except FileExistsError:
            pass
        pairs = utils.get_images(args.radar_dir, after=start, before=stop)
        for dt, src in pairs:
            out_name = "%s.png" % strftime(dt, utils.FMT)
            dst = join(out_subd, out_name)
            with open(src, "rb") as fi, open(dst, "wb") as fo:
                fo.write(fi.read())
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sim_dir", metavar="NETCDF_SIM_DIR")
    parser.add_argument("radar_dir", metavar="PNG_RADAR_DIR")
    parser.add_argument("-o", "--out-dir", metavar="DIR", default=os.getcwd())
    main(parser.parse_args(sys.argv[1:]))
