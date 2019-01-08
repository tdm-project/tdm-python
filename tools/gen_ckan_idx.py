"""\
Generate JSON resource index files for CKAN import.
"""

from glob import glob
from string import Template
import argparse
import datetime
import io
import json
import os
import re
import sys

join = os.path.join
strptime = datetime.datetime.strptime

ID_MAP = {
    "meteosim": ("bolam", "moloch"),
    "radar": ("cag01est2400",),
}
DS_RPATH = Template(join("tdm", "datasets", "${source}", "events"))
RA_RPATH = Template(join("tdm", "odata", "product", "${source}", "${id}"))


def get_stubs(stubs_dir):
    rval = {}
    for entry in os.scandir(stubs_dir):
        if entry.is_dir():
            continue
        date, ext = os.path.splitext(entry.name)
        if ext.lower() != ".json":
            continue
        rval[date] = entry.path
    return rval


def map_events(stubs, fs_root):
    m = {date: {"stub": json_path} for date, json_path in stubs.items()}
    for source, id_list in ID_MAP.items():
        ds_rpath = DS_RPATH.substitute(source=source)
        for entry in os.scandir(join(fs_root, ds_rpath)):
            if entry.name in m:
                m[entry.name].setdefault("ds", {})[source] = entry.path
        for id in id_list:
            ra_rpath = RA_RPATH.substitute(source=source, id=id)
            for entry in os.scandir(join(fs_root, ra_rpath)):
                if source == "radar":
                    date = entry.name
                else:
                    name = entry.name.rsplit("_", 1)[-1]
                    date_obj = strptime(name, "%Y%m%d%H").date()
                    date = datetime.date.strftime(date_obj, "%Y-%m-%d")
                ra_map = m[date].setdefault("ra", {})
                ra_map.setdefault(source, {})[id] = entry.path
    return m


def dump_event_map(m):
    for date, event in m.items():
        print(f"  date: {date}")
        print(f"    stub: {event['stub']}")
        for cat in "ds", "ra":
            print(f"    {cat}:")
            for src, subm in event[cat].items():
                if cat == "ds":
                    print(f"      {src}: {subm}")
                else:
                    print(f"      {src}:")
                    for id, path in subm.items():
                        print(f"        {id}: {path}")


def main(args):
    with io.open(args.desc_map, "rt", encoding="utf-8") as f:
        temp = json.load(f)
        short_desc_map, desc_map = temp["short"], temp["long"]
    try:
        os.makedirs(args.out_dir)
    except FileExistsError:
        pass
    stubs = get_stubs(args.stubs_dir)
    event_map = map_events(stubs, args.in_dir)
    print(f"{len(event_map)} events found")
    dump_event_map(event_map)

    for date, event in event_map.items():
        with io.open(event["stub"], "rt") as f:
            desc = json.load(f)
        resources = desc["resources"]

        # handle datasets
        for src, event_path in event["ds"].items():
            for proc_id in os.scandir(event_path):
                if src == "radar":
                    for ds in os.scandir(proc_id.path):
                        url = re.sub(f"^{args.in_dir}", args.base_url, ds.path)
                        resources.append({
                            "url": url,
                            "name": "_".join([
                                "bulk",
                                short_desc_map[src],
                                short_desc_map[proc_id.name]
                            ]),
                            "format": "netcdf",
                            "description": " - ".join([
                                desc_map[src],
                                desc_map[proc_id.name]
                            ])
                        })
                else:
                    for proj in os.scandir(proc_id.path):
                        for ds in os.scandir(proj.path):
                            url = re.sub(
                                f"^{args.in_dir}", args.base_url, ds.path
                            )
                            resources.append({
                                "url": url,
                                "name": "_".join([
                                    "bulk",
                                    short_desc_map[src],
                                    short_desc_map[proc_id.name],
                                    short_desc_map[proj.name],
                                ]),
                                "format": "netcdf",
                                "description": " - ".join([
                                    desc_map[src],
                                    desc_map[proc_id.name],
                                    desc_map[proj.name],
                                ])
                            })

        # handle "random" access
        for src, res_map in event["ra"].items():
            if src == "meteosim":
                for proc_id, path in res_map.items():
                    desc_path = glob(f"{path}/*/description.json")[0]
                    url = re.sub(
                        f"^{args.in_dir}", args.base_url, desc_path
                    )
                    resources.append({
                        "url": url,
                        "name": "_".join([
                            "ra",
                            short_desc_map[src],
                            short_desc_map[proc_id],
                            "latlon",
                        ]),
                        "format": "json",
                        "description": " - ".join([
                            desc_map[src],
                            desc_map[proc_id],
                            "lat-lon geotiff",
                        ])
                    })
            else:
                path = [_ for _ in res_map.values()][0]
                for entry in os.scandir(path):
                    desc_path = join(entry.path, "description.json")
                    url = re.sub(
                        f"^{args.in_dir}", args.base_url, desc_path
                    )
                    resources.append({
                        "url": url,
                        "name": "_".join([
                            "ra",
                            short_desc_map[src],
                            short_desc_map[entry.name],
                            "latlon",
                        ]),
                        "format": "json",
                        "description": " - ".join([
                            desc_map[src],
                            desc_map[entry.name],
                            "lat-lon geotiff",
                        ])
                    })

        out_path = join(args.out_dir, os.path.basename(event["stub"]))
        with io.open(out_path, "wt", encoding="utf-8") as f:
            f.write(json.dumps(desc, indent=4, sort_keys=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stubs_dir", metavar="STUBS_DIR",
                        help="dir containing the top-level JSON stubs")
    parser.add_argument("desc_map", metavar="DESC_MAP_JSON",
                        help="JSON resource description map")
    parser.add_argument("base_url", metavar="BASE_URL")
    parser.add_argument("-i", "--in-dir", metavar="DIR", default=os.getcwd())
    parser.add_argument("-o", "--out-dir", metavar="DIR",
                        default=join(os.getcwd(), "ckan_upload"))
    parser.add_argument("--overwrite", action="store_true")
    main(parser.parse_args(sys.argv[1:]))
