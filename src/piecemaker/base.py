import os
import decimal
import math
from tempfile import SpooledTemporaryFile
from glob import glob
import json
import subprocess

import svgwrite
from PIL import Image
from bs4 import BeautifulSoup
from pixsaw.base import Handler
from glue.managers.simple import SimpleManager

from paths.interlockingnubs import HorizontalPath, VerticalPath
from piecemaker.tools import rasterize_svgfiles, potrace

class PMHandler(Handler):
    mask_prefix = ''
    piece_prefix = ''

class Pieces(object):
    """
    Creates the piece pngs and pieces info.
    """
    def __init__(self, svgfile, image, mydir, scale=100, max_pixels=0):
        " Resize the image if needed. "
        #self._image = image
        im = Image.open(image).copy()
        # work on a copy of the image that has been scaled
        (image_root, ext) = os.path.splitext(image)
        self._scaled_image = os.path.join(mydir, 'original-%s%s' % (scale, ext))
        im.save(self._scaled_image)

        self._mydir = mydir

        scale = int(scale)
        self.scale = scale

        if scale != 100:
            (w, h) = im.size
            w = int(w * (scale/100.0))
            h = int(h * (scale/100.0))
            im = im.resize((w, h))
            im.save(self._scaled_image)

        (width, height) = im.size

        if max_pixels > 0 and (width*height) > max_pixels:
            # resize the image using image magick @
            # TODO: how to do this with PIL?
            # '%i@' % max_pixels
            subprocess.call(['convert', self._scaled_image, '-resize', '{0}@'.format(max_pixels), '-strip', self._scaled_image])
            im = Image.open(self._scaled_image)
            (width, height) = im.size
        im.close()

        # scale the svg file
        svgfile_soup = BeautifulSoup(open(svgfile), 'xml')
        linessvg = svgfile_soup.svg
        linessvg['width'] = width
        linessvg['height'] = height
        (linessvg_name, ext) = os.path.splitext(os.path.basename(svgfile))
        # scaled_svg is saved at the top level and not inside the scaled
        # directories
        scaled_svg = os.path.join(os.path.dirname(svgfile), '%s-%s.svg' % (linessvg_name, scale))
        scaled_svg_file = open(scaled_svg, 'w')
        scaled_svg_file.write(unicode(svgfile_soup))
        scaled_svg_file.close()

        # rasterize the svgfile
        rasterize_svgfiles([scaled_svg,])
        (root, ext) = os.path.splitext(scaled_svg)
        linesfile = "%s.png" % root

        self._mask_dir = os.path.join(mydir, 'mask')
        os.mkdir(self._mask_dir)
        self._raster_dir = os.path.join(mydir, 'raster')
        os.mkdir(self._raster_dir)
        self._jpg_dir = os.path.join(mydir, 'jpg')
        os.mkdir(self._jpg_dir)
        self._vector_dir = os.path.join(mydir, 'vector')
        os.mkdir(self._vector_dir)
        self._pixsaw_handler = PMHandler(mydir, linesfile, mask_dir='mask',
                raster_dir='raster', jpg_dir='jpg')

        self.width = width
        self.height = height

    def cut(self):
        self._pixsaw_handler.process(self._scaled_image)

        for piece in glob(os.path.join(self._raster_dir, "*.png")):
            potrace(piece, self._vector_dir)

        pieces_json = open(os.path.join(self._mydir, 'pieces.json'), 'r')
        self.pieces = json.load(pieces_json)


    def generate_resources(self):
        " Create the extra resources to display the pieces. "

        sprite = self._generate_sprite()

        (sprite_width, sprite_height) = sprite.canvas_size
        sprite_layout = {} # used for showing example layout
        for image in sprite.images:
            filename, ext = image.filename.rsplit('.', 1)
            sprite_layout[int(filename)] = (image.x, image.y)

        self._generate_vector(sprite_width, sprite_height, sprite_layout)

        self._sprite_proof(sprite_width, sprite_height, sprite_layout)

    def _sprite_proof(self, sprite_width, sprite_height, sprite_layout):
        """ Create a sprite proof showing how the image was cut. Should look like
        original. """
        template = """
<!doctype html>
<html>
<head>
<title>Sprite Proof - {scale}</title>
<link rel="stylesheet" href="raster.css">
<style>
{style}
</style>
</head>
<body>
{pieces}
</body>
</html>
        """
        style = """
            .pc {
                    position: absolute;
                    text-indent: -999em;
                }
                .pc:hover {
                    text-indent: 0;
                }
        """
        pieces_html = []
        for (k, v) in self.pieces.items():
            x = v[0]
            y = v[1]
            el = """<div class='pc pc--{scale} pc-{k}' style='left:{x}px;top:{y}px;'>{k}</div>""".format(**{
                'scale': self.scale,
                'k': k,
                'x': x,
                'y': y
                })
            pieces_html.append(el)

        pieces = ''.join(pieces_html)
        html = template.format(**{
            'scale': self.scale,
            'pieces': pieces,
            'style': style
            })

        f = open(os.path.join(self._mydir, 'sprite_proof.html'), 'w')
        f.write(html)
        f.close()


    def _generate_sprite(self):
        " create the css and sprite using glue "
        sprite_manager = SimpleManager(
                source=self._raster_dir,
                css_namespace='pc',
                css_pseudo_class_separator='__',
                css_sprite_namespace='',
                css_url='',
                html=True,
                ratios='1',
                follow_links=False,
                quiet=False,
                recursive=False,
                force=False,
                algorithm='square',
                algorithm_ordering='maxside',
                crop=False,
                padding='0',
                margin='0',
                png8=False,
                retina=False,
                output=self._mydir,
                img_dir=self._mydir,
                css_dir=self._mydir,
                html_dir=self._mydir,
                css_cachebuster=True,
                css_cachebuster_filename=False,
                css_cachebuster_only_sprites=False,
                css_separator='-',
                enabled_formats=['css', 'html', 'img'],
                )
        sprite_manager.process()

        return sprite_manager.sprites[0]

    def _generate_vector(self, sprite_width, sprite_height, sprite_layout):
        " parse the individual piece svg's and create the svg. "

        dwg = svgwrite.Drawing(size=(sprite_width, sprite_height), profile="full")
        dwg.viewbox(width=sprite_width, height=sprite_height)
        dwg.set_desc(title="svg preview", desc="")

        common_path = os.path.commonprefix([self._scaled_image, self._mydir])
        relative_scaled_image = self._scaled_image[len(common_path)+1:]
        source_image = dwg.defs.add(dwg.image(relative_scaled_image,
            id="source-image-%s" % self.scale, width=self.width, height=self.height))

        for i in range(0,len(self.pieces)):
            piece_svg = os.path.join(self._vector_dir, "%s.svg" % i)
            piece_bbox = self.pieces[str(i)]
            preview_offset = sprite_layout[i]

            piece_soup = BeautifulSoup(open(piece_svg), 'xml')
            svg = piece_soup.svg
            first_g = svg.g

            clip_path = dwg.defs.add(dwg.clipPath())
            clip_path['id'] = "piece-mask-%s-%s" % (self.scale, i)
            clip_path['transform'] = first_g.get('transform')
            # Later the clip_path gets filled in with the contents

            piece_fragment = dwg.defs.add(dwg.svg())
            piece_fragment['id'] = "piece-fragment-%s-%s" % (self.scale, i)

            vb = svg.get('viewBox')
            #TODO could also be separated by ','?
            (minx, miny, vbwidth, vbheight) = vb.split(' ')
            piece_fragment.viewbox(
                    minx=piece_bbox[0],
                    miny=piece_bbox[1],
                    width=vbwidth,
                    height=vbheight)
            piece_fragment['width'] = vbwidth
            piece_fragment['height'] = vbheight

            use = piece_fragment.add(dwg.use(source_image))

            example_use = dwg.add(dwg.use(piece_fragment,
                clip_path="url(#piece-mask-%s-%s)" % (self.scale, i)))
            # layout the svg pieces exactly like glue did.
            example_use['transform'] = "translate( %s, %s )" % (preview_offset)
            example_use['class'] = 'example'

        preview_soup = BeautifulSoup(dwg.tostring(), 'xml')

        for i in range(0,len(self.pieces)):
            piece_svg = os.path.join(self._vector_dir, "%s.svg" % i)
            piece_soup = BeautifulSoup(open(piece_svg), 'xml')
            svg = piece_soup.svg
            first_g = svg.find('g')
            piece_mask_tag = preview_soup.defs.find("clipPath",
                    id="piece-mask-%s-%s" % (self.scale, i))
            if piece_mask_tag:
                new_g = first_g.wrap( preview_soup.new_tag('g') )
                first_g.unwrap() # don't need this g with it's attributes
                piece_mask_tag.append(new_g)
                piece_mask_tag.g.unwrap() # strip out the g leaving contents

        out = open(os.path.join(self._mydir, "preview.svg"), 'w')
        out.write(preview_soup.prettify())
        out.close()

