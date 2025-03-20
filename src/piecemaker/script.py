import os
import json
import argparse
from math import ceil, sqrt
from random import randint

from PIL import Image

from piecemaker.base import Pieces, variants
from piecemaker.adjacent import Adjacent
from piecemaker.distribution import random_piece_distribution, regions_set, bbox_layout
from piecemaker.lines_svg import create_lines_svg
from piecemaker.reduce import reduce_size
from piecemaker._version import __version__


def piecemaker():
    parser = argparse.ArgumentParser(
        description="Create jigsaw puzzle pieces.",
    )
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument(
        "--dir",
        "-d",
        action="store",
        help="set the directory to store the files in",
    )
    parser.add_argument(
        "--number-of-pieces",
        "-n",
        action="store",
        default=0,
        type=int,
        help="""Target count of pieces. Will be adjusted depending on other
criteria. If set to 0 then will fit as many pieces in depending on
the minimum piece size.""",
    )
    parser.add_argument(
        "--svg",
        "-s",
        action="store",
        help="Set the clips svg file instead of creating jigsaw pieces.",
    )

    parser.add_argument(
        "--exclude-outside-piece-container",
        action="store_true",
        default=False,
        help="Exclude creating a piece for the outside container that matches the width and height of the image",
    )
    parser.add_argument(
        "--exclude-piece-size",
        action="store",
        default="0x0",
        help="Exclude creating any pieces that are larger in width or height. 0x0 will not exclude pieces.",
    )

    parser.add_argument(
        "--minimum-piece-size",
        action="store",
        type=int,
        default=25,
        help="""Minimum piece size.
Will change the count of pieces to meet this if not set to 0.""",
    )

    parser.add_argument(
        "--maximum-piece-size",
        action="store",
        type=int,
        default=0,
        help="""Maximum piece size.
Will resize the image if not set to 0 and should be at least greater than double the
set minimum piece size.""",
    )

    # TODO: use percent instead of 'scale'
    parser.add_argument(
        "--scaled-sizes",
        action="store",
        default="100",
        help="""Comma separated list of sizes to scale for. Must include 100 at least.
Any that are too small will not be created and a minimum scale will be
done for the ones that were dropped.
Example: 33,68,100,150 for 4 scaled puzzles with the last one being at 150%%.""",
    )

    parser.add_argument(
        "--use-max-size",
        action="store_true",
        default=False,
        help="""Use the largest size when creating the size-100 directory instead of the smallest possible.""",
    )
    variants_list = sorted(variants)
    parser.add_argument(
        "--variant",
        action="store",
        default=variants_list[0],
        choices=variants_list,
        help=f"""Piece cut variant to use. Defaults to '{variants_list[0]}' if not using svg file.""",
    )

    distributions = (
        "default", # random nonoverlapping left_side top_middle bottom_middle
        "joined",  # Useful for testing a puzzle
        "random",
        "nonoverlapping",
        "overlapping",
        "center",
        "left_side",
        "top_middle",
        "bottom_middle",
        "right_side",
    )
    parser.add_argument(
        "--distribution",
        action="store",
        default=(distributions[0],),
        nargs="*",
        choices=distributions,
        help="""Piece distribution to use. If 'default' is used it will override any other choices.""",
    )

    parser.add_argument(
        "--table-size-factor",
        action="store",
        type=str,
        default="2.5x2.5",
        help="Width and height of table based on image dimensions. Default is '2.5x2.5'."
    )

    parser.add_argument(
        "--gap",
        default=True,
        action="store_false",
        help="Leave gap between pieces.",
    )

    parser.add_argument(
        "--trust-image-file",
        default=False,
        action="store_true",
        help="Trust the image file and remove max image pixels limit",
    )

    parser.add_argument(
        "--floodfill-min",
        action="store",
        default=400,
        type=int,
        help="Minimum pixels to floodfill for a piece",
    )
    parser.add_argument(
        "--floodfill-max",
        action="store",
        default=50_000_000,
        type=int,
        help="Max pixels to floodfill at a time",
    )

    parser.add_argument(
        "--mix-sides",
        action="store_true",
        default=False,
        help="""Mix which side of a piece is displayed if using multiple images.""",
    )

    parser.add_argument(
        "--rotate",
        action="store",
        default="0,0,1",
        help="Random rotate pieces range for start, stop, step",
    )

    parser.add_argument("image", nargs="+", help="JPG image")

    args = parser.parse_args()

    table_width_factor, table_height_factor = tuple(map(lambda x: max(1, float(x)), args.table_size_factor.split("x", 2)))

    if not args.dir:
        parser.error("Must set a directory to store generated files")

    scaled_sizes = set([int(x) for x in args.scaled_sizes.split(",")])
    if 100 not in scaled_sizes:
        parser.error("Must have at least a '100' in scaled sizes.")

    images = args.image
    imagefile = images[0]

    minimum_piece_size = args.minimum_piece_size
    maximum_piece_size = args.maximum_piece_size
    mydir = args.dir

    if maximum_piece_size != 0 and maximum_piece_size <= minimum_piece_size * 2:
        parser.error(
            "Maximum piece size should be more than double of minimum piece size if set."
        )

    minimum_scale = min(scaled_sizes)
    overlap_threshold = int(minimum_piece_size)

    if args.trust_image_file:
        # No warning about possible DecompressionBombWarning since the image
        # being used is trusted.
        Image.MAX_IMAGE_PIXELS = None

    im = Image.open(imagefile)
    (width, height) = im.size
    im.close()

    if not args.svg:
        # create a grid of puzzle pieces in svg
        if minimum_piece_size < 0:
            parser.error("Invalid minimum piece size")
        if minimum_piece_size < 25:
            print("Warning: a minimum piece size less than 25 is not recommended.")

        if args.number_of_pieces < 0:
            parser.error("Invalid number of pieces")

        if minimum_piece_size < 1 and args.number_of_pieces < 1:
            parser.error(
                """
Must set minimum piece size greater than 0
or set number of pieces greater than 0.
                """
            )


        (imagefile, jpc) = create_lines_svg(
            output_dir=mydir,
            minimum_piece_size=minimum_piece_size,
            maximum_piece_size=maximum_piece_size,
            width=width,
            height=height,
            number_of_pieces=args.number_of_pieces,
            imagefile=imagefile,
            variant=args.variant,
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
        if minimum_scale <= 100:
            minimum_scale = min(
                100, ceil((new_minimum_piece_size / max_piece_side) * 100.0)
            )
        overlap_threshold = int((min_piece_side * 0.5) - (min_piece_side * 0.10))
    else:
        svgfile = args.svg

    scaled_sizes.add(minimum_scale)
    sizes = list(scaled_sizes)
    sizes.sort()

    scale_for_size_100 = 100 if (args.use_max_size or args.svg) else minimum_scale

    full_size_dir = os.path.join(mydir, f"size-{scale_for_size_100}")
    os.mkdir(full_size_dir)

    exclude_width = None
    exclude_height = None
    if args.exclude_outside_piece_container:
        exclude_width = width
        exclude_height = height
    if args.exclude_piece_size != "0x0":
        exclude_piece_width, exclude_piece_height = map(int, args.exclude_piece_size.split("x")[:2])
        if exclude_piece_width == 0:
            exclude_width = None
        else:
            exclude_width = min(exclude_width or width, width, exclude_piece_width)
        if exclude_piece_height == 0:
            exclude_height = None
        else:
            exclude_height = min(exclude_height or height, height, exclude_piece_height)

    rotate = tuple(range(*(int(x) for x in args.rotate.split(","))))

    pieces = Pieces(
        svgfile,
        images,
        full_size_dir,
        scale=scale_for_size_100,
        max_pixels=(width * height),
        include_border_pixels=args.gap,
        exclude_size=(exclude_width, exclude_height),
        floodfill_min=args.floodfill_min,
        floodfill_max=args.floodfill_max,
        mix_sides=args.mix_sides,
        rotate=rotate,
    )
    scaled_images = pieces._scaled_images

    pieces.cut()

    pieces.generate_resources()

    piece_count = len(pieces.pieces)

    for size in sizes:
        if size == scale_for_size_100:
            continue
        if not args.use_max_size and size > scale_for_size_100:
            # Scaling up the pieces when the max piece size is set in order to
            # fit the image dimensions is not ideal.
            continue
        reduce_size(
            scale=size,
            minimum_scale=scale_for_size_100,
            output_dir=mydir,
            scaled_images=scaled_images,
        )

    im = Image.open(scaled_images[0])
    (width, height) = im.size
    im.close()
    table_width = int(width * table_width_factor)
    table_height = int(height * table_height_factor)
    outline_offset_x = int((table_width - width) * 0.5)
    outline_offset_y = int((table_height - height) * 0.5)

    with open(
        os.path.join(mydir, f"size-{scale_for_size_100}", "pieces.json"), "r"
    ) as pieces_json:
        piece_bboxes = json.load(pieces_json)
    with open(
        os.path.join(mydir, f"size-{scale_for_size_100}", "sides.json"), "r"
    ) as f:
        sides = json.load(f)
    piece_properties = []
    default_region_set = ("left_side", "top_middle", "bottom_middle")

    if "joined" in args.distribution:
        pieces_distribution = bbox_layout(
            table_bbox=(0, 0, table_width, table_height),
            piece_bboxes=piece_bboxes,
        )
    else:  # Defaults to random
        pieces_distribution = random_piece_distribution(
            table_bbox=(0, 0, table_width, table_height),
            outline_bbox=(
                outline_offset_x,
                outline_offset_y,
                outline_offset_x + width,
                outline_offset_y + height,
            ),
            piece_bboxes={k: v[9:13] + [v[4]] for k, v in piece_bboxes.items()},
            regions=default_region_set if "default" in args.distribution else set(args.distribution).intersection(regions_set) or default_region_set,
            nonoverlapping=True if "default" in args.distribution else "nonoverlapping" in args.distribution,
        )

    side_count = len(images)
    for (i, bbox) in piece_bboxes.items():
        # TODO: set grouping ids to pieces. Should be a tuple for each side.
        #   Example (group ids would be arbitrary):
        #   solid color = group id 0,
        #   2 solid colors = group id 5,
        #   3 solid colors = group id 6,
        #   more than 3 solid colors = group id 7,
        #   red pieces = group id 1,
        #   blue pieces = group id 2,
        #   green pieces = group id 4,
        #   edge pieces = group id 3,
        # Considering a two-sided puzzle:
        #   default is ungrouped: g = ((), ())
        #   A solid blue edge piece: g = ((0, 2, 3,), (3,))
        #   A multicolor edge piece: g = ((3,), (3,))
        #   A piece with both blue and green: g = ((2, 4), ())
        # Edge piece detection could be based on adjacent count.
        piece_properties.append(
            {
                "id": i,
                "x": pieces_distribution[i][0],
                "y": pieces_distribution[i][1],
                "ox": outline_offset_x + bbox[0],
                "oy": outline_offset_y + bbox[1],
                "ow": bbox[2] - bbox[0],  # width before rotation
                "oh": bbox[3] - bbox[1],  # height before rotation
                "r": randint(0, 360) if rotate else 0,  # random rotation of piece
                "s": 0 if side_count == 1 else randint(0, side_count - 1),  # random piece side
                "w": bbox[11] - bbox[9],
                "h": bbox[12] - bbox[10],
                "rotate": bbox[4],  # correct rotation of piece
                "sides": sides.get(i,(0,)),  # correct side (duplicates sides.json)
                "g": 0,  # grouping id
                "cx": bbox[5],  # center_x
                "cy": bbox[6],  # center_y
                "cxo": bbox[7],  # center_x_offset
                "cyo": bbox[8],  # center_y_offset
            }
        )
    # create index.json
    data = {
        "version": __version__,
        "generator": "piecemaker",
        "piece_cut_variant": args.variant if not args.svg else os.path.basename(args.svg),
        "full_size": scale_for_size_100,
        "sizes": sizes,
        "sides": tuple(range(side_count)),  # index from images
        "images": [
            dict(
                license="",
                title=os.path.splitext(os.path.basename(image))[0],
                description="",
                author_name="",
                author_url="",  # Author's profile page if applicable
                origin_url="",  # image source, image link
            ) for image in images
        ],
        "piece_count": piece_count,
        "image_width": width,
        "image_height": height,
        "outline_bbox": [
            outline_offset_x,
            outline_offset_y,
            outline_offset_x + width,
            outline_offset_y + height,
        ],
        "puzzle_author": "",
        "puzzle_link": "",
        "table_width": table_width,
        "table_height": table_height,
        "piece_distribution": " ".join(args.distribution),
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
