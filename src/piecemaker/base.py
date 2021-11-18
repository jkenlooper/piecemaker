from __future__ import absolute_import
from __future__ import division
from builtins import str
from builtins import range
from builtins import object
import os
from glob import iglob
import json
import subprocess

import svgwrite
from PIL import Image
from bs4 import BeautifulSoup
from pixsaw.base import Handler

from .paths import interlockingnubs, stochasticnubs
from piecemaker.tools import (
    rasterize_svgfile,
    potrace,
    cap_dimensions,
    gridify,
)
from piecemaker.sprite import (
    generate_data_uris,
    generate_sprite_without_padding_layout,
    generate_sprite_with_padding_layout,
    generate_sprite_svg_clip_paths,
    generate_sprite_svg_fragments,
)
from piecemaker.cut_proof import generate_cut_proof_html
from piecemaker.sprite_raster_proof import generate_sprite_raster_proof_html
from piecemaker.sprite_vector_proof import generate_sprite_vector_proof_html

variants = {
    interlockingnubs.__name__.replace("piecemaker.paths.", ""),
    stochasticnubs.__name__.replace("piecemaker.paths.", ""),
}


class PMHandler(Handler):
    mask_prefix = ""
    piece_prefix = ""


class Pieces(object):
    """
    Creates the piece pngs and pieces info.
    """

    def __init__(self, svgfile, image, mydir, scale=100, max_pixels=0, include_border_pixels=True):
        " Resize the image if needed. "
        self.mydir = mydir
        self.scale = int(scale)
        original_im = Image.open(image)
        im = original_im.copy()
        original_im.close()
        # work on a copy of the image that has been scaled
        (image_root, _) = os.path.splitext(image)
        self._scaled_image = os.path.join(self.mydir, "original-resized.jpg")
        im.save(self._scaled_image)

        if self.scale != 100:
            (w, h) = im.size
            (w, h) = cap_dimensions(w, h, max_pixels * (self.scale / 100.0))
            im = im.resize((w, h))
            im.save(self._scaled_image)

        (width, height) = im.size
        im.close()

        # scale the svg file
        svgfile_soup = BeautifulSoup(open(svgfile), "xml")
        linessvg = svgfile_soup.svg
        linessvg["width"] = width
        linessvg["height"] = height
        (linessvg_name, ext) = os.path.splitext(os.path.basename(svgfile))
        # scaled_svg is saved at the top level and not inside the scaled
        # directories
        scaled_svg = os.path.join(
            os.path.dirname(svgfile), f"{linessvg_name}-resized.svg"
        )
        scaled_svg_file = open(scaled_svg, "w")
        # Bit of a hack to work around the lxml parser not handling the default
        # namespace.
        scaled_svg_file.write(str(svgfile_soup.svg).replace("xmlns:=", "xmlns="))
        scaled_svg_file.close()

        # rasterize the svgfile
        scaled_png = rasterize_svgfile(scaled_svg, width, height)

        self._mask_dir = os.path.join(self.mydir, "mask")
        os.mkdir(self._mask_dir)
        self._raster_dir = os.path.join(self.mydir, "raster")
        os.mkdir(self._raster_dir)
        self._raster_with_padding_dir = os.path.join(self.mydir, "raster_with_padding")
        os.mkdir(self._raster_with_padding_dir)
        self._vector_dir = os.path.join(self.mydir, "vector")
        os.mkdir(self._vector_dir)
        self._pixsaw_handler = PMHandler(
            self.mydir,
            scaled_png,
            mask_dir="mask",
            raster_dir="raster",
            jpg_dir="raster_with_padding",
            include_border_pixels=include_border_pixels,
        )

        self.width = width
        self.height = height

    def cut(self):
        self._pixsaw_handler.process(self._scaled_image)
        for piece in iglob(os.path.join(self._raster_dir, "*.png")):
            subprocess.run([
                "optipng",
                "-clobber",
                "-quiet",
                piece
            ], check=True)

        for piece in iglob(os.path.join(self._mask_dir, "*.bmp")):
            potrace(piece, self._vector_dir)

        with open(os.path.join(self.mydir, "pieces.json"), "r") as pieces_json:
            self.pieces = json.load(pieces_json)

    def generate_resources(self):
        " Create the extra resources to display the pieces. "
        generate_data_uris(
            raster_dir=os.path.join(self.mydir, "raster"),
            output_dir=self.mydir,
        )

        sprite_without_padding_layout = generate_sprite_without_padding_layout(
            raster_dir=os.path.join(self.mydir, "raster"),
            output_dir=self.mydir,
        )
        sprite_with_padding_layout = generate_sprite_with_padding_layout(
            raster_dir=os.path.join(self.mydir, "raster_with_padding"),
            output_dir=self.mydir,
        )
        jpg_sprite_file_name = os.path.join(self.mydir, "sprite_with_padding.jpg")

        generate_sprite_svg_clip_paths(
            output_dir=self.mydir,
            scale=self.scale,
            pieces_json_file=os.path.join(self.mydir, "pieces.json"),
            vector_dir=self._vector_dir,
        )
        generate_sprite_svg_fragments(
            sprite_layout=sprite_with_padding_layout,
            jpg_sprite_file_name=jpg_sprite_file_name,
            scaled_image=self._scaled_image,
            output_dir=self.mydir,
            scale=self.scale,
        )

        generate_sprite_raster_proof_html(
            pieces_json_file=os.path.join(self.mydir, "pieces.json"),
            output_dir=self.mydir,
            sprite_layout=sprite_without_padding_layout,
            scale=self.scale,
        )
        generate_sprite_vector_proof_html(
            mydir=self.mydir,
            output_dir=self.mydir,
            sprite_layout=sprite_with_padding_layout,
            scale=self.scale,
        )
        generate_cut_proof_html(
            pieces_json_file=os.path.join(self.mydir, "pieces.json"),
            output_dir=self.mydir,
            scale=self.scale,
        )


