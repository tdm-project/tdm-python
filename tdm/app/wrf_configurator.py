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
Prepare WRF configuration files
"""

import argparse
import yaml
from tdm.wrf import configurator
from tdm.wrf import summarizer
from tdm.wrf import configuration_checker
from tdm import __version__ as version


from datetime import datetime

NOW = datetime.now()

SUPPORTED_TARGETS = ['WPS', 'WRF']


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def kv_pair(s):
    try:
        k, v = s.split("=", 1)
    except ValueError:
        raise argparse.ArgumentTypeError("arg must be in the k=v form")
    v = int(v) if is_int(v) else float(v) if is_float(v) else v
    return k, v


class UpdateMap(argparse.Action):
    """\
    Update the destination map with a K=V pair.

    >>> parser = argparse.ArgumentParser()
    >>> _ = parser.add_argument("-D", metavar="K=V", action=UpdateMap)
    >>> args = parser.parse_args(["-D", "k1=v1", "-D", "k2=v2", "-D", "k2=v3"])
    >>> args.D == {'k1': 'v1', 'k2': 'v3'}
    True
    """

    def __init__(self, option_strings, dest, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in {"help", "metavar"}}
        kwargs["type"] = kv_pair
        super(UpdateMap, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, {})
        getattr(namespace, self.dest).update([values])


def generate_header(target):
    now = datetime.utcnow()
    header = """
# WRF CONFIGURATOR V{} {}
# {}
""".format(version, target, now.strftime("%Y-%m-%d_%H:%M:%Sz"))
    return header


def write_wps(config, ostream):
    ostream.write(generate_header('WPS'))
    ostream.write(config.generate_share())
    ostream.write(config.generate_geogrid())
    ostream.write(config.generate_ungrib())
    ostream.write(config.generate_metgrid())


def write_wrf(config, ostream):
    ostream.write(generate_header('WRF'))
    ostream.write(config.generate_time_control())
    ostream.write(config.generate_domains())
    ostream.write(config.generate_physics())
    ostream.write(config.generate_fdda())
    ostream.write(config.generate_dynamics())
    ostream.write(config.generate_bdy_control())
    ostream.write(config.generate_grib2())
    ostream.write(config.generate_namelist_quilt())


def main(args):
    config = configurator.make(yaml.load(args.config.read()))
    if args.D:
        config.update(args.D)
    checker = configuration_checker(config)
    if not checker.check():
        print("Faults in the provided configuration")
        for f in checker.faults:
            print(f)
        exit(1)

    if args.summarize:
        s = summarizer(config)
        print(s.summarize())
        exit(0)

    if args.print:
        for k in args.print:
            print('{}'.format(config[k]))
        exit(0)

    if args.target == 'WPS':
        write_wps(config, args.ofile)
    elif args.target == 'WRF':
        write_wrf(config, args.ofile)


def add_parser(subparsers):
    parser = subparsers.add_parser(
        "wrf_configurator",
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--summarize", action="store_true",
                        help="Summarize configuration info and exit")
    parser.add_argument('--target', metavar="|".join(SUPPORTED_TARGETS),
                        choices=SUPPORTED_TARGETS, default='WPS')
    parser.add_argument('--config',
                        type=argparse.FileType('r', encoding='UTF-8'))
    parser.add_argument('--ofile',
                        type=argparse.FileType('w', encoding='UTF-8'))
    parser.add_argument('-D', metavar='K=V', action=UpdateMap,
                        help='Add/update configuration item.')
    parser.add_argument('-P', '--print', metavar='K', action='append',
                        help='Print configuration value for key K.')
    parser.set_defaults(func=main)
