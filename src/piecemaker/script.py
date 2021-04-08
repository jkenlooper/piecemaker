from builtins import str
from builtins import range
import os
import json
from optparse import OptionParser
from random import randint
#import time
from math import ceil, sqrt

from PIL import Image

from piecemaker.base import JigsawPieceClipsSVG, Pieces
from piecemaker.adjacent import Adjacent

from piecemaker._version import __version__


def piecemaker():
    parser = OptionParser(
        usage="%prog [options] path/to/image",
        version=__version__,
        description="create jigsaw puzzle pieces",
    )

    parser.add_option(
        "--dir",
        "-d",
        action="store",
        type="string",
        help="set the directory to store the files in",
    )
    parser.add_option(
        "--number-of-pieces",
        "-n",
        action="store",
        default=0,
        type="int",
        help="""Target count of pieces. Will be adjusted depending on other
criteria. If set to 0 then will fit as many pieces in depending on
the minimum piece size.""",
    )
    parser.add_option(
        "--svg",
        "-s",
        action="store",
        type="string",
        help="set the clips svg file instead of creating jigsaw pieces",
    )

    parser.add_option(
        "--no-svg-files",
        action="store_true",
        default=False,
        help="""skip creating the pieces in svg format""",
    )

    parser.add_option(
        "--minimum-piece-size",
        action="store",
        type="int",
        default=25,
        help="""Minimum piece size.
Will change the count of pieces to meet this if not set to 0.""",
    )

    parser.add_option(
        "--scaled-sizes",
        action="store",
        type="string",
        default="100",
        help="""Comma separated list of sizes to scale for. Must include 100 at least.
Any that are too small will not be created and a minimum scale will be
done for the ones that were dropped.
Example: 33,68,100,150 for 4 scaled puzzles with the last one being at 150%.""",
    )

    parser.add_option(
        "--just-clips",
        action="store_true",
        default=False,
        help="only create a clips svg file",
    )

    parser.add_option(
        "--width",
        action="store",
        type="int",
        help="""Width of the image or clips svg viewbox.
Will scale to this width if image is set.""",
    )
    parser.add_option(
        "--height",
        action="store",
        type="int",
        help="""Height of the image or clips svg viewbox.
Will scale to this height if image is set.""",
    )

    parser.add_option(
        "--adjacent",
        action="store_true",
        default=True,
        help="""Create the adjacent.json file with list of
adjacent pieces for each piece.""",
    )

    parser.add_option(
        "--variant",
        action="store",
        type="choice",
        default="interlockingnubs",
        choices=["interlockingnubs", "stochasticnubs"],
        help="""Piece cut variant to use.""",
    )

    (options, args) = parser.parse_args()

    if not options.dir:
        parser.error("Must set a directory to store generated files")

    if not options.just_clips and not args:
        parser.error("Must set an image if not just making clips.")

    if len(args) > 1:
        parser.error("Multiple pictures are not supported, yet.")

    scaled_sizes = [int(x) for x in options.scaled_sizes.split(",")]
    if 100 not in scaled_sizes:
        parser.error("Must have at least a '100' in scaled sizes.")
    scaled_sizes.remove(100)
    scaled_sizes.insert(0, 100)

    if args:
        imagefile = args[0]

    minimum_piece_size = options.minimum_piece_size

    if not options.svg:
        # create a grid of puzzle pieces in svg
        if minimum_piece_size < 0:
            parser.error("Invalid minimum piece size")
        if minimum_piece_size < 25:
            print(f"Warning: a minimum piece size less than 25 is not recommended.")

        if options.number_of_pieces < 0:
            parser.error("Invalid number of pieces")

        if minimum_piece_size < 1 and options.number_of_pieces < 1:
            parser.error(
                """
Must set minimum piece size greater than 0
or set number of pieces greater than 0.
                """
            )

        if not args and not (options.width and options.height):
            parser.error("Must set an image or specify both width and height.")

        if args and not (options.width and options.height):
            # TODO: handle more than just one picture
            im = Image.open(imagefile)
            (width, height) = im.size
            im.close()
        else:
            width = options.width
            height = options.height

        #extra_width = (width % options.minimum_piece_size) - options.minimum_piece_size
        #extra_height = height % options.minimum_piece_size
        minimum_piece_size = max(
            minimum_piece_size + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
            minimum_piece_size + (abs((height % minimum_piece_size) / minimum_piece_size - 1))
        )
        minimum_piece_size = max(
            minimum_piece_size + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
            minimum_piece_size + (abs((height % minimum_piece_size) / minimum_piece_size - 1))
        )
        minimum_piece_size = max(
            minimum_piece_size + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
            minimum_piece_size + (abs((height % minimum_piece_size) / minimum_piece_size - 1))
        )
        print(f"minimum_piece_size {minimum_piece_size}")
        jpc = JigsawPieceClipsSVG(
            width=width,
            height=height,
            pieces=options.number_of_pieces,
            minimum_piece_size=minimum_piece_size,
            variant=options.variant
        )
        svgfile = os.path.join(options.dir, "lines.svg")
        f = open(svgfile, "w")
        f.write(jpc.svg())
        f.close()
    else:
        # TODO:
        svgfile = options.svg

    if not options.just_clips:
        # should be at least one image set in args: imagefile
        if not (options.width and options.height):
            # Will get the width and height from the svg viewbox.
            size = None
        else:
            size = (options.width, options.height)

        mydir = options.dir

        max_piece_side = max(jpc._piece_width, jpc._piece_height)
        #print(f"max piece side {max_piece_side}")
        max_piece_size = sqrt(width * height) / sqrt(jpc.pieces)
        #print(f"max piece size {max_piece_size}")
        #minimum_scale = min(100, ceil(((minimum_piece_size * minimum_piece_size) / (max_piece_side * max_piece_side)) * 100.0))
        minimum_pixels = jpc.pieces * (minimum_piece_size * minimum_piece_size)
        #print(f"minimum_pixels {minimum_pixels}")
        minimum_side = sqrt(minimum_pixels)
        #print(f"minimum_side {minimum_side}")
        side_count = sqrt(jpc.pieces)
        #print(f"side_count {side_count}")
        new_minimum_piece_size = ceil(minimum_side / side_count)
        #print(f"new_minimum_piece_size {new_minimum_piece_size}")

        minimum_scale = min(100, ceil((new_minimum_piece_size / max_piece_side) * 100.0))

        #minimum_pixels = max_pixels * (minimum_scale / 100.0)

        #minimum_scale = min(100, ceil(max(
        #    (((minimum_piece_size) * (jpc._cols * 1)) / width) * 100.0,
        #    (((minimum_piece_size) * (jpc._rows * 1)) / height) * 100.0
        #)))
        #print(f"minimum scale {minimum_scale}")
        scaled_sizes = list(filter(lambda x: x >= minimum_scale, scaled_sizes))
        if minimum_scale not in scaled_sizes:
            scaled_sizes.insert(1, minimum_scale)
        dimensions = {}
        # First one will always be '100'
        piece_count_at_100_scale = None
        for scale in scaled_sizes:
            #print(f"minimum_piece_size * (width / ceil(jpc._piece_width)) > width * (scale / 100.0)")
            #print(f"{minimum_piece_size} * ({width} / {ceil(jpc._piece_width)}) > {width} * ({scale} / 100.0)")
            #print(f"{minimum_piece_size * (width / ceil(jpc._piece_width))} > {width * (scale / 100.0)}")
            #if minimum_piece_size * (width / ceil(jpc._piece_width)) > width * (scale / 100.0):
            #    print(f"Skipping {scale} since width is too small")
            #    continue
            #print(f"minimum_piece_size * (height / jpc._piece_height) > height * (scale / 100.0)")
            #print(f"{minimum_piece_size * (height / jpc._piece_height)} > {height * (scale / 100.0)}")
            #if minimum_piece_size * (height / ceil(jpc._piece_height)) > height * (scale / 100.0):
            #    print(f"Skipping {scale} since height is too small")
            #    continue
            scaled_dir = os.path.join(mydir, f"scale-{scale}")
            os.mkdir(scaled_dir)

            #start = time.perf_counter()
            pieces = Pieces(
                svgfile,
                imagefile,
                scaled_dir,
                scale=scale,
                max_pixels=(width * height),
                vector=not options.no_svg_files,
            )
            #stop = time.perf_counter()
            #print(f"Pieces init {stop - start}")

            #start = time.perf_counter()
            pieces.cut()
            #stop = time.perf_counter()
            #print(f"cut {stop - start}")

            #start = time.perf_counter()
            pieces.generate_resources()
            #stop = time.perf_counter()
            #print(f"generate_resources {stop - start}")

            piece_count = len(pieces.pieces)
            piece_bboxes = pieces.pieces
            if scale == 100:
                piece_count_at_100_scale = piece_count
            if piece_count_at_100_scale == piece_count:
                dimensions[scale] = {
                    "width": pieces.width,
                    "height": pieces.height,
                    "table_width": int(pieces.width * 2.5),
                    "table_height": int(pieces.height * 2.5),
                    "board_url": f"puzzle_board-{scale}.html",
                }
            else:
                print(f"Skipping scale {scale} since the piece count is not equal to piece count at 100 scale.")

        tw = dimensions[100]["table_width"]
        th = dimensions[100]["table_height"]
        piece_properties = []
        for i in range(0, piece_count):
            piece_properties.append(
                {
                    "id": i,
                    "x": randint(0, tw),
                    "y": randint(0, th),
                    "w": piece_bboxes[str(i)][2] - piece_bboxes[str(i)][0],
                    "h": piece_bboxes[str(i)][3] - piece_bboxes[str(i)][1],
                    "r": 0,
                    "s": 0,
                    "g": 0,
                }
            )
        # create index.json
        successful_scaled_sizes = list(dimensions.keys())
        successful_scaled_sizes.sort()
        data = {
            "version": __version__,
            "generator": "piecemaker",
            "scaled": successful_scaled_sizes,
            "sides": [0],
            "piece_count": piece_count,
            "image_author": "",
            "image_link": "",
            "image_title": "",
            "image_description": "",
            "puzzle_author": "",
            "puzzle_link": "",
            "scaled_dimensions": dimensions,
            "piece_properties": piece_properties,
        }
        f = open(os.path.join(mydir, "index.json"), "w")
        json.dump(data, f, indent=2)
        f.close()

        if options.adjacent:
            scaled_dir = os.path.join(mydir, f"scale-100")
            #start = time.perf_counter()
            adjacent = Adjacent(scaled_dir)
            #stop = time.perf_counter()
            #print(f"adjacent {stop - start}")
            f = open(os.path.join(mydir, "adjacent.json"), "w")
            json.dump(adjacent.adjacent_pieces, f)
            f.close()
