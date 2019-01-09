"""\
Rotate radar images.

Images are cropped back to their original size (since all valid data lies
within a circle, there is no loss).

cag01est2400 images prior to 2018-12-21 17:30 need to be rotated by 54
degrees, hence the angle default.
"""

import argparse
import os
import sys

from imageio import imread, imwrite
from scipy.ndimage import rotate

import tdm.radar.utils as utils

ANGLE = 54
CVAL = 0  # OK for both signal and mask


def main(args):
    try:
        os.makedirs(args.out_dir)
    except FileExistsError:
        pass
    pairs = utils.get_images(args.in_dir)
    if len(pairs) == 0:
        raise RuntimeError(f"no radar image found in ${args.in_dir}")
    dts, paths = zip(*pairs)
    print(f"{args.in_dir}: {len(pairs)} images, from {dts[0]} to {dts[-1]}")
    print(f"  0/{len(paths)}")
    for i, p in enumerate(paths):
        if ((i + 1) % 10 == 0):
            print(f"  {i + 1}/{len(paths)}")
        out_p = os.path.join(args.out_dir, os.path.basename(p))
        if args.verbose:
            print(f"    writing {out_p}")
        data = imread(p)
        r_data = rotate(data, args.angle, reshape=False, cval=CVAL)
        imwrite(out_p, r_data, optimize=args.optimize)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("in_dir", metavar="IN_DIR", help="input directory")
    parser.add_argument("out_dir", metavar="OUT_DIR", help="output directory")
    parser.add_argument("-a", "--angle", metavar="DEGREES", default=ANGLE)
    parser.add_argument("-o", "--optimize", action="store_true",
                        help="minimize output file size")
    parser.add_argument("-v", "--verbose", action="store_true")
    main(parser.parse_args(sys.argv[1:]))
