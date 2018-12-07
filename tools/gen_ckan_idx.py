"""\
Generate JSON resource index files for CKAN import.

For now, this is just a quick hack with no CLI. Read it carefully and change
top references as needed (e.g., FS_ROOT, URL_ROOT).
"""

from pathlib import Path
from urllib.parse import urljoin
import io
import json
import os

FS_ROOT = "/data"
URL_ROOT = "https://foo.bar.it"
EVENTS_RPATH = "tdm/datasets/radar/events"
GEOTIFF_RPATH = "tdm/odata/product/radar/cag01est2400"
OUT_DIR = os.path.join(str(Path.home()), "ckan_upload")

RESOURCE_DESC_HEAD = (
    "Rainfall rate in mm/h from radar cag01est2400. Area: "
    "lon:8.751948:9.466604, lat:38.951127:39.505794"
)
RESOLUTION_DESC = {
    "high_res": "One set of values per minute",
    "low_res": "Average values over 1h windows",
}
RESOLUTION_NAME = {
    "high_res": "High resolution",
    "low_res": "Low resolution",
}


def main():
    events_dir = os.path.join(FS_ROOT, EVENTS_RPATH)
    geotiffs_dir = os.path.join(FS_ROOT, GEOTIFF_RPATH)
    for event in os.listdir(events_dir):
        ev_dir = os.path.join(events_dir, event)
        if not os.path.isdir(ev_dir):
            continue
        geo_dir = os.path.join(geotiffs_dir, event)
        assert os.path.isdir(geo_dir)
        desc = {
            "package": {
                "name": f"radar_{event}",
                "title": f"Radar rainfall {event}",
                "owner_org": "tdm",
                "license_id": "cc-by",
                "groups": [
                    "meteo"
                ],
                "tags": [
                    "radar",
                    "rainfall"
                ],
                "notes": f"Radar rainfall dataset for weather event {event}",
            },
        }
        resources = []
        print(f"event: {event}")
        print("  netcdf:")
        for restype in os.listdir(ev_dir):
            res_dir = os.path.join(ev_dir, restype)
            if not os.path.isdir(res_dir):
                continue
            print("    resource: %r" % (restype,))
            res_desc = (
                f"{RESOURCE_DESC_HEAD}. {RESOLUTION_DESC[restype]}. "
                "Format: NetCDF. Projection: EPSG:3003."
            )
            for name in os.listdir(res_dir):
                url = urljoin(URL_ROOT, os.path.join(
                    EVENTS_RPATH, event, restype, name)
                )
                resources.append({
                    "url": url,
                    "name": f"{RESOLUTION_NAME[restype]} Rainfall NetCDF",
                    "format": "netcdf",
                    "description": res_desc,
                })
        print("  geotiff:")
        for restype in os.listdir(geo_dir):
            res_dir = os.path.join(geo_dir, restype)
            if not os.path.isdir(res_dir):
                continue
            print("    resource: %r" % (restype,))
            res_desc = (
                f"{RESOURCE_DESC_HEAD}. {RESOLUTION_DESC[restype]}. "
                "Format: GeoTIFF. Projection: EPSG:4326."
            )
            url = urljoin(URL_ROOT, os.path.join(
                GEOTIFF_RPATH, event, restype, "description.json")
            )
            resources.append({
                "url": url,
                "name": f"{RESOLUTION_NAME[restype]} Rainfall GeoTIFF",
                "format": "json",
                "description": res_desc,
            })
        desc["resources"] = resources
        out_path = os.path.join(OUT_DIR, f"ckan_upload_{event}.json")
        with io.open(out_path, "wt") as f:
            f.write(json.dumps(desc, indent=4, sort_keys=False))


if __name__ == "__main__":
    main()
