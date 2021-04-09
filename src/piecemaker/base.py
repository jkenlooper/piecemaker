from __future__ import absolute_import
from __future__ import division
from builtins import str
from builtins import range
from builtins import object
import os
from glob import iglob
import json
#import time

import svgwrite
from PIL import Image
from bs4 import BeautifulSoup
from pixsaw.base import Handler
from glue.managers.simple import SimpleManager

from .paths import interlockingnubs, stochasticnubs
from piecemaker.tools import (
    rasterize_svgfile,
    potrace,
    cap_dimensions,
    gridify,
)
from piecemaker.sprite_proof import generate_sprite_proof_html
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

    def __init__(self, svgfile, image, mydir, scale=100, max_pixels=0, vector=True):
        " Resize the image if needed. "
        self.vector = vector
        self.mydir = mydir
        self.scale = int(scale)
        original_im = Image.open(image)
        im = original_im.copy()
        original_im.close()
        # work on a copy of the image that has been scaled
        (image_root, ext) = os.path.splitext(image)
        self._scaled_image = os.path.join(self.mydir, f"original-{self.scale}{ext}")
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
            os.path.dirname(svgfile), f"{linessvg_name}-{self.scale}.svg"
        )
        scaled_svg_file = open(scaled_svg, "w")
        # Bit of a hack to work around the lxml parser not handling the default
        # namespace.
        scaled_svg_file.write(str(svgfile_soup.svg).replace("xmlns:=", "xmlns="))
        scaled_svg_file.close()

        # rasterize the svgfile
        scaled_png = rasterize_svgfile(scaled_svg)

        self._mask_dir = os.path.join(self.mydir, "mask")
        os.mkdir(self._mask_dir)
        self._raster_dir = os.path.join(self.mydir, "raster")
        os.mkdir(self._raster_dir)
        self._raster_with_padding_dir = os.path.join(self.mydir, "raster_with_padding")
        os.mkdir(self._raster_with_padding_dir)
        if self.vector:
            self._vector_dir = os.path.join(self.mydir, "vector")
            os.mkdir(self._vector_dir)
        self._pixsaw_handler = PMHandler(
            self.mydir, scaled_png, mask_dir="mask", raster_dir="raster", jpg_dir="raster_with_padding"
        )

        self.width = width
        self.height = height

    def cut(self):
        self._pixsaw_handler.process(self._scaled_image)

        if self.vector:
            for piece in iglob(os.path.join(self._mask_dir, "*.bmp")):
                potrace(piece, self._vector_dir)

        pieces_json = open(os.path.join(self.mydir, "pieces.json"), "r")
        self.pieces = json.load(pieces_json)

    def generate_resources(self):
        " Create the extra resources to display the pieces. "

        #start = time.perf_counter()
        sprite = self._generate_sprite()
        #stop = time.perf_counter()
        #print(f"_generate_sprite {stop - start}")

        (sprite_width, sprite_height) = sprite.canvas_size
        sprite_layout = {}  # used for showing example layout
        for image in sprite.images:
            filename, ext = image.filename.rsplit(".", 1)
            sprite_layout[int(filename)] = (image.x, image.y, image.width, image.height)

        if self.vector:
            raster_png = sprite.sprite_path()

            # No warning about possible DecompressionBombWarning since the png
            # here has been generated on this side.
            Image.MAX_IMAGE_PIXELS = None

            png_sprite = Image.open(raster_png)
            jpg_sprite = png_sprite.convert("RGB")
            png_sprite.close()
            os.unlink(raster_png)
            jpg_sprite_file_name = os.path.join(self.mydir, "sprite_with_padding.jpg")
            jpg_sprite.save(jpg_sprite_file_name)
            jpg_sprite.close()
            #start = time.perf_counter()
            self._generate_vector(
                sprite_width, sprite_height, sprite_layout, jpg_sprite_file_name
            )
            #stop = time.perf_counter()
            #print(f"_generate_vector {stop - start}")
            #start = time.perf_counter()
            generate_sprite_vector_proof_html(
                pieces_json_file=os.path.join(self.mydir, "pieces.json"),
                sprite_svg_file=os.path.join(self.mydir, "sprite.svg"),
                output_dir=self.mydir,
                sprite_layout=sprite_layout,
                scale=self.scale,
            )
            #stop = time.perf_counter()
            #print(f"_sprite_vector_proof {stop - start}")

        #start = time.perf_counter()
        #self._sprite_proof(sprite_width, sprite_height, sprite_layout)
        generate_sprite_proof_html(
            pieces_json_file=os.path.join(self.mydir, "pieces.json"),
            output_dir=self.mydir,
            scale=self.scale
        )
        #stop = time.perf_counter()
        #print(f"_sprite_proof {stop - start}")

    def _generate_sprite(self):
        " create the css and sprite using glue "
        sprite_manager = SimpleManager(
            source=self._raster_with_padding_dir,
            css_namespace="pc",
            css_pseudo_class_separator="__",
            css_sprite_namespace="",
            css_url="",
            html=False,
            ratios="1",
            follow_links=False,
            quiet=True,
            recursive=False,
            force=True,
            algorithm="square",
            algorithm_ordering="maxside",
            crop=False,
            padding="0",
            margin="0",
            png8=False,
            retina=False,
            output=self.mydir,
            img_dir=self.mydir,
            css_dir=self.mydir,
            html_dir=self.mydir,
            css_cachebuster=True,
            css_cachebuster_filename=False,
            css_cachebuster_only_sprites=False,
            css_separator="-",
            enabled_formats=["img"],
        )
        sprite_manager.process()

        return sprite_manager.sprites[0]

    def _generate_vector(
        self, sprite_width, sprite_height, sprite_layout, jpg_sprite_file_name
    ):
        " parse the individual piece svg's and create the svg. "

        with open(
            os.path.join(self.mydir, "piece_id_to_mask.json"), "r"
        ) as piece_id_to_mask_json:
            piece_id_to_mask = json.load(piece_id_to_mask_json)
        dwg = svgwrite.Drawing(
            size=(0, 0),
        )
        dwg.set_desc(title="svg preview", desc="")

        common_path = os.path.commonprefix([self._scaled_image, self.mydir])
        relative_scaled_image = jpg_sprite_file_name[len(common_path) + 1:]
        source_image = dwg.defs.add(
            dwg.image(
                relative_scaled_image,
                id=f"source-image-{self.scale}",
            )
        )

        for (i, piece_bbox) in self.pieces.items():
            mask_id = piece_id_to_mask[i]
            piece_svg = os.path.join(self._vector_dir, f"{mask_id}.svg")
            preview_offset = sprite_layout[int(i)]

            piece_soup = BeautifulSoup(open(piece_svg), "xml")
            svg = piece_soup.svg
            first_g = svg.g

            clip_path = dwg.defs.add(dwg.clipPath())
            clip_path["id"] = f"piece-mask-{self.scale}-{i}"
            clip_path["transform"] = first_g.get("transform")
            clip_path["shape-rendering"] = "crispEdges"
            # Later the clip_path gets filled in with the contents

            piece_fragment = dwg.defs.add(dwg.svg())
            piece_fragment["id"] = f"piece-fragment-{self.scale}-{i}"

            vb = svg.get("viewBox")
            # TODO could also be separated by ','?
            (minx, miny, vbwidth, vbheight) = map(float, vb.split(" "))
            piece_fragment.viewbox(
                minx=preview_offset[0],
                miny=preview_offset[1],
                width=preview_offset[2],
                height=preview_offset[3],
            )
            piece_fragment["width"] = preview_offset[2]
            piece_fragment["height"] = preview_offset[3]

            piece_fragment.add(dwg.use(source_image))

        sprite_svg = BeautifulSoup(dwg.tostring(), "xml")

        for (i, piece_bbox) in self.pieces.items():
            mask_id = piece_id_to_mask[i]
            piece_svg = os.path.join(self._vector_dir, f"{mask_id}.svg")
            piece_soup = BeautifulSoup(open(piece_svg), "xml")
            svg = piece_soup.svg
            first_g = svg.find("g")
            piece_mask_tag = sprite_svg.defs.find(
                "clipPath", id=f"piece-mask-{self.scale}-{i}"
            )
            if piece_mask_tag:
                new_g = first_g.wrap(sprite_svg.new_tag("g"))
                first_g.unwrap()  # don't need this g with it's attributes
                piece_mask_tag.append(new_g)
                piece_mask_tag.g.unwrap()  # strip out the g leaving contents

        with open(os.path.join(self.mydir, "sprite.svg"), "w") as out:
            out.write(sprite_svg.decode(formatter=None))


