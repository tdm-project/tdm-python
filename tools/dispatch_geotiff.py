"""\
Rearrange single-timestamp geotiff images into a structured dir tree.

For now, this is just a quick hack with no CLI. Read it carefully and change
top references as needed (e.g., IN_DATA, FS_ROOT, URL_ROOT).

WARNING: this **moves** files, so it's not idempotent.
"""

from urllib.parse import urljoin
import datetime
import io
import json
import os

basename = os.path.basename
join = os.path.join
splitext = os.path.splitext
strptime = datetime.datetime.strptime


IN_DATA = "/data/inbox/radar_data/geotiff"
FS_ROOT = "/data"
URL_ROOT = "https://foo.bar.it"
PROC_ID = "high_res"

FMT = "%Y-%m-%d_%H:%M:%S"
DATE_FMT = FMT.split("_", 1)[0]
TIFF_EXT = frozenset((".tif", ".tiff"))

RADAR_RPATH = "tdm/odata/product/radar"
RADAR_ID = "cag01est2400"
MIN_LON, MAX_LON = 8.7519483, 9.4666037
MIN_LAT, MAX_LAT = 38.9511270, 39.5057942
GEORECT = "lon:%.6f:%.6f_lat:%.6f:%.6f" % (MIN_LON, MAX_LON, MIN_LAT, MAX_LAT)
FIELD = "rainfall_rate"


def get_fmap():
    rval = {}
    root = join(IN_DATA, PROC_ID)
    assert os.path.isdir(root)
    for acq_id in os.listdir(root):
        try:
            strptime(acq_id, DATE_FMT)
        except ValueError:
            continue
        subd = join(root, acq_id)
        assert os.path.isdir(subd)
        event_map = rval[acq_id] = {}
        for name in os.listdir(subd):
            dt, ext = splitext(name)
            if ext not in TIFF_EXT:
                continue
            path = join(subd, name)
            event_map[dt] = path
    return rval


def move_all(fmap):
    root = join(FS_ROOT, RADAR_RPATH, RADAR_ID)
    web_root = urljoin(URL_ROOT, join(RADAR_RPATH, RADAR_ID))
    for acq_id, d in fmap.items():
        print(f"moving data for: {acq_id}")
        event_root = join(root, acq_id)
        web_event_root = join(web_root, acq_id)
        resources = []
        for dt, src in d.items():
            d = join(event_root, PROC_ID, dt, GEORECT, FIELD)
            web_d = join(web_event_root, PROC_ID, dt, GEORECT, FIELD)
            try:
                os.makedirs(d)
            except FileExistsError:
                pass
            name = basename(src)
            dst = join(d, name)
            url = join(web_d, name)
            os.rename(src, dst)
            # print(f"rename {src} to {dst}")
            stat = os.stat(dst)
            resources.append({
                "name": name,
                "description": f"{RADAR_ID} rainfall, {dt}",
                "url": url,
                "format": "TIFF",
                "mimetype": "image/tiff",
                "created": stat.st_ctime,
                "last_modified": stat.st_mtime,
                "size": stat.st_size,
            })
        desc = {
            "result": {
                "resources": resources
            }
        }
        desc_path = join(event_root, PROC_ID, "description.json")
        with io.open(desc_path, "wt") as f:
            f.write(json.dumps(desc, indent=4, sort_keys=False))


def main():
    print("mapping files")
    fmap = get_fmap()
    print(f"events: {len(fmap)}")
    print(f"geotiffs: {sum(len(_) for _ in fmap.values())}")
    for acq_id, d in sorted(fmap.items()):
        print(f"  {acq_id}: {len(d)}")
    print(f"georect: {GEORECT}")
    print()
    move_all(fmap)


if __name__ == "__main__":
    main()
