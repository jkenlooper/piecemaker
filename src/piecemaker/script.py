import os
import json
import subprocess
from optparse import OptionParser
from random import randint

from setuptools_scm import get_version
from PIL import Image

from piecemaker.base import JigsawPieceClipsSVG, Pieces
from piecemaker.adjacent import Adjacent

def piecemaker():
    parser = OptionParser(usage="%prog [options] path/to/image",
            version=get_version(),
            description="create jigsaw puzzle pieces")

    parser.add_option("--dir", "-d",
            action="store",
            type="string",
            help="Set the directory to store the files in.",)
    parser.add_option("--number-of-pieces", "-n",
            action="store",
            default=0,
            type="int",
            help="""
Target count of pieces. Will be adjusted depending on other
criteria. If set to 0 then will fit as many pieces in depending on
the minimum piece size.
            """,)
    parser.add_option("--svg", "-s",
            action="store",
            type="string",
            help="Set the clips svg file instead of creating jigsaw pieces.",)
    parser.add_option("--minimum-piece-size",
            action="store",
            type="int",
            default=42,
            help="Minimum piece size.  Will change the count of pieces to meet this if not set to 0.",)

    parser.add_option("--max-pixels",
            action="store",
            type="int",
            default=0,
            help="""
            Maximum pixels for the image.  Will scale down the original image
            to meet this requirement if not set to 0.
            """,)
    parser.add_option("--scaled-sizes",
            action="store",
            type="string",
            default="100",
            help="""
            List of sizes to scale for. Separated with commas. example:
            33,68,100,150 for 4 scaled puzzles with the last one being at 150%.
            """,)

    parser.add_option("--just-clips",
            action="store_true",
            default=False,
            help="Only create a clips svg file",)

    parser.add_option("--width",
            action="store",
            type="int",
            help="""
            Width of the image or clips svg viewbox, will scale to this width
            if image is set.
            """,)
    parser.add_option("--height",
            action="store",
            type="int",
            help="""
            Height of the image or clips svg viewbox, will scale to this height
            if image is set.
            """,)

    parser.add_option("--adjacent",
            action="store_true",
            default=True,
            help="""
            Create the adjacent.json file with list of adjacent pieces for each
            piece.
            """,)

    (options, args) = parser.parse_args()

    if not options.dir:
        parser.error("Must set a directory to store generated files")

    if not options.just_clips and not args:
        parser.error("Must set an image if not just making clips.")

    if len(args) > 1:
        parser.error("Multiple pictures are not supported, yet.")

    if not "100" in options.scaled_sizes:
        parser.error("Must have at least a '100' in scaled sizes.")
    scaled_sizes = [int(x) for x in options.scaled_sizes.split(',')]


    if args:
        imagefile = args[0]

    if not options.svg:
        # create a grid of puzzle pieces in svg
        if options.minimum_piece_size < 0:
            parser.error("Invalid minimum piece size")

        if options.number_of_pieces < 0:
            parser.error("Invalid number of pieces")

        if (options.minimum_piece_size < 1 and options.number_of_pieces < 1):
            parser.error("Must set minimum piece size greater than 0 or set number of pieces greater then 0.")

        if not args and not (options.width and options.height):
            parser.error("Must set an image or specify both width and height.")

        if args and not (options.width and options.height):
            #TODO: handle more then just one picture
            im = Image.open(imagefile)
            (width, height) = im.size
        else:
            width = options.width
            height = options.height


        jpc = JigsawPieceClipsSVG(
                width=width,
                height=height,
                pieces=options.number_of_pieces,
                minimum_piece_size=options.minimum_piece_size)
        svgfile = os.path.join(options.dir, 'lines.svg')
        f = open(svgfile, 'w')
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

        piece_count = 0
        dimensions = {}
        for scale in scaled_sizes:
            scaled_dir = os.path.join(mydir, 'scale-%i' % scale)
            os.mkdir(scaled_dir)

            pieces = Pieces(svgfile, imagefile, scaled_dir, scale=scale, max_pixels=options.max_pixels)

            pieces.cut()

            pieces.generate_resources()

            piece_count = len(pieces.pieces)
            piece_bboxes = pieces.pieces
            dimensions[scale] = {
                    "width": pieces.width,
                    "height": pieces.height,
                    "table_width": int(pieces.width * 2.5),
                    "table_height": int(pieces.height * 2.5),
                    "board_url": "puzzle_board-%s.html" % scale,
                    }

        tw = dimensions[100]['table_width']
        th = dimensions[100]['table_height']
        piece_properties = []
        for i in range(0, piece_count):
            piece_properties.append({
                  "id": i,
                  "x": randint(0,tw),
                  "y": randint(0,th),
                  "w": piece_bboxes[str(i)][2] - piece_bboxes[str(i)][0],
                  "h": piece_bboxes[str(i)][3] - piece_bboxes[str(i)][1],
                  "r": 0,
                  "s": 0,
                  "g": 0
                })
        # create index.json
        data = {
                "version": "alpha",
                "generator": "piecemaker cli",
                "scaled": scaled_sizes,
                "sides": [0],
                "piece_count": piece_count,
                "image_author": "none",
                "image_link": "none",
                "image_title": "none",
                "image_description": "none",
                "puzzle_author": "yup",
                "puzzle_link": "yup",
                "scaled_dimensions": dimensions,
                "piece_properties": piece_properties,
                }
        f = open(os.path.join(mydir, 'index.json'), 'w')
        json.dump(data, f, indent=4)
        f.close()

        if options.adjacent:
            first_scaled_dir = os.path.join(mydir, 'scale-%i' % scaled_sizes[0])
            adjacent = Adjacent(first_scaled_dir)
            f = open(os.path.join(mydir, 'adjacent.json'), 'w')
            json.dump(adjacent.adjacent_pieces, f)
            f.close()