class JigsawPieceClipsSVG(object):
    """
    Renders a svg file of jigsaw puzzle piece paths.
    """

    title = "Jigsaw puzzle piece clips"

    def __init__(
        self, width, height, pieces=0, minimum_piece_size=42, maximum_piece_size=85, variant="interlockingnubs"
    ):

        self.width = width
        self.height = height
        self.minimum_piece_size = minimum_piece_size
        self.maximum_piece_size = maximum_piece_size
        if variant not in variants:
            raise Exception("invalid variant")
        self.HorizontalPath = globals().get(variant).HorizontalPath
        self.VerticalPath = globals().get(variant).VerticalPath
        self.pieces = pieces
        self.stroke_width = 0.1

        if minimum_piece_size > 0:
            # Get the maximum number of pieces that can fit within the
            # dimensions depending on the minimum piece size.
            max_pieces_that_will_fit = max(2, int(
                (width / minimum_piece_size) * (height / minimum_piece_size)
            ))
            print(f"max pieces that will fit {max_pieces_that_will_fit}")
            print(f"pieces requested {self.pieces}")

            if self.pieces > 0:
                # Only use the piece count that is smaller to avoid getting too
                # small of pieces.
                self.pieces = min(max_pieces_that_will_fit, self.pieces)
            else:
                self.pieces = max_pieces_that_will_fit

        print(f"pieces adjusted {self.pieces}")

        (self._rows, self._cols, self._piece_width, self._piece_height) = gridify(
            width, height, self.pieces, self.minimum_piece_size
        )

        # adjust piece count
        self.pieces = self._rows * self._cols
        # set piece dimensions
        # self._piece_width = float(width) / float(self._cols)
        # self._piece_height = float(height) / float(self._rows)
        print(f"pieces actual {self.pieces}")
        print(f"piece size {self._piece_width} x {self._piece_height}")

        description = f"Created with the piecemaker. Piece count: {self.pieces}"
        # create a drawing
        # Use shape-rendering='optimizeSpeed' to not anti-alias the lines
        self._dwg = svgwrite.Drawing(
            size=(self.width, self.height),
            profile="full",
            **{"shape-rendering": "geometricPrecision"},
        )
        self._dwg.viewbox(width=self.width, height=self.height)
        self._dwg.stretch()
        self._dwg.set_desc(title=self.title, desc=description)

        self._create_lines()

    def svg(self, filename=None):
        if filename is None:
            return self._dwg.tostring()
        else:
            # TODO: write svg to filename
            pass

    def _create_lines(self):
        # create vertical and horizontal lines on a white background
        self._initial_bg()
        self._vertical_lines()
        self._horizontal_lines()

    def _initial_bg(self):
        layer = self._dwg.add(self._dwg.g())
        g = layer.add(self._dwg.g())
        fullsize_rect = g.add(
            self._dwg.rect(insert=(0, 0), size=(self.width, self.height))
        )
        fullsize_rect["fill"] = "white"

    def _vertical_lines(self):
        layer = self._dwg.add(self._dwg.g())
        for i in range(0, self._cols - 1):  # except last one
            g = layer.add(self._dwg.g())
            start = (i + 1) * self._piece_width
            curvelines = [
                "M 0 0 ",  # origin
                "L %f 0 " % start,
            ]
            for j in range(0, self._rows):
                interlockingnub_path = self.VerticalPath(
                    width=self._piece_height, height=self._piece_width
                )
                curvelines.append(interlockingnub_path.render())

            curvelines.append("L 0 %i " % self.height)  # end
            curveline = " ".join(curvelines)
            path = g.add(self._dwg.path(curveline))
            path["stroke"] = "black"
            path["stroke-width"] = str(self.stroke_width)
            path["style"] = "vector-effect:non-scaling-stroke;"
            path["fill"] = "none"

    def _horizontal_lines(self):
        layer = self._dwg.add(self._dwg.g())
        for i in range(0, self._rows - 1):  # except last one
            g = layer.add(self._dwg.g())
            start = (i + 1) * self._piece_height
            curvelines = [
                "M 0 0 ",
                "L 0 %f " % start,
            ]
            for j in range(0, self._cols):
                interlockingnub_path = self.HorizontalPath(
                    width=self._piece_width, height=self._piece_height
                )
                curvelines.append(interlockingnub_path.render())

            curvelines.append("L %i 0 " % self.width)  # end
            curveline = " ".join(curvelines)
            path = g.add(self._dwg.path(curveline))
            path["stroke"] = "black"
            path["stroke-width"] = str(self.stroke_width)
            path["style"] = "vector-effect:non-scaling-stroke;"
            path["fill"] = "none"