# see adjacent.py


class JigsawPieceClipsSVG(object):
    """
    Renders a svg file of jigsaw puzzle piece paths.
    """

    title = "Jigsaw puzzle piece clips"

    def __init__(
        self, width, height, pieces=0, minimum_piece_size=42, variant="interlockingnubs"
    ):

        self.width = width
        self.height = height
        self.minimum_piece_size = minimum_piece_size
        if variant not in variants:
            raise Exception("invalid variant")
        self.HorizontalPath = globals().get(variant).HorizontalPath
        self.VerticalPath = globals().get(variant).VerticalPath
        self.pieces = pieces

        if minimum_piece_size > 0:
            # Get the maximum number of pieces that can fit within the
            # dimensions depending on the minimum piece size.
            max_pieces_that_will_fit = int(
                (width / minimum_piece_size) * (height / minimum_piece_size)
            )
            print(f"max pieces that will fit {max_pieces_that_will_fit}")
            print(f"pieces requested {self.pieces}")

            if self.pieces > 0:
                # Only use the piece count that is smaller to avoid getting too
                # small of pieces.
                self.pieces = min(max_pieces_that_will_fit, self.pieces)
            else:
                self.pieces = max_pieces_that_will_fit

        print(f"pieces adjusted {self.pieces}")

        (self._rows, self._cols, self._piece_width, self._piece_height) = gridify(width, height, self.pieces, self.minimum_piece_size)

        # adjust piece count
        self.pieces = self._rows * self._cols
        # set piece dimensions
        #self._piece_width = float(width) / float(self._cols)
        #self._piece_height = float(height) / float(self._rows)
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
            path["stroke-width"] = "1"
            path["style"] = "vector-effect:non-scaling-stroke;"
            # svgo will optimize by moving the style for vector-effect to be an
            # attribute.  path["vector-effect"] = "non-scaling-stroke"
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
            path["stroke-width"] = "1"
            path["style"] = "vector-effect:non-scaling-stroke;"
            # svgo will optimize by moving the style for vector-effect to be an
            # attribute.  path["vector-effect"] = "non-scaling-stroke"
            path["fill"] = "none"
