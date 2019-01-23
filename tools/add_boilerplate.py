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
Add or update Apache 2.0 boilerplate notice.
"""

import io
import datetime
import os
import re

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
TOP_DIR = os.path.dirname(THIS_DIR)
LICENSE = os.path.join(TOP_DIR, "LICENSE")

OWNER = "CRS4"
YEAR_RANGE = f"2018-{datetime.date.today().year}"
BOILERPLATE_START = "Copyright [yyyy] [name of copyright owner]"
BOILERPLATE_START_REPL = f"Copyright {YEAR_RANGE} {OWNER}"
PATTERN = re.compile(f"Copyright.*{OWNER}")

EXCLUDE_FILE = frozenset((
    ".dockerignore",
    "Dockerfile",
    "LICENSE",
    "README.md",
    "version.py",
))
EXCLUDE_EXT = frozenset(("grib2", "png", "rst", "tif", "yml"))


def get_boilerplate():
    with io.open(LICENSE, "rt") as f:
        license = f.read()
    template = license[license.find(BOILERPLATE_START):]
    return template.replace(BOILERPLATE_START, BOILERPLATE_START_REPL)


def comment(text, char="#"):
    out_lines = []
    for line in text.splitlines():
        line = line.strip()
        out_lines.append(char if not line else f"{char} {line}")
    return "\n".join(out_lines) + "\n"


# only handles python files for now
def add_boilerplate(boilerplate, fn):
    with io.open(fn, "rt") as f:
        text = f.read()
    if not text:
        return
    m = PATTERN.search(text)
    if m:
        # update existing
        with io.open(fn, "wt") as f:
            f.write(text.replace(m.group(), BOILERPLATE_START_REPL))
        return
    # add new
    if text.startswith("#!"):
        head, tail = text.split("\n", 1)
        if "python" not in head:
            return
        head += "\n\n"
    else:
        if not fn.endswith(".py"):
            return
        head, tail = "", text
    boilerplate = comment(boilerplate)
    if not tail.startswith("\n"):
        boilerplate += "\n"
    with io.open(fn, "wt") as f:
        f.write(f"{head}{boilerplate}{tail}")


def main():
    join = os.path.join
    bp = get_boilerplate()
    for root, dirs, files in os.walk(TOP_DIR):
        dirs[:] = [_ for _ in dirs if not _.startswith(".")]
        for name in files:
            if name in EXCLUDE_FILE:
                continue
            if name.rsplit(".", 1)[-1] in EXCLUDE_EXT:
                continue
            path = join(root, name)
            add_boilerplate(bp, path)


if __name__ == "__main__":
    main()