# see adjacent.py

class JigsawPieceClipsSVG(object):
    """
    Renders a svg file of jigsaw puzzle piece paths.
    """
    title = "Jigsaw puzzle piece clips"
    minimum_count_of_pieces = 9
    maximum_count_of_pieces = 50000 #how many is too many?

    def __init__(self, width, height, pieces=0, minimum_piece_size=42,
            ):

        if minimum_piece_size > 0:
            # Get the maximum number of pieces that can fit within the
            # dimensions depending on the minimum piece size.
            max_pieces_that_will_fit = int((width/minimum_piece_size)*(height/minimum_piece_size))
            if pieces > 0:
                # Only use the piece count that is smaller to avoid getting too
                # small of pieces.
                pieces = min(max_pieces_that_will_fit, pieces)
            else:
                pieces = max_pieces_that_will_fit

        pieces = max(pieces, self.minimum_count_of_pieces)
        pieces = min(pieces, self.maximum_count_of_pieces)

        (self._rows, self._cols) = self._gridify(width, height, pieces)

        #adjust piece count
        pieces = self._pieces = self._rows*self._cols
        #set piece dimensions
        self._piece_width = float(width)/float(self._cols)
        self._piece_height = float(height)/float(self._rows)

        self._width = width
        self._height = height

        description = "Created with the piecemaker. Piece count: %i" % pieces
        # create a drawing
        # Use shape-rendering='optimizeSpeed' to not anti-alias the lines
        self._dwg = svgwrite.Drawing(size=(self._width,self._height), profile='full', **{'shape-rendering': 'optimizeSpeed'})
        self._dwg.viewbox(width=self._width, height=self._height)
        self._dwg.stretch()
        self._dwg.set_desc(title=self.title, desc=description)

        self._create_lines()

    def _gridify(self, width, height, pieces, add_more_pieces=True):
        """
        Based on area of the box, determine the count of rows and cols that
        will meet the number of pieces.
        """
        area = decimal.Decimal(width * height)
        s = area.sqrt()
        n = decimal.Decimal(pieces).sqrt()
        piece_size = float(s/n)
        # use math.ceil to at least have the target count of pieces
        rounder = math.ceil
        if not add_more_pieces:
            rounder = math.floor
        rows = int(rounder(height/piece_size))
        cols = int(rounder(width/piece_size))
        return (rows, cols)

    def svg(self, filename=None):
        if not filename:
            return self._dwg.tostring()
        else:
            #TODO: write svg to filename
            pass

    def _create_lines(self):
        # create vertical and horizontal lines on a white background
        self._initial_bg()
        self._vertical_lines()
        self._horizontal_lines()

    def _initial_bg(self):
        layer = self._dwg.add(self._dwg.g())
        g = layer.add(self._dwg.g())
        fullsize_rect = g.add(self._dwg.rect(insert=(0,0), size=(self._width, self._height)))
        fullsize_rect['fill'] = 'white'

    def _vertical_lines(self):
        layer = self._dwg.add(self._dwg.g())
        for i in range(0, self._cols-1): #except last one
            g = layer.add(self._dwg.g())
            start = (i+1)*self._piece_width
            curvelines = [
                    'M 0 0 ', # origin
                    'L %f 0 ' % start,
                    ]
            for j in range(0, self._rows):
                interlockingnub_path = VerticalPath(width=self._piece_height)
                curvelines.append(interlockingnub_path.render())

            curvelines.append('L 0 %i ' % self._height) # end
            curveline = ' '.join(curvelines)
            path = g.add(self._dwg.path(curveline))
            path['stroke'] = 'black'
            path['stroke-width'] = '1'
            path['fill'] = 'none'

    def _horizontal_lines(self):
        layer = self._dwg.add(self._dwg.g())
        for i in range(0, self._rows-1): #except last one
            g = layer.add(self._dwg.g())
            start = (i+1)*self._piece_height
            curvelines = [
                    'M 0 0 ',
                    'L 0 %f ' % start,
                    ]
            for j in range(0, self._cols):
                interlockingnub_path = HorizontalPath(width=self._piece_width)
                curvelines.append(interlockingnub_path.render())

            curvelines.append('L %i 0 ' % self._width) # end
            curveline = ' '.join(curvelines)
            path = g.add(self._dwg.path(curveline))
            path['stroke'] = 'black'
            path['stroke-width'] = '1'
            path['fill'] = 'none'
