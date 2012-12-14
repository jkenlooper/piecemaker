import os
import decimal
import math
from tempfile import SpooledTemporaryFile
from glob import glob

import svgwrite
from PIL import Image
from bs4 import BeautifulSoup
from scissors.base import Scissors, Clips


from paths.interlockingnubs import HorizontalPath, VerticalPath

class Pieces(object):
    """
    Creates the piece pngs and pieces info. Lets Scissors do most of the work.
    """
    def __init__(self, svgfile, image, mydir, scale=100, max_pixels=0):
        " Resize the image if needed. "
        # TODO: work on a copy of the image or not?
        self._image = image
        im = Image.open(image)

        self._mydir = mydir

        scale = int(scale)

        if scale != 100:
            (w, h) = im.size
            w = int(w * (scale/100.0))
            h = int(h * (scale/100.0))
            im.resize((w, h))

        (width, height) = im.size

        if max_pixels > 0 and (width*height) > max_pixels:
            # resize the image using image magick @
            # TODO: how to do this with PIL?
            # '%i@' % max_pixels
            (width, height) = im.size

        im.save(image)

        self._clips = Clips(svgfile=svgfile,
                    clips_dir=mydir,
                    size=(width, height))

        self.width = width
        self.height = height

    def cut(self):
        scissors = Scissors(self._clips, self._image, self._mydir)
        scissors.cut()

    def generate_resources(self):
        " Create the extra resources to display the pieces. "
        # TODO: create the css and sprite using glue

        # TODO: use the width and height from the glue sprite.
        sprite_width = 1024
        sprite_height = 1024

        # TODO: layout the svg pieces exactly like glue did.

        # parse the individual piece svg's and create the svg
        dwg = svgwrite.Drawing(size=(sprite_width, sprite_height), profile="full")
        dwg.viewbox(width=sprite_width, height=sprite_height)
        dwg.set_desc(title="svg preview", desc="")

        source_image = dwg.defs.add(dwg.image())
        source_image['id'] = "source-image"
        source_image['width'] = self.width #TODO: set px on these?
        source_image['height'] = self.height
        source_image['xlink:href'] = self._image

        i = 0
        for piece_svg in glob(os.path.join(self._mydir, "*.svg")):
            i = i + 1

            piece_soup = BeautifulSoup(open(piece_svg), 'xml')
            svg = piece_soup.svg
            first_g = svg.g

            clip_path = dwg.defs.add(dwg.clipPath())
            clip_path['id'] = "piece-mask-%s" % i
            clip_path['transform'] = first_g.get('transform')
            # Later the clip_path gets filled in with the contents

            piece_fragment = dwg.defs.add(dwg.svg())
            piece_fragment['id'] = "piece-fragment-%s" % i

            vb = svg.get('viewBox')
            #TODO could also be separated by ','?
            (minx, miny, vbwidth, vbheight) = vb.split(' ')
            #TODO get offset for this piece and set it on the viewbox
            piece_fragment.viewbox(width=vbwidth, height=vbheight)
            piece_fragment['width'] = vbwidth
            piece_fragment['height'] = vbheight

            use = piece_fragment.add(dwg.use(source_image))

            #for tag in first_g.children:
            #    path = clip_path.add(dwg.path())
            #    path['d'] = first_
        preview_soup = BeautifulSoup(dwg.tostring(), 'xml')
        for piece_svg in glob(os.path.join(self._mydir, "*.svg")):
            i = i + 1
            piece_soup = BeautifulSoup(open(piece_svg), 'xml')
            svg = piece_soup.svg
            first_g = svg.g
            piece_mask_tag = preview_soup.find(id="piece-mask-%s" % i)
            piece_mask_tag.append(first_g.contents)
        

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
        self._dwg = svgwrite.Drawing(size=(self._width,self._height), profile='full')
        self._dwg.viewbox(width=self._width, height=self._height)
        self._dwg.stretch()
        self._dwg.set_desc(title=self.title, desc=description)

        self._create_layers()

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

    def _create_layers(self):
        # create 2 layers
        self._vertical_layer()
        self._horizontal_layer()

    def _vertical_layer(self):
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
        g = layer.add(self._dwg.g())
        fullsize_rect = g.add(self._dwg.rect(insert=(0,0), size=(self._width, self._height)))

    def _horizontal_layer(self):
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
        g = layer.add(self._dwg.g())
        fullsize_rect = g.add(self._dwg.rect(insert=(0,0), size=(self._width, self._height)))



