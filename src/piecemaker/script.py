import os
import json
from optparse import OptionParser
from random import randint
from math import ceil, sqrt

from PIL import Image

from piecemaker.base import Pieces, variants
from piecemaker.adjacent import Adjacent
from piecemaker.lines_svg import create_lines_svg
from piecemaker.reduce import reduce_size
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
        "--minimum-piece-size",
        action="store",
        type="int",
        default=25,
        help="""Minimum piece size.
Will change the count of pieces to meet this if not set to 0.""",
    )

    parser.add_option(
        "--maximum-piece-size",
        action="store",
        type="int",
        default=0,
        help="""Maximum piece size.
Will resize the image if not set to 0 and should be at least greater than double the
set minimum piece size.""",
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
        choices=list(variants),
        help=f"""Piece cut variant to use. Defaults to 'interlockingnubs'.  Other choices are: {list(variants)}""",
    )

    (options, args) = parser.parse_args()

    if not options.dir:
        parser.error("Must set a directory to store generated files")

    if not args:
        parser.error("Must set an image as an arg.")

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
    maximum_piece_size = options.maximum_piece_size
    mydir = options.dir

    if maximum_piece_size != 0 and maximum_piece_size <= minimum_piece_size * 2:
        parser.error(
            "Maximum piece size should be more than double of minimum piece size if set."
        )

    if not options.svg:
        # create a grid of puzzle pieces in svg
        if minimum_piece_size < 0:
            parser.error("Invalid minimum piece size")
        if minimum_piece_size < 25:
            print("Warning: a minimum piece size less than 25 is not recommended.")

        if options.number_of_pieces < 0:
            parser.error("Invalid number of pieces")

        if minimum_piece_size < 1 and options.number_of_pieces < 1:
            parser.error(
                """
Must set minimum piece size greater than 0
or set number of pieces greater than 0.
                """
            )

        im = Image.open(imagefile)
        (width, height) = im.size
        im.close()

        (imagefile, jpc) = create_lines_svg(
            output_dir=mydir,
            minimum_piece_size=minimum_piece_size,
            maximum_piece_size=maximum_piece_size,
            width=width,
            height=height,
            number_of_pieces=options.number_of_pieces,
            imagefile=imagefile,
            variant=options.variant,
        )
        svgfile = os.path.join(mydir, "lines.svg")

        max_piece_side = max(jpc._piece_width, jpc._piece_height)
        minimum_pixels = jpc.pieces * (minimum_piece_size * minimum_piece_size)
        minimum_side = sqrt(minimum_pixels)
        side_count = sqrt(jpc.pieces)
        new_minimum_piece_size = ceil(minimum_side / side_count)
        minimum_scale = min(
            100, ceil((new_minimum_piece_size / max_piece_side) * 100.0)
        )
    else:
        svgfile = options.svg
        minimum_scale = min(scaled_sizes)

    table_width = int(width * 2.5)
    table_height = int(height * 2.5)

    scaled_sizes_greater_than_minimum = list(
        filter(lambda x: x >= minimum_scale, scaled_sizes)
    )
    if minimum_scale not in scaled_sizes_greater_than_minimum:
        scaled_sizes_greater_than_minimum.insert(1, minimum_scale)
    successful_scaled_sizes = []
    # First one will always be '100'
    piece_count_at_100_scale = None
    for scale in scaled_sizes_greater_than_minimum:
        scaled_dir = os.path.join(mydir, f"scale-{scale}")
        os.mkdir(scaled_dir)

        pieces = Pieces(
            svgfile,
            imagefile,
            scaled_dir,
            scale=scale,
            max_pixels=(width * height),
        )

        pieces.cut()

        pieces.generate_resources()

        piece_count = len(pieces.pieces)
        if scale == 100:
            piece_count_at_100_scale = piece_count
        if piece_count_at_100_scale == piece_count:
            successful_scaled_sizes.append(scale)
        else:
            print(
                f"Skipping scale {scale} since the piece count is not equal to piece count at 100 scale."
            )

    # Reset minimum_scale in case it was dropped out of the successful_scaled_sizes.
    successful_scaled_sizes.sort()
    minimum_scale = min(100, successful_scaled_sizes[0])

    scaled_sizes_less_than_minimum = list(
        filter(lambda x: x < minimum_scale, scaled_sizes)
    )
    for scale in scaled_sizes_less_than_minimum:
        reduce_size(
            scale=scale,
            minimum_scale=minimum_scale,
            output_dir=mydir,
        )

    with open(os.path.join(mydir, "scale-100", "pieces.json"), "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)
    piece_properties = []
    # TODO: Distribute pieces starting at the top and working down. Skip
    # placing pieces in the center box.
    for (i, bbox) in piece_bboxes.items():
        # TODO: set rotation of pieces
        # TODO: implement multiple sided pieces
        # TODO: set grouping ids to pieces.
        #   Example:
        #   red pieces = group id 1,
        #   blue pieces = group id 2,
        #   ungrouped pieces = group id 0,
        piece_properties.append(
            {
                "id": i,
                "x": randint(0, table_width - (bbox[2] - bbox[0])),
                "y": randint(0, table_height - (bbox[3] - bbox[1])),
                "r": 0,  # random rotation of piece
                "s": 0,  # random piece side
                "w": bbox[2] - bbox[0],
                "h": bbox[3] - bbox[1],
                "rotate": 0,  # correct rotation of piece
                "g": 0,  # grouping id
            }
        )
    # create index.json
    data = {
        "version": __version__,
        "generator": "piecemaker",
        "piece_cut_variant": options.variant,
        "scaled": successful_scaled_sizes,
        "reduced": scaled_sizes_less_than_minimum,
        "sides": [0],
        "piece_count": piece_count,
        "image_author": "",
        "image_link": "",
        "image_title": "",
        "image_description": "",
        "puzzle_author": "",
        "puzzle_link": "",
        "table_width": table_width,
        "table_height": table_height,
        "piece_properties": piece_properties,
    }
    f = open(os.path.join(mydir, "index.json"), "w")
    json.dump(data, f, indent=2)
    f.close()

    if options.adjacent:
        scaled_dir = os.path.join(mydir, "scale-100")
        adjacent = Adjacent(scaled_dir)
        f = open(os.path.join(mydir, "adjacent.json"), "w")
        json.dump(adjacent.adjacent_pieces, f)
        f.close()
