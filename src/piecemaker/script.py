from builtins import str
from builtins import range
import os
import json
from optparse import OptionParser
from random import randint
from math import ceil, sqrt
import shutil
from glob import iglob

from PIL import Image

from piecemaker.base import JigsawPieceClipsSVG, Pieces, variants
from piecemaker.adjacent import Adjacent
from piecemaker.tools import scale_down_imgfile, potrace, gridify, cap_dimensions
from piecemaker.sprite import generate_sprite_layout, generate_sprite_svg
from piecemaker.sprite_proof import generate_sprite_proof_html
from piecemaker.sprite_vector_proof import generate_sprite_vector_proof_html

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
        choices=list(variants),
        help=f"""Piece cut variant to use. Defaults to 'interlockingnubs'.  Other choices are: {list(variants)}""",
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

        minimum_piece_size = max(
            minimum_piece_size
            + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
            minimum_piece_size
            + (abs((height % minimum_piece_size) / minimum_piece_size - 1)),
        )
        minimum_piece_size = max(
            minimum_piece_size
            + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
            minimum_piece_size
            + (abs((height % minimum_piece_size) / minimum_piece_size - 1)),
        )
        minimum_piece_size = max(
            minimum_piece_size
            + (abs((width % minimum_piece_size) / minimum_piece_size - 1)),
            minimum_piece_size
            + (abs((height % minimum_piece_size) / minimum_piece_size - 1)),
        )
        print(f"minimum_piece_size {minimum_piece_size}")
        (rows, cols, piece_width, piece_height) = gridify(
            width, height, options.number_of_pieces, minimum_piece_size
        )
        _imagefile = imagefile
        if (
            maximum_piece_size != 0
            and maximum_piece_size > minimum_piece_size * 2
            and maximum_piece_size + minimum_piece_size < max(piece_width, piece_height)
        ):
            im = Image.open(_imagefile)
            mxpx = (maximum_piece_size * maximum_piece_size) * (rows * cols)
            (width, height) = cap_dimensions(width, height, mxpx)
            im = im.resize((width, height))
            (width, height) = im.size
            _imagefile = os.path.join(mydir, f"resized-{os.path.basename(_imagefile)}")
            im.save(_imagefile)
            im.close()
        jpc = JigsawPieceClipsSVG(
            width=width,
            height=height,
            pieces=options.number_of_pieces,
            minimum_piece_size=minimum_piece_size,
            variant=options.variant,
        )
        svgfile = os.path.join(mydir, "lines.svg")
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

        max_piece_side = max(jpc._piece_width, jpc._piece_height)
        # print(f"max piece side {max_piece_side}")
        max_piece_size = sqrt(width * height) / sqrt(jpc.pieces)
        # print(f"max piece size {max_piece_size}")
        minimum_pixels = jpc.pieces * (minimum_piece_size * minimum_piece_size)
        # print(f"minimum_pixels {minimum_pixels}")
        minimum_side = sqrt(minimum_pixels)
        # print(f"minimum_side {minimum_side}")
        side_count = sqrt(jpc.pieces)
        # print(f"side_count {side_count}")
        new_minimum_piece_size = ceil(minimum_side / side_count)
        # print(f"new_minimum_piece_size {new_minimum_piece_size}")

        minimum_scale = min(
            100, ceil((new_minimum_piece_size / max_piece_side) * 100.0)
        )

        scaled_sizes_greater_than_minimum = list(
            filter(lambda x: x >= minimum_scale, scaled_sizes)
        )
        if minimum_scale not in scaled_sizes_greater_than_minimum:
            scaled_sizes_greater_than_minimum.insert(1, minimum_scale)
        dimensions = {}
        # First one will always be '100'
        piece_count_at_100_scale = None
        for scale in scaled_sizes_greater_than_minimum:
            scaled_dir = os.path.join(mydir, f"scale-{scale}")
            os.mkdir(scaled_dir)

            pieces = Pieces(
                svgfile,
                _imagefile,
                scaled_dir,
                scale=scale,
                max_pixels=(width * height),
            )

            pieces.cut()

            pieces.generate_resources()

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
                print(
                    f"Skipping scale {scale} since the piece count is not equal to piece count at 100 scale."
                )

        # Reset minimum_scale in case it was dropped out of the dimensions.
        minimum_scale = min(100, sorted(dimensions.keys())[0])

        scaled_sizes_less_than_minimum = list(
            filter(lambda x: x < minimum_scale, scaled_sizes)
        )
        for scale in scaled_sizes_less_than_minimum:
            factor = scale / minimum_scale
            minimum_scaled_dir = os.path.join(mydir, f"scale-{minimum_scale}")
            scaled_dir = os.path.join(mydir, f"scale-{scale}")

            shutil.copytree(minimum_scaled_dir, scaled_dir)
            os.rename(
                os.path.join(scaled_dir, f"lines-{minimum_scale}.png"),
                os.path.join(scaled_dir, f"lines-{scale}.png"),
            )
            os.rename(
                os.path.join(scaled_dir, f"original-{minimum_scale}.jpg"),
                os.path.join(scaled_dir, f"original-{scale}.jpg"),
            )

            for filename in [
                "masks.json",
                "sprite_proof.html",
                "sprite.svg",
                "sprite_vector_proof.html",
                "sprite_with_padding.jpg",
                "sprite_layout.json",
            ]:
                os.unlink(os.path.join(scaled_dir, filename))
            shutil.rmtree(os.path.join(scaled_dir, "vector"))

            [
                scale_down_imgfile(imgfile, factor)
                for imgfile in iglob(f"{scaled_dir}/**/*.jpg", recursive=True)
            ]
            [
                scale_down_imgfile(imgfile, factor)
                for imgfile in iglob(f"{scaled_dir}/**/*.png", recursive=True)
            ]
            [
                scale_down_imgfile(imgfile, factor)
                for imgfile in iglob(f"{scaled_dir}/**/*.bmp", recursive=True)
            ]

            with open(os.path.join(scaled_dir, "pieces.json"), "r") as pieces_json:
                piece_bboxes = json.load(pieces_json)
            with open(
                os.path.join(scaled_dir, "piece_id_to_mask.json"), "r"
            ) as piece_id_to_mask_json:
                piece_id_to_mask = json.load(piece_id_to_mask_json)
            for (i, bbox) in piece_bboxes.items():
                # TODO: open each png in raster/ or open each non-padded bmp in mask/
                # update the width and height on bbox
                im = Image.open(
                    os.path.join(scaled_dir, "mask", f"{piece_id_to_mask[i]}.bmp")
                )
                (width, height) = im.size
                im.close()
                bbox[0] = round(bbox[0] * factor)
                bbox[1] = round(bbox[1] * factor)
                bbox[2] = width
                bbox[3] = height
            with open(os.path.join(scaled_dir, "pieces.json"), "w") as pieces_json:
                json.dump(piece_bboxes, pieces_json)

            os.mkdir(os.path.join(scaled_dir, "vector"))
            for piece in iglob(os.path.join(scaled_dir, "mask", "*.bmp")):
                potrace(piece, os.path.join(scaled_dir, "vector"))

            sprite_layout = generate_sprite_layout(
                raster_dir=os.path.join(scaled_dir, "raster_with_padding"),
                output_dir=scaled_dir,
            )
            jpg_sprite_file_name = os.path.join(scaled_dir, "sprite_with_padding.jpg")

            generate_sprite_svg(
                sprite_layout=sprite_layout,
                jpg_sprite_file_name=jpg_sprite_file_name,
                scaled_image=os.path.join(scaled_dir, f"original-{scale}.jpg"),
                output_dir=scaled_dir,
                scale=scale,
                pieces_json_file=os.path.join(scaled_dir, "pieces.json"),
                vector_dir=os.path.join(scaled_dir, "vector"),
            )

            generate_sprite_vector_proof_html(
                pieces_json_file=os.path.join(scaled_dir, "pieces.json"),
                sprite_svg_file=os.path.join(scaled_dir, "sprite.svg"),
                output_dir=scaled_dir,
                sprite_layout=sprite_layout,
                scale=scale,
            )
            generate_sprite_proof_html(
                pieces_json_file=os.path.join(scaled_dir, "pieces.json"),
                output_dir=scaled_dir,
                scale=scale,
            )

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
            scaled_dir = os.path.join(mydir, "scale-100")
            adjacent = Adjacent(scaled_dir)
            f = open(os.path.join(mydir, "adjacent.json"), "w")
            json.dump(adjacent.adjacent_pieces, f)
            f.close()
