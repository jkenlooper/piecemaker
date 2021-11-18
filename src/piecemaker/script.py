import os
import json
from optparse import OptionParser
from math import ceil, sqrt

from PIL import Image

from piecemaker.base import Pieces, variants
from piecemaker.adjacent import Adjacent
from piecemaker.distribution import random_outside
from piecemaker.lines_svg import create_lines_svg
from piecemaker.reduce import reduce_size
from piecemaker.table_proof import generate_table_proof_html
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

    # TODO: use percent instead of 'scale'
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
        "--use-max-size",
        action="store_true",
        default=False,
        help="""Use the largest size when creating the size-100 directory instead of the smallest possible.""",
    )

    parser.add_option(
        "--variant",
        action="store",
        type="choice",
        default="interlockingnubs",
        choices=list(variants),
        help=f"""Piece cut variant to use. Defaults to 'interlockingnubs'.  Other choices are: {list(variants)}""",
    )

    parser.add_option(
        "--gap",
        default=True,
        action="store_false",
        help="Leave gap between pieces.",
    )

    (options, args) = parser.parse_args()

    if not options.dir:
        parser.error("Must set a directory to store generated files")

    if not args:
        parser.error("Must set an image as an arg.")

    if len(args) > 1:
        parser.error("Multiple pictures are not supported, yet.")

    scaled_sizes = set([int(x) for x in options.scaled_sizes.split(",")])
    if 100 not in scaled_sizes:
        parser.error("Must have at least a '100' in scaled sizes.")

    if args:
        imagefile = args[0]

    minimum_piece_size = options.minimum_piece_size
    maximum_piece_size = options.maximum_piece_size
    mydir = options.dir

    if maximum_piece_size != 0 and maximum_piece_size <= minimum_piece_size * 2:
        parser.error(
            "Maximum piece size should be more than double of minimum piece size if set."
        )

    minimum_scale = min(scaled_sizes)
    overlap_threshold = int(minimum_piece_size)
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
        width = jpc.width
        height = jpc.height

        max_piece_side = max(jpc._piece_width, jpc._piece_height)
        min_piece_side = min(jpc._piece_width, jpc._piece_height)
        minimum_pixels = jpc.pieces * (minimum_piece_size * minimum_piece_size)
        minimum_side = sqrt(minimum_pixels)
        side_count = sqrt(jpc.pieces)
        new_minimum_piece_size = ceil(minimum_side / side_count)
        if minimum_scale < 100:
            minimum_scale = min(
                100, ceil((new_minimum_piece_size / max_piece_side) * 100.0)
            )
        overlap_threshold = int((min_piece_side * 0.5) - (min_piece_side * 0.10))
    else:
        svgfile = options.svg

    scaled_sizes.add(minimum_scale)
    sizes = list(scaled_sizes)
    sizes.sort()

    scale_for_size_100 = 100 if options.use_max_size else minimum_scale

    full_size_dir = os.path.join(mydir, f"size-{scale_for_size_100}")
    os.mkdir(full_size_dir)

    pieces = Pieces(
        svgfile,
        imagefile,
        full_size_dir,
        scale=scale_for_size_100,
        max_pixels=(width * height),
        include_border_pixels=options.gap,
    )
    imagefile = pieces._scaled_image

    pieces.cut()

    pieces.generate_resources()

    piece_count = len(pieces.pieces)

    for size in sizes:
        if size == scale_for_size_100:
            continue
        reduce_size(
            scale=size,
            minimum_scale=scale_for_size_100,
            output_dir=mydir,
        )

    im = Image.open(imagefile)
    (width, height) = im.size
    im.close()
    table_width = int(width * 2.5)
    table_height = int(height * 2.5)
    outline_offset_x = int((table_width - width) * 0.5)
    outline_offset_y = int((table_height - height) * 0.5)

    with open(os.path.join(mydir, f"size-{scale_for_size_100}", "pieces.json"), "r") as pieces_json:
        piece_bboxes = json.load(pieces_json)
    piece_properties = []
    pieces_distribution = random_outside(
        table_bbox=[0, 0, table_width, table_height],
        outline_bbox=[outline_offset_x, outline_offset_y, outline_offset_x + width, outline_offset_y + height],
        piece_bboxes=piece_bboxes,
        regions=("left_side", "top_middle", "bottom_middle")
    )
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
                "x": pieces_distribution[i][0],
                "y": pieces_distribution[i][1],
                "ox": outline_offset_x + bbox[0],
                "oy": outline_offset_y + bbox[1],
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
        "full_size": scale_for_size_100,
        "sizes": sizes,
        "sides": [0],
        "piece_count": piece_count,
        "image_author": "",
        "image_link": "",
        "image_title": "",
        "image_description": "",
        "image_width": width,
        "image_height": height,
        "outline_bbox": [outline_offset_x, outline_offset_y, outline_offset_x + width, outline_offset_y + height],
        "puzzle_author": "",
        "puzzle_link": "",
        "table_width": table_width,
        "table_height": table_height,
        "piece_properties": piece_properties,
    }
    f = open(os.path.join(mydir, "index.json"), "w")
    json.dump(data, f, indent=2)
    f.close()

    scaled_dir = os.path.join(mydir, f"size-{scale_for_size_100}")
    adjacent = Adjacent(scaled_dir, overlap_threshold=overlap_threshold)
    f = open(os.path.join(mydir, "adjacent.json"), "w")
    json.dump(adjacent.adjacent_pieces, f)
    f.close()

    generate_table_proof_html(mydir=mydir)
