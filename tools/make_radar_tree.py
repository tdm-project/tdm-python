#!/usr/bin/env python3

"""\
Generate the 'random access' tree for radar geotiffs.

Expected input dir structure: <PROC_ID>/<ACQ_ID>/<DATETIME>.tif

E.g., 1h/2018-10-10/2018-10-10_00:00:00.tif
"""

import argparse
import io
import json
import os
import shutil
import sys

join = os.path.join
splitext = os.path.splitext

TIFF_EXT = frozenset((".tif", ".tiff"))
RADAR_ID = "cag01est2400"
BASE_RPATH = join("tdm", "odata", "product", "radar", RADAR_ID)
MIN_LON, MAX_LON = 8.7519483, 9.4666037
MIN_LAT, MAX_LAT = 38.9511270, 39.5057942
GEORECT = "lon:%.6f:%.6f_lat:%.6f:%.6f" % (MIN_LON, MAX_LON, MIN_LAT, MAX_LAT)
DESC_NAME = "description.json"
TIFF_NAME = "rain.tif"


def idirs(scan_it):
    return (_ for _ in scan_it if _.is_dir())


class Dispatcher(object):

    def __init__(self, in_dir, fs_root, web_root):
        self.in_dir = in_dir
        self.fs_root = fs_root
        self.web_root = web_root
        self.rpath = BASE_RPATH

    def dispatch(self, move=False):
        transfer = os.rename if move else shutil.copy2
        for proc_id in idirs(os.scandir(self.in_dir)):
            if proc_id.name == os.path.basename(self.fs_root):
                continue
            print(f"proc_id: {proc_id.name}")
            for acq_id in idirs(os.scandir(proc_id.path)):
                print(f"  acq_id: {acq_id.name}")
                self.__handle_event(acq_id, proc_id, transfer)

    def __handle_event(self, acq_id, proc_id, transfer):
        rpath = join(self.rpath, acq_id.name, proc_id.name)
        resources = []
        for img in os.scandir(acq_id.path):
            self.__handle_img(img, rpath, transfer, resources)
        desc = {
            "result": {
                "resources": resources
            }
        }
        desc_path = join(self.fs_root, rpath, DESC_NAME)
        with io.open(desc_path, "wt") as f:
            f.write(json.dumps(desc, indent=4, sort_keys=False))

    def __handle_img(self, img, event_rpath, transfer, resources):
        dt, ext = splitext(img.name)
        if ext not in TIFF_EXT or img.is_dir():
            return
        img_rpath = join(event_rpath, dt, GEORECT)
        stat = img.stat()
        resources.append({
            "name": img.name,
            "description": f"{RADAR_ID} rainfall, {dt}",
            "url": join(self.web_root, img_rpath, TIFF_NAME),
            "format": "TIFF",
            "mimetype": "image/tiff",
            "created": stat.st_ctime,
            "last_modified": stat.st_mtime,
            "size": stat.st_size,
        })
        img_dir = join(self.fs_root, img_rpath)
        try:
            os.makedirs(img_dir)
        except FileExistsError:
            pass
        transfer(img.path, join(img_dir, TIFF_NAME))


def main(args):
    try:
        os.makedirs(args.out_dir)
    except FileExistsError:
        if not args.overwrite:
            raise RuntimeError(f"{args.out_dir} exists")
    dispatcher = Dispatcher(args.in_dir, args.out_dir, args.base_url)
    dispatcher.dispatch(move=args.move)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", metavar="BASE_URL")
    parser.add_argument("-i", "--in-dir", metavar="DIR", default=os.getcwd())
    parser.add_argument("-o", "--out-dir", metavar="DIR",
                        default=join(os.getcwd(), "tree"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--move", action="store_true")
    main(parser.parse_args(sys.argv[1:]))
